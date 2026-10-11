"""Controlled 17-mechanism studies using the production review pipeline."""

from __future__ import annotations

import json
import shutil
from dataclasses import replace
from pathlib import Path

from prthinker.benchmark_execution import CountingRetriever
from prthinker.benchmark_measurement import MeasuredBackend
from prthinker.benchmark_scoring import _score_outcome
from prthinker.benchmark_session import (
    CaseExecution,
    UnsupportedCaseError,
    file_hash,
    run_session,
    verify_bundle,
    write_json,
)
from prthinker.finding_clusters import (
    FindingClusterStore,
    format_clusters_block,
    greedy_cluster,
)
from prthinker.incremental_save import IncrementalReviewWriter, ReviewMeta
from prthinker.injection_guard import redact_injection
from prthinker.lessons import LessonsStore, format_lessons_block
from prthinker.paired_statistics import holm, paired_summary
from prthinker.pipeline import CoTPipeline
from prthinker.pipeline_types import PerFileReviewOptions
from prthinker.rag import NoOpRetriever
from prthinker.repo_kg import KnowledgeGraphStore, format_kg_block
from prthinker.review_cache import ReviewCache

MECHANISMS = (
    "adversarial_robustness", "dialogue", "counterfactual", "provenance",
    "force_push_differential", "suggestion_sandbox", "api_drift", "pr_type",
    "reproducibility", "dependency_upgrade", "personas", "risk_weighted",
    "diff_entropy", "lessons", "clustering", "knowledge_graph", "incremental_save",
)
_OPTIONS = {
    "counterfactual": {"counterfactual": True}, "provenance": {"provenance": True},
    "suggestion_sandbox": {"verify_suggestions": True},
    "api_drift": {"api_consistency_check": True}, "pr_type": {"pr_classify": True},
    "reproducibility": {"reproducibility_check": True},
    "dependency_upgrade": {"dep_upgrade_check": True},
    "personas": {"persona_set": ("security", "performance", "readability")},
    "risk_weighted": {"risk_weighted": True}, "diff_entropy": {"diff_entropy_check": True},
}
_FIXTURES = {
    "dialogue": "dialogue", "force_push_differential": "cache",
    "suggestion_sandbox": "workdir", "risk_weighted": "workdir",
    "lessons": "lessons", "clustering": "clusters", "knowledge_graph": "kg",
}


def make_plan(controls: dict, cases: Path) -> dict:
    required = ("model_revision", "adapter_state", "precision", "steps", "decoding_mode", "max_new_tokens")
    if any(key not in controls for key in required):
        raise ValueError("control configuration must pin model, adapter, precision, steps, decoding and generation limit")
    return {
        "schema_version": 1, "cases_sha256": file_hash(cases), "controls": controls,
        "conditions": [{"name": "control", "changed_factor": None}] +
                      [{"name": name, "changed_factor": name} for name in MECHANISMS],
        "correction_family": "all treatment-by-dimension tests",
    }


def validate_plan(plan: dict, cases: Path):
    expected = make_plan(plan["controls"], cases)
    if plan != expected:
        raise ValueError("study plan must contain the fixed control and exactly 17 single-factor treatments")


class StudyExecution:
    """Every condition gets fresh pipeline state and an isolated fixture copy."""

    def __init__(self, backend, controls, factor, directory, fixtures=None, retriever=None):
        self.backend, self.controls, self.factor = MeasuredBackend(backend), controls, factor
        self.directory = directory
        self.fixtures = fixtures or {}
        self.retriever = CountingRetriever(retriever or NoOpRetriever())

    def __call__(self, case):
        required = _FIXTURES.get(self.factor)
        if required and required not in self.fixtures:
            raise UnsupportedCaseError(f"{self.factor} requires frozen {required} fixtures")
        self.retriever.count = 0
        self.backend.reset()
        diff = case.prompt
        if self.factor == "adversarial_robustness":
            diff = redact_injection(diff)
        options = PerFileReviewOptions(inline_review=True, **_OPTIONS.get(self.factor, {}))
        options = self._configure(options, case)
        pipeline = CoTPipeline(self.backend, self.retriever, steps=tuple(self.controls["steps"]),
                               max_new_tokens=self.controls["max_new_tokens"])
        result = pipeline.run_per_file(diff, options)
        payload = {"findings": [finding.model_dump(mode="json") for finding in result.inline_findings],
                   "step_outputs": result.step_outputs}
        if self.factor == "clustering":
            payload["clusters"] = [cluster.size for cluster in greedy_cluster(FindingClusterStore(Path(self.fixtures["clusters"])).load())]
        return CaseExecution(json.dumps(payload, ensure_ascii=False), self.retriever.count, **self.backend.metrics())

    def _configure(self, options, case):
        factor, fixtures = self.factor, self.fixtures
        if factor == "dialogue":
            options = replace(options, dialogue_block=fixtures["dialogue"])
        if factor == "lessons":
            options = replace(options, dialogue_block=format_lessons_block(list(LessonsStore(Path(fixtures["lessons"])))))
        if factor == "clustering":
            clusters = greedy_cluster(FindingClusterStore(Path(fixtures["clusters"])).load())
            options = replace(options, dialogue_block=format_clusters_block(clusters))
        if factor == "knowledge_graph":
            if not fixtures.get("workdir"):
                raise UnsupportedCaseError("knowledge graph requires a frozen workdir")
            store = KnowledgeGraphStore(Path(fixtures["kg"]))
            options = replace(options, dialogue_block=format_kg_block(store.all_symbols(Path(fixtures["workdir"]))))
        if factor == "force_push_differential":
            options = replace(options, review_cache=ReviewCache(Path(fixtures["cache"])),
                              cache_repo="study", cache_pr_number=1)
        if factor == "risk_weighted":
            options = replace(options, risk_workdir=Path(fixtures["workdir"]))
        if factor == "suggestion_sandbox":
            if not fixtures.get("verify_cmd"):
                raise UnsupportedCaseError("suggestion sandbox requires a frozen verification command")
            options = replace(options, verify_workdir=Path(fixtures["workdir"]), verify_cmd=fixtures["verify_cmd"])
        if factor == "incremental_save":
            writer = IncrementalReviewWriter(self.directory / "incremental" / file_hash_text(case.case_id),
                                             meta=ReviewMeta(repo="study", pr_number=1, head_sha="fixed", started_at="fixed"))
            options = replace(options, on_file_done=writer.write_file_result)
        return options


def file_hash_text(text: str) -> str:
    import hashlib
    return hashlib.sha256(text.encode()).hexdigest()


def run_study(plan: dict, cases: Path, output: Path, factory, *, fixtures=None, retriever_factory=None):
    validate_plan(plan, cases)
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / "study.json", plan)
    frozen = _freeze_fixtures(fixtures or {}, output / "fixtures")
    for condition in plan["conditions"]:
        directory = output / condition["name"]
        backend = factory(plan["controls"])
        try:
            state = _freeze_fixtures(frozen, output / ("state-" + condition["name"]))
            strategy = StudyExecution(backend, plan["controls"], condition["changed_factor"],
                                      directory, fixtures=state,
                                      retriever=retriever_factory() if retriever_factory else None)
            run_session(cases, directory, strategy,
                        controls=plan["controls"] | {"changed_factor": condition["changed_factor"]})
        finally:
            backend.close()


def _freeze_fixtures(fixtures, destination):
    """Copy mutable databases per condition; callers' stores stay immutable."""
    destination.mkdir(parents=True, exist_ok=False)
    frozen = dict(fixtures)
    hashes = {}
    if "workdir" in fixtures:
        source = Path(fixtures["workdir"]).resolve()
        target = destination / "workdir"
        shutil.copytree(source, target, symlinks=True,
                        ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__"))
        frozen["workdir"] = str(target)
        hashes["workdir"] = {path.relative_to(target).as_posix(): file_hash(path)
                             for path in sorted(target.rglob("*"))
                             if path.is_file() and not path.is_symlink()}
    for key in ("cache", "lessons", "clusters", "kg"):
        if key in fixtures:
            source = Path(fixtures[key])
            target = destination / (key + source.suffix)
            shutil.copyfile(source, target)
            frozen[key] = str(target)
            if key == "kg" and "workdir" in fixtures:
                store = KnowledgeGraphStore(target)
                original_root = Path(fixtures["workdir"])
                store.rebuild(Path(frozen["workdir"]), store.all_symbols(original_root),
                              store.all_imports(original_root))
            hashes[key] = file_hash(target)
    write_json(destination / "manifest.json", {"hashes": hashes})
    return frozen


def compare_study(directory: Path, *, samples=2000, seed=0) -> dict:
    plan = json.loads((directory / "study.json").read_text(encoding="utf-8"))
    validate_plan(plan, directory / "control" / "cases.jsonl")
    control = verify_bundle(directory / "control")
    if control["controls"] != plan["controls"] | {"changed_factor": None}:
        raise ValueError("baseline controls do not match study plan")
    baseline = _scores(directory / "control")
    reports = []
    for condition in plan["conditions"][1:]:
        manifest = verify_bundle(directory / condition["name"])
        expected = plan["controls"] | {"changed_factor": condition["changed_factor"]}
        if manifest["controls"] != expected or manifest["dataset"]["sha256"] != plan["cases_sha256"]:
            raise ValueError("ablation condition changed an uncontrolled factor")
        current = _scores(directory / condition["name"])
        paired = sorted(baseline.keys() & current.keys())
        for dimension in ("precision", "recall", "f1"):
            differences = [getattr(current[key], dimension) - getattr(baseline[key], dimension) for key in paired]
            report = paired_summary(differences, samples=samples, seed=seed)
            reports.append({"treatment": condition["name"], "dimension": dimension,
                            "excluded_pairs": len(plan_case_ids(directory)) - len(paired), **report})
    measured = [report for report in reports if report["p_value"] is not None]
    for report, probability in zip(measured, holm([report["p_value"] for report in measured])):
        report["holm_p_value"] = probability
    return {"schema_version": 1, "measurement": "objective_matching", "comparisons": reports,
            "correction_family": "all treatment-by-dimension tests", "seed": seed}


def plan_case_ids(directory):
    return verify_bundle(directory / "control")["case_order"]


def _scores(directory):
    verify_bundle(directory)
    cases = {row["case_id"]: row for row in map(json.loads, (directory / "cases.jsonl").read_text(encoding="utf-8").splitlines())}
    rows = map(json.loads, (directory / "outcomes.jsonl").read_text(encoding="utf-8").splitlines())
    return {row["case_id"]: _score_outcome(row["case_id"], row["raw_output"],
                                          cases[row["case_id"]].get("metadata", {}))
            for row in rows if row["status"] == "success"}

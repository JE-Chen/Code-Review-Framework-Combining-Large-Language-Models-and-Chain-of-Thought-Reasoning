"""Controlled study plans cannot silently change multiple factors."""

import json

import pytest

from prthinker.ablation_study import (
    MECHANISMS,
    compare_study,
    make_plan,
    run_study,
    validate_plan,
)
from prthinker.paired_statistics import holm, paired_summary, wilcoxon
from tests.conftest import FakeBackend

CONTROLS = {"model_revision": "fixed", "adapter_state": "none", "precision": "bf16",
            "steps": ["first_summary"], "decoding_mode": "greedy", "max_new_tokens": 32}


def cases(tmp_path):
    source = tmp_path / "cases.jsonl"
    source.write_text(json.dumps({"case_id": "a", "prompt": "diff --git a/mod.py b/mod.py\n--- a/mod.py\n+++ b/mod.py\n@@ -1 +1 @@\n-x=1\n+x=2\n",
                                  "metadata": {"ground_truth": []}}) + "\n", encoding="utf-8")
    return source


def test_plan_has_exactly_seventeen_controlled_treatments(tmp_path):
    source = cases(tmp_path)
    plan = make_plan(CONTROLS, source)
    assert len(plan["conditions"]) == 18
    assert {row["changed_factor"] for row in plan["conditions"][1:]} == set(MECHANISMS)
    validate_plan(plan, source)
    plan["conditions"].pop()
    with pytest.raises(ValueError):
        validate_plan(plan, source)


def test_study_records_unsupported_conditions_instead_of_fake_success(tmp_path):
    source = cases(tmp_path)
    target = tmp_path / "study"
    plan = make_plan(CONTROLS, source)
    run_study(plan, source, target, lambda _controls: FakeBackend(["[]"] * 30))
    report = compare_study(target, samples=10)
    assert len(report["comparisons"]) == 51
    for name in ("dialogue", "lessons", "knowledge_graph"):
        manifest = json.loads((target / name / "manifest.json").read_text())
        assert manifest["outcomes"]["states"]["unsupported"] == 1
    assert all(row.get("holm_p_value", 1) >= row["p_value"] for row in report["comparisons"] if row["p_value"] is not None)


def test_exact_paired_statistics():
    assert wilcoxon([1, 1, 1])["p_value"] == 0.25
    assert wilcoxon([0, 0])["p_value"] == 1
    assert paired_summary([])["mean_difference"] is None
    assert paired_summary([1, 1], samples=10)["ci95"] == [1, 1]
    assert holm([0.01, 0.04, 0.03]) == pytest.approx([0.03, 0.06, 0.06])
    large = wilcoxon([1] * 1000)
    assert "normal approximation" in large["method"]
    assert large["p_value"] < 1e-15
    with pytest.raises(ValueError, match="finite"):
        wilcoxon([float("nan")])


def test_frozen_repository_and_graph_are_remapped_and_isolated(tmp_path):
    from pathlib import Path

    from prthinker.ablation_study import _freeze_fixtures
    from prthinker.repo_kg import KnowledgeGraphStore, Symbol

    repository = tmp_path / "repository"
    repository.mkdir()
    (repository / "mod.py").write_text("def original(): pass\n")
    database = tmp_path / "graph.sqlite"
    KnowledgeGraphStore(database).rebuild(repository, [Symbol("original", "function", "mod.py", 1)])
    frozen = _freeze_fixtures({"workdir": str(repository), "kg": str(database)}, tmp_path / "frozen")
    assert KnowledgeGraphStore(Path(frozen["kg"])).all_symbols(Path(frozen["workdir"]))[0].symbol == "original"
    (Path(frozen["workdir"]) / "mod.py").write_text("changed")
    assert "original" in (repository / "mod.py").read_text()


def test_study_counts_rules_that_actually_enter_prompts(tmp_path):
    from prthinker.ablation_study import StudyExecution
    from prthinker.benchmark import load_cases
    from prthinker.rag import RAGRetriever

    class Retriever(RAGRetriever):
        def retrieve(self, _prompt):
            return ["FIXED_RETRIEVED_RULE"]

    backend = FakeBackend(["[]"] * 10)
    execute = StudyExecution(backend, CONTROLS, None, tmp_path, retriever=Retriever())
    result = execute(load_cases(cases(tmp_path))[0])
    assert result.retrieved_documents > 0
    assert any("FIXED_RETRIEVED_RULE" in prompt for prompt, _limit in backend.calls)

"""CLI handlers for deterministic benchmark conversion and evaluation."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from prthinker.ablation import compare_runs
from prthinker.benchmark_datasets import convert_dataset
from prthinker.benchmark_execution import PromptExecution, ReviewExecution
from prthinker.benchmark_measurement import public_configuration
from prthinker.benchmark_scoring import aggregate, score_files
from prthinker.benchmark_session import (
    file_hash,
    run_session,
    validate_dataset_manifest,
    verify_bundle,
)
from prthinker.cli_io import emit_text

DATASETS = (
    "codefuse-cr-bench",
    "swe-prbench",
    "contextcrbench",
    "swrbench",
    "c-crab",
    "codereviewqa",
    "contextbench",
    "core-bench",
)


def add_benchmark_parser(sub, common=None) -> None:
    root = sub.add_parser(
        "benchmark", help="Convert, score, and compare review benchmarks"
    )
    actions = root.add_subparsers(dest="benchmark_action", required=True)
    convert = actions.add_parser("convert")
    convert.add_argument("source", type=Path)
    convert.add_argument("target", type=Path)
    convert.add_argument("--dataset", required=True, choices=DATASETS)
    run = actions.add_parser("run", parents=[common] if common is not None else [])
    run.add_argument("cases", type=Path)
    run.add_argument("output_dir", type=Path)
    run.add_argument("--benchmark-model", default="")
    run.add_argument("--seed", type=int, default=None)
    run.add_argument("--dataset-manifest", type=Path)
    run.add_argument("--control-manifest", type=Path)
    run.add_argument("--review-pipeline", action="store_true")
    validate = actions.add_parser("validate")
    validate.add_argument("directory", type=Path)
    score = actions.add_parser("score")
    score.add_argument("cases", type=Path)
    score.add_argument("outcomes", type=Path)
    score.add_argument("--output", type=Path)
    score.add_argument("--bootstrap-samples", type=int, default=1000)
    score.add_argument("--seed", type=int, default=0)
    compare = actions.add_parser("compare")
    compare.add_argument("cases", type=Path)
    compare.add_argument("baseline", type=Path)
    compare.add_argument("treatment", type=Path)
    compare.add_argument("--baseline-name", default="baseline")
    compare.add_argument("--treatment-name", default="treatment")
    compare.add_argument("--output", type=Path)
    compare.add_argument("--bootstrap-samples", type=int, default=2000)
    compare.add_argument("--seed", type=int, default=0)


def _emit(payload, output: Path | None) -> None:
    emit_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", output)


def _run_convert(args: argparse.Namespace) -> int:
    """Handle ``benchmark convert``."""
    count = convert_dataset(args.source, args.target, dataset=args.dataset)
    _emit({"dataset": args.dataset, "cases": count, "output": str(args.target)}, None)
    return 0


def _run_benchmark(args: argparse.Namespace) -> int:
    """Handle ``benchmark run`` by executing cases against a backend."""
    from prthinker.backends import create_backend
    from prthinker.cli_review import _build_config, _build_retriever

    if args.output_dir.exists():
        raise FileExistsError(f"benchmark output directory already exists: {args.output_dir}")
    config = _build_config(args)
    controls = json.loads(args.control_manifest.read_text(encoding="utf-8")) if args.control_manifest else {}
    resolved = {"seed": args.seed, "max_new_tokens": config.max_new_tokens,
                "steps": list(config.steps)}
    if args.seed is None and "seed" in controls:
        resolved["seed"] = controls["seed"]
    for key, value in resolved.items():
        if key in controls and controls[key] != value:
            raise ValueError(f"CLI {key} conflicts with control manifest")
    controls.update(resolved)
    provenance = validate_dataset_manifest(args.dataset_manifest, args.cases) if args.dataset_manifest else None
    backend = create_backend(config)
    try:
        controls.update(backend=backend.backend_kind(), model=backend.model_name())
        if args.benchmark_model:
            controls["model_label"] = args.benchmark_model
        controls["resolved_configuration"] = public_configuration(config)
        controls = public_configuration(controls)
        strategy = (ReviewExecution(backend, controls, retriever=_build_retriever(args, config))
                    if args.review_pipeline else PromptExecution(backend, config.max_new_tokens))
        manifest = run_session(args.cases, args.output_dir, strategy, controls=controls, provenance=provenance)
    finally:
        backend.close()
    data = verify_bundle(args.output_dir)
    _emit({"manifest": str(manifest), "cases": data["outcomes"]["count"], "states": data["outcomes"]["states"]}, None)
    return 1 if data["outcomes"]["states"]["failed"] else 0


def _run_score(args: argparse.Namespace, baseline) -> int:
    """Handle ``benchmark score`` for a single run."""
    _emit(
        {
            "measurement": "objective_matching",
            "cases_sha256": file_hash(args.cases),
            "outcomes_sha256": file_hash(args.outcomes),
            "states": _outcome_states(args.outcomes),
            "aggregate": aggregate(baseline, args.bootstrap_samples, args.seed),
            "cases": [
                asdict(x) | {"precision": x.precision, "recall": x.recall, "f1": x.f1}
                for x in baseline
            ],
        },
        args.output,
    )
    return 0


def _outcome_states(path):
    counts = {"success": 0, "failed": 0, "unsupported": 0}
    for row in map(json.loads, path.read_text(encoding="utf-8").splitlines()):
        status = row.get("status", "success")
        if status not in counts:
            raise ValueError("invalid outcome state")
        counts[status] += 1
    return counts


def _run_compare(args: argparse.Namespace, baseline) -> int:
    """Handle ``benchmark compare`` for a paired run."""
    treatment = score_files(args.cases, args.treatment)
    result = compare_runs(
        args.baseline_name,
        baseline,
        args.treatment_name,
        treatment,
        args.bootstrap_samples,
        args.seed,
    )
    _emit(asdict(result), args.output)
    return 0


def command(args: argparse.Namespace) -> int:
    """Dispatch a ``benchmark`` sub-action to its handler."""
    if args.benchmark_action == "convert":
        return _run_convert(args)
    if args.benchmark_action == "run":
        return _run_benchmark(args)
    if args.benchmark_action == "validate":
        _emit(verify_bundle(args.directory), None)
        return 0
    baseline = score_files(
        args.cases, args.outcomes if args.benchmark_action == "score" else args.baseline
    )
    if args.benchmark_action == "score":
        return _run_score(args, baseline)
    return _run_compare(args, baseline)

"""CLI handlers for deterministic benchmark conversion and evaluation."""

from __future__ import annotations
import argparse
import json
from dataclasses import asdict
from pathlib import Path
from prthinker.ablation import compare_runs
from prthinker.benchmark_datasets import convert_dataset
from prthinker.benchmark_scoring import aggregate, score_files
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
    from prthinker.benchmark import load_cases, run_cases, write_run_bundle
    from prthinker.cli_review import _build_config

    config = _build_config(args)
    backend = create_backend(config)
    try:
        outcomes = run_cases(
            backend, load_cases(args.cases), max_new_tokens=config.max_new_tokens
        )
        manifest = write_run_bundle(
            args.cases,
            outcomes,
            args.output_dir,
            backend=backend.backend_kind(),
            model=args.benchmark_model or backend.model_name(),
            seed=args.seed,
            parameters={"max_new_tokens": config.max_new_tokens},
        )
    finally:
        backend.close()
    _emit({"manifest": str(manifest), "cases": len(outcomes)}, None)
    return 0


def _run_score(args: argparse.Namespace, baseline) -> int:
    """Handle ``benchmark score`` for a single run."""
    _emit(
        {
            "aggregate": aggregate(baseline, args.bootstrap_samples, args.seed),
            "cases": [
                asdict(x) | {"precision": x.precision, "recall": x.recall, "f1": x.f1}
                for x in baseline
            ],
        },
        args.output,
    )
    return 0


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
    baseline = score_files(
        args.cases, args.outcomes if args.benchmark_action == "score" else args.baseline
    )
    if args.benchmark_action == "score":
        return _run_score(args, baseline)
    return _run_compare(args, baseline)

"""Score ContextBench predictions with the framework's retrieval scorer.

Thin driver: the file/line coverage/precision maths lives in the framework
core (:mod:`prthinker.retrieval_scoring`). This script only does the
ContextBench-specific I/O — loading each case's gold context from the source
rows — and validates the framework scorer against the official evaluator's
existing per-case outputs (``--validate``).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))

from prthinker.retrieval_scoring import (  # noqa: E402
    aggregate_retrieval,
    score_retrieval_case,
)

SOURCE = ROOT / "contextbench_verified_25.jsonl"
OFFICIAL_RESULTS = ROOT / "contextbench_official_lexical_baseline_results.jsonl"
OFFICIAL_PREDS = ROOT / "contextbench_official_lexical_baseline.jsonl"


def _read_jsonl(path: Path) -> list[dict]:
    """Return the parsed non-empty JSON objects in a .jsonl file."""
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def load_gold(source: Path = SOURCE) -> dict[str, list[dict]]:
    """Map each instance id to its ``gold_context`` span list."""
    gold: dict[str, list[dict]] = {}
    for row in _read_jsonl(source):
        raw = row["gold_context"]
        gold[row["original_inst_id"]] = json.loads(raw) if isinstance(raw, str) else raw
    return gold


def score_file(predictions: list[dict], gold: dict[str, list[dict]]) -> dict:
    """Score prediction records; returns per-case + micro aggregate."""
    cases = []
    per_case = []
    for pred in predictions:
        traj = pred.get("traj_data", {})
        case = score_retrieval_case(
            traj.get("pred_files", []), traj.get("pred_spans", {}), gold[pred["instance_id"]]
        )
        cases.append(case)
        per_case.append({
            "instance_id": pred["instance_id"],
            "file": vars(case.file),
            "line": vars(case.line),
        })
    return {"cases_scored": len(cases), "aggregate": aggregate_retrieval(cases), "cases": per_case}


def validate_against_official() -> bool:
    """Assert the framework metrics equal the official per-case outputs."""
    gold = load_gold()
    preds = {p["instance_id"]: p for p in _read_jsonl(OFFICIAL_PREDS)}
    official = {r["instance_id"]: r for r in _read_jsonl(OFFICIAL_RESULTS)}
    mismatches = 0
    for iid, off in official.items():
        traj = preds[iid]["traj_data"]
        case = score_retrieval_case(traj["pred_files"], traj["pred_spans"], gold[iid])
        for dim, score in (("file", case.file), ("line", case.line)):
            for key in ("intersection", "gold_size", "pred_size"):
                if getattr(score, key) != off["final"][dim][key]:
                    mismatches += 1
                    print(f"MISMATCH {iid} {dim}.{key}")
    print(f"validated {len(official)} cases, {mismatches} field mismatches")
    return mismatches == 0


def _report(report: dict) -> None:
    """Print the one-line file/line summary of a score report."""
    agg = report["aggregate"]
    print(
        f"cases={report['cases_scored']} "
        f"file(cov={agg['file']['coverage']:.4f} prec={agg['file']['precision']:.4f} "
        f"f1={agg['file']['f1']:.4f}) "
        f"line(cov={agg['line']['coverage']:.4f} prec={agg['line']['precision']:.4f})"
    )


def _main() -> int:
    """CLI: ``--validate`` or score a predictions .jsonl against gold."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("predictions", nargs="?", help="predictions .jsonl to score")
    parser.add_argument("--output", help="write the score report JSON here")
    parser.add_argument("--validate", action="store_true",
                        help="check the scorer reproduces the official outputs")
    args = parser.parse_args()
    if args.validate:
        return 0 if validate_against_official() else 1
    if not args.predictions:
        parser.error("give a predictions file or --validate")
    report = score_file(_read_jsonl(Path(args.predictions)), load_gold())
    _report(report)
    if args.output:
        Path(args.output).write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())

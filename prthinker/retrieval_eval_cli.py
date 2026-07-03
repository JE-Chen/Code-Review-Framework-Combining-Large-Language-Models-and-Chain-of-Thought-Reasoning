"""CLI aggregation for retrieval evaluation records."""

from __future__ import annotations
import argparse
import json
from dataclasses import asdict
from pathlib import Path
from statistics import mean
from prthinker.retrieval_eval import evaluate


def add_parser(sub):
    p = sub.add_parser("retrieval-eval", help="Score retrieval JSONL records")
    p.add_argument("input", type=Path)
    p.add_argument("--output", type=Path)


def command(args: argparse.Namespace) -> int:
    rows = []
    with args.input.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                row = json.loads(line)
                rows.append(
                    evaluate(
                        row.get("retrieved", []),
                        row.get("expected", []),
                        row.get("used", []),
                        row.get("cited_correct", []),
                    )
                )
    aggregate = {
        name: (mean(getattr(row, name) for row in rows) if rows else 0.0)
        for name in ("recall", "precision", "utilization", "citation_correctness")
    }
    text = (
        json.dumps(
            {
                "cases": len(rows),
                "aggregate": aggregate,
                "rows": [asdict(row) for row in rows],
            },
            indent=2,
        )
        + "\n"
    )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0

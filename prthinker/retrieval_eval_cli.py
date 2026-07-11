"""CLI aggregation for retrieval evaluation records."""

from __future__ import annotations
import argparse
import json
from dataclasses import asdict
from pathlib import Path
from statistics import mean
from typing import Any
from prthinker.cli_io import emit_text
from prthinker.retrieval_eval import RetrievalMetrics, evaluate

_BASE_METRICS = ("recall", "precision", "utilization", "citation_correctness")
_SPAN_METRICS = ("line_hit_at_k", "window_recall", "block_f1")


def add_parser(sub):
    p = sub.add_parser("retrieval-eval", help="Score retrieval JSONL records")
    p.add_argument("input", type=Path)
    p.add_argument("--output", type=Path)


def _evaluate_row(row: dict[str, Any]) -> RetrievalMetrics:
    """Score one JSONL record; span keys are optional (tolerant metrics)."""
    return evaluate(
        row.get("retrieved", []),
        row.get("expected", []),
        row.get("used", []),
        row.get("cited_correct", []),
        pred_spans=row.get("pred_spans"),
        gold_spans=row.get("gold_spans"),
        sources=row.get("sources"),
    )


def _load_rows(path: Path) -> list[RetrievalMetrics]:
    """Evaluate every non-blank JSONL line of ``path``."""
    rows: list[RetrievalMetrics] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(_evaluate_row(json.loads(line)))
    return rows


def _aggregate(rows: list[RetrievalMetrics]) -> dict[str, float]:
    """Base-metric means (0.0 when empty) plus span-metric means when present.

    Span metrics average only the rows where they were computed (rows without
    span data, or with an empty gold line set, score ``None`` and are
    excluded); when no row carries them the keys are omitted so pre-existing
    outputs stay byte-identical.
    """
    aggregate = {
        name: (mean(getattr(row, name) for row in rows) if rows else 0.0)
        for name in _BASE_METRICS
    }
    for name in _SPAN_METRICS:
        values = [value for row in rows if (value := getattr(row, name)) is not None]
        if values:
            aggregate[name] = mean(values)
    return aggregate


def _row_dict(row: RetrievalMetrics) -> dict[str, float]:
    """Serialize a row, dropping the optional metrics that were not computed."""
    return {key: value for key, value in asdict(row).items() if value is not None}


def command(args: argparse.Namespace) -> int:
    rows = _load_rows(args.input)
    text = (
        json.dumps(
            {
                "cases": len(rows),
                "aggregate": _aggregate(rows),
                "rows": [_row_dict(row) for row in rows],
            },
            indent=2,
        )
        + "\n"
    )
    emit_text(text, args.output)
    return 0

"""Score repository-context retrieval against gold context spans.

The framework-core scorer for :mod:`prthinker.repo_retrieval`: given predicted
files/spans and a case's gold context (a list of ``{file, start_line,
end_line}`` records), it reports file- and line-level coverage (recall) and
precision, and micro-averages them across cases. The aggregation matches the
official EuniAI/ContextBench evaluator (Σintersection / Σgold and
Σintersection / Σpred), so a framework retriever can be scored in-process
without the external evaluator.

This is distinct from :mod:`prthinker.benchmark_scoring`, which fuzzy-matches
review *findings*; here we score *context retrieval* set overlap.

Runner-safe: pure stdlib.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable, Sequence

_START_KEYS = ("start", "start_line")
_END_KEYS = ("end", "end_line")
_SYMBOL_RE = re.compile(r"(?:def|class)\s+([A-Za-z_]\w*)")


@dataclass(frozen=True)
class DimensionScore:
    """Coverage/precision for one retrieval dimension (file or line)."""

    coverage: float
    precision: float
    intersection: int
    gold_size: int
    pred_size: int

    @property
    def f1(self) -> float:
        """Harmonic mean of coverage (recall) and precision."""
        total = self.coverage + self.precision
        return 2 * self.coverage * self.precision / total if total else 0.0


@dataclass(frozen=True)
class RetrievalCaseScore:
    """File- and line-level scores for one predicted case."""

    file: DimensionScore
    line: DimensionScore


def _mapping_bounds(span: dict) -> tuple[int, int] | None:
    """Read ``(start, end)`` from a start/end mapping, or None if absent."""
    start = next((span[key] for key in _START_KEYS if key in span), None)
    end = next((span[key] for key in _END_KEYS if key in span), None)
    if start is None or end is None:
        return None
    return int(start), int(end)


def _span_bounds(span: Any) -> tuple[int, int] | None:
    """Read ``(start, end)`` from a (start, end) pair or a start/end mapping."""
    if isinstance(span, dict):
        return _mapping_bounds(span)
    if isinstance(span, (tuple, list)) and len(span) >= 2:
        return int(span[0]), int(span[1])
    return None


def gold_files(gold_spans: Iterable[dict]) -> set[str]:
    """Unique gold file paths from a case's span records."""
    return {span["file"] for span in gold_spans}


def gold_lines(gold_spans: Iterable[dict]) -> set[tuple[str, int]]:
    """The set of gold ``(file, line)`` pairs across all span records."""
    lines: set[tuple[str, int]] = set()
    for span in gold_spans:
        for line in range(int(span["start_line"]), int(span["end_line"]) + 1):
            lines.add((span["file"], line))
    return lines


def predicted_lines(pred_spans: dict[str, list]) -> set[tuple[str, int]]:
    """The set of predicted ``(file, line)`` pairs from a spans mapping."""
    lines: set[tuple[str, int]] = set()
    for path, spans in pred_spans.items():
        for span in spans:
            bounds = _span_bounds(span)
            if bounds is None:
                continue
            for line in range(bounds[0], bounds[1] + 1):
                lines.add((path, line))
    return lines


def _dimension(intersection: int, gold_size: int, pred_size: int) -> DimensionScore:
    """Build a DimensionScore from raw confusion counts."""
    return DimensionScore(
        coverage=intersection / gold_size if gold_size else 0.0,
        precision=intersection / pred_size if pred_size else 0.0,
        intersection=intersection,
        gold_size=gold_size,
        pred_size=pred_size,
    )


def score_retrieval_case(
    pred_files: Iterable[str],
    pred_spans: dict[str, list],
    gold_spans: Iterable[dict],
) -> RetrievalCaseScore:
    """File + line coverage/precision for one predicted case against gold."""
    gold_spans = list(gold_spans)
    gfiles = gold_files(gold_spans)
    pfiles = set(pred_files)
    glines = gold_lines(gold_spans)
    plines = predicted_lines(pred_spans)
    return RetrievalCaseScore(
        file=_dimension(len(gfiles & pfiles), len(gfiles), len(pfiles)),
        line=_dimension(len(glines & plines), len(glines), len(plines)),
    )


def gold_symbols(gold_spans: Iterable[dict]) -> set[str]:
    """Best-effort def/class names defined in the gold span ``content`` fields.

    Approximate: the official evaluator derives symbols with a full AST parser;
    this regex over the gold content is a local stand-in, so symbol scores are
    indicative, not official.
    """
    names: set[str] = set()
    for span in gold_spans:
        names.update(_SYMBOL_RE.findall(str(span.get("content", ""))))
    return names


def _flatten_symbols(pred_symbols: dict[str, list] | None) -> set[str]:
    """Flatten a per-file predicted-symbols mapping to a single name set."""
    return {name for names in (pred_symbols or {}).values() for name in names}


def score_symbols(pred_symbols: dict[str, list] | None, gold_spans: Iterable[dict]) -> DimensionScore:
    """Best-effort symbol coverage/precision (def/class name overlap)."""
    gold = gold_symbols(gold_spans)
    pred = _flatten_symbols(pred_symbols)
    return _dimension(len(gold & pred), len(gold), len(pred))


def _micro(scores: Sequence[DimensionScore]) -> dict[str, float]:
    """Micro-average a list of dimension scores (matches the official metric)."""
    intersection = sum(score.intersection for score in scores)
    gold_total = sum(score.gold_size for score in scores)
    pred_total = sum(score.pred_size for score in scores)
    dimension = _dimension(intersection, gold_total, pred_total)
    return {
        "coverage": dimension.coverage,
        "precision": dimension.precision,
        "f1": dimension.f1,
    }


def aggregate_retrieval(cases: Sequence[RetrievalCaseScore]) -> dict[str, dict]:
    """Micro-averaged file and line coverage/precision/F1 across cases."""
    return {
        "cases": len(cases),
        "file": _micro([case.file for case in cases]),
        "line": _micro([case.line for case in cases]),
    }

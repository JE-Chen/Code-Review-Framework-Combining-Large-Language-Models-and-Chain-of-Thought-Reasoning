"""Retrieval recall, precision, utilization, and citation correctness.

When line-level span data is supplied, :func:`evaluate` additionally fills
the tolerant localization metrics (``line_hit_at_k`` / ``window_recall`` /
``block_f1``) from :mod:`prthinker.retrieval_scoring`; without span data the
optional fields stay ``None`` and pre-existing readers are unaffected.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from prthinker import retrieval_scoring


@dataclass(frozen=True)
class RetrievalMetrics:
    recall: float
    precision: float
    utilization: float
    citation_correctness: float
    line_hit_at_k: float | None = None
    window_recall: float | None = None
    block_f1: float | None = None


def _span_metrics(
    pred_spans: dict[str, list] | None,
    gold_spans: Iterable[dict] | None,
    sources: dict[str, str] | None,
) -> dict[str, float | None]:
    """Tolerant localization metrics, or nothing when no gold spans given."""
    if gold_spans is None:
        return {}
    gold = list(gold_spans)
    spans = pred_spans or {}
    return {
        "line_hit_at_k": retrieval_scoring.line_hit_at_k(spans, gold),
        "window_recall": retrieval_scoring.window_recall(spans, gold),
        "block_f1": retrieval_scoring.block_f1(spans, gold, sources),
    }


def evaluate(retrieved, expected, used, cited_correct,
             *, pred_spans=None, gold_spans=None, sources=None):
    r, e, u = set(retrieved), set(expected), set(used)
    hits = len(r & e)
    return RetrievalMetrics(
        hits / len(e) if e else 1.0,
        hits / len(r) if r else (1.0 if not e else 0.0),
        len(r & u) / len(r) if r else 1.0,
        sum(bool(x) for x in cited_correct) / len(cited_correct)
        if cited_correct
        else 1.0,
        **_span_metrics(pred_spans, gold_spans, sources),
    )

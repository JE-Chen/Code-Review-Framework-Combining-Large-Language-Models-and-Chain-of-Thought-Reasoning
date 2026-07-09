"""Retrieval recall, precision, utilization, and citation correctness."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievalMetrics:
    recall: float
    precision: float
    utilization: float
    citation_correctness: float


def evaluate(retrieved, expected, used, cited_correct):
    r, e, u = set(retrieved), set(expected), set(used)
    hits = len(r & e)
    return RetrievalMetrics(
        hits / len(e) if e else 1.0,
        hits / len(r) if r else (1.0 if not e else 0.0),
        len(r & u) / len(r) if r else 1.0,
        sum(bool(x) for x in cited_correct) / len(cited_correct)
        if cited_correct
        else 1.0,
    )

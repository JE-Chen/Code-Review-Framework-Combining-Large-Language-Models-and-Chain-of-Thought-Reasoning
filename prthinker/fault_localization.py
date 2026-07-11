"""Spectrum-based fault localisation (SBFL) math and signal fusion.

Pure functions over a per-test coverage matrix: Ochiai and Tarantula
suspiciousness scores per ``(path, line)``, plus a weighted
reciprocal-rank fusion that combines SBFL with stack-trace frames and
static-retrieval line hints into one ranked candidate list. This is the
scoring half of execution-grounded localisation — collecting the matrix
lives in :mod:`prthinker.coverage_runner`, the retriever integration in
:mod:`prthinker.execution_retriever`.

Runner-safe: pure stdlib (``math`` / ``collections`` / ``dataclasses``).
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from math import sqrt
from typing import Mapping, Sequence

OCHIAI = "ochiai"
TARANTULA = "tarantula"
FORMULAS = (OCHIAI, TARANTULA)

# Default fusion weights: SBFL and the stack trace are direct execution
# evidence and weigh equally; static retrieval hints are supporting
# context at half weight. The rank offset is the standard RRF constant.
DEFAULT_SBFL_WEIGHT = 1.0
DEFAULT_TRACE_WEIGHT = 1.0
DEFAULT_RETRIEVAL_WEIGHT = 0.5
_RRF_RANK_OFFSET = 60.0

LineKey = tuple[str, int]


@dataclass(frozen=True)
class CoverageMatrix:
    """Per-test line coverage plus each test's pass / fail outcome.

    ``coverage`` maps a test id to the set of ``(path, line)`` pairs it
    executed; ``outcomes`` maps the same test ids to ``True`` (passed)
    or ``False`` (failed).
    """

    coverage: Mapping[str, set[LineKey]] = field(default_factory=dict)
    outcomes: Mapping[str, bool] = field(default_factory=dict)

    @property
    def failed_tests(self) -> tuple[str, ...]:
        """Ids of the tests that failed, sorted for determinism."""
        return tuple(sorted(t for t, ok in self.outcomes.items() if not ok))

    @property
    def passed_tests(self) -> tuple[str, ...]:
        """Ids of the tests that passed, sorted for determinism."""
        return tuple(sorted(t for t, ok in self.outcomes.items() if ok))


@dataclass(frozen=True)
class FusionWeights:
    """Per-signal weights for :func:`fuse_signals`."""

    sbfl: float = DEFAULT_SBFL_WEIGHT
    trace: float = DEFAULT_TRACE_WEIGHT
    retrieval: float = DEFAULT_RETRIEVAL_WEIGHT


def _ochiai(failed_cov: int, passed_cov: int, total_failed: int) -> float:
    """Ochiai suspiciousness with a zero-division guard."""
    denominator = sqrt(total_failed * (failed_cov + passed_cov))
    return failed_cov / denominator if denominator else 0.0


def _tarantula(
    failed_cov: int, passed_cov: int, total_failed: int, total_passed: int
) -> float:
    """Tarantula suspiciousness with zero-division guards."""
    failed_ratio = failed_cov / total_failed if total_failed else 0.0
    passed_ratio = passed_cov / total_passed if total_passed else 0.0
    total = failed_ratio + passed_ratio
    return failed_ratio / total if total else 0.0


def _line_tallies(matrix: CoverageMatrix) -> dict[LineKey, tuple[int, int]]:
    """Per line: (number of failed, number of passed) tests covering it."""
    failed_cov: dict[LineKey, int] = defaultdict(int)
    passed_cov: dict[LineKey, int] = defaultdict(int)
    for test_id, lines in matrix.coverage.items():
        bucket = passed_cov if matrix.outcomes.get(test_id, False) else failed_cov
        for key in lines:
            bucket[key] += 1
    return {
        key: (failed_cov.get(key, 0), passed_cov.get(key, 0))
        for key in set(failed_cov) | set(passed_cov)
    }


def sbfl_scores(
    matrix: CoverageMatrix, formula: str = OCHIAI
) -> dict[LineKey, float]:
    """Suspiciousness score for every covered ``(path, line)``.

    ``formula`` selects :data:`OCHIAI` or :data:`TARANTULA`; anything
    else raises :class:`ValueError`. All-zero denominators score 0.0.
    """
    if formula not in FORMULAS:
        raise ValueError(f"unknown SBFL formula: {formula!r} (expected one of {FORMULAS})")
    total_failed = len(matrix.failed_tests)
    total_passed = len(matrix.passed_tests)
    scores: dict[LineKey, float] = {}
    for key, (failed_cov, passed_cov) in _line_tallies(matrix).items():
        if formula == OCHIAI:
            scores[key] = _ochiai(failed_cov, passed_cov, total_failed)
        else:
            scores[key] = _tarantula(failed_cov, passed_cov, total_failed, total_passed)
    return scores


def top_suspicious(
    scores: Mapping[LineKey, float], k: int
) -> list[tuple[str, int, float]]:
    """The ``k`` highest-scoring lines as ``(path, line, score)``, best first.

    Ties break deterministically by path then line; ``k <= 0`` yields [].
    """
    if k <= 0:
        return []
    ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    return [(path, line, score) for (path, line), score in ranked[:k]]


def _as_line(item: object) -> LineKey:
    """Coerce a ``(path, line)`` tuple or a TraceFrame-like object to a key."""
    path = getattr(item, "path", None)
    if path is not None:
        return (str(path), int(getattr(item, "line", 0)))
    pair = tuple(item)  # type: ignore[arg-type]
    return (str(pair[0]), int(pair[1]))


def fuse_signals(
    sbfl: Mapping[LineKey, float],
    trace_frames: Sequence[object],
    retrieval_lines: Sequence[object],
    weights: FusionWeights | None = None,
) -> list[tuple[str, int, float]]:
    """Weighted reciprocal-rank fusion of the three localisation signals.

    Each signal contributes ``weight / (60 + rank)`` per line (standard
    RRF), so a line surfacing high in several signals outranks a line
    strong in only one. ``trace_frames`` and ``retrieval_lines`` accept
    ``(path, line)`` tuples or objects with ``path`` / ``line``
    attributes, already in rank order. Returns ``(path, line, score)``
    sorted best first, ties broken by path then line.
    """
    active = weights or FusionWeights()
    ranked_sbfl = [(path, line) for path, line, _ in top_suspicious(sbfl, len(sbfl))]
    signals = (
        (ranked_sbfl, active.sbfl),
        ([_as_line(frame) for frame in trace_frames], active.trace),
        ([_as_line(hint) for hint in retrieval_lines], active.retrieval),
    )
    fused: dict[LineKey, float] = defaultdict(float)
    for ranked, weight in signals:
        for rank, key in enumerate(dict.fromkeys(ranked)):
            fused[key] += weight / (_RRF_RANK_OFFSET + rank + 1)
    return sorted(
        ((path, line, score) for (path, line), score in fused.items()),
        key=lambda item: (-item[2], item[0], item[1]),
    )


__all__ = [
    "DEFAULT_RETRIEVAL_WEIGHT",
    "DEFAULT_SBFL_WEIGHT",
    "DEFAULT_TRACE_WEIGHT",
    "FORMULAS",
    "OCHIAI",
    "TARANTULA",
    "CoverageMatrix",
    "FusionWeights",
    "fuse_signals",
    "sbfl_scores",
    "top_suspicious",
]

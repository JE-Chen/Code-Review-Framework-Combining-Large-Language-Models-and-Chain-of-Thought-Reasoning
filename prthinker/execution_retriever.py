"""Execution-grounded retrieval — fuse runtime evidence into localisation.

Static retrieval's line-level accuracy is capped by what the text alone
can say; execution signals break that ceiling. This module wraps any
base :class:`~prthinker.repo_retrieval.RepoContextRetriever` with two
runtime signals: stack-trace frames mined from the query text (a diff /
issue often embeds the failing traceback) and SBFL suspiciousness from
an optional per-test coverage matrix (pre-built, or collected by
running the configured failing / passing tests). The signals are fused
with the base retriever's own hits by weighted reciprocal-rank fusion;
the returned context re-ranks files by fused evidence and carries the
fused suspicious lines as extra single-line span hints.

Everything is optional: with no trace in the query and no tests / matrix
configured, the base retriever's context is returned unchanged.

Runner-safe: stdlib + the sibling prthinker modules only.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from prthinker.coverage_runner import (
    DEFAULT_TEST_CMD,
    DEFAULT_TEST_TIMEOUT,
    collect_coverage,
)
from prthinker.fault_localization import (
    FORMULAS,
    OCHIAI,
    CoverageMatrix,
    FusionWeights,
    LineKey,
    fuse_signals,
    sbfl_scores,
)
from prthinker.repo_retrieval import RepoContext, RepoContextRetriever
from prthinker.stack_trace import TraceFrame, parse_traceback

log = logging.getLogger(__name__)

_DEFAULT_MAX_LINE_HINTS = 20


@dataclass(frozen=True)
class ExecutionSignalsConfig:
    """Knobs for execution grounding, grouped to keep call sites small.

    ``matrix`` supplies a pre-built coverage matrix directly; otherwise,
    when ``failing_tests`` is non-empty, the matrix is collected once
    per workdir by running the failing + passing tests under coverage.
    """

    test_cmd: tuple[str, ...] = DEFAULT_TEST_CMD
    failing_tests: tuple[str, ...] = ()
    passing_tests: tuple[str, ...] = ()
    matrix: CoverageMatrix | None = None
    formula: str = OCHIAI
    weights: FusionWeights | None = None
    timeout: float = DEFAULT_TEST_TIMEOUT
    max_line_hints: int = _DEFAULT_MAX_LINE_HINTS


def _is_safe_relative(path: str) -> bool:
    """Reject absolute paths, drive letters and ``..`` from trace content."""
    if path.startswith("/") or ":" in path:
        return False
    return ".." not in path.split("/")


def _retrieval_lines(context: RepoContext) -> list[LineKey]:
    """The base retriever's span starts as ranked (path, line) hints."""
    return [
        (rel, start)
        for rel in context.files
        for start, _end in context.spans.get(rel, [])
    ]


def _rank_files(
    base_files: tuple[str, ...],
    fused: list[tuple[str, int, float]],
    workdir: Path,
) -> list[str]:
    """Files ordered by fused evidence first, then remaining base order.

    A fused path outside the base context is admitted only when it is a
    safe repo-relative path to a real file, so junk mined from logs
    never enters the context.
    """
    ranked: list[str] = []
    for path, _line, _score in fused:
        if path in ranked:
            continue
        if path in base_files:
            ranked.append(path)
        elif _is_safe_relative(path) and (workdir / path).is_file():
            ranked.append(path)
    ranked.extend(rel for rel in base_files if rel not in ranked)
    return ranked


def _merge_spans(
    base: RepoContext, files: list[str], fused: list[tuple[str, int, float]]
) -> dict[str, list[tuple[int, int]]]:
    """Base spans plus one-line hint spans for the fused suspicious lines."""
    spans = {rel: list(base.spans.get(rel, [])) for rel in files}
    for path, line, _score in fused:
        covered = any(start <= line <= end for start, end in spans.get(path, ()))
        if path in spans and not covered:
            spans[path].append((line, line))
    return {rel: sorted(rel_spans) for rel, rel_spans in spans.items()}


def _merge_symbols(
    base: RepoContext, files: list[str], frames: list[TraceFrame]
) -> dict[str, list[str]]:
    """Base symbols plus the function names named by the trace frames."""
    symbols = {rel: list(base.symbols.get(rel, [])) for rel in files}
    for frame in frames:
        known = symbols.get(frame.path)
        if known is not None and frame.symbol and frame.symbol not in known:
            known.append(frame.symbol)
    return symbols


class ExecutionGroundedRetriever(RepoContextRetriever):
    """Wrap a base retriever with stack-trace and SBFL evidence fusion.

    The base retriever is injected (Dependency Injection); this class
    never chooses a static strategy itself. Coverage collection runs at
    most once per workdir per retriever lifetime.
    """

    def __init__(
        self,
        base: RepoContextRetriever,
        config: ExecutionSignalsConfig | None = None,
    ) -> None:
        self._base = base
        self._config = config or ExecutionSignalsConfig()
        if self._config.formula not in FORMULAS:
            raise ValueError(
                f"unknown SBFL formula: {self._config.formula!r} "
                f"(expected one of {FORMULAS})"
            )
        self._matrix_cache: dict[Path, CoverageMatrix] = {}

    def retrieve(self, query: str, workdir: Path) -> RepoContext:
        """Retrieve, then re-rank with whatever execution evidence exists.

        With no traceback in the query and no SBFL signal the base
        context is returned as-is (execution grounding degrades to the
        base retriever unchanged).
        """
        workdir = Path(workdir)
        base_ctx = self._base.retrieve(query, workdir)
        frames = parse_traceback(query, workdir=workdir)
        scores = self._sbfl(workdir)
        if not frames and not scores:
            return base_ctx
        fused = fuse_signals(
            scores, frames, _retrieval_lines(base_ctx), self._config.weights
        )[: self._config.max_line_hints]
        files = _rank_files(base_ctx.files, fused, workdir)
        return RepoContext(
            tuple(files),
            _merge_spans(base_ctx, files, fused),
            _merge_symbols(base_ctx, files, frames),
        )

    def _sbfl(self, workdir: Path) -> dict[LineKey, float]:
        """Positive SBFL scores, or empty when there is no failure signal."""
        matrix = self._config.matrix or self._collected(workdir)
        if matrix is None or not matrix.failed_tests:
            return {}
        raw = sbfl_scores(matrix, self._config.formula)
        return {key: score for key, score in raw.items() if score > 0.0}

    def _collected(self, workdir: Path) -> CoverageMatrix | None:
        """Collect (and memoize per workdir) the coverage matrix, if configured."""
        cfg = self._config
        if not cfg.failing_tests:
            return None
        key = workdir.resolve()
        if key not in self._matrix_cache:
            log.info(
                "collecting execution coverage for %d test(s) under %s",
                len(cfg.failing_tests) + len(cfg.passing_tests), workdir,
            )
            self._matrix_cache[key] = collect_coverage(
                workdir,
                test_cmd=cfg.test_cmd,
                test_ids=[*cfg.failing_tests, *cfg.passing_tests],
                timeout=cfg.timeout,
            )
        return self._matrix_cache[key]


def create_execution_retriever(
    base: RepoContextRetriever, **knobs
) -> ExecutionGroundedRetriever:
    """Factory: wrap ``base`` with execution grounding.

    ``knobs`` are the :class:`ExecutionSignalsConfig` fields; sequence
    knobs accept any iterable and ``weights`` also accepts a plain
    ``(sbfl, trace, retrieval)`` tuple. This is the single entry point
    the retriever factory wires against.
    """
    for key in ("test_cmd", "failing_tests", "passing_tests"):
        if knobs.get(key) is not None:
            knobs[key] = tuple(knobs[key])
        elif key in knobs:
            del knobs[key]
    weights = knobs.get("weights")
    if isinstance(weights, (list, tuple)):
        knobs["weights"] = FusionWeights(*weights)
    return ExecutionGroundedRetriever(base, config=ExecutionSignalsConfig(**knobs))


__all__ = [
    "ExecutionGroundedRetriever",
    "ExecutionSignalsConfig",
    "create_execution_retriever",
]

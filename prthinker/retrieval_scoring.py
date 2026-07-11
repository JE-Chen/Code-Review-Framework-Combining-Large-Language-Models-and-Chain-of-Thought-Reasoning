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

Besides the exact-overlap file/line/symbol scores, the module offers three
tolerant localization metrics (the exact set-overlap line F1 treats the gold
fix-patch lines as the only valid answer, which under-credits retrievers that
find *a* correct location):

- :func:`line_hit_at_k` — 1.0 when any of the first ``k`` predicted lines is a
  gold line, else 0.0.
- :func:`window_recall` — fraction of gold lines with a predicted line within
  ``±window`` in the same file.
- :func:`block_f1` — F1 over enclosing def/class block identifiers
  (``(path, start, end)``), with fixed-size line buckets as the fallback for
  non-Python files or lines outside any block.

Shared empty-set conventions for the three tolerant metrics: an empty gold
line set makes the metric undefined — the per-case function returns ``None``
and the case is excluded from aggregation; an empty prediction against a
non-empty gold scores 0.0.

Runner-safe: pure stdlib (plus the stdlib-only block-span helper from
:mod:`prthinker.repo_retrieval`).
"""

from __future__ import annotations

import ast
import re
import textwrap
from dataclasses import dataclass
from typing import Any, Iterable, Sequence

from prthinker.repo_retrieval import enclosing_blocks

_START_KEYS = ("start", "start_line")
_END_KEYS = ("end", "end_line")
_SYMBOL_RE = re.compile(r"(?:def|class)\s+([A-Za-z_]\w*)")
_DEF_NODES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)

# Tolerant-localization defaults (module constants, not CLI knobs — the
# retrieval CLIs have no per-metric flags to mirror).
_HIT_K = 10
_WINDOW = 3
_FALLBACK_BLOCK_LINES = 20
_PYTHON_SUFFIX = ".py"


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
    """File- and line-level scores for one predicted case.

    The three tolerant localization fields are optional (``None`` when not
    computed, or when the case has no gold lines) so pre-existing callers that
    construct only ``file`` + ``line`` are unaffected.
    """

    file: DimensionScore
    line: DimensionScore
    line_hit_at_k: float | None = None
    window_recall: float | None = None
    block_f1: float | None = None


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


def _ast_symbols(source: str) -> set[str] | None:
    """def/class names via a real AST parse, or None if the snippet won't parse.

    Closer to the official evaluator's AST extraction than the regex: it ignores
    ``def``/``class`` tokens inside strings and comments, so it does not
    over-count. A gold snippet is often an indented method body, so a raw parse
    is retried after dedenting before giving up.
    """
    for candidate in (source, textwrap.dedent(source)):
        try:
            tree = ast.parse(candidate)
        except (SyntaxError, ValueError):
            continue
        return {node.name for node in ast.walk(tree) if isinstance(node, _DEF_NODES)}
    return None


def gold_symbols(gold_spans: Iterable[dict]) -> set[str]:
    """def/class names defined in the gold span ``content`` fields.

    Uses a real AST parse when the content is parseable (matching the official
    evaluator's AST-based symbol extraction) and falls back to a regex only for
    snippets that do not parse standalone.
    """
    names: set[str] = set()
    for span in gold_spans:
        content = str(span.get("content", ""))
        ast_names = _ast_symbols(content)
        names.update(ast_names if ast_names is not None else _SYMBOL_RE.findall(content))
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


_TOLERANT_METRICS = ("line_hit_at_k", "window_recall", "block_f1")


def _ordered_predicted_lines(pred_spans: dict[str, list]) -> list[tuple[str, int]]:
    """Predicted ``(file, line)`` pairs in prediction order, first-seen dedup.

    Order = mapping insertion order, then span list order within a file, then
    ascending line numbers within a span. This is the "top-k" order used by
    :func:`line_hit_at_k`.
    """
    pairs = (
        (path, line)
        for path, spans in pred_spans.items()
        for span in spans
        if (bounds := _span_bounds(span)) is not None
        for line in range(bounds[0], bounds[1] + 1)
    )
    return list(dict.fromkeys(pairs))


def line_hit_at_k(pred_spans: dict[str, list], gold_spans: Iterable[dict], k: int = _HIT_K) -> float | None:
    """1.0 if any of the first ``k`` predicted lines is a gold line, else 0.0.

    Rewards finding *a* correct location instead of reproducing the exact
    patch line set. "First k" follows :func:`_ordered_predicted_lines`; a gold
    line in any gold file counts. Empty gold returns ``None`` (case excluded
    from aggregation); an empty prediction scores 0.0.
    """
    if k < 1:
        raise ValueError(f"k must be >= 1, got {k}")
    glines = gold_lines(gold_spans)
    if not glines:
        return None
    top = _ordered_predicted_lines(pred_spans)[:k]
    return 1.0 if any(pair in glines for pair in top) else 0.0


def _near_hit(pair: tuple[str, int], plines: set[tuple[str, int]], window: int) -> bool:
    """True when a predicted line in the same file is within ±window of pair."""
    path, line = pair
    return any((path, line + offset) in plines for offset in range(-window, window + 1))


def window_recall(pred_spans: dict[str, list], gold_spans: Iterable[dict], window: int = _WINDOW) -> float | None:
    """Fraction of gold lines with a predicted line within ±window, same file.

    Tolerant of off-by-a-few localization: a gold line counts as covered when
    any predicted line in the same file is at most ``window`` lines away
    (inclusive — exactly ``±window`` counts). Empty gold returns ``None``
    (case excluded from aggregation); an empty prediction scores 0.0.
    """
    if window < 0:
        raise ValueError(f"window must be >= 0, got {window}")
    glines = gold_lines(gold_spans)
    if not glines:
        return None
    plines = predicted_lines(pred_spans)
    return sum(1 for pair in glines if _near_hit(pair, plines, window)) / len(glines)


def _bucket_span(line: int) -> tuple[int, int]:
    """Fixed-size bucket span containing ``line`` (1-20, 21-40, ...)."""
    start = ((line - 1) // _FALLBACK_BLOCK_LINES) * _FALLBACK_BLOCK_LINES + 1
    return start, start + _FALLBACK_BLOCK_LINES - 1


def _innermost_block(blocks: list[tuple[int, int, str]], line: int) -> tuple[int, int] | None:
    """Smallest (latest-starting) def/class span containing ``line``, if any."""
    best: tuple[int, int] | None = None
    for start, end, _name in blocks:
        if start <= line <= end and (best is None or start >= best[0]):
            best = (start, end)
    return best


def _blocks_for_path(path: str, sources: dict[str, str], cache: dict[str, list]) -> list:
    """def/class blocks for a Python path with known source; else no blocks."""
    if path not in cache:
        text = sources.get(path)
        parses = path.endswith(_PYTHON_SUFFIX) and text is not None
        cache[path] = enclosing_blocks(text.splitlines()) if parses else []
    return cache[path]


def _block_ids(
    lines: Iterable[tuple[str, int]], sources: dict[str, str], cache: dict[str, list]
) -> set[tuple[str, int, int]]:
    """Map ``(file, line)`` pairs to block identifiers ``(path, start, end)``.

    A line maps to its innermost enclosing def/class block (via
    :func:`prthinker.repo_retrieval.enclosing_blocks`) when the file is Python
    and its source is available; otherwise — non-Python file, missing source,
    or a line outside every block — it falls back to the fixed-size
    ``_FALLBACK_BLOCK_LINES``-line bucket containing it.
    """
    ids: set[tuple[str, int, int]] = set()
    for path, line in lines:
        span = _innermost_block(_blocks_for_path(path, sources, cache), line)
        ids.add((path, *(span or _bucket_span(line))))
    return ids


def block_f1(
    pred_spans: dict[str, list],
    gold_spans: Iterable[dict],
    sources: dict[str, str] | None = None,
) -> float | None:
    """Per-case F1 over enclosing-block identifiers (path + span).

    Gold and predicted lines are mapped to block identifiers per
    :func:`_block_ids`, and the score is the set F1 of the two identifier
    sets — set-overlap at block granularity. ``sources`` maps file paths to
    their full text; paths without a source use the bucket fallback. Empty
    gold returns ``None`` (case excluded from aggregation); an empty
    prediction scores 0.0.
    """
    glines = gold_lines(gold_spans)
    if not glines:
        return None
    cache: dict[str, list] = {}
    gblocks = _block_ids(glines, sources or {}, cache)
    pblocks = _block_ids(predicted_lines(pred_spans), sources or {}, cache)
    return 2 * len(gblocks & pblocks) / (len(gblocks) + len(pblocks))


def score_retrieval_case_extended(
    pred_files: Iterable[str],
    pred_spans: dict[str, list],
    gold_spans: Iterable[dict],
    *,
    sources: dict[str, str] | None = None,
    hit_k: int = _HIT_K,
    window: int = _WINDOW,
) -> RetrievalCaseScore:
    """Exact file/line scores plus the three tolerant localization metrics."""
    gold_spans = list(gold_spans)
    base = score_retrieval_case(pred_files, pred_spans, gold_spans)
    return RetrievalCaseScore(
        file=base.file,
        line=base.line,
        line_hit_at_k=line_hit_at_k(pred_spans, gold_spans, hit_k),
        window_recall=window_recall(pred_spans, gold_spans, window),
        block_f1=block_f1(pred_spans, gold_spans, sources),
    )


def _mean_present(values: Iterable[float | None]) -> float | None:
    """Mean of the non-None values, or None when every value is None."""
    present = [value for value in values if value is not None]
    return sum(present) / len(present) if present else None


def aggregate_retrieval(cases: Sequence[RetrievalCaseScore]) -> dict[str, dict]:
    """Micro-averaged file and line coverage/precision/F1 across cases.

    When any case carries the tolerant localization metrics, their per-case
    means (cases scored ``None`` excluded) are added under ``line_hit_at_k`` /
    ``window_recall`` / ``block_f1``; otherwise the keys are omitted so
    pre-existing outputs are byte-identical.
    """
    result: dict[str, Any] = {
        "cases": len(cases),
        "file": _micro([case.file for case in cases]),
        "line": _micro([case.line for case in cases]),
    }
    for name in _TOLERANT_METRICS:
        mean = _mean_present(getattr(case, name, None) for case in cases)
        if mean is not None:
            result[name] = mean
    return result

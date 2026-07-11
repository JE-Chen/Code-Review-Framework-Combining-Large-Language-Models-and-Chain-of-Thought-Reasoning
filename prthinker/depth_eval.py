"""Depth-eval harness — measure what adaptive step planning costs and saves.

Runs the same diff corpus twice — once with ``step_plan="full"`` and once
with ``step_plan="adaptive"`` — through two independently constructed
pipelines, pairs the findings across the two runs, and reports the
review-quality delta (matched / missing / extra findings, gate-severity
recall) next to the model-call and token savings. Pure orchestration and
arithmetic: no backend, retriever, or CLI concerns live here — the caller
supplies a pipeline factory (see :class:`PipelineProbe`).
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from prthinker.backends.base import InferenceBackend, Usage
from prthinker.review_rollups import ordered_tiers, tier_distribution
from prthinker.step_planner import STEP_PLAN_ADAPTIVE, STEP_PLAN_FULL

if TYPE_CHECKING:
    from prthinker.pipeline import PerFileReviewOptions, ReviewResult
    from prthinker.schemas import InlineFinding

# Findings at these severities drive the review gate; losing one to depth
# pruning is the regression the harness exists to quantify.
_GATE_SEVERITIES = frozenset({"error", "warning"})

# Line tolerance when pairing findings across the two runs: reduced-depth
# prompts often anchor the same remark a line or two away.
_LINE_WINDOW = 2

# Char-count fallback mirrors the telemetry layer's estimate for backends
# that report no usage block (local / remote HTTP).
_EST_CHARS_PER_TOKEN = 4


class SupportsPerFileReview(Protocol):
    """The single pipeline capability the harness depends on."""

    def run_per_file(
        self,
        diff_text: str,
        options: "PerFileReviewOptions | None" = None,
    ) -> "ReviewResult":
        """Review every file in ``diff_text`` and return the result."""


class CountingBackend(InferenceBackend):
    """Backend wrapper counting model calls and (reported or estimated) tokens.

    Wrap the real backend before handing it to the pipeline, then read
    :meth:`snapshot` for cumulative ``(calls, tokens)`` totals. Tokens come
    from the inner backend's ``last_usage()`` when it reports one, else
    from a char-count estimate.
    """

    def __init__(self, inner: InferenceBackend) -> None:
        self._inner = inner
        self._calls = 0
        self._tokens = 0

    def generate(
        self,
        prompt: str,
        max_new_tokens: int,
        *,
        cancel_event: "object | None" = None,
    ) -> str:
        text = self._inner.generate(
            prompt, max_new_tokens, cancel_event=cancel_event
        )
        self._calls += 1
        self._tokens += self._token_cost(prompt, text)
        return text

    def _token_cost(self, prompt: str, text: str) -> int:
        usage = self._inner.last_usage()
        if usage is not None:
            return usage.prompt_tokens + usage.completion_tokens
        return (len(prompt) + len(text)) // _EST_CHARS_PER_TOKEN

    def snapshot(self) -> tuple[int, int]:
        """Cumulative ``(calls, tokens)`` counted so far."""
        return self._calls, self._tokens

    def last_usage(self) -> Usage | None:
        return self._inner.last_usage()

    def backend_kind(self) -> str:
        return self._inner.backend_kind()

    def model_name(self) -> str:
        return self._inner.model_name()

    def max_concurrency(self) -> int:
        return self._inner.max_concurrency()

    def close(self) -> None:
        self._inner.close()


@dataclass(frozen=True)
class PipelineProbe:
    """A freshly built pipeline plus its cumulative usage snapshot source.

    ``usage_snapshot`` returns cumulative ``(calls, tokens)`` — typically
    :meth:`CountingBackend.snapshot`. ``close`` (optional) releases the
    probe's resources once its mode finishes.
    """

    pipeline: SupportsPerFileReview
    usage_snapshot: Callable[[], tuple[int, int]]
    close: Callable[[], None] | None = None


PipelineFactory = Callable[[str], PipelineProbe]


@dataclass(frozen=True)
class ModeUsage:
    """Model calls and tokens consumed by one mode over one or more diffs."""

    calls: int = 0
    tokens: int = 0


@dataclass(frozen=True)
class MatchOutcome:
    """Pairing of one diff's findings across the full and adaptive runs."""

    matched_full: tuple["InlineFinding", ...]
    missing: tuple["InlineFinding", ...]
    extra: tuple["InlineFinding", ...]

    @property
    def matched(self) -> int:
        return len(self.matched_full)


@dataclass(frozen=True)
class DiffComparison:
    """Full-vs-adaptive outcome for a single diff of the corpus."""

    index: int
    full_findings: int
    adaptive_findings: int
    matched: int
    adaptive_missing: int
    adaptive_extra: int
    gate_full: int
    gate_matched: int
    tier_counts: dict[str, int]
    full_usage: ModeUsage
    adaptive_usage: ModeUsage


@dataclass(frozen=True)
class DepthEvalReport:
    """Aggregate full-vs-adaptive comparison over a diff corpus."""

    diffs: tuple[DiffComparison, ...]

    @property
    def full_findings(self) -> int:
        return sum(diff.full_findings for diff in self.diffs)

    @property
    def adaptive_findings(self) -> int:
        return sum(diff.adaptive_findings for diff in self.diffs)

    @property
    def matched(self) -> int:
        return sum(diff.matched for diff in self.diffs)

    @property
    def adaptive_missing(self) -> int:
        return sum(diff.adaptive_missing for diff in self.diffs)

    @property
    def adaptive_extra(self) -> int:
        return sum(diff.adaptive_extra for diff in self.diffs)

    @property
    def gate_full(self) -> int:
        return sum(diff.gate_full for diff in self.diffs)

    @property
    def gate_matched(self) -> int:
        return sum(diff.gate_matched for diff in self.diffs)

    @property
    def gate_recall(self) -> float:
        """Share of full-mode error/warning findings the adaptive run kept."""
        if self.gate_full == 0:
            return 1.0
        return self.gate_matched / self.gate_full

    @property
    def tier_counts(self) -> dict[str, int]:
        """Adaptive-run depth-tier distribution merged across all diffs."""
        counts: Counter[str] = Counter()
        for diff in self.diffs:
            counts.update(diff.tier_counts)
        return dict(counts)

    @property
    def full_usage(self) -> ModeUsage:
        return _sum_usage(diff.full_usage for diff in self.diffs)

    @property
    def adaptive_usage(self) -> ModeUsage:
        return _sum_usage(diff.adaptive_usage for diff in self.diffs)


def _sum_usage(usages: Iterable[ModeUsage]) -> ModeUsage:
    calls = tokens = 0
    for usage in usages:
        calls += usage.calls
        tokens += usage.tokens
    return ModeUsage(calls=calls, tokens=tokens)


# ---------- finding matching ------------------------------------------------


def _take_exact(
    finding: "InlineFinding", remaining: list["InlineFinding"]
) -> "InlineFinding | None":
    """Pop and return the remaining finding sharing ``finding_id``, if any."""
    for index, candidate in enumerate(remaining):
        if candidate.finding_id and candidate.finding_id == finding.finding_id:
            return remaining.pop(index)
    return None


def _take_nearest(
    finding: "InlineFinding",
    remaining: list["InlineFinding"],
    line_window: int,
) -> "InlineFinding | None":
    """Pop the closest same-path same-severity finding within the window."""
    best_index = -1
    best_distance = line_window + 1
    for index, candidate in enumerate(remaining):
        if candidate.path != finding.path or candidate.severity != finding.severity:
            continue
        distance = abs(candidate.line - finding.line)
        if distance < best_distance:
            best_index, best_distance = index, distance
    if best_index < 0:
        return None
    return remaining.pop(best_index)


def match_findings(
    full: Sequence["InlineFinding"],
    adaptive: Sequence["InlineFinding"],
    *,
    line_window: int = _LINE_WINDOW,
) -> MatchOutcome:
    """Pair full-mode findings with their adaptive-mode counterparts.

    Identical ``finding_id``s pair first (byte-identical findings); the
    remainder pair greedily by (path, same severity, line within
    ``±line_window``), nearest line first. Unpaired full-mode findings are
    *missing*; unpaired adaptive-mode findings are *extra*.
    """
    remaining = list(adaptive)
    matched_full: list["InlineFinding"] = []
    pending: list["InlineFinding"] = []
    for finding in full:
        target = matched_full if _take_exact(finding, remaining) else pending
        target.append(finding)
    missing: list["InlineFinding"] = []
    for finding in pending:
        near = _take_nearest(finding, remaining, line_window)
        (matched_full if near is not None else missing).append(finding)
    return MatchOutcome(
        matched_full=tuple(matched_full),
        missing=tuple(missing),
        extra=tuple(remaining),
    )


# ---------- comparison run --------------------------------------------------


def _validate_options(
    options_full: "PerFileReviewOptions",
    options_adaptive: "PerFileReviewOptions",
) -> None:
    """Reject option sets that would make the two runs incomparable."""
    if options_full.step_plan != STEP_PLAN_FULL:
        raise ValueError(
            f"options_full.step_plan must be '{STEP_PLAN_FULL}', "
            f"got '{options_full.step_plan}'"
        )
    if options_adaptive.step_plan != STEP_PLAN_ADAPTIVE:
        raise ValueError(
            f"options_adaptive.step_plan must be '{STEP_PLAN_ADAPTIVE}', "
            f"got '{options_adaptive.step_plan}'"
        )
    if (
        options_full.review_cache is not None
        or options_adaptive.review_cache is not None
    ):
        raise ValueError(
            "review_cache must be disabled in both modes so cached findings "
            "cannot cross-contaminate the comparison"
        )


def _run_mode(
    pipeline_factory: PipelineFactory,
    mode: str,
    diffs: Sequence[str],
    options: "PerFileReviewOptions",
) -> list[tuple["ReviewResult", ModeUsage]]:
    """Run every diff through one freshly built pipeline for ``mode``."""
    probe = pipeline_factory(mode)
    runs: list[tuple["ReviewResult", ModeUsage]] = []
    try:
        previous = probe.usage_snapshot()
        for diff_text in diffs:
            result = probe.pipeline.run_per_file(diff_text, options)
            current = probe.usage_snapshot()
            runs.append(
                (
                    result,
                    ModeUsage(
                        calls=current[0] - previous[0],
                        tokens=current[1] - previous[1],
                    ),
                )
            )
            previous = current
    finally:
        if probe.close is not None:
            probe.close()
    return runs


def _result_findings(result: "ReviewResult") -> list["InlineFinding"]:
    """One diff's findings, read from per-file results to avoid duplicates."""
    if result.per_file:
        return [f for fr in result.per_file for f in fr.inline_findings]
    return list(result.inline_findings)


def _gate_count(findings: Iterable["InlineFinding"]) -> int:
    return sum(1 for f in findings if f.severity in _GATE_SEVERITIES)


def _compare_diff(
    index: int,
    full_run: tuple["ReviewResult", ModeUsage],
    adaptive_run: tuple["ReviewResult", ModeUsage],
) -> DiffComparison:
    """Match one diff's two runs and fold the outcome into a comparison row."""
    full_result, full_usage = full_run
    adaptive_result, adaptive_usage = adaptive_run
    full_findings = _result_findings(full_result)
    adaptive_findings = _result_findings(adaptive_result)
    outcome = match_findings(full_findings, adaptive_findings)
    return DiffComparison(
        index=index,
        full_findings=len(full_findings),
        adaptive_findings=len(adaptive_findings),
        matched=outcome.matched,
        adaptive_missing=len(outcome.missing),
        adaptive_extra=len(outcome.extra),
        gate_full=_gate_count(full_findings),
        gate_matched=_gate_count(outcome.matched_full),
        tier_counts=tier_distribution(adaptive_result),
        full_usage=full_usage,
        adaptive_usage=adaptive_usage,
    )


def run_depth_comparison(
    pipeline_factory: PipelineFactory,
    diffs: Sequence[str],
    options_full: "PerFileReviewOptions",
    options_adaptive: "PerFileReviewOptions",
) -> DepthEvalReport:
    """Run every diff at full and adaptive depth and compare the outcomes.

    ``pipeline_factory`` is called once per mode with the step-plan name
    (``"full"`` first, then ``"adaptive"``) and must return a fresh
    :class:`PipelineProbe` each time, so no state — backend, retriever,
    cache — leaks between the two runs. Both option sets must carry their
    mode's ``step_plan`` and a disabled ``review_cache``.
    """
    _validate_options(options_full, options_adaptive)
    full_runs = _run_mode(pipeline_factory, STEP_PLAN_FULL, diffs, options_full)
    adaptive_runs = _run_mode(
        pipeline_factory, STEP_PLAN_ADAPTIVE, diffs, options_adaptive
    )
    return DepthEvalReport(
        diffs=tuple(
            _compare_diff(index, full, adaptive)
            for index, (full, adaptive) in enumerate(zip(full_runs, adaptive_runs))
        )
    )


# ---------- markdown rendering ----------------------------------------------


def _tier_table(tier_counts: dict[str, int]) -> list[str]:
    """Per-tier markdown rows for the adaptive run's depth distribution."""
    if not tier_counts:
        return ["_No files were reviewed._"]
    rows = ["| Tier | Files |", "| --- | ---: |"]
    rows += [
        f"| {tier} | {tier_counts[tier]} |" for tier in ordered_tiers(tier_counts)
    ]
    return rows


def _per_diff_table(diffs: Sequence[DiffComparison]) -> list[str]:
    """Per-diff markdown rows: finding deltas and call counts side by side."""
    rows = [
        "| Diff | Full findings | Adaptive findings | Matched | Missing | "
        "Extra | Full calls | Adaptive calls |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    rows += [
        f"| {d.index} | {d.full_findings} | {d.adaptive_findings} | "
        f"{d.matched} | {d.adaptive_missing} | {d.adaptive_extra} | "
        f"{d.full_usage.calls} | {d.adaptive_usage.calls} |"
        for d in diffs
    ]
    return rows


def format_markdown(report: DepthEvalReport) -> str:
    """Render the depth-eval report as a markdown document."""
    lines = [
        "# Review depth evaluation",
        "",
        f"Diffs compared: {len(report.diffs)}",
        "",
        "| Metric | Full | Adaptive |",
        "| --- | ---: | ---: |",
        f"| Findings | {report.full_findings} | {report.adaptive_findings} |",
        f"| Model calls | {report.full_usage.calls} "
        f"| {report.adaptive_usage.calls} |",
        f"| Tokens | {report.full_usage.tokens} "
        f"| {report.adaptive_usage.tokens} |",
        "",
        f"- Matched findings: {report.matched}",
        f"- Missing in adaptive: {report.adaptive_missing}",
        f"- Extra in adaptive: {report.adaptive_extra}",
        f"- Gate-severity recall (error/warning): {report.gate_recall:.2f} "
        f"({report.gate_matched}/{report.gate_full})",
        "",
        "## Adaptive tier distribution",
        "",
        *_tier_table(report.tier_counts),
        "",
        "## Per-diff breakdown",
        "",
        *_per_diff_table(report.diffs),
    ]
    return "\n".join(lines).rstrip() + "\n"


__all__ = [
    "CountingBackend",
    "DepthEvalReport",
    "DiffComparison",
    "MatchOutcome",
    "ModeUsage",
    "PipelineFactory",
    "PipelineProbe",
    "SupportsPerFileReview",
    "format_markdown",
    "match_findings",
    "run_depth_comparison",
]

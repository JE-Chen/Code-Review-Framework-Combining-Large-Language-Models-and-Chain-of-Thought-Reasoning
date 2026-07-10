"""Adaptive per-file step planning — scale review depth to each change.

Every file in a PR historically ran the full CoT chain (summary, first
review, linter, code smell, total summary) regardless of what changed.
For a one-line docs fix that is five model calls spent re-stating the
obvious; for a large or high-risk change the full sweep is exactly what
is wanted. This module decides, per :class:`~prthinker.diff.FileDiff`,
which of the configured steps are actually worth running.

The planner is pure and deterministic: it looks only at the diff (size,
file kind) and the optional risk score the pipeline already computes.
``--step-plan full`` (the default) bypasses it entirely, preserving the
historical behaviour.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from prthinker.steps import CompactReviewStep, UnifiedReviewStep

if TYPE_CHECKING:
    from prthinker.diff import FileDiff
    from prthinker.steps import ReviewStep

STEP_PLAN_FULL = "full"
STEP_PLAN_ADAPTIVE = "adaptive"
STEP_PLAN_CHOICES = (STEP_PLAN_FULL, STEP_PLAN_ADAPTIVE)

TIER_SKIP = "skip"
TIER_TRIVIAL = "trivial"
TIER_STANDARD = "standard"
TIER_DEEP = "deep"

# Documentation / declarative-config files: prose or data, not logic.
# The inline-findings pass still sees them; the CoT analysis chain
# (naming, code smells, lint) has nothing to say about them.
_LOW_RISK_SUFFIXES = frozenset(
    {
        ".md",
        ".rst",
        ".txt",
        ".json",
        ".yml",
        ".yaml",
        ".toml",
        ".ini",
        ".cfg",
        ".lock",
        ".svg",
    }
)

_TRIVIAL_MAX_CHANGED_LINES = 5
_DEEP_MIN_CHANGED_LINES = 200
_DEEP_MIN_RISK_SCORE = 0.7

# Machine-written files nobody hand-reviews: lockfiles, minified bundles,
# generated protobuf/snapshot artifacts, vendored trees. Reviewing them
# wastes model calls and the findings are unactionable — the change is
# regenerated, not edited. Matched against the full repo-relative path.
_GENERATED_PATH_RE = re.compile(
    r"(?:^|/)("
    r"package-lock\.json|yarn\.lock|pnpm-lock\.yaml|poetry\.lock|uv\.lock|"
    r"Cargo\.lock|composer\.lock|Gemfile\.lock|go\.sum"
    r")$"
    r"|(?:\.(?:min\.js|min\.css|map|pb\.go|snap)|_pb2\.py)$"
    r"|(?:^|/)(?:vendor|node_modules|dist|build|__snapshots__)/"
)

# Output-producing per-file steps that stay at every depth: they are what
# the reviewer actually consumes (findings, orientation), not analysis
# scaffolding feeding a later synthesis.
_ALWAYS_KEEP = frozenset({"inline_findings", "walkthrough"})
# Mid-size changes also keep counterfactual exploration when configured;
# it rides on the surviving inline findings.
_STANDARD_KEEP = _ALWAYS_KEEP | frozenset({"counterfactual"})
# The analysis scaffolding the CompactReviewStep substitutes for at
# reduced depth (one model call instead of five).
_ANALYSIS_STEPS = frozenset(
    {"first_summary", "first_code_review", "linter", "code_smell", "total_summary"}
)


@dataclass(frozen=True)
class StepPlan:
    """The steps chosen for one file, plus what was pruned and why."""

    tier: str
    steps: tuple[type["ReviewStep"], ...]
    skipped: tuple[str, ...]


def changed_line_count(fd: "FileDiff") -> int:
    """Count added plus removed lines in a file diff (headers excluded)."""
    count = 0
    for line in fd.raw.splitlines():
        if line.startswith(("+++", "---")):
            continue
        if line.startswith(("+", "-")):
            count += 1
    return count


def is_whitespace_only_change(fd: "FileDiff") -> bool:
    """True when every added line differs from some removed line only in
    whitespace — reformatting with no content change."""
    added: list[str] = []
    removed: set[str] = set()
    for line in fd.raw.splitlines():
        if line.startswith("+++") or line.startswith("---"):
            continue
        if line.startswith("+"):
            added.append("".join(line[1:].split()))
        elif line.startswith("-"):
            removed.add("".join(line[1:].split()))
    if not added and not removed:
        return False
    return all(content in removed for content in added)


def classify_depth(fd: "FileDiff", *, risk: float | None = None) -> str:
    """Assign a review-depth tier to one file diff.

    Risk wins over size: a three-line change to a historically risky file
    is not trivial. Machine-generated files and whitespace-only
    reformatting skip review entirely; documentation / config files are
    trivial regardless of size — a large prose rewrite does not need a
    code-smell pass.
    """
    if risk is not None and risk >= _DEEP_MIN_RISK_SCORE:
        return TIER_DEEP
    path = PurePosixPath(fd.path).as_posix()
    if _GENERATED_PATH_RE.search(path):
        return TIER_SKIP
    if is_whitespace_only_change(fd):
        return TIER_SKIP
    if PurePosixPath(path).suffix.lower() in _LOW_RISK_SUFFIXES:
        return TIER_TRIVIAL
    lines = changed_line_count(fd)
    if lines <= _TRIVIAL_MAX_CHANGED_LINES:
        return TIER_TRIVIAL
    if lines >= _DEEP_MIN_CHANGED_LINES:
        return TIER_DEEP
    return TIER_STANDARD


def plan_steps(
    fd: "FileDiff",
    all_steps: tuple[type["ReviewStep"], ...],
    *,
    risk: float | None = None,
) -> StepPlan:
    """Prune the configured step chain to what this file actually needs.

    Reduced tiers substitute :class:`~prthinker.steps.CompactReviewStep`
    for the analysis chain: one model call covering review/lint/smells
    plus a brief conclusion, instead of five. Deep tier keeps everything.
    """
    tier = classify_depth(fd, risk=risk)
    if tier == TIER_DEEP:
        return StepPlan(tier=tier, steps=tuple(all_steps), skipped=())
    if tier == TIER_SKIP:
        skipped = tuple(cls.name for cls in all_steps)
        return StepPlan(tier=tier, steps=(), skipped=skipped)
    keep = _ALWAYS_KEEP if tier == TIER_TRIVIAL else _STANDARD_KEEP
    candidates = [cls for cls in all_steps if cls.name in keep]
    candidates = _substitute_reduced_review(all_steps, candidates, tier)
    kept = _enforce_dependencies(candidates)
    kept_names = {cls.name for cls in kept}
    skipped = tuple(cls.name for cls in all_steps if cls.name not in kept_names)
    return StepPlan(tier=tier, steps=tuple(kept), skipped=skipped)


def _substitute_reduced_review(
    all_steps: tuple[type["ReviewStep"], ...],
    candidates: list[type["ReviewStep"]],
    tier: str,
) -> list[type["ReviewStep"]]:
    """Swap the pruned analysis chain for its single-call replacement.

    Standard tier with inline findings configured merges analysis and
    findings into ONE :class:`~prthinker.steps.UnifiedReviewStep` call —
    unless counterfactual is kept, which needs the ``inline_findings``
    step result before it runs, so that combination keeps the two-call
    compact + inline shape.
    """
    if not _needs_compact_substitute(all_steps, candidates, tier):
        return candidates
    names = {cls.name for cls in candidates}
    if (
        tier == TIER_STANDARD
        and "inline_findings" in names
        and "counterfactual" not in names
    ):
        return [
            UnifiedReviewStep if cls.name == "inline_findings" else cls
            for cls in candidates
        ]
    return [CompactReviewStep, *candidates]


def _needs_compact_substitute(
    all_steps: tuple[type["ReviewStep"], ...],
    candidates: list[type["ReviewStep"]],
    tier: str,
) -> bool:
    """Substitute the compact single-call review for a pruned analysis chain.

    Standard tier always reviews via the compact step. Trivial tier only
    falls back to it when no output step (inline findings / walkthrough)
    survived — the file still gets looked at, just once. A chain that
    configured no analysis steps has nothing to substitute.
    """
    if not any(cls.name in _ANALYSIS_STEPS for cls in all_steps):
        return False
    if tier == TIER_STANDARD:
        return True
    return not candidates


def _enforce_dependencies(
    candidates: list[type["ReviewStep"]],
) -> list[type["ReviewStep"]]:
    """Drop steps whose declared prerequisites were pruned.

    Steps run in order, so a prerequisite always precedes its dependent;
    a single forward pass with the running kept-set is sufficient.
    ``total_summary`` synthesises whatever analysis ran, so it survives
    with *any* of its inputs present (the prompt marks the rest skipped);
    every other dependent step needs *all* of its prerequisites.
    """
    kept: list[type["ReviewStep"]] = []
    names: set[str] = set()
    for cls in candidates:
        requires = tuple(getattr(cls, "_REQUIRES", ()))
        if requires:
            if cls.name == "total_summary":
                satisfied = any(req in names for req in requires)
            else:
                satisfied = all(req in names for req in requires)
            if not satisfied:
                continue
        kept.append(cls)
        names.add(cls.name)
    return kept


__all__ = [
    "STEP_PLAN_ADAPTIVE",
    "STEP_PLAN_CHOICES",
    "STEP_PLAN_FULL",
    "StepPlan",
    "TIER_DEEP",
    "TIER_SKIP",
    "TIER_STANDARD",
    "TIER_TRIVIAL",
    "changed_line_count",
    "classify_depth",
    "is_whitespace_only_change",
    "plan_steps",
]

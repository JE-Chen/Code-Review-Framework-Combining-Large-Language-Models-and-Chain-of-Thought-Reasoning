"""Aggregate evidence, verification, provenance, and retrieval signals."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from prthinker.schemas import SEVERITY_ORDER

if TYPE_CHECKING:
    from prthinker.pipeline import ReviewResult
    from prthinker.schemas import InlineFinding


_VERIFICATION_STATUSES = ("pass", "fail", "skip", "error")
_EVIDENCE_STATUSES = ("confirmed", "rejected", "inconclusive", "unsupported", "error")

# Display order for review-depth tiers: shallow to deep, then the
# no-planner default. Unknown tiers sort last, alphabetically.
_TIER_DISPLAY_ORDER = ("skip", "trivial", "standard", "deep", "full")
_STEP_PLAN_KEY = "step_plan"


@dataclass(frozen=True)
class ReviewRollup:
    findings: int = 0
    suggestions: int = 0
    verification: dict[str, int] = field(default_factory=dict)
    evidence: dict[str, int] = field(default_factory=dict)
    evidence_kinds: dict[str, int] = field(default_factory=dict)
    provenance_backed: int = 0
    confidence_scored: int = 0
    rag_cited: int = 0
    retrieved_docs: int = 0
    # Per-file review-depth tier counts. Empty (row hidden) when no file
    # carried a step_plan key — i.e. the adaptive planner never ran.
    tier_distribution: dict[str, int] = field(default_factory=dict)

    @property
    def verified_pass(self) -> int:
        return self.verification.get("pass", 0)

    @property
    def verified_problem(self) -> int:
        return self.verification.get("fail", 0) + self.verification.get("error", 0)

    @property
    def evidence_backed(self) -> int:
        return self.evidence.get("confirmed", 0)


def all_findings(result: "ReviewResult") -> list["InlineFinding"]:
    """Flatten the top-level and per-file findings into one list."""
    findings = list(result.inline_findings)
    for file_result in result.per_file:
        findings.extend(file_result.inline_findings)
    return findings


def severity_counts(findings: "list[InlineFinding]") -> dict[str, int]:
    """Count findings per severity, always returning every known bucket."""
    counts = {sev: 0 for sev in SEVERITY_ORDER}
    for finding in findings:
        # Unknown severities (should not happen given the schema) are
        # bucketed under "info" rather than dropped, so the total stays
        # honest.
        counts[finding.severity if finding.severity in counts else "info"] += 1
    return counts


def tier_distribution(result: "ReviewResult") -> dict[str, int]:
    """Per-file review-depth tier counts for a review result.

    Files whose ``step_outputs`` carry no ``step_plan`` key ran the full
    chain and are counted under ``"full"``.
    """
    counts = Counter(
        fr.step_outputs.get(_STEP_PLAN_KEY, "full") for fr in result.per_file
    )
    return dict(counts)


def ordered_tiers(counts: dict[str, int]) -> list[str]:
    """Tier names sorted shallow-to-deep; unknown tiers last, alphabetically."""

    def sort_key(tier: str) -> tuple[int, str]:
        if tier in _TIER_DISPLAY_ORDER:
            return _TIER_DISPLAY_ORDER.index(tier), tier
        return len(_TIER_DISPLAY_ORDER), tier

    return sorted(counts, key=sort_key)


def _planned_tier_distribution(result: "ReviewResult") -> dict[str, int]:
    """Tier counts when the planner ran on at least one file, else empty.

    The empty dict keeps the "Review depth" rollup row (and therefore every
    renderer's output) byte-identical for full-plan reviews.
    """
    if any(_STEP_PLAN_KEY in fr.step_outputs for fr in result.per_file):
        return tier_distribution(result)
    return {}


def _count_docs(result: "ReviewResult") -> int:
    docs = set(result.rag_docs)
    for file_result in result.per_file:
        docs.update(file_result.rag_docs)
    return len(docs)


@dataclass
class _RollupCounters:
    """Mutable accumulators threaded through the per-finding tally loop."""

    verification: Counter = field(
        default_factory=lambda: Counter({status: 0 for status in _VERIFICATION_STATUSES})
    )
    evidence: Counter = field(
        default_factory=lambda: Counter({status: 0 for status in _EVIDENCE_STATUSES})
    )
    evidence_kinds: Counter = field(default_factory=Counter)
    suggestions: int = 0
    provenance_backed: int = 0
    confidence_scored: int = 0
    rag_cited: int = 0


def _tally_provenance(counters: _RollupCounters, provenance) -> None:
    if provenance.citations:
        counters.provenance_backed += 1
    if provenance.confidence is not None:
        counters.confidence_scored += 1
    if any(citation.kind == "rag_rule" for citation in provenance.citations):
        counters.rag_cited += 1


def _tally_finding(counters: _RollupCounters, finding: "InlineFinding") -> None:
    if finding.suggestion:
        counters.suggestions += 1
    if finding.verification is not None:
        counters.verification[finding.verification.status] += 1
    if finding.provenance is not None:
        _tally_provenance(counters, finding.provenance)
    for item in finding.evidence:
        counters.evidence[item.status] += 1
        counters.evidence_kinds[item.kind] += 1


def rollup_review(result: "ReviewResult") -> ReviewRollup:
    """Return a compact audit-signal rollup for reports and PR summaries."""
    findings = all_findings(result)
    counters = _RollupCounters()
    for finding in findings:
        _tally_finding(counters, finding)
    return ReviewRollup(
        findings=len(findings),
        suggestions=counters.suggestions,
        verification=dict(counters.verification),
        evidence=dict(counters.evidence),
        evidence_kinds=dict(counters.evidence_kinds),
        provenance_backed=counters.provenance_backed,
        confidence_scored=counters.confidence_scored,
        rag_cited=counters.rag_cited,
        retrieved_docs=_count_docs(result),
        tier_distribution=_planned_tier_distribution(result),
    )


def rollup_rows(rollup: ReviewRollup) -> list[tuple[str, str]]:
    """Label/value pairs for the audit rollup, shared by every renderer.

    Single source of truth for the rollup lines: the markdown rollup, the
    HTML report's audit section, and the PR-comment digest all format from
    these rows, so the wording can never drift between outputs.
    """
    rows = [
        (
            "Findings",
            f"{rollup.findings} finding(s) · "
            f"{rollup.confidence_scored} confidence-scored",
        ),
        (
            "Verification",
            f"{rollup.verified_pass} pass · "
            f"{rollup.verification.get('fail', 0)} fail · "
            f"{rollup.verification.get('skip', 0)} skip · "
            f"{rollup.verification.get('error', 0)} error",
        ),
        (
            "Auto-fix safety",
            f"{rollup.suggestions} suggestion(s) · "
            f"{rollup.verified_pass} sandbox-verified · "
            f"{rollup.verified_problem} failed/error",
        ),
        (
            "Evidence",
            f"{rollup.evidence_backed} confirmed · "
            f"{rollup.evidence.get('rejected', 0)} rejected · "
            f"{rollup.evidence.get('inconclusive', 0)} inconclusive · "
            f"{rollup.evidence.get('unsupported', 0)} unsupported · "
            f"{rollup.evidence.get('error', 0)} error",
        ),
        (
            "Retrieval/provenance",
            f"{rollup.retrieved_docs} retrieved doc(s) · "
            f"{rollup.provenance_backed} provenance-backed finding(s) · "
            f"{rollup.rag_cited} RAG-cited",
        ),
    ]
    rows.extend(_optional_rollup_rows(rollup))
    return rows


def _optional_rollup_rows(rollup: ReviewRollup) -> list[tuple[str, str]]:
    """Rows that only appear when their signal is present at all."""
    rows: list[tuple[str, str]] = []
    if rollup.tier_distribution:
        depth = " · ".join(
            f"{tier}: {rollup.tier_distribution[tier]}"
            for tier in ordered_tiers(rollup.tier_distribution)
        )
        rows.append(("Review depth", depth))
    if rollup.evidence_kinds:
        kinds = " · ".join(
            f"{kind}: {count}"
            for kind, count in sorted(rollup.evidence_kinds.items())
        )
        rows.append(("Evidence kinds", kinds))
    return rows


def format_markdown_rollup(
    result: "ReviewResult", rollup: ReviewRollup | None = None
) -> list[str]:
    """Markdown bullets for the audit-signal rollup.

    ``rollup`` lets a caller that already computed the rollup pass it in;
    it is derived from ``result`` when omitted.
    """
    rollup = rollup if rollup is not None else rollup_review(result)
    return ["## Audit rollups", ""] + [
        f"- {label}: {value}" for label, value in rollup_rows(rollup)
    ]


__all__ = [
    "ReviewRollup",
    "all_findings",
    "format_markdown_rollup",
    "ordered_tiers",
    "rollup_review",
    "rollup_rows",
    "severity_counts",
    "tier_distribution",
]

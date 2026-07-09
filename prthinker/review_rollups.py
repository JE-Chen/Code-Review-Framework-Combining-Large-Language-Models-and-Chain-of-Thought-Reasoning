"""Aggregate evidence, verification, provenance, and retrieval signals."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from prthinker.pipeline import ReviewResult
    from prthinker.schemas import InlineFinding


_VERIFICATION_STATUSES = ("pass", "fail", "skip", "error")
_EVIDENCE_STATUSES = ("confirmed", "rejected", "inconclusive", "unsupported", "error")


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

    @property
    def verified_pass(self) -> int:
        return self.verification.get("pass", 0)

    @property
    def verified_problem(self) -> int:
        return self.verification.get("fail", 0) + self.verification.get("error", 0)

    @property
    def evidence_backed(self) -> int:
        return self.evidence.get("confirmed", 0)


def _all_findings(result: "ReviewResult") -> list["InlineFinding"]:
    findings = list(result.inline_findings)
    for file_result in result.per_file:
        findings.extend(file_result.inline_findings)
    return findings


def _count_docs(result: "ReviewResult") -> int:
    docs = set(result.rag_docs)
    for file_result in result.per_file:
        docs.update(file_result.rag_docs)
    return len(docs)


def rollup_review(result: "ReviewResult") -> ReviewRollup:
    """Return a compact audit-signal rollup for reports and PR summaries."""
    findings = _all_findings(result)
    verification = Counter({status: 0 for status in _VERIFICATION_STATUSES})
    evidence = Counter({status: 0 for status in _EVIDENCE_STATUSES})
    evidence_kinds: Counter[str] = Counter()
    suggestions = provenance_backed = confidence_scored = rag_cited = 0
    for finding in findings:
        if finding.suggestion:
            suggestions += 1
        if finding.verification is not None:
            verification[finding.verification.status] += 1
        if finding.provenance is not None:
            if finding.provenance.citations:
                provenance_backed += 1
            if finding.provenance.confidence is not None:
                confidence_scored += 1
            if any(citation.kind == "rag_rule" for citation in finding.provenance.citations):
                rag_cited += 1
        for item in finding.evidence:
            evidence[item.status] += 1
            evidence_kinds[item.kind] += 1
    return ReviewRollup(
        findings=len(findings),
        suggestions=suggestions,
        verification=dict(verification),
        evidence=dict(evidence),
        evidence_kinds=dict(evidence_kinds),
        provenance_backed=provenance_backed,
        confidence_scored=confidence_scored,
        rag_cited=rag_cited,
        retrieved_docs=_count_docs(result),
    )


def format_markdown_rollup(result: "ReviewResult") -> list[str]:
    """Markdown bullets for the audit-signal rollup."""
    rollup = rollup_review(result)
    lines = [
        "## Audit rollups",
        "",
        (
            f"- Verification: {rollup.verified_pass} pass · "
            f"{rollup.verification.get('fail', 0)} fail · "
            f"{rollup.verification.get('skip', 0)} skip · "
            f"{rollup.verification.get('error', 0)} error"
        ),
        (
            f"- Auto-fix safety: {rollup.suggestions} suggestion(s) · "
            f"{rollup.verified_pass} sandbox-verified · "
            f"{rollup.verified_problem} failed/error"
        ),
        (
            f"- Evidence: {rollup.evidence_backed} confirmed · "
            f"{rollup.evidence.get('rejected', 0)} rejected · "
            f"{rollup.evidence.get('inconclusive', 0)} inconclusive"
        ),
        (
            f"- Retrieval/provenance: {rollup.retrieved_docs} retrieved doc(s) · "
            f"{rollup.provenance_backed} provenance-backed finding(s) · "
            f"{rollup.rag_cited} RAG-cited"
        ),
    ]
    if rollup.evidence_kinds:
        kinds = " · ".join(
            f"{kind}: {count}" for kind, count in sorted(rollup.evidence_kinds.items())
        )
        lines.append(f"- Evidence kinds: {kinds}")
    return lines


__all__ = ["ReviewRollup", "format_markdown_rollup", "rollup_review"]

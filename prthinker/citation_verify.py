"""Read-only verification of provenance citations on inline findings.

Cross-checks each :class:`~prthinker.schemas.ProvenanceCitation` attached to an
:class:`~prthinker.schemas.InlineFinding` against the sizes of the RAG-rule and
accepted-example corpora it can legally point at, and against the set of diff
lines the finding is allowed to ground itself on. Pure and runner-safe: stdlib
only, no model inference, and the input findings are never mutated.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from prthinker.schemas import InlineFinding, ProvenanceCitation

_KIND_RAG_RULE = "rag_rule"
_KIND_ACCEPTED_EXAMPLE = "accepted_example"
_KIND_DIFF_EVIDENCE = "diff_evidence"


@dataclass(frozen=True)
class CitationIssue:
    """One citation that fails verification, located at a finding's line."""

    path: str
    line: int
    kind: str
    reason: str


def _check_index_citation(
    finding: InlineFinding,
    citation: ProvenanceCitation,
    upper_bound: int,
    corpus_label: str,
) -> CitationIssue | None:
    """Return an issue if a 1-based index citation falls outside ``[1, bound]``."""
    index = citation.index
    if index is None:
        return CitationIssue(
            path=finding.path,
            line=finding.line,
            kind=citation.kind,
            reason=f"{corpus_label} citation has no index",
        )
    if index < 1 or index > upper_bound:
        return CitationIssue(
            path=finding.path,
            line=finding.line,
            kind=citation.kind,
            reason=(
                f"{corpus_label} index {index} out of range "
                f"(1..{upper_bound})"
            ),
        )
    return None


def _check_diff_evidence(
    finding: InlineFinding,
    citation: ProvenanceCitation,
    allowed_lines: set[int] | None,
) -> CitationIssue | None:
    """Return an issue if any cited diff line is outside ``allowed_lines``."""
    if allowed_lines is None:
        return None
    outside = sorted(line for line in citation.lines if line not in allowed_lines)
    if not outside:
        return None
    return CitationIssue(
        path=finding.path,
        line=finding.line,
        kind=citation.kind,
        reason=f"diff_evidence lines {outside} outside allowed diff lines",
    )


def _verify_citation(
    finding: InlineFinding,
    citation: ProvenanceCitation,
    n_rag_rules: int,
    n_accepted_examples: int,
    allowed_lines: set[int] | None,
) -> CitationIssue | None:
    """Dispatch a single citation to the checker for its ``kind``."""
    if citation.kind == _KIND_RAG_RULE:
        return _check_index_citation(finding, citation, n_rag_rules, "rag_rule")
    if citation.kind == _KIND_ACCEPTED_EXAMPLE:
        return _check_index_citation(
            finding, citation, n_accepted_examples, "accepted_example"
        )
    if citation.kind == _KIND_DIFF_EVIDENCE:
        return _check_diff_evidence(finding, citation, allowed_lines)
    return None


def verify_citations(
    findings: Iterable[InlineFinding],
    *,
    n_rag_rules: int,
    n_accepted_examples: int,
    allowed_lines: set[int] | None = None,
) -> list[CitationIssue]:
    """Return citation issues across ``findings`` without mutating them."""
    issues: list[CitationIssue] = []
    for finding in findings:
        provenance = finding.provenance
        if provenance is None:
            continue
        for citation in provenance.citations:
            issue = _verify_citation(
                finding,
                citation,
                n_rag_rules,
                n_accepted_examples,
                allowed_lines,
            )
            if issue is not None:
                issues.append(issue)
    return issues

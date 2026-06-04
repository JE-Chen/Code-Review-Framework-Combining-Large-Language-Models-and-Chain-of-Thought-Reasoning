"""Unit tests for prthinker.citation_verify."""

from __future__ import annotations

from prthinker.citation_verify import CitationIssue, verify_citations
from prthinker.schemas import (
    InlineFinding,
    Provenance,
    ProvenanceCitation,
)

_PATH = "src/mod.py"


def _finding(citations: list[ProvenanceCitation] | None, line: int = 5) -> InlineFinding:
    provenance = Provenance(citations=citations) if citations is not None else None
    return InlineFinding(
        path=_PATH,
        line=line,
        comment="example finding",
        provenance=provenance,
    )


def test_out_of_range_rag_rule_flagged() -> None:
    finding = _finding([ProvenanceCitation(kind="rag_rule", index=4)])
    issues = verify_citations(
        [finding], n_rag_rules=2, n_accepted_examples=0
    )
    assert len(issues) == 1
    assert issues[0].kind == "rag_rule"
    assert issues[0].path == _PATH
    assert issues[0].line == 5
    assert "out of range" in issues[0].reason


def test_valid_rag_index_not_flagged() -> None:
    finding = _finding([ProvenanceCitation(kind="rag_rule", index=2)])
    issues = verify_citations(
        [finding], n_rag_rules=2, n_accepted_examples=0
    )
    assert issues == []


def test_accepted_example_range() -> None:
    in_range = _finding(
        [ProvenanceCitation(kind="accepted_example", index=3)], line=7
    )
    out_of_range = _finding(
        [ProvenanceCitation(kind="accepted_example", index=4)], line=8
    )
    issues = verify_citations(
        [in_range, out_of_range], n_rag_rules=0, n_accepted_examples=3
    )
    assert len(issues) == 1
    assert issues[0].line == 8
    assert issues[0].kind == "accepted_example"


def test_diff_evidence_outside_allowed_lines_flagged() -> None:
    finding = _finding(
        [ProvenanceCitation(kind="diff_evidence", lines=[10, 99])]
    )
    issues = verify_citations(
        [finding],
        n_rag_rules=0,
        n_accepted_examples=0,
        allowed_lines={10, 11, 12},
    )
    assert len(issues) == 1
    assert issues[0].kind == "diff_evidence"
    assert "99" in issues[0].reason


def test_diff_evidence_all_within_allowed_lines_not_flagged() -> None:
    finding = _finding(
        [ProvenanceCitation(kind="diff_evidence", lines=[10, 11])]
    )
    issues = verify_citations(
        [finding],
        n_rag_rules=0,
        n_accepted_examples=0,
        allowed_lines={10, 11, 12},
    )
    assert issues == []


def test_diff_evidence_skipped_when_allowed_lines_none() -> None:
    finding = _finding(
        [ProvenanceCitation(kind="diff_evidence", lines=[999])]
    )
    issues = verify_citations([finding], n_rag_rules=0, n_accepted_examples=0)
    assert issues == []


def test_findings_without_provenance_produce_no_issues() -> None:
    findings = [_finding(None), _finding([])]
    issues = verify_citations(
        [findings[0]],
        n_rag_rules=5,
        n_accepted_examples=5,
        allowed_lines={1, 2},
    )
    issues_empty = verify_citations(
        [findings[1]], n_rag_rules=5, n_accepted_examples=5
    )
    assert issues == []
    assert issues_empty == []


def test_empty_findings_iterable() -> None:
    assert verify_citations([], n_rag_rules=3, n_accepted_examples=3) == []


def test_boundary_index_one_and_upper() -> None:
    lower = _finding([ProvenanceCitation(kind="rag_rule", index=1)], line=1)
    upper = _finding([ProvenanceCitation(kind="rag_rule", index=2)], line=2)
    issues = verify_citations(
        [lower, upper], n_rag_rules=2, n_accepted_examples=0
    )
    assert issues == []


def test_empty_corpus_flags_any_index() -> None:
    finding = _finding([ProvenanceCitation(kind="rag_rule", index=1)])
    issues = verify_citations(
        [finding], n_rag_rules=0, n_accepted_examples=0
    )
    assert len(issues) == 1
    assert "out of range" in issues[0].reason


def test_does_not_mutate_findings() -> None:
    citation = ProvenanceCitation(kind="rag_rule", index=99)
    finding = _finding([citation])
    snapshot = finding.model_dump()
    verify_citations([finding], n_rag_rules=1, n_accepted_examples=0)
    assert finding.model_dump() == snapshot


def test_citation_issue_is_frozen() -> None:
    issue = CitationIssue(path=_PATH, line=1, kind="rag_rule", reason="x")
    try:
        issue.line = 2  # type: ignore[misc]
    except AttributeError:
        return
    raise AssertionError("CitationIssue should be frozen")

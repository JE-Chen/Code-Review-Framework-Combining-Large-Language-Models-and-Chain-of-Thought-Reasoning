"""Tests for the shared audit-rollup helpers (review_rollups)."""

from __future__ import annotations

from prthinker.pipeline import FileReviewResult, ReviewResult
from prthinker.review_rollups import (
    ReviewRollup,
    all_findings,
    format_markdown_rollup,
    rollup_review,
    rollup_rows,
    severity_counts,
)
from prthinker.schemas import (
    Evidence,
    InlineFinding,
    Provenance,
    ProvenanceCitation,
    SuggestionVerification,
)


def _finding(path="a.py", line=5, severity="warning", comment="x", **kw):
    return InlineFinding(
        path=path, line=line, severity=severity, comment=comment, **kw
    )


def _pf(path="f.py", findings=None) -> FileReviewResult:
    return FileReviewResult(
        path=path, rag_docs=[], step_outputs={},
        inline_findings=findings or [],
    )


def _result(findings=None, per_file=None) -> ReviewResult:
    return ReviewResult(
        code_diff="", rag_docs=[],
        inline_findings=findings or [], per_file=per_file or [],
    )


# ----- all_findings --------------------------------------------------------

def test_all_findings_flattens_top_level_and_per_file():
    top = _finding(comment="top")
    nested = _finding(path="f.py", comment="nested")
    result = _result(findings=[top], per_file=[_pf(findings=[nested])])
    flat = all_findings(result)
    assert [f.comment for f in flat] == ["top", "nested"]


def test_all_findings_empty_result():
    assert all_findings(_result()) == []


def test_all_findings_per_file_only():
    nested = _finding(path="f.py")
    assert all_findings(_result(per_file=[_pf(findings=[nested])])) == [nested]


# ----- severity_counts -----------------------------------------------------

def test_severity_counts_all_buckets_present():
    counts = severity_counts([_finding(severity="error")])
    assert counts == {"error": 1, "warning": 0, "info": 0}


def test_severity_counts_empty_input():
    assert severity_counts([]) == {"error": 0, "warning": 0, "info": 0}


def test_severity_counts_unknown_bucketed_into_info():
    bad = _finding()
    object.__setattr__(bad, "severity", "critical")
    assert severity_counts([bad]) == {"error": 0, "warning": 0, "info": 1}


# ----- rollup_rows ---------------------------------------------------------

_EXPECTED_LABELS = [
    "Findings",
    "Verification",
    "Auto-fix safety",
    "Evidence",
    "Retrieval/provenance",
]


def test_rollup_rows_labels_and_order_for_empty_rollup():
    rows = rollup_rows(ReviewRollup())
    assert [label for label, _ in rows] == _EXPECTED_LABELS


def test_rollup_rows_surfaces_findings_and_confidence_scored():
    rows = dict(rollup_rows(ReviewRollup(findings=3, confidence_scored=2)))
    assert rows["Findings"] == "3 finding(s) · 2 confidence-scored"


def test_rollup_rows_surfaces_unsupported_and_error_evidence():
    rollup = ReviewRollup(evidence={"confirmed": 1, "unsupported": 2, "error": 1})
    rows = dict(rollup_rows(rollup))
    assert "2 unsupported" in rows["Evidence"]
    assert "1 error" in rows["Evidence"]


def test_rollup_rows_verification_wording():
    rollup = ReviewRollup(verification={"pass": 2, "fail": 1, "skip": 0, "error": 0})
    rows = dict(rollup_rows(rollup))
    assert rows["Verification"] == "2 pass · 1 fail · 0 skip · 0 error"


def test_rollup_rows_evidence_kinds_only_when_present():
    assert "Evidence kinds" not in dict(rollup_rows(ReviewRollup()))
    rollup = ReviewRollup(evidence_kinds={"test": 2, "lint": 1})
    assert dict(rollup_rows(rollup))["Evidence kinds"] == "lint: 1 · test: 2"


# ----- rollup_review -------------------------------------------------------

def _rich_finding() -> InlineFinding:
    return _finding(
        suggestion="return 1",
        verification=SuggestionVerification(status="pass", verify_cmd="pytest"),
        provenance=Provenance(
            confidence=0.9,
            citations=[ProvenanceCitation(kind="rag_rule", index=1)],
        ),
        evidence=[
            Evidence(kind="test", status="confirmed", tool="pytest", summary="ok")
        ],
    )


def test_rollup_review_counts_audit_signals():
    rollup = rollup_review(_result(findings=[_rich_finding()]))
    assert rollup.findings == 1
    assert rollup.suggestions == 1
    assert rollup.verified_pass == 1
    assert rollup.confidence_scored == 1
    assert rollup.provenance_backed == 1
    assert rollup.rag_cited == 1
    assert rollup.evidence_backed == 1


def test_rollup_review_empty_result_is_all_zero():
    rollup = rollup_review(_result())
    assert rollup.findings == 0
    assert rollup.suggestions == 0
    assert all(v == 0 for v in rollup.verification.values())


# ----- format_markdown_rollup ----------------------------------------------

def test_format_markdown_rollup_formats_from_rows():
    lines = format_markdown_rollup(_result(findings=[_rich_finding()]))
    assert lines[0] == "## Audit rollups"
    assert any(line.startswith("- Verification: 1 pass") for line in lines)
    assert any("1 finding(s) · 1 confidence-scored" in line for line in lines)


def test_format_markdown_rollup_accepts_precomputed_rollup():
    result = _result(findings=[_rich_finding()])
    precomputed = rollup_review(result)
    assert format_markdown_rollup(result, precomputed) == format_markdown_rollup(result)


def test_format_markdown_rollup_uses_supplied_rollup_verbatim():
    # A caller-supplied rollup wins over re-deriving from the result.
    lines = format_markdown_rollup(_result(), ReviewRollup(findings=42))
    assert any("42 finding(s)" in line for line in lines)

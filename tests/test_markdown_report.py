"""Tests for the standalone Markdown report exporter."""

from __future__ import annotations

from prthinker.markdown_report import render_markdown, write_markdown
from prthinker.pipeline import FileReviewResult, ReviewResult
from prthinker.schemas import Evidence, InlineFinding, Provenance, ProvenanceCitation, SuggestionVerification


def _finding(path="a.py", line=5, severity="warning", comment="needs work"):
    return InlineFinding(path=path, line=line, severity=severity, comment=comment)


def _pf(path, findings=None, **kw) -> FileReviewResult:
    return FileReviewResult(
        path=path, rag_docs=[], step_outputs={},
        inline_findings=findings or [], **kw,
    )


def _result(findings=None, per_file=None, code_diff="diff") -> ReviewResult:
    return ReviewResult(
        code_diff=code_diff, rag_docs=[],
        inline_findings=findings or [], per_file=per_file or [],
    )


def test_has_title_and_summary():
    out = render_markdown(_result())
    assert out.startswith("# prthinker review")
    assert "## Summary" in out
    assert "Total findings: 0" in out


def test_custom_title():
    assert render_markdown(_result(), title="My Review").startswith("# My Review")


def test_summary_counts_and_diff_totals():
    diff = (
        "diff --git a/a.py b/a.py\n--- a/a.py\n+++ b/a.py\n"
        "@@ -1,1 +1,2 @@\n-old\n+new1\n+new2\n"
    )
    out = render_markdown(_result([_finding(severity="error")], code_diff=diff))
    assert "1 file(s) changed · +2 −1" in out
    assert "error: 1" in out


def test_per_file_sections_with_findings():
    pf = _pf("src/x.py", [_finding(path="src/x.py", comment="boom", line=3)])
    out = render_markdown(_result(per_file=[pf]))
    assert "### src/x.py" in out
    assert "`src/x.py:3` **[warning]** boom" in out


def test_binary_and_deleted_flagged():
    out = render_markdown(_result(per_file=[
        _pf("img.png", is_binary=True), _pf("old.py", is_deleted=True),
    ]))
    assert "### img.png (binary)" in out
    assert "### old.py (deleted)" in out
    assert "_No findings._" in out


def test_signals_section():
    diff = (
        "diff --git a/a.py b/a.py\n--- a/a.py\n+++ b/a.py\n"
        "@@ -0,0 +1,1 @@\n+<<<<<<< HEAD\n"
    )
    out = render_markdown(_result(code_diff=diff))
    assert "## Orientation signals" in out
    assert "Leftover merge-conflict marker" in out


def test_no_signals_section_when_clean():
    out = render_markdown(_result(code_diff=""))
    assert "## Orientation signals" not in out


def test_multiline_comment_collapsed():
    out = render_markdown(_result([_finding(comment="line1\nline2")]))
    assert "line1 line2" in out


def test_write_markdown_roundtrips(tmp_path):
    out_path = tmp_path / "nested" / "report.md"
    write_markdown(_result([_finding(comment="boom")]), out_path)
    text = out_path.read_text(encoding="utf-8")
    assert text == render_markdown(_result([_finding(comment="boom")]))
    assert "boom" in text


def test_audit_rollups_rendered():
    finding = InlineFinding(
        path="a.py",
        line=1,
        comment="x",
        suggestion="return 1",
        verification=SuggestionVerification(status="pass", verify_cmd="pytest"),
        provenance=Provenance(
            confidence=0.8,
            citations=[ProvenanceCitation(kind="rag_rule", index=1)],
        ),
        evidence=[
            Evidence(kind="test", status="confirmed", tool="pytest", summary="pass")
        ],
    )
    out = render_markdown(_result([finding], code_diff=""))
    assert "## Audit rollups" in out
    assert "Verification: 1 pass" in out
    assert "1 provenance-backed" in out


def test_rollup_surfaces_findings_and_confidence_scored():
    finding = InlineFinding(
        path="a.py", line=1, comment="x",
        provenance=Provenance(confidence=0.8, citations=[]),
    )
    out = render_markdown(_result([finding], code_diff=""))
    assert "Findings: 1 finding(s) · 1 confidence-scored" in out


def test_render_markdown_accepts_precomputed_rollup():
    from prthinker.review_rollups import rollup_review

    result = _result([_finding()], code_diff="")
    precomputed = rollup_review(result)
    assert render_markdown(result, rollup=precomputed) == render_markdown(result)

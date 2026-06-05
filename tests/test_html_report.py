"""Tests for the standalone HTML review report renderer."""

from __future__ import annotations

import sys
from pathlib import Path

# Make ``prthinker`` importable when running pytest from the repo root.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from prthinker.html_report import (  # noqa: E402
    render_report,
    severity_counts,
    write_report,
)
from prthinker.pipeline import FileReviewResult, ReviewResult  # noqa: E402
from prthinker.schemas import InlineFinding  # noqa: E402


def _finding(
    path: str = "src/app.py",
    line: int = 10,
    severity: str = "warning",
    comment: str = "consider renaming",
) -> InlineFinding:
    return InlineFinding(
        path=path, line=line, severity=severity, comment=comment,
    )


def test_output_contains_finding_text() -> None:
    result = ReviewResult(
        code_diff="diff",
        rag_docs=[],
        inline_findings=[_finding(comment="unique-marker-text")],
    )
    out = render_report(result)
    assert "unique-marker-text" in out
    assert "src/app.py:10" in out
    assert "[warning]" in out


def test_script_content_is_escaped() -> None:
    payload = "<script>alert('xss')</script>"
    result = ReviewResult(
        code_diff="diff",
        rag_docs=[],
        inline_findings=[_finding(comment=payload, path="<b>p</b>.py")],
    )
    out = render_report(result)
    # The raw, unescaped tag must NOT appear anywhere in the document.
    assert "<script>" not in out
    assert "</script>" not in out
    assert "<b>p</b>.py" not in out
    # The escaped form must be present.
    assert "&lt;script&gt;" in out
    assert "&lt;b&gt;p&lt;/b&gt;.py" in out


def test_title_is_escaped() -> None:
    result = ReviewResult(code_diff="", rag_docs=[])
    out = render_report(result, title="<i>evil</i>")
    assert "<i>evil</i>" not in out
    assert "&lt;i&gt;evil&lt;/i&gt;" in out


def test_empty_result_still_valid_html() -> None:
    result = ReviewResult(code_diff="", rag_docs=[])
    out = render_report(result)
    assert out.startswith("<!DOCTYPE html>")
    assert "<html" in out
    assert "</html>" in out
    assert "<body>" in out and "</body>" in out
    # No findings → all severity counts are zero.
    assert "Total findings: 0" in out


def test_severity_counts_correct() -> None:
    findings = [
        _finding(severity="error"),
        _finding(severity="error"),
        _finding(severity="warning"),
        _finding(severity="info"),
        _finding(severity="info"),
        _finding(severity="info"),
    ]
    counts = severity_counts(findings)
    assert counts == {"error": 2, "warning": 1, "info": 3}


def test_severity_counts_aggregates_top_and_per_file() -> None:
    per_file = FileReviewResult(
        path="src/b.py",
        rag_docs=[],
        step_outputs={},
        inline_findings=[_finding(severity="error", path="src/b.py")],
    )
    result = ReviewResult(
        code_diff="diff",
        rag_docs=[],
        inline_findings=[_finding(severity="warning")],
        per_file=[per_file],
    )
    out = render_report(result)
    assert "Total findings: 2" in out
    assert "error: 1" in out
    assert "warning: 1" in out
    assert "info: 0" in out
    # Per-file section header renders the file path.
    assert "src/b.py" in out


def test_binary_and_deleted_files_are_marked() -> None:
    binary = FileReviewResult(
        path="img.png", rag_docs=[], step_outputs={},
        inline_findings=[], is_binary=True,
    )
    deleted = FileReviewResult(
        path="old.py", rag_docs=[], step_outputs={},
        inline_findings=[], is_deleted=True,
    )
    result = ReviewResult(
        code_diff="diff", rag_docs=[], per_file=[binary, deleted],
    )
    out = render_report(result)
    assert "img.png (binary)" in out
    assert "old.py (deleted)" in out
    assert "No findings." in out


def test_write_report_roundtrip(tmp_path: Path) -> None:
    result = ReviewResult(
        code_diff="diff",
        rag_docs=[],
        inline_findings=[_finding(comment="written-finding")],
    )
    out_path = tmp_path / "nested" / "report.html"
    write_report(result, out_path)
    assert out_path.exists()
    written = out_path.read_text(encoding="utf-8")
    assert written == render_report(result)
    assert "written-finding" in written


_CONFLICT_DIFF = (
    "diff --git a/a.py b/a.py\n"
    "--- a/a.py\n"
    "+++ b/a.py\n"
    "@@ -0,0 +1,1 @@\n"
    "+<<<<<<< HEAD\n"
)


def test_orientation_signals_section_rendered() -> None:
    result = ReviewResult(code_diff=_CONFLICT_DIFF, rag_docs=[])
    out = render_report(result)
    assert "Orientation signals" in out
    assert "Leftover merge-conflict marker" in out
    assert "a.py:1" in out


def test_no_signals_section_when_clean() -> None:
    result = ReviewResult(code_diff="", rag_docs=[])
    out = render_report(result)
    assert "Orientation signals" not in out


def test_signal_path_is_escaped() -> None:
    diff = (
        "diff --git a/x b/<b>x</b>.py\n"
        "--- a/x\n"
        "+++ b/<b>x</b>.py\n"
        "@@ -0,0 +1,1 @@\n"
        "+<<<<<<< HEAD\n"
    )
    result = ReviewResult(code_diff=diff, rag_docs=[])
    out = render_report(result)
    assert "<b>x</b>.py" not in out
    assert "&lt;b&gt;x&lt;/b&gt;.py" in out


def test_unknown_severity_buckets_into_info() -> None:
    # The schema constrains severity, but the counter must not KeyError
    # on a value outside the known ladder.
    bad = _finding()
    object.__setattr__(bad, "severity", "critical")
    counts = severity_counts([bad])
    assert counts == {"error": 0, "warning": 0, "info": 1}


def test_report_has_embedded_style_and_footer() -> None:
    result = ReviewResult(code_diff="", rag_docs=[])
    out = render_report(result)
    assert "<style>" in out and "</style>" in out
    assert "<footer>" in out
    assert "Generated by prthinker" in out


def test_summary_shows_diff_totals() -> None:
    diff = (
        "diff --git a/a.py b/a.py\n"
        "--- a/a.py\n"
        "+++ b/a.py\n"
        "@@ -1,2 +1,3 @@\n"
        " keep\n"
        "+added one\n"
        "+added two\n"
        "-removed one\n"
    )
    result = ReviewResult(code_diff=diff, rag_docs=[])
    out = render_report(result)
    assert "1 file(s) changed" in out
    assert "+2 −1" in out


def test_no_diff_totals_when_no_diff() -> None:
    result = ReviewResult(code_diff="", rag_docs=[])
    out = render_report(result)
    assert "file(s) changed" not in out

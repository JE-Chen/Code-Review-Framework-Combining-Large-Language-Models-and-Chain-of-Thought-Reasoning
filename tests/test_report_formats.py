"""Tests for the report-format registry and the --report-dir writer."""

from __future__ import annotations

import json

from prthinker.pipeline import ReviewResult
from prthinker.report_formats import REPORT_FORMATS, write_report_dir
from prthinker.schemas import InlineFinding


def _finding(path="a.py", line=5, severity="warning", comment="boom"):
    return InlineFinding(path=path, line=line, severity=severity, comment=comment)


def _result() -> ReviewResult:
    diff = (
        "diff --git a/a.py b/a.py\n--- a/a.py\n+++ b/a.py\n"
        "@@ -0,0 +1,1 @@\n+<<<<<<< HEAD\n"
    )
    return ReviewResult(code_diff=diff, rag_docs=[], inline_findings=[_finding()])


def test_registry_has_expected_formats():
    names = {fmt.name for fmt in REPORT_FORMATS}
    assert names == {
        "sarif", "html", "markdown", "codequality",
        "sonar", "junit", "csv", "metrics",
    }


def test_registry_filenames_unique():
    files = [fmt.filename for fmt in REPORT_FORMATS]
    assert len(files) == len(set(files))


def test_write_report_dir_emits_every_file(tmp_path):
    out_dir = tmp_path / "reports"
    written = write_report_dir(_result(), out_dir)
    assert len(written) == len(REPORT_FORMATS)
    for fmt in REPORT_FORMATS:
        assert (out_dir / fmt.filename).exists()


def test_write_report_dir_creates_missing_directory(tmp_path):
    out_dir = tmp_path / "nested" / "deep"
    write_report_dir(_result(), out_dir)
    assert (out_dir / "prthinker.sarif").exists()


def test_written_json_files_are_valid(tmp_path):
    out_dir = tmp_path / "reports"
    write_report_dir(_result(), out_dir)
    for name in ("gl-code-quality.json", "sonar-issues.json", "metrics.json",
                 "prthinker.sarif"):
        json.loads((out_dir / name).read_text(encoding="utf-8"))


def test_returns_paths_in_registry_order(tmp_path):
    written = write_report_dir(_result(), tmp_path / "r")
    assert [p.name for p in written] == [fmt.filename for fmt in REPORT_FORMATS]

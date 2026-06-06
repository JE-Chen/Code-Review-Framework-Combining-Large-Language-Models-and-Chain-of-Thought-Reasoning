"""Tests for the CSV exporter."""

from __future__ import annotations

import csv
import io

from prthinker.csv_report import to_csv_string, write_csv
from prthinker.pipeline import ReviewResult
from prthinker.schemas import InlineFinding


def _finding(path="a.py", line=5, severity="warning", comment="needs work"):
    return InlineFinding(path=path, line=line, severity=severity, comment=comment)


def _result(findings=None, code_diff="diff") -> ReviewResult:
    return ReviewResult(
        code_diff=code_diff, rag_docs=[], inline_findings=findings or []
    )


def _rows(text: str) -> list[dict]:
    return list(csv.DictReader(io.StringIO(text)))


def test_header_only_when_empty():
    text = to_csv_string(_result(code_diff=""))
    rows = _rows(text)
    assert rows == []
    assert text.splitlines()[0] == "type,rule,severity,path,line,message"


def test_finding_row():
    rows = _rows(to_csv_string(_result([_finding(comment="boom", line=7)])))
    assert len(rows) == 1
    row = rows[0]
    assert row["type"] == "finding"
    assert row["rule"] == "prthinker/warning"
    assert row["severity"] == "warning"
    assert row["path"] == "a.py"
    assert row["line"] == "7"
    assert row["message"] == "boom"


def test_comment_with_comma_and_newline_is_quoted():
    payload = "has, comma\nand newline"
    rows = _rows(to_csv_string(_result([_finding(comment=payload)])))
    assert rows[0]["message"] == payload


def test_signal_rows_included():
    diff = (
        "diff --git a/a.py b/a.py\n"
        "--- a/a.py\n"
        "+++ b/a.py\n"
        "@@ -0,0 +1,1 @@\n"
        "+<<<<<<< HEAD\n"
    )
    rows = _rows(to_csv_string(_result(code_diff=diff)))
    sig = next(r for r in rows if r["rule"] == "prthinker/merge-conflict")
    assert sig["type"] == "signal"
    assert sig["severity"] == "error"
    assert sig["path"] == "a.py"
    assert sig["line"] == "1"


def test_pathless_signal_is_omitted():
    diff = (
        "diff --git a/old.py b/new.py\n"
        "similarity index 100%\n"
        "rename from old.py\n"
        "rename to new.py\n"
    )
    rows = _rows(to_csv_string(_result(code_diff=diff)))
    # rename carries a path (new.py), so it IS present.
    assert any(r["rule"] == "prthinker/rename" and r["path"] == "new.py" for r in rows)


def test_write_csv_roundtrips(tmp_path):
    out = tmp_path / "findings.csv"
    write_csv(_result([_finding(comment="boom")]), out)
    rows = _rows(out.read_text(encoding="utf-8"))
    assert rows[0]["message"] == "boom"


def test_findings_and_signals_both_present():
    diff = (
        "diff --git a/a.py b/a.py\n"
        "--- a/a.py\n"
        "+++ b/a.py\n"
        "@@ -0,0 +1,1 @@\n"
        "+<<<<<<< HEAD\n"
    )
    rows = _rows(to_csv_string(_result([_finding(severity="error")], code_diff=diff)))
    types = {r["type"] for r in rows}
    assert types == {"finding", "signal"}

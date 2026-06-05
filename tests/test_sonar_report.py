"""Tests for the SonarQube generic-issue exporter."""

from __future__ import annotations

import json

from prthinker.pipeline import ReviewResult
from prthinker.schemas import InlineFinding
from prthinker.sonar_report import severity_to_sonar, to_sonar, write_sonar


def _finding(path="a.py", line=5, severity="warning", comment="x"):
    return InlineFinding(path=path, line=line, severity=severity, comment=comment)


def _result(findings=None, code_diff="diff") -> ReviewResult:
    return ReviewResult(
        code_diff=code_diff, rag_docs=[], inline_findings=findings or []
    )


def test_severity_mapping():
    assert severity_to_sonar("error") == "CRITICAL"
    assert severity_to_sonar("warning") == "MAJOR"
    assert severity_to_sonar("info") == "INFO"
    assert severity_to_sonar("unknown") == "INFO"


def test_empty_result_has_empty_issues():
    assert to_sonar(_result(code_diff="")) == {"issues": []}


def test_finding_issue_shape():
    issue = to_sonar(_result([_finding(comment="boom", line=7)]))["issues"][0]
    assert issue["engineId"] == "prthinker"
    assert issue["ruleId"] == "prthinker/warning"
    assert issue["severity"] == "MAJOR"
    assert issue["type"] == "CODE_SMELL"
    assert issue["primaryLocation"]["filePath"] == "a.py"
    assert issue["primaryLocation"]["message"] == "boom"
    assert issue["primaryLocation"]["textRange"]["startLine"] == 7


def test_error_finding_is_bug_and_critical():
    issue = to_sonar(_result([_finding(severity="error")]))["issues"][0]
    assert issue["type"] == "BUG"
    assert issue["severity"] == "CRITICAL"


def test_pathless_signal_falls_back_to_line_one():
    # A located rename has no line; the signal path falls back to line 1.
    diff = (
        "diff --git a/old.py b/new.py\nsimilarity index 100%\n"
        "rename from old.py\nrename to new.py\n"
    )
    issue = next(
        i for i in to_sonar(_result(code_diff=diff))["issues"]
        if i["ruleId"] == "prthinker/rename"
    )
    assert issue["primaryLocation"]["textRange"]["startLine"] == 1


def test_signals_included_with_path():
    diff = (
        "diff --git a/a.py b/a.py\n--- a/a.py\n+++ b/a.py\n"
        "@@ -0,0 +1,1 @@\n+<<<<<<< HEAD\n"
    )
    issues = to_sonar(_result(code_diff=diff))["issues"]
    conflict = next(i for i in issues if i["ruleId"] == "prthinker/merge-conflict")
    assert conflict["severity"] == "CRITICAL"
    assert conflict["type"] == "BUG"


def test_pathless_signal_skipped():
    diff = (
        "diff --git a/old.py b/new.py\nsimilarity index 50%\n"
        "rename from old.py\nrename to new.py\n"
        "--- a/old.py\n+++ b/new.py\n@@ -1 +1 @@\n-a\n+b\n"
    )
    issues = to_sonar(_result(code_diff=diff))["issues"]
    # rename carries new.py, so it IS present (path is not None).
    assert any(i["ruleId"] == "prthinker/rename" for i in issues)


def test_write_sonar_roundtrips(tmp_path):
    out = tmp_path / "sonar.json"
    write_sonar(_result([_finding(comment="boom")]), out)
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["issues"][0]["primaryLocation"]["message"] == "boom"

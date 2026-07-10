"""Tests for the GitLab Code Quality (CodeClimate) exporter."""

from __future__ import annotations

import json

from prthinker.codequality import (
    severity_to_codeclimate,
    to_codequality,
    write_codequality,
)
from prthinker.pipeline import ReviewResult
from prthinker.schemas import InlineFinding


def _finding(path="a.py", line=5, severity="warning", comment="x") -> InlineFinding:
    return InlineFinding(path=path, line=line, severity=severity, comment=comment)


def _result(findings=None, code_diff="diff") -> ReviewResult:
    return ReviewResult(
        code_diff=code_diff, rag_docs=[], inline_findings=findings or []
    )


def test_severity_mapping():
    assert severity_to_codeclimate("error") == "critical"
    assert severity_to_codeclimate("warning") == "major"
    assert severity_to_codeclimate("info") == "info"
    assert severity_to_codeclimate("unknown") == "info"


def test_empty_result_is_empty_list():
    assert to_codequality(_result()) == []


def test_finding_maps_to_issue():
    issue = to_codequality(_result([_finding(comment="boom", line=7)]))[0]
    assert issue["description"] == "boom"
    assert issue["check_name"] == "prthinker/warning"
    assert issue["severity"] == "major"
    assert issue["location"] == {"path": "a.py", "lines": {"begin": 7}}
    assert len(issue["fingerprint"]) == 64  # sha256 hex


def test_fingerprint_is_stable_and_distinct():
    a = to_codequality(_result([_finding(comment="x", line=1)]))[0]
    b = to_codequality(_result([_finding(comment="x", line=1)]))[0]
    c = to_codequality(_result([_finding(comment="y", line=1)]))[0]
    assert a["fingerprint"] == b["fingerprint"]
    assert a["fingerprint"] != c["fingerprint"]


def test_signals_included_with_location():
    diff = (
        "diff --git a/a.py b/a.py\n"
        "--- a/a.py\n"
        "+++ b/a.py\n"
        "@@ -0,0 +1,1 @@\n"
        "+<<<<<<< HEAD\n"
    )
    issues = to_codequality(_result(code_diff=diff))
    conflict = next(i for i in issues if i["check_name"] == "prthinker/merge-conflict")
    assert conflict["severity"] == "critical"
    assert conflict["location"]["lines"]["begin"] == 1


def test_pathless_signal_anchored_at_line_one():
    diff = (
        "diff --git a/old.py b/new.py\n"
        "similarity index 100%\n"
        "rename from old.py\n"
        "rename to new.py\n"
    )
    issues = to_codequality(_result(code_diff=diff))
    rename = next(i for i in issues if i["check_name"] == "prthinker/rename")
    assert rename["location"] == {"path": "new.py", "lines": {"begin": 1}}


def test_write_codequality_roundtrips(tmp_path):
    out = tmp_path / "gl-code-quality.json"
    write_codequality(_result([_finding(comment="boom")]), out)
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert isinstance(loaded, list)
    assert loaded[0]["description"] == "boom"


def test_findings_and_signals_coexist():
    diff = (
        "diff --git a/a.py b/a.py\n"
        "--- a/a.py\n"
        "+++ b/a.py\n"
        "@@ -0,0 +1,1 @@\n"
        "+<<<<<<< HEAD\n"
    )
    names = {i["check_name"] for i in to_codequality(
        _result([_finding(severity="error")], code_diff=diff))}
    assert "prthinker/error" in names
    assert "prthinker/merge-conflict" in names


def test_fingerprint_pinned_known_answer():
    # Known-answer pin: sha256 of "prthinker/warning\0src/app.py\x0010\0boom".
    # GitLab dedups by fingerprint, so this value must never change.
    issue = to_codequality(
        _result([_finding(path="src/app.py", line=10, severity="warning", comment="boom")])
    )[0]
    assert issue["fingerprint"] == (
        "97e31f15f1e9c112fdee8ea2983451f8a534f26ff92841f5e0d67cdf05e1f7e4"
    )

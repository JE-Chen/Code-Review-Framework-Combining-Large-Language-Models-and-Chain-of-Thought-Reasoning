"""Tests for the machine-readable metrics rollup."""

from __future__ import annotations

import json

from prthinker.metrics import (
    METRICS_SCHEMA_VERSION,
    compute_metrics,
    write_metrics,
)
from prthinker.pipeline import FileReviewResult, ReviewResult
from prthinker.schemas import InlineFinding


def _finding(path="a.py", line=1, severity="warning", comment="x"):
    return InlineFinding(path=path, line=line, severity=severity, comment=comment)


def _result(findings=None, per_file=None, code_diff="diff") -> ReviewResult:
    return ReviewResult(
        code_diff=code_diff, rag_docs=[],
        inline_findings=findings or [], per_file=per_file or [],
    )


def test_empty_result_metrics():
    m = compute_metrics(_result(code_diff=""))
    assert m["schema_version"] == METRICS_SCHEMA_VERSION
    assert m["files_reviewed"] == 0
    assert m["findings"] == {"total": 0, "by_severity": {"error": 0, "warning": 0, "info": 0}}
    assert m["signals"]["total"] == 0
    assert m["diff"] == {"files_changed": 0, "added": 0, "removed": 0}


def test_finding_counts_by_severity():
    findings = [_finding(severity="error"), _finding(severity="warning"),
                _finding(severity="warning"), _finding(severity="info")]
    m = compute_metrics(_result(findings))
    assert m["findings"]["total"] == 4
    assert m["findings"]["by_severity"] == {"error": 1, "warning": 2, "info": 1}


def test_files_reviewed_counts_per_file():
    per_file = [
        FileReviewResult(path="a.py", rag_docs=[], step_outputs={}, inline_findings=[]),
        FileReviewResult(path="b.py", rag_docs=[], step_outputs={}, inline_findings=[]),
    ]
    assert compute_metrics(_result(per_file=per_file))["files_reviewed"] == 2


def test_diff_metrics_from_real_diff():
    diff = (
        "diff --git a/a.py b/a.py\n"
        "--- a/a.py\n"
        "+++ b/a.py\n"
        "@@ -1,1 +1,2 @@\n"
        "-old\n"
        "+new one\n"
        "+new two\n"
    )
    m = compute_metrics(_result(code_diff=diff))
    assert m["diff"] == {"files_changed": 1, "added": 2, "removed": 1}


def test_signal_metrics_by_rule_and_level():
    diff = (
        "diff --git a/a.py b/a.py\n"
        "--- a/a.py\n"
        "+++ b/a.py\n"
        "@@ -0,0 +1,2 @@\n"
        "+<<<<<<< HEAD\n"
        "+# TODO later\n"
    )
    sig = compute_metrics(_result(code_diff=diff))["signals"]
    assert sig["total"] >= 2
    assert sig["by_rule"]["merge-conflict"] == 1
    assert sig["by_rule"]["deferred-marker"] == 1
    assert sig["by_level"]["error"] >= 1


def test_unknown_severity_buckets_into_info():
    bad = _finding()
    object.__setattr__(bad, "severity", "critical")
    m = compute_metrics(_result([bad]))
    assert m["findings"]["by_severity"]["info"] == 1


def test_write_metrics_roundtrips(tmp_path):
    out = tmp_path / "metrics.json"
    write_metrics(_result([_finding(severity="error")]), out)
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["findings"]["by_severity"]["error"] == 1


def test_metrics_json_serializable():
    # Counter-derived dicts must serialize cleanly.
    diff = (
        "diff --git a/a.py b/a.py\n--- a/a.py\n+++ b/a.py\n"
        "@@ -0,0 +1,1 @@\n+<<<<<<< HEAD\n"
    )
    m = compute_metrics(_result(code_diff=diff))
    assert json.loads(json.dumps(m)) == m

"""Tests for the structured signals layer."""

from __future__ import annotations

from prthinker.signals import SignalFinding, collect_signal_findings


def _by_rule(findings: list[SignalFinding]) -> dict[str, SignalFinding]:
    return {f.rule_id: f for f in findings}


def test_empty_diff_yields_no_findings():
    assert collect_signal_findings("") == []


def test_bidi_is_error_with_location():
    diff = (
        "diff --git a/a.py b/a.py\n"
        "--- a/a.py\n"
        "+++ b/a.py\n"
        "@@ -0,0 +1,1 @@\n"
        f"+x = 1  # {chr(0x202E)}hidden\n"
    )
    finding = _by_rule(collect_signal_findings(diff))["trojan-source"]
    assert finding.level == "error"
    assert finding.path == "a.py"
    assert finding.line == 1


def test_conflict_is_error():
    diff = (
        "diff --git a/a.py b/a.py\n"
        "--- a/a.py\n"
        "+++ b/a.py\n"
        "@@ -0,0 +1,1 @@\n"
        "+<<<<<<< HEAD\n"
    )
    finding = _by_rule(collect_signal_findings(diff))["merge-conflict"]
    assert finding.level == "error"
    assert finding.line == 1


def test_debug_and_swallowed_are_warnings():
    diff = (
        "diff --git a/a.py b/a.py\n"
        "--- a/a.py\n"
        "+++ b/a.py\n"
        "@@ -0,0 +1,3 @@\n"
        "+breakpoint()\n"
        "+except Exception:\n"
        "+    pass\n"
    )
    rules = _by_rule(collect_signal_findings(diff))
    assert rules["debug-statement"].level == "warning"
    assert rules["swallowed-exception"].level == "warning"


def test_exec_bit_mode_change_is_warning():
    diff = "diff --git a/run.sh b/run.sh\nold mode 100644\nnew mode 100755\n"
    finding = _by_rule(collect_signal_findings(diff))["file-mode-change"]
    assert finding.level == "warning"
    assert "now executable" in finding.message


def test_non_exec_mode_change_is_note():
    diff = "diff --git a/x b/x\nold mode 100755\nnew mode 100644\n"
    finding = _by_rule(collect_signal_findings(diff))["file-mode-change"]
    assert finding.level == "note"


def test_rename_carries_new_path_and_similarity():
    diff = (
        "diff --git a/old.py b/new.py\n"
        "similarity index 90%\n"
        "rename from old.py\n"
        "rename to new.py\n"
    )
    finding = _by_rule(collect_signal_findings(diff))["rename"]
    assert finding.path == "new.py"
    assert "old.py" in finding.message
    assert "90% similar" in finding.message


def test_noise_and_coverage_from_diff_paths():
    diff = (
        "diff --git a/poetry.lock b/poetry.lock\n"
        "--- a/poetry.lock\n"
        "+++ b/poetry.lock\n"
        "@@ -0,0 +1,1 @@\n"
        "+dep = 1\n"
        "diff --git a/prthinker/x.py b/prthinker/x.py\n"
        "--- a/prthinker/x.py\n"
        "+++ b/prthinker/x.py\n"
        "@@ -0,0 +1,1 @@\n"
        "+y = 2\n"
    )
    rules = _by_rule(collect_signal_findings(diff))
    assert rules["low-attention-file"].path == "poetry.lock"
    assert rules["coverage-gap"].path == "prthinker/x.py"


def test_security_findings_come_first():
    diff = (
        "diff --git a/a.py b/a.py\n"
        "--- a/a.py\n"
        "+++ b/a.py\n"
        "@@ -0,0 +1,2 @@\n"
        "+<<<<<<< HEAD\n"
        "+# TODO later\n"
    )
    findings = collect_signal_findings(diff)
    levels = [f.level for f in findings]
    # The error (conflict) precedes the note (marker).
    assert levels.index("error") < levels.index("note")

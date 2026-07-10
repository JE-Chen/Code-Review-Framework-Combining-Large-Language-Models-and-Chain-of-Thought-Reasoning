"""Tests for the structured signals layer."""

from __future__ import annotations

from prthinker import signals
from prthinker.signals import (
    RULE_PREFIX,
    SignalFinding,
    collect_signal_findings,
    report_fingerprint,
)


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


# ----- shared-parse signals (deleted / binary) -----------------------------

def test_deleted_file_signal():
    diff = (
        "diff --git a/gone.py b/gone.py\n"
        "deleted file mode 100644\n"
        "--- a/gone.py\n"
        "+++ /dev/null\n"
    )
    finding = _by_rule(collect_signal_findings(diff))["file-deleted"]
    assert finding.level == "note"
    assert finding.path == "gone.py"


def test_binary_change_signal():
    diff = (
        "diff --git a/img.png b/img.png\n"
        "Binary files a/img.png and b/img.png differ\n"
    )
    finding = _by_rule(collect_signal_findings(diff))["binary-change"]
    assert finding.level == "note"
    assert finding.path == "img.png"


# ----- memoisation ---------------------------------------------------------

def _conflict_diff(path: str) -> str:
    return (
        f"diff --git a/{path} b/{path}\n"
        f"--- a/{path}\n"
        f"+++ b/{path}\n"
        "@@ -0,0 +1,1 @@\n"
        "+<<<<<<< HEAD\n"
    )


def test_memo_serves_repeat_calls_without_recompute(monkeypatch):
    calls = {"n": 0}
    real_collect = signals._collect

    def counting(diff_text: str):
        calls["n"] += 1
        return real_collect(diff_text)

    monkeypatch.setattr(signals, "_SIGNAL_MEMO", {})
    monkeypatch.setattr(signals, "_collect", counting)
    diff = _conflict_diff("memo-probe.py")
    first = collect_signal_findings(diff)
    second = collect_signal_findings(diff)
    assert calls["n"] == 1
    assert first == second


def test_memo_returns_fresh_list_each_call(monkeypatch):
    monkeypatch.setattr(signals, "_SIGNAL_MEMO", {})
    diff = _conflict_diff("fresh-list.py")
    first = collect_signal_findings(diff)
    first.append("sentinel")
    second = collect_signal_findings(diff)
    assert "sentinel" not in second


def test_memo_size_is_capped(monkeypatch):
    monkeypatch.setattr(signals, "_SIGNAL_MEMO", {})
    for i in range(signals._MEMO_MAX_ENTRIES + 3):
        collect_signal_findings(_conflict_diff(f"cap-{i}.py"))
    assert len(signals._SIGNAL_MEMO) <= signals._MEMO_MAX_ENTRIES


def test_memo_evicts_oldest_and_recomputes(monkeypatch):
    calls = {"n": 0}
    real_collect = signals._collect

    def counting(diff_text: str):
        calls["n"] += 1
        return real_collect(diff_text)

    monkeypatch.setattr(signals, "_SIGNAL_MEMO", {})
    monkeypatch.setattr(signals, "_collect", counting)
    first_diff = _conflict_diff("evict-0.py")
    collect_signal_findings(first_diff)
    for i in range(1, signals._MEMO_MAX_ENTRIES + 1):
        collect_signal_findings(_conflict_diff(f"evict-{i}.py"))
    calls["n"] = 0
    collect_signal_findings(first_diff)  # evicted -> recomputed
    assert calls["n"] == 1


def test_memoised_empty_diff_stays_empty():
    assert collect_signal_findings("") == []
    assert collect_signal_findings("") == []


# ----- RULE_PREFIX / report_fingerprint ------------------------------------

def test_rule_prefix_value():
    assert RULE_PREFIX == "prthinker"


def test_report_fingerprint_pinned_value():
    # Pin: the SARIF and CodeClimate fingerprints must never change across
    # refactors, or code-scanning dedup breaks between runs.
    assert report_fingerprint("prthinker/warning", "src/app.py", 10, "boom") == (
        "97e31f15f1e9c112fdee8ea2983451f8a534f26ff92841f5e0d67cdf05e1f7e4"
    )


def test_report_fingerprint_stable_and_distinct():
    a = report_fingerprint("r", "p.py", 1, "x")
    b = report_fingerprint("r", "p.py", 1, "x")
    c = report_fingerprint("r", "p.py", 2, "x")
    assert a == b
    assert a != c


def test_report_fingerprint_empty_inputs_still_hash():
    digest = report_fingerprint("", "", 0, "")
    assert len(digest) == 64
    assert digest != report_fingerprint("", "", 1, "")

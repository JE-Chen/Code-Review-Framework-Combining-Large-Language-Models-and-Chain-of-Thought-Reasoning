"""Tests for prthinker.cli_review per-file filtering and auto-fix dispatch."""

from __future__ import annotations

import sys
import types
from argparse import Namespace
from dataclasses import dataclass

import pytest

from prthinker import cli_review
from prthinker.pipeline import ReviewResult
from prthinker.schemas import InlineFinding


@dataclass
class _FakeFileDiff:
    """Minimal stand-in for a parsed unified-diff file entry."""

    path: str


def _args(**overrides) -> Namespace:
    """Build an argparse-style namespace with sensible filter defaults."""
    base = {"target_file": "", "exclude_globs": ""}
    base.update(overrides)
    return Namespace(**base)


# --- _filter_per_file_targets ------------------------------------------------

def test_filter_no_args_is_noop():
    files = [_FakeFileDiff("a.py"), _FakeFileDiff("b.py")]
    assert cli_review._filter_per_file_targets(files, _args()) == files


def test_filter_empty_file_list():
    assert cli_review._filter_per_file_targets([], _args()) == []


def test_filter_target_file_selects_single_path():
    files = [_FakeFileDiff("a.py"), _FakeFileDiff("b.py")]
    out = cli_review._filter_per_file_targets(files, _args(target_file="b.py"))
    assert [f.path for f in out] == ["b.py"]


def test_filter_target_file_no_match_yields_empty():
    files = [_FakeFileDiff("a.py")]
    out = cli_review._filter_per_file_targets(
        files, _args(target_file="missing.py")
    )
    assert out == []


def test_filter_target_whitespace_only_is_noop():
    files = [_FakeFileDiff("a.py"), _FakeFileDiff("b.py")]
    out = cli_review._filter_per_file_targets(files, _args(target_file="   "))
    assert out == files


def test_filter_exclude_globs_drops_matches():
    files = [_FakeFileDiff("src/a.py"), _FakeFileDiff("gen/b.py")]
    out = cli_review._filter_per_file_targets(
        files, _args(exclude_globs="gen/*")
    )
    assert [f.path for f in out] == ["src/a.py"]


def test_filter_exclude_globs_multiple_patterns():
    files = [
        _FakeFileDiff("a.py"),
        _FakeFileDiff("b.txt"),
        _FakeFileDiff("c.md"),
    ]
    out = cli_review._filter_per_file_targets(
        files, _args(exclude_globs="*.txt, *.md")
    )
    assert [f.path for f in out] == ["a.py"]


def test_filter_exclude_globs_empty_entries_ignored():
    files = [_FakeFileDiff("a.py")]
    out = cli_review._filter_per_file_targets(
        files, _args(exclude_globs=" , , ")
    )
    assert out == files


def test_filter_target_and_exclude_combined():
    files = [_FakeFileDiff("keep.py"), _FakeFileDiff("keep.py.bak")]
    out = cli_review._filter_per_file_targets(
        files, _args(target_file="keep.py", exclude_globs="*.bak")
    )
    assert [f.path for f in out] == ["keep.py"]


def test_filter_missing_attrs_default_to_noop():
    files = [_FakeFileDiff("a.py")]
    assert cli_review._filter_per_file_targets(files, Namespace()) == files


# --- _maybe_open_auto_fix_pr -------------------------------------------------

def _finding(path="a.py", severity="warning", suggestion="fix"):
    return InlineFinding(
        path=path,
        line=1,
        severity=severity,
        comment="c",
        suggestion=suggestion,
    )


def _result(*findings) -> ReviewResult:
    return ReviewResult(
        code_diff="", rag_docs=[], inline_findings=list(findings)
    )


def _gh():
    return types.SimpleNamespace(pr_number=7)


def test_auto_fix_below_threshold_skips(monkeypatch):
    called = []

    def _fail(*a, **k):
        called.append(True)

    monkeypatch.setattr(cli_review, "_resolve_auto_fix_base_branch", _fail)
    args = Namespace(auto_fix_threshold=3, auto_fix_base_branch="main")
    cli_review._maybe_open_auto_fix_pr(_gh(), args, _result(_finding()))
    assert called == []


def test_auto_fix_eligible_filter_ignores_info_and_no_suggestion():
    res = _result(
        _finding(severity="info"),
        _finding(suggestion=None),
        _finding(),
    )
    eligible = [
        f for f in res.inline_findings
        if f.severity == "warning" and f.suggestion is not None
    ]
    assert len(eligible) == 1


def test_auto_fix_base_branch_explicit_used(monkeypatch):
    seen = {}
    fake_mod = types.ModuleType("prthinker.auto_fix")

    def _open(**kwargs):
        seen.update(kwargs)
        return None

    fake_mod.open_auto_fix_pr = _open
    monkeypatch.setitem(sys.modules, "prthinker.auto_fix", fake_mod)

    args = Namespace(auto_fix_threshold=1, auto_fix_base_branch="release")
    cli_review._maybe_open_auto_fix_pr(_gh(), args, _result(_finding()))
    assert seen["base_branch"] == "release"
    assert "a.py" in seen["findings_by_file"]


def test_auto_fix_base_branch_fetched_when_unset(monkeypatch):
    fetch_mod = types.ModuleType("prthinker.github_api")
    fetch_mod.fetch_pr_base_branch = lambda gh: "fetched-main"
    monkeypatch.setitem(sys.modules, "prthinker.github_api", fetch_mod)

    seen = {}
    open_mod = types.ModuleType("prthinker.auto_fix")
    open_mod.open_auto_fix_pr = lambda **k: seen.update(k) or None
    monkeypatch.setitem(sys.modules, "prthinker.auto_fix", open_mod)

    args = Namespace(auto_fix_threshold=1, auto_fix_base_branch="")
    cli_review._maybe_open_auto_fix_pr(_gh(), args, _result(_finding()))
    assert seen["base_branch"] == "fetched-main"


def test_auto_fix_base_branch_fetch_error_aborts(monkeypatch):
    fetch_mod = types.ModuleType("prthinker.github_api")

    def _raise(gh):
        raise RuntimeError("boom")

    fetch_mod.fetch_pr_base_branch = _raise
    monkeypatch.setitem(sys.modules, "prthinker.github_api", fetch_mod)

    opened = []
    open_mod = types.ModuleType("prthinker.auto_fix")
    open_mod.open_auto_fix_pr = lambda **k: opened.append(k)
    monkeypatch.setitem(sys.modules, "prthinker.auto_fix", open_mod)

    args = Namespace(auto_fix_threshold=1, auto_fix_base_branch="")
    cli_review._maybe_open_auto_fix_pr(_gh(), args, _result(_finding()))
    assert opened == []


def test_open_auto_fix_handles_open_error(monkeypatch, caplog):
    open_mod = types.ModuleType("prthinker.auto_fix")

    def _raise(**k):
        raise RuntimeError("nope")

    open_mod.open_auto_fix_pr = _raise
    monkeypatch.setitem(sys.modules, "prthinker.auto_fix", open_mod)

    with caplog.at_level("ERROR"):
        cli_review._open_auto_fix_pr_and_report(_gh(), {"a.py": []}, "main")
    assert any("Auto-fix failed" in r.message for r in caplog.records)


def test_open_auto_fix_none_result_logs_no_edits(monkeypatch, caplog):
    open_mod = types.ModuleType("prthinker.auto_fix")
    open_mod.open_auto_fix_pr = lambda **k: None
    monkeypatch.setitem(sys.modules, "prthinker.auto_fix", open_mod)

    with caplog.at_level("INFO"):
        cli_review._open_auto_fix_pr_and_report(_gh(), {"a.py": []}, "main")
    assert any("no edits applied" in r.message for r in caplog.records)


# --- _maybe_open_auto_fix_mr (GitLab twin) -----------------------------------

def _mr_args(**overrides):
    defaults = {
        "auto_fix_threshold": 1,
        "auto_fix_base_branch": "main",
        "repo": "g/p",
        "github_token": "tok",
        "pr_number": 7,
    }
    defaults.update(overrides)
    return Namespace(**defaults)


def _stub_auto_fix_module(monkeypatch, opener):
    from prthinker.auto_fix import GitLabMRTarget

    mod = types.ModuleType("prthinker.auto_fix")
    mod.GitLabMRTarget = GitLabMRTarget
    mod.open_auto_fix_mr = opener
    monkeypatch.setitem(sys.modules, "prthinker.auto_fix", mod)
    return GitLabMRTarget


def test_auto_fix_mr_below_threshold_skips(monkeypatch):
    opened = []
    _stub_auto_fix_module(monkeypatch, lambda *a: opened.append(a))
    args = _mr_args(auto_fix_threshold=3)
    adapter = types.SimpleNamespace(base_url="https://gl/api/v4")
    cli_review._maybe_open_auto_fix_mr(args, _result(_finding()), adapter)
    assert opened == []


def test_auto_fix_mr_builds_target_from_args_and_adapter(monkeypatch):
    seen = {}

    def _open(target, findings_by_file, base_branch, repo_root):
        seen.update(
            target=target, findings_by_file=findings_by_file,
            base_branch=base_branch, repo_root=repo_root,
        )
        return None

    _stub_auto_fix_module(monkeypatch, _open)
    adapter = types.SimpleNamespace(base_url="https://gl.example/api/v4")
    cli_review._maybe_open_auto_fix_mr(
        _mr_args(auto_fix_base_branch="release"),
        _result(_finding()),
        adapter,
    )
    assert seen["base_branch"] == "release"
    assert "a.py" in seen["findings_by_file"]
    assert seen["target"].project == "g/p"
    assert seen["target"].mr_iid == 7
    assert seen["target"].base_url == "https://gl.example/api/v4"


def test_auto_fix_mr_base_branch_from_adapter(monkeypatch):
    seen = {}
    _stub_auto_fix_module(
        monkeypatch, lambda t, f, base_branch, r: seen.update(b=base_branch)
    )
    adapter = types.SimpleNamespace(
        base_url="https://gl/api/v4",
        fetch_base_branch=lambda: "fetched-main",
    )
    cli_review._maybe_open_auto_fix_mr(
        _mr_args(auto_fix_base_branch=""), _result(_finding()), adapter
    )
    assert seen["b"] == "fetched-main"


def test_auto_fix_mr_base_branch_fetch_error_aborts(monkeypatch):
    opened = []
    _stub_auto_fix_module(monkeypatch, lambda *a: opened.append(a))

    def _raise():
        raise RuntimeError("boom")

    adapter = types.SimpleNamespace(
        base_url="https://gl/api/v4", fetch_base_branch=_raise
    )
    cli_review._maybe_open_auto_fix_mr(
        _mr_args(auto_fix_base_branch=""), _result(_finding()), adapter
    )
    assert opened == []


def test_auto_fix_mr_open_error_is_swallowed(monkeypatch, caplog):
    def _raise(*a):
        raise RuntimeError("nope")

    _stub_auto_fix_module(monkeypatch, _raise)
    adapter = types.SimpleNamespace(base_url="https://gl/api/v4")
    with caplog.at_level("ERROR"):
        cli_review._maybe_open_auto_fix_mr(
            _mr_args(), _result(_finding()), adapter
        )
    assert any("Auto-fix failed" in r.message for r in caplog.records)


# --- _maybe_prepend_ci_signals (adapter polymorphism) -------------------------

def _ci_args(**overrides):
    defaults = {
        "include_ci_signals": True,
        "ci_signal_max_jobs": 5,
        "ci_signal_tail_chars": 100,
    }
    defaults.update(overrides)
    return Namespace(**defaults)


def test_ci_signals_prepended_from_adapter():
    from prthinker.ci_signals import FailureSignal

    adapter = types.SimpleNamespace(
        fetch_ci_failure_signals=lambda sha, *, max_jobs, log_tail_chars: [
            FailureSignal(
                workflow_name="ci", job_name="pytest",
                conclusion="failure", log_tail="assert boom",
            )
        ]
    )
    out = cli_review._maybe_prepend_ci_signals(
        _ci_args(), "DIFF", "sha1", adapter
    )
    assert out.endswith("DIFF")
    assert "assert boom" in out


def test_ci_signals_skipped_when_disabled():
    def _fail(*a, **k):
        raise AssertionError("adapter must not be called")

    adapter = types.SimpleNamespace(fetch_ci_failure_signals=_fail)
    out = cli_review._maybe_prepend_ci_signals(
        _ci_args(include_ci_signals=False), "DIFF", "sha1", adapter
    )
    assert out == "DIFF"


def test_ci_signals_skipped_without_head_sha():
    def _fail(*a, **k):
        raise AssertionError("adapter must not be called")

    adapter = types.SimpleNamespace(fetch_ci_failure_signals=_fail)
    assert cli_review._maybe_prepend_ci_signals(
        _ci_args(), "DIFF", None, adapter
    ) == "DIFF"


def test_ci_signals_empty_leaves_diff_untouched():
    adapter = types.SimpleNamespace(
        fetch_ci_failure_signals=lambda sha, *, max_jobs, log_tail_chars: []
    )
    assert cli_review._maybe_prepend_ci_signals(
        _ci_args(), "DIFF", "sha1", adapter
    ) == "DIFF"


def test_resolve_base_branch_explicit_short_circuits(monkeypatch):
    def _boom(gh):
        raise AssertionError("should not fetch when branch is set")

    fetch_mod = types.ModuleType("prthinker.github_api")
    fetch_mod.fetch_pr_base_branch = _boom
    monkeypatch.setitem(sys.modules, "prthinker.github_api", fetch_mod)

    args = Namespace(auto_fix_base_branch="dev")
    assert cli_review._resolve_auto_fix_base_branch(_gh(), args) == "dev"


def test_resolve_base_branch_fetch_returns_none_on_error(monkeypatch):
    fetch_mod = types.ModuleType("prthinker.github_api")

    def _raise(gh):
        raise ValueError("x")

    fetch_mod.fetch_pr_base_branch = _raise
    monkeypatch.setitem(sys.modules, "prthinker.github_api", fetch_mod)

    args = Namespace(auto_fix_base_branch="")
    assert cli_review._resolve_auto_fix_base_branch(_gh(), args) is None


# --------------------------------------------------------------------------
# _gate_line (#2): info count + first-blocker link
# --------------------------------------------------------------------------

def _f(severity: str, path: str = "a.py", line: int = 1) -> InlineFinding:
    return InlineFinding(path=path, line=line, severity=severity, comment="c")


def test_gate_line_none_when_not_gating():
    assert cli_review._gate_line(Namespace(gate_on="none"), _result()) is None


def test_gate_line_reports_all_three_severity_counts():
    result = _result(_f("error"), _f("warning"), _f("info"))
    line = cli_review._gate_line(Namespace(gate_on="error"), result)
    assert "1 error, 1 warning, 1 info" in line
    assert "❌ failure" in line


def test_gate_line_links_first_blocker_on_failure():
    result = _result(_f("warning", line=4), _f("error", path="b.py", line=8))
    line = cli_review._gate_line(
        Namespace(gate_on="error"), result, files_url="https://x/files"
    )
    # error floor: the error finding is the blocker, not the earlier warning.
    assert "first blocker:" in line
    assert "b.py:8" in line


def test_gate_line_no_blocker_when_passing():
    result = _result(_f("warning"))
    line = cli_review._gate_line(Namespace(gate_on="error"), result)
    assert "✅ success" in line
    assert "first blocker" not in line


def test_gate_line_warning_floor_blocker_prefers_error():
    result = _result(_f("warning", line=3), _f("error", line=9))
    line = cli_review._gate_line(Namespace(gate_on="warning"), result)
    assert "first blocker:" in line
    assert "a.py:9" in line  # error outranks warning in priority order


# --------------------------------------------------------------------------
# _extra_sections: orientation blocks below the digest
# --------------------------------------------------------------------------

def _per_file(path: str) -> object:
    from prthinker.pipeline import FileReviewResult

    return FileReviewResult(
        path=path, rag_docs=[], step_outputs={}, inline_findings=[]
    )


def _result_with_files(*paths) -> ReviewResult:
    files = [_per_file(p) for p in paths]
    return ReviewResult(code_diff="", rag_docs=[], per_file=files)


def test_extra_sections_coverage_gap_always_on():
    # No flags enabled, but a prod file without a test still surfaces.
    args = Namespace()
    result = _result_with_files("prthinker/x.py")
    sections = cli_review._extra_sections(args, result, None)
    assert any("without a matching test change" in s for s in sections)


def test_extra_sections_gated_features_off_by_default():
    args = Namespace()
    result = _result_with_files("prthinker/x.py")
    sections = cli_review._extra_sections(args, result, None)
    blob = "\n".join(sections)
    assert "Suggested review order" not in blob   # --review-order off
    assert "high-risk file" not in blob           # --risk-weighted off
    assert "Change map" not in blob               # --change-map off


def test_extra_sections_review_order_gated_off_without_kg():
    # Flag on but no KG store present → still empty (best-effort).
    args = Namespace(review_order=True, kg_store="/nonexistent/kg.sqlite")
    result = _result_with_files("a/foo.py", "a/bar.py")
    sections = cli_review._extra_sections(args, result, None)
    assert all("Suggested review order" not in s for s in sections)


def test_extra_sections_includes_checklist_for_error_finding():
    fr = _per_file("a.py")
    fr.inline_findings.append(
        InlineFinding(path="a.py", line=2, severity="error", comment="boom")
    )
    result = ReviewResult(code_diff="", rag_docs=[], per_file=[fr])
    sections = cli_review._extra_sections(Namespace(), result, None)
    assert any("Reviewer checklist" in s for s in sections)


def test_extra_sections_rename_note_from_diff():
    diff = (
        "diff --git a/old.py b/new.py\n"
        "similarity index 100%\n"
        "rename from old.py\n"
        "rename to new.py\n"
    )
    result = ReviewResult(code_diff=diff, rag_docs=[], per_file=[_per_file("new.py")])
    sections = cli_review._extra_sections(Namespace(), result, None)
    assert any("renamed or moved" in s for s in sections)


def test_extra_sections_noise_note_always_on():
    result = _result_with_files("poetry.lock")
    sections = cli_review._extra_sections(Namespace(), result, None)
    assert any("low-attention file(s)" in s for s in sections)


def test_extra_sections_new_marker_note_from_diff():
    diff = (
        "diff --git a/a.py b/a.py\n"
        "--- a/a.py\n"
        "+++ b/a.py\n"
        "@@ -0,0 +1,1 @@\n"
        "+# TODO: wire this up\n"
    )
    result = ReviewResult(code_diff=diff, rag_docs=[], per_file=[_per_file("a.py")])
    sections = cli_review._extra_sections(Namespace(), result, None)
    assert any("deferred-work marker(s) added" in s for s in sections)


def test_extra_sections_clean_diff_adds_no_new_blocks():
    # An empty diff + handwritten file: rename/noise/marker notes self-omit.
    result = _result_with_files("prthinker/cli.py")
    blob = "\n".join(cli_review._extra_sections(Namespace(), result, None))
    assert "renamed or moved" not in blob
    assert "low-attention file(s)" not in blob
    assert "deferred-work marker(s)" not in blob
    assert "formatting only" not in blob
    assert "binary file(s) changed" not in blob
    assert "merge-conflict marker(s)" not in blob
    assert "file mode change(s)" not in blob
    assert "file(s) deleted" not in blob
    assert "debug statement(s)" not in blob
    assert "large contiguous block" not in blob
    assert "swallowed exception(s)" not in blob
    assert "hidden bidi" not in blob


def test_extra_sections_bidi_note_from_diff():
    diff = (
        "diff --git a/a.py b/a.py\n"
        "--- a/a.py\n"
        "+++ b/a.py\n"
        "@@ -0,0 +1,1 @@\n"
        f"+x = 1  # {chr(0x202E)}hidden\n"
    )
    result = ReviewResult(code_diff=diff, rag_docs=[], per_file=[_per_file("a.py")])
    sections = cli_review._extra_sections(Namespace(), result, None)
    assert any("hidden bidi" in s for s in sections)


def test_extra_sections_swallowed_except_from_diff():
    diff = (
        "diff --git a/a.py b/a.py\n"
        "--- a/a.py\n"
        "+++ b/a.py\n"
        "@@ -0,0 +1,2 @@\n"
        "+except Exception:\n"
        "+    pass\n"
    )
    result = ReviewResult(code_diff=diff, rag_docs=[], per_file=[_per_file("a.py")])
    sections = cli_review._extra_sections(Namespace(), result, None)
    assert any("swallowed exception(s)" in s for s in sections)


def test_extra_sections_debug_note_from_diff():
    diff = (
        "diff --git a/a.py b/a.py\n"
        "--- a/a.py\n"
        "+++ b/a.py\n"
        "@@ -0,0 +1,1 @@\n"
        "+    breakpoint()\n"
    )
    result = ReviewResult(code_diff=diff, rag_docs=[], per_file=[_per_file("a.py")])
    sections = cli_review._extra_sections(Namespace(), result, None)
    assert any("debug statement(s)" in s for s in sections)


def test_extra_sections_conflict_note_from_diff():
    diff = (
        "diff --git a/a.py b/a.py\n"
        "--- a/a.py\n"
        "+++ b/a.py\n"
        "@@ -0,0 +1,1 @@\n"
        "+<<<<<<< HEAD\n"
    )
    result = ReviewResult(code_diff=diff, rag_docs=[], per_file=[_per_file("a.py")])
    sections = cli_review._extra_sections(Namespace(), result, None)
    assert any("merge-conflict marker(s)" in s for s in sections)


def test_extra_sections_mode_note_from_diff():
    diff = "diff --git a/run.sh b/run.sh\nold mode 100644\nnew mode 100755\n"
    result = ReviewResult(
        code_diff=diff, rag_docs=[], per_file=[_per_file("run.sh")]
    )
    sections = cli_review._extra_sections(Namespace(), result, None)
    assert any("file mode change(s)" in s for s in sections)


def test_extra_sections_deleted_note_from_diff():
    diff = (
        "diff --git a/old.py b/old.py\n"
        "deleted file mode 100644\n"
        "--- a/old.py\n"
        "+++ /dev/null\n"
        "@@ -1 +0,0 @@\n"
        "-x = 1\n"
    )
    result = ReviewResult(
        code_diff=diff, rag_docs=[], per_file=[_per_file("old.py")]
    )
    sections = cli_review._extra_sections(Namespace(), result, None)
    assert any("file(s) deleted" in s for s in sections)


def test_extra_sections_whitespace_note_from_diff():
    diff = (
        "diff --git a/a.py b/a.py\n"
        "--- a/a.py\n"
        "+++ b/a.py\n"
        "@@ -1,1 +1,1 @@\n"
        "-x=1\n"
        "+x = 1\n"
    )
    result = ReviewResult(code_diff=diff, rag_docs=[], per_file=[_per_file("a.py")])
    sections = cli_review._extra_sections(Namespace(), result, None)
    assert any("formatting only" in s for s in sections)


def test_extra_sections_binary_note_from_diff():
    diff = (
        "diff --git a/logo.png b/logo.png\n"
        "index abc..def 100644\n"
        "Binary files a/logo.png and b/logo.png differ\n"
    )
    result = ReviewResult(
        code_diff=diff, rag_docs=[], per_file=[_per_file("logo.png")]
    )
    sections = cli_review._extra_sections(Namespace(), result, None)
    assert any("binary file(s) changed" in s for s in sections)


def test_wire_rag_threshold_defaults_to_legacy_value():
    config = _make_config(rag_threshold=None)
    assert cli_review._wire_rag_threshold(config) == 0.7


def test_wire_rag_threshold_explicit_value_passes_through():
    config = _make_config(rag_threshold=0.32)
    assert cli_review._wire_rag_threshold(config) == 0.32


def test_wire_rag_threshold_zero_is_not_treated_as_unset():
    config = _make_config(rag_threshold=0.0)
    assert cli_review._wire_rag_threshold(config) == 0.0


def test_config_rag_threshold_defaults_to_none():
    assert _make_config().rag_threshold is None


def _make_config(**overrides):
    from prthinker.config import Config, BackendKind, RemoteBackendConfig

    base = dict(
        backend=BackendKind.REMOTE,
        remote=RemoteBackendConfig(url="https://example.test"),
    )
    base.update(overrides)
    return Config(**base)


# --- _flag: boolean CLI-flag reader -------------------------------------------

def test_flag_true_when_set():
    assert cli_review._flag(Namespace(judge=True), "judge") is True


def test_flag_false_when_unset_attribute():
    assert cli_review._flag(Namespace(), "judge") is False


def test_flag_coerces_truthy_and_falsy_values():
    assert cli_review._flag(Namespace(judge=1), "judge") is True
    assert cli_review._flag(Namespace(judge=None), "judge") is False
    assert cli_review._flag(Namespace(judge=""), "judge") is False


def test_collect_core_kwargs_uses_flags():
    args = Namespace(
        inline_review=True,
        judge=True,
        max_findings_per_file=5,
        step_plan="full",
    )
    kwargs = cli_review._collect_core_kwargs(args)
    assert kwargs["judge"] is True
    assert kwargs["self_correct"] is False  # missing attr → False
    assert kwargs["max_findings_per_file"] == 5


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

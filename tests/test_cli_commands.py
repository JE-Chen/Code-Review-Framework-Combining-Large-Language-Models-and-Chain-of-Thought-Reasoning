"""Behaviour tests for prthinker.cli_commands aggregate handlers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from prthinker import cli_commands
from prthinker.pipeline import FileReviewResult, ReviewResult


def _make_args(**overrides: object) -> argparse.Namespace:
    defaults: dict[str, object] = {
        "repo": "owner/repo",
        "pr_number": 7,
        "github_token": "tok",
        "aggregate_from": "",
        "platform": "github",
        "platform_base_url": None,
        "marker": "<!--prthinker-->",
        "gate_on": "none",
        "dry_run": False,
        "judge": False,
        "inline_review": False,
    }
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


def _file_result(path: str, verdict: object = None) -> FileReviewResult:
    return FileReviewResult(
        path=path,
        rag_docs=[],
        step_outputs={},
        inline_findings=[],
        verdict=verdict,
    )


def _review(per_file: list[FileReviewResult]) -> ReviewResult:
    return ReviewResult(
        code_diff="",
        rag_docs=[],
        step_outputs={},
        inline_findings=[],
        per_file=per_file,
    )


class _FakeAdapter:
    """Records adapter interactions for assertions."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []
        self.head_sha_value: str | None = "deadbeef"
        self.fetch_head_sha_error: Exception | None = None
        self.submit_inline_error: Exception | None = None
        self.gate_handle = object()

    def fetch_head_sha(self) -> str:
        self.calls.append(("fetch_head_sha", None))
        if self.fetch_head_sha_error is not None:
            raise self.fetch_head_sha_error
        if self.head_sha_value is None:
            raise RuntimeError("no sha")
        return self.head_sha_value

    def open_gate(self, head_sha: str) -> object:
        self.calls.append(("open_gate", head_sha))
        return self.gate_handle

    def upsert_summary_comment(self, body: str) -> int:
        self.calls.append(("upsert_summary_comment", body))
        return 123

    def upsert_summary_comments(self, bodies: list[str]) -> list[int]:
        return [self.upsert_summary_comment(b) for b in bodies]

    def submit_inline_review(self, findings, summary_body, event):  # noqa: ANN001
        self.calls.append(("submit_inline_review", event))
        if self.submit_inline_error is not None:
            raise self.submit_inline_error
        return "rev1"

    def close_gate(self, handle, result):  # noqa: ANN001
        self.calls.append(("close_gate", result.conclusion))


# --- _validate_aggregate_args ------------------------------------------------

def test_validate_args_missing_repo() -> None:
    with pytest.raises(SystemExit, match="--repo"):
        cli_commands._validate_aggregate_args(_make_args(repo=""))


def test_validate_args_missing_pr_number() -> None:
    with pytest.raises(SystemExit, match="--pr-number"):
        cli_commands._validate_aggregate_args(_make_args(pr_number=0))


def test_validate_args_missing_token() -> None:
    with pytest.raises(SystemExit, match="--github-token"):
        cli_commands._validate_aggregate_args(_make_args(github_token=""))  # nosec B106 - test fixture, not a credential


def test_validate_args_missing_input_dir() -> None:
    with pytest.raises(SystemExit, match="--aggregate-from"):
        cli_commands._validate_aggregate_args(_make_args(aggregate_from="  "))


def test_validate_args_input_not_dir(tmp_path: Path) -> None:
    missing = tmp_path / "nope"
    with pytest.raises(SystemExit, match="is not a directory"):
        cli_commands._validate_aggregate_args(_make_args(aggregate_from=str(missing)))


def test_validate_args_ok(tmp_path: Path) -> None:
    result = cli_commands._validate_aggregate_args(
        _make_args(aggregate_from=str(tmp_path))
    )
    assert result == tmp_path


# --- _open_aggregate_gate ----------------------------------------------------

def test_open_gate_disabled_when_gate_none() -> None:
    adapter = _FakeAdapter()
    assert cli_commands._open_aggregate_gate(_make_args(gate_on="none"), adapter) is None
    assert adapter.calls == []


def test_open_gate_disabled_when_dry_run() -> None:
    adapter = _FakeAdapter()
    args = _make_args(gate_on="error", dry_run=True)
    assert cli_commands._open_aggregate_gate(args, adapter) is None
    assert adapter.calls == []


def test_open_gate_returns_handle() -> None:
    adapter = _FakeAdapter()
    args = _make_args(gate_on="error")
    handle = cli_commands._open_aggregate_gate(args, adapter)
    assert handle is adapter.gate_handle
    assert ("open_gate", "deadbeef") in adapter.calls


def test_open_gate_skips_on_fetch_error() -> None:
    adapter = _FakeAdapter()
    adapter.fetch_head_sha_error = RuntimeError("boom")
    args = _make_args(gate_on="error")
    assert cli_commands._open_aggregate_gate(args, adapter) is None
    assert ("open_gate", "deadbeef") not in [c for c in adapter.calls]


# --- _resolve_review_event ---------------------------------------------------

def test_resolve_event_default_when_no_judge() -> None:
    merged = _review([_file_result("a.py")])
    assert cli_commands._resolve_review_event(_make_args(judge=False), merged) == "COMMENT"


def test_resolve_event_default_when_no_per_file() -> None:
    merged = _review([])
    assert cli_commands._resolve_review_event(_make_args(judge=True), merged) == "COMMENT"


def test_resolve_event_default_when_no_verdicts() -> None:
    merged = _review([_file_result("a.py", verdict=None)])
    assert cli_commands._resolve_review_event(_make_args(judge=True), merged) == "COMMENT"


# --- _submit_aggregate_inline_review -----------------------------------------

def test_submit_inline_skipped_when_disabled() -> None:
    adapter = _FakeAdapter()
    merged = _review([_file_result("a.py")])
    cli_commands._submit_aggregate_inline_review(
        _make_args(inline_review=False), adapter, merged, "COMMENT"
    )
    assert adapter.calls == []


def test_submit_inline_swallows_error() -> None:
    adapter = _FakeAdapter()
    adapter.submit_inline_error = RuntimeError("422")
    fr = _file_result("a.py")
    fr.inline_findings = [object()]
    merged = _review([fr])
    merged.inline_findings = [object()]
    # Must not raise.
    cli_commands._submit_aggregate_inline_review(
        _make_args(inline_review=True), adapter, merged, "COMMENT"
    )
    assert ("submit_inline_review", "COMMENT") in adapter.calls


# --- _close_aggregate_gate ---------------------------------------------------

def test_close_gate_noop_when_no_handle() -> None:
    adapter = _FakeAdapter()
    merged = _review([_file_result("a.py")])
    cli_commands._close_aggregate_gate(_make_args(gate_on="error"), adapter, merged, None)
    assert adapter.calls == []


def test_close_gate_closes_handle() -> None:
    adapter = _FakeAdapter()
    merged = _review([_file_result("a.py")])
    cli_commands._close_aggregate_gate(
        _make_args(gate_on="error"), adapter, merged, adapter.gate_handle
    )
    assert any(c[0] == "close_gate" for c in adapter.calls)


# --- _cmd_aggregate end to end ----------------------------------------------

def test_cmd_aggregate_no_json(tmp_path: Path) -> None:
    args = _make_args(aggregate_from=str(tmp_path))
    assert cli_commands._cmd_aggregate(args) == 0


def test_cmd_aggregate_dry_run(tmp_path: Path, monkeypatch, capsys) -> None:
    partial = {
        "code_diff": "",
        "rag_docs": [],
        "step_outputs": {},
        "inline_findings": [],
        "per_file": [
            {
                "path": "a.py",
                "rag_docs": [],
                "step_outputs": {},
                "inline_findings": [],
            }
        ],
    }
    (tmp_path / "p1.json").write_text(json.dumps(partial), encoding="utf-8")
    adapter = _FakeAdapter()
    monkeypatch.setattr(
        "prthinker.platforms.create_platform_adapter",
        lambda *a, **k: adapter,
    )
    args = _make_args(aggregate_from=str(tmp_path), dry_run=True)
    rc = cli_commands._cmd_aggregate(args)
    assert rc == 0
    # Dry run posts nothing.
    assert adapter.calls == []
    out = capsys.readouterr().out
    assert out  # body written to stdout


def _status_args(**overrides: object) -> argparse.Namespace:
    base = {
        "platform": "github", "platform_base_url": None,
        "repo": "o/r", "pr_number": 7, "github_token": "tok",
        "marker": "<!--prthinker-->", "dry_run": False, "gate_on": "none",
    }
    base.update(overrides)
    return argparse.Namespace(**base)


def test_cmd_post_status_dry_run(capsys) -> None:
    rc = cli_commands._cmd_post_status(_status_args(dry_run=True))
    assert rc == 0
    out = capsys.readouterr().out
    assert "Review in progress" in out
    assert "<!--prthinker-->" in out


def test_cmd_post_status_upserts_placeholder(monkeypatch) -> None:
    adapter = _FakeAdapter()
    monkeypatch.setattr(
        "prthinker.platforms.create_platform_adapter", lambda *a, **k: adapter
    )
    rc = cli_commands._cmd_post_status(_status_args())
    assert rc == 0
    posted = [c for c in adapter.calls if c[0] == "upsert_summary_comment"]
    assert posted and "Review in progress" in posted[0][1]


def test_maybe_write_job_summary(tmp_path: Path, monkeypatch) -> None:
    from prthinker.cli_review import _maybe_write_job_summary
    summary = tmp_path / "summary.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary))
    _maybe_write_job_summary("## digest\nhello")
    assert "## digest" in summary.read_text(encoding="utf-8")


def test_maybe_write_job_summary_noop_without_env(monkeypatch) -> None:
    from prthinker.cli_review import _maybe_write_job_summary
    monkeypatch.delenv("GITHUB_STEP_SUMMARY", raising=False)
    # Must not raise when the env var is absent.
    _maybe_write_job_summary("ignored")


def test_maybe_write_sarif(tmp_path: Path) -> None:
    out = tmp_path / "out.sarif"
    merged = _review([_file_result("a.py")])
    cli_commands._maybe_write_sarif(_make_args(sarif_out=str(out)), merged)
    assert out.exists()
    assert "$schema" in out.read_text(encoding="utf-8")


def test_maybe_write_sarif_noop_when_unset(tmp_path: Path) -> None:
    merged = _review([_file_result("a.py")])
    cli_commands._maybe_write_sarif(_make_args(sarif_out=""), merged)  # no raise


def test_cmd_aggregate_posts_summary(tmp_path: Path, monkeypatch) -> None:
    partial = {
        "code_diff": "",
        "rag_docs": [],
        "step_outputs": {},
        "inline_findings": [],
        "per_file": [
            {
                "path": "a.py",
                "rag_docs": [],
                "step_outputs": {},
                "inline_findings": [],
            }
        ],
    }
    (tmp_path / "p1.json").write_text(json.dumps(partial), encoding="utf-8")
    adapter = _FakeAdapter()
    monkeypatch.setattr(
        "prthinker.platforms.create_platform_adapter",
        lambda *a, **k: adapter,
    )
    args = _make_args(aggregate_from=str(tmp_path))
    rc = cli_commands._cmd_aggregate(args)
    assert rc == 0
    assert any(c[0] == "upsert_summary_comment" for c in adapter.calls)


def _stats_args(tmp_path: Path, **overrides: object) -> argparse.Namespace:
    defaults = {
        "telemetry_path": str(tmp_path / "telemetry.sqlite"),
        "cache_path": str(tmp_path / "prompt-cache.sqlite"),
        "since_days": None,
    }
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


def _record_call(path: Path, **overrides: object) -> None:
    from prthinker.telemetry import CallRecord, TelemetrySink

    fields = {
        "backend": "openai",
        "model": "gpt-4o-mini",
        "prompt_tokens": 100,
        "completion_tokens": 50,
        "tokens_estimated": False,
        "latency_ms": 123.0,
        "cache_hit": False,
        "error": None,
    }
    fields.update(overrides)
    TelemetrySink(path).record(CallRecord(**fields))


def test_cmd_stats_missing_telemetry(tmp_path: Path, capsys) -> None:
    args = _stats_args(tmp_path)
    rc = cli_commands._cmd_stats(args)
    assert rc == 1
    captured = capsys.readouterr()
    assert "No telemetry file" in captured.err


def test_cmd_stats_empty_window(tmp_path: Path, capsys) -> None:
    from prthinker.telemetry import TelemetrySink

    tpath = tmp_path / "telemetry.sqlite"
    TelemetrySink(tpath)  # create empty db file
    args = _stats_args(tmp_path)
    rc = cli_commands._cmd_stats(args)
    assert rc == 0
    captured = capsys.readouterr()
    assert "No calls recorded" in captured.out


def test_cmd_stats_reports_calls(tmp_path: Path, capsys) -> None:
    tpath = tmp_path / "telemetry.sqlite"
    _record_call(tpath)
    _record_call(tpath, cache_hit=True)
    args = _stats_args(tmp_path)
    rc = cli_commands._cmd_stats(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "# prthinker stats — all-time" in out
    assert "openai" in out
    assert "gpt-4o-mini" in out
    assert "Total: 2 call(s), 1 cache hits (50.0%)" in out


def test_cmd_stats_since_days_label(tmp_path: Path, capsys) -> None:
    tpath = tmp_path / "telemetry.sqlite"
    _record_call(tpath)
    args = _stats_args(tmp_path, since_days=7)
    rc = cli_commands._cmd_stats(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "last 7 day(s)" in out


def test_cmd_stats_truncates_long_model(tmp_path: Path, capsys) -> None:
    tpath = tmp_path / "telemetry.sqlite"
    long_model = "x" * 40
    _record_call(tpath, model=long_model)
    args = _stats_args(tmp_path)
    rc = cli_commands._cmd_stats(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert ("x" * 33 + "..") in out


def test_cmd_stats_includes_cache_summary(tmp_path: Path, capsys) -> None:
    tpath = tmp_path / "telemetry.sqlite"
    _record_call(tpath)
    from prthinker.cache import PromptCache

    cpath = tmp_path / "prompt-cache.sqlite"
    PromptCache(cpath)  # create cache db so cache_path.exists()
    args = _stats_args(tmp_path)
    rc = cli_commands._cmd_stats(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "Cache:" in out
    assert "entries stored" in out


# --- report links footer + html report --------------------------------------

def test_report_links_footer_with_artifacts(monkeypatch) -> None:
    from prthinker.cli_review import _report_links_footer
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.com")
    monkeypatch.setenv("GITHUB_REPOSITORY", "o/r")
    monkeypatch.setenv("GITHUB_RUN_ID", "123")
    args = _make_args(sarif_out="x.sarif", html_report="r.html", pr_number=7)
    footer = _report_links_footer(args)
    assert "**Reports:**" in footer
    assert "actions/runs/123" in footer
    assert "report.html" in footer and "prthinker.sarif" in footer
    assert "security/code-scanning?query=pr%3A7" in footer


def test_report_links_footer_none_without_ci(monkeypatch) -> None:
    from prthinker.cli_review import _report_links_footer
    monkeypatch.delenv("GITHUB_RUN_ID", raising=False)
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
    args = _make_args(sarif_out="", html_report="", repo="", pr_number=0)
    assert _report_links_footer(args) is None


def test_append_report_links_appends_to_last_page(monkeypatch) -> None:
    from prthinker.cli_review import _append_report_links
    monkeypatch.setenv("GITHUB_REPOSITORY", "o/r")
    monkeypatch.setenv("GITHUB_RUN_ID", "9")
    pages = ["page1", "page2"]
    _append_report_links(_make_args(html_report="r.html"), pages)
    assert "Reports:" in pages[-1] and "Reports:" not in pages[0]


def test_maybe_write_html_report(tmp_path: Path) -> None:
    out = tmp_path / "r.html"
    merged = _review([_file_result("a.py")])
    cli_commands._maybe_write_html_report(_make_args(html_report=str(out)), merged)
    assert out.exists()


# --- full-scan coverage gating ----------------------------------------------

class _PathsAdapter(_FakeAdapter):
    def __init__(self, paths):
        super().__init__()
        self._paths = paths

    def fetch_changed_paths(self):
        return self._paths


def test_missing_review_files_detects_gap() -> None:
    merged = _review([_file_result("a.py")])
    adapter = _PathsAdapter(["a.py", "b.py"])
    missing, expected = cli_commands._missing_review_files(_make_args(), adapter, merged)
    assert missing == ["b.py"] and expected == 2


def test_missing_review_files_respects_exclude_globs() -> None:
    merged = _review([_file_result("a.py")])
    adapter = _PathsAdapter(["a.py", "datas/big.json"])
    missing, expected = cli_commands._missing_review_files(
        _make_args(exclude_globs="datas/*"), adapter, merged
    )
    assert missing == [] and expected == 1


def test_missing_review_files_fails_open_on_error() -> None:
    merged = _review([_file_result("a.py")])
    # _FakeAdapter has no fetch_changed_paths override -> base returns []? It's
    # not a PlatformAdapter subclass, so attribute is missing -> AttributeError
    # caught -> fail open.
    missing, expected = cli_commands._missing_review_files(_make_args(), _FakeAdapter(), merged)
    assert missing == [] and expected == 0


def test_withhold_partial_review_posts_notice() -> None:
    merged = _review([_file_result("a.py")])
    adapter = _PathsAdapter(["a.py", "b.py"])
    withheld = cli_commands._withhold_partial_review(
        _make_args(require_full_scan=True), adapter, merged
    )
    assert withheld is True
    posted = [c for c in adapter.calls if c[0] == "upsert_summary_comment"]
    assert posted and "Review in progress" in posted[0][1] and "1/2" in posted[0][1]


def test_withhold_disabled_by_default() -> None:
    merged = _review([_file_result("a.py")])
    adapter = _PathsAdapter(["a.py", "b.py"])
    assert cli_commands._withhold_partial_review(_make_args(), adapter, merged) is False


def test_no_withhold_when_complete() -> None:
    merged = _review([_file_result("a.py"), _file_result("b.py")])
    adapter = _PathsAdapter(["a.py", "b.py"])
    assert cli_commands._withhold_partial_review(
        _make_args(require_full_scan=True), adapter, merged
    ) is False


# ----- harvest platform dispatch -------------------------------------------------


def _harvest_args(**overrides) -> argparse.Namespace:
    base = {
        "platform": "github",
        "platform_base_url": None,
        "repo": "g/p",
        "github_token": "tok",
        "pr_number": None,
        "max_prs": 50,
        "out": Path("unused.jsonl"),
    }
    base.update(overrides)
    return argparse.Namespace(**base)


def _fake_stats():
    from prthinker.harvest import HarvestStats

    return HarvestStats(prs_scanned=1)


def test_cmd_harvest_dispatches_to_gitlab(monkeypatch, capsys) -> None:
    seen = {}

    def _fake(project, token, *, store, mr_iid, max_mrs, base_url):
        seen.update(project=project, token=token, mr_iid=mr_iid,
                    max_mrs=max_mrs, base_url=base_url)
        del store
        return _fake_stats()

    monkeypatch.setattr(cli_commands.gitlab_harvest, "harvest", _fake)
    monkeypatch.delenv("CI_API_V4_URL", raising=False)
    rc = cli_commands._cmd_harvest(_harvest_args(platform="gitlab", pr_number=9))
    assert rc == 0
    assert seen == {
        "project": "g/p", "token": "tok", "mr_iid": 9, "max_mrs": 50,
        "base_url": "https://gitlab.com/api/v4",
    }
    assert "PRs scanned: 1" in capsys.readouterr().out


def test_cmd_harvest_github_stays_on_github_path(monkeypatch) -> None:
    called = {}

    def _fake(repo, token, *, store, pr_number, max_prs):
        called.update(repo=repo, token=token, pr_number=pr_number,
                      max_prs=max_prs)
        del store
        return _fake_stats()

    monkeypatch.setattr(cli_commands, "harvest", _fake)
    rc = cli_commands._cmd_harvest(_harvest_args())
    assert rc == 0
    assert called["repo"] == "g/p"


def test_cmd_harvest_rejects_unsupported_platform() -> None:
    with pytest.raises(SystemExit, match="not supported"):
        cli_commands._cmd_harvest(_harvest_args(platform="gitea"))


def test_cmd_harvest_requires_repo_and_token() -> None:
    with pytest.raises(SystemExit, match="CI_PROJECT_PATH"):
        cli_commands._cmd_harvest(_harvest_args(repo=""))
    with pytest.raises(SystemExit, match="GITLAB_TOKEN"):
        cli_commands._cmd_harvest(_harvest_args(github_token=""))


def test_cmd_harvest_accepted_dispatches_to_gitlab(monkeypatch) -> None:
    seen = {}

    def _fake(project, token, *, store, mr_iid, max_mrs, base_url):
        seen.update(project=project, base_url=base_url)
        del token, store, mr_iid, max_mrs
        return _fake_stats()

    monkeypatch.setattr(
        cli_commands.gitlab_harvest, "harvest_accepted", _fake
    )
    monkeypatch.setenv("CI_API_V4_URL", "https://gl.example.com/api/v4")
    rc = cli_commands._cmd_harvest_accepted(_harvest_args(platform="gitlab"))
    assert rc == 0
    # Self-hosted API root autodetected from the GitLab CI environment.
    assert seen["base_url"] == "https://gl.example.com/api/v4"


def test_gitlab_harvest_base_url_prefers_explicit_flag(monkeypatch) -> None:
    monkeypatch.setenv("CI_API_V4_URL", "https://gl.example.com/api/v4")
    args = _harvest_args(platform_base_url="https://explicit/api/v4")
    assert cli_commands._gitlab_harvest_base_url(args) == "https://explicit/api/v4"

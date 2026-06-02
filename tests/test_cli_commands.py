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
        cli_commands._validate_aggregate_args(_make_args(github_token=""))


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

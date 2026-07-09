"""Tests for the ``issue-fix`` CLI command wiring."""

from __future__ import annotations

import argparse
import json

import prthinker.issue_fix_cli as cli
from prthinker.cli_parser import _build_parser


class _ScriptedBackend:
    def __init__(self, response: str) -> None:
        self._response = response

    def generate(self, prompt: str, max_new_tokens: int) -> str:
        return self._response


def _patch_backend(monkeypatch, response: str) -> None:
    monkeypatch.setattr(cli, "_build_config", lambda args: object())
    monkeypatch.setattr(cli, "create_backend", lambda config: _ScriptedBackend(response))


def test_parser_registers_issue_fix_with_backend_args():
    parser = _build_parser()
    args = parser.parse_args(["issue-fix", "--workdir", ".", "some issue"])
    assert args.command == "issue-fix"
    assert args.retriever == "graph-rerank"  # default
    assert hasattr(args, "backend")  # inherited common backend args


def test_command_emits_valid_proposal(tmp_path, monkeypatch, capsys):
    (tmp_path / "a.py").write_text("def f():\n    return WRONG\n", encoding="utf-8")
    _patch_backend(monkeypatch, json.dumps(
        [{"file": "a.py", "original": "return WRONG", "replacement": "return RIGHT"}]
    ))
    args = argparse.Namespace(
        issue="f returns wrong", issue_file=None, workdir=tmp_path,
        retriever="lexical", top_k=5, max_retries=0, output=None,
        patch=None, apply=False, test_cmd=None, test_timeout=600.0,
    )
    rc = cli.command(args)
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["valid"] is True
    assert payload["edits"][0]["replacement"] == "return RIGHT"


def test_command_writes_output_file(tmp_path, monkeypatch):
    (tmp_path / "a.py").write_text("x = 1\n", encoding="utf-8")
    _patch_backend(monkeypatch, json.dumps(
        [{"file": "a.py", "original": "x = 1", "replacement": "x = 2"}]
    ))
    out = tmp_path / "out" / "proposal.json"
    args = argparse.Namespace(
        issue="fix x", issue_file=None, workdir=tmp_path,
        retriever="lexical", top_k=5, max_retries=0, output=out,
        patch=None, apply=False, test_cmd=None, test_timeout=600.0,
    )
    assert cli.command(args) == 0
    assert json.loads(out.read_text(encoding="utf-8"))["valid"] is True


def test_command_writes_patch_and_applies(tmp_path, monkeypatch):
    (tmp_path / "a.py").write_text("x = 1\n", encoding="utf-8")
    _patch_backend(monkeypatch, json.dumps(
        [{"file": "a.py", "original": "x = 1", "replacement": "x = 2"}]
    ))
    patch = tmp_path / "fix.patch"
    args = argparse.Namespace(
        issue="fix x", issue_file=None, workdir=tmp_path,
        retriever="lexical", top_k=5, max_retries=0, output=None,
        patch=patch, apply=True, test_cmd=None, test_timeout=600.0,
    )
    assert cli.command(args) == 0
    assert "+x = 2" in patch.read_text(encoding="utf-8")
    # --apply mutated the work-tree
    assert (tmp_path / "a.py").read_text(encoding="utf-8") == "x = 2\n"


def test_command_test_cmd_runs_pass_at_1_check(tmp_path, monkeypatch, capsys):
    from prthinker.execution_sandbox import ExecutionResult

    (tmp_path / "a.py").write_text("x = 1\n", encoding="utf-8")
    _patch_backend(monkeypatch, json.dumps(
        [{"file": "a.py", "original": "x = 1", "replacement": "x = 2"}]
    ))

    class _FakeExec:
        def run(self, command, workdir, timeout):
            return ExecutionResult(0, "ok", "")

    monkeypatch.setattr(cli, "LocalExecutor", _FakeExec)
    args = argparse.Namespace(
        issue="fix x", issue_file=None, workdir=tmp_path,
        retriever="lexical", top_k=5, max_retries=0, output=None,
        patch=None, apply=False, test_cmd="pytest -q", test_timeout=60.0,
    )
    assert cli.command(args) == 0  # exit code reflects the passing test command
    assert "PASSED" in capsys.readouterr().err
    assert (tmp_path / "a.py").read_text(encoding="utf-8") == "x = 2\n"  # fix applied


def test_command_rejects_empty_issue(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", type("S", (), {"read": staticmethod(lambda: "  ")})())
    args = argparse.Namespace(
        issue="-", issue_file=None, workdir=tmp_path,
        retriever="lexical", top_k=5, max_retries=0, output=None,
        patch=None, apply=False, test_cmd=None, test_timeout=600.0,
    )
    assert cli.command(args) == 2
    assert "needs an issue" in capsys.readouterr().err


def test_command_returns_1_when_no_valid_edit(tmp_path, monkeypatch, capsys):
    (tmp_path / "a.py").write_text("x = 1\n", encoding="utf-8")
    _patch_backend(monkeypatch, json.dumps(
        [{"file": "a.py", "original": "MISSING", "replacement": "x = 2"}]
    ))
    args = argparse.Namespace(
        issue="fix", issue_file=None, workdir=tmp_path,
        retriever="lexical", top_k=5, max_retries=0, output=None,
        patch=None, apply=False, test_cmd=None, test_timeout=600.0,
    )
    assert cli.command(args) == 1
    assert json.loads(capsys.readouterr().out)["valid"] is False

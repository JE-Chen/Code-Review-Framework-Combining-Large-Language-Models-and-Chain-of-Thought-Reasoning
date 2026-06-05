"""Tests for the standalone ``triage`` command."""

from __future__ import annotations

import argparse
import io
import sys

import pytest

from prthinker import cli_triage

_CONFLICT_DIFF = (
    "diff --git a/a.py b/a.py\n"
    "--- a/a.py\n"
    "+++ b/a.py\n"
    "@@ -0,0 +1,1 @@\n"
    "+<<<<<<< HEAD\n"
)

_CLEAN_DIFF = (
    "diff --git a/docs/x.md b/docs/x.md\n"
    "--- a/docs/x.md\n"
    "+++ b/docs/x.md\n"
    "@@ -1 +1 @@\n"
    "-old\n"
    "+new\n"
)


def _args(**kw) -> argparse.Namespace:
    base = dict(
        diff_file=None,
        staged=False,
        against=None,
        exit_nonzero_on_signal=False,
    )
    base.update(kw)
    return argparse.Namespace(**base)


def test_triage_reads_stdin_and_reports_signal(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO(_CONFLICT_DIFF))
    rc = cli_triage._cmd_triage(_args())
    out = capsys.readouterr().out
    assert rc == 0
    assert "prthinker triage —" in out
    assert "merge-conflict marker(s)" in out


def test_triage_clean_diff_reports_no_signals(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO(_CLEAN_DIFF))
    rc = cli_triage._cmd_triage(_args())
    out = capsys.readouterr().out
    assert rc == 0
    assert "No triage signals" in out


def test_triage_empty_diff(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("   \n"))
    rc = cli_triage._cmd_triage(_args())
    out = capsys.readouterr().out
    assert rc == 0
    assert "empty diff" in out


def test_triage_exit_nonzero_on_signal(monkeypatch):
    monkeypatch.setattr(sys, "stdin", io.StringIO(_CONFLICT_DIFF))
    rc = cli_triage._cmd_triage(_args(exit_nonzero_on_signal=True))
    assert rc == 1


def test_triage_exit_zero_on_clean_even_with_flag(monkeypatch):
    monkeypatch.setattr(sys, "stdin", io.StringIO(_CLEAN_DIFF))
    rc = cli_triage._cmd_triage(_args(exit_nonzero_on_signal=True))
    assert rc == 0


def test_triage_reads_diff_file(tmp_path, capsys):
    diff_path = tmp_path / "pr.diff"
    diff_path.write_text(_CONFLICT_DIFF, encoding="utf-8")
    rc = cli_triage._cmd_triage(_args(diff_file=diff_path))
    out = capsys.readouterr().out
    assert rc == 0
    assert "merge-conflict marker(s)" in out


def test_triage_missing_diff_file_returns_error(tmp_path, capsys):
    missing = tmp_path / "nope.diff"
    rc = cli_triage._cmd_triage(_args(diff_file=missing))
    assert rc == 1
    assert "cannot read" in capsys.readouterr().err


def test_triage_header_counts_files_and_lines(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO(_CONFLICT_DIFF))
    cli_triage._cmd_triage(_args())
    out = capsys.readouterr().out
    assert "1 file(s)" in out
    assert "+1" in out


def test_against_uses_git(monkeypatch, capsys):
    captured = {}

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        return argparse.Namespace(stdout=_CONFLICT_DIFF, returncode=0)

    monkeypatch.setattr(cli_triage.subprocess, "run", fake_run)
    rc = cli_triage._cmd_triage(_args(against="origin/main"))
    assert rc == 0
    assert captured["cmd"] == ["git", "diff", "origin/main"]
    assert "merge-conflict marker(s)" in capsys.readouterr().out


def test_staged_uses_git_cached(monkeypatch):
    captured = {}

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        return argparse.Namespace(stdout=_CLEAN_DIFF, returncode=0)

    monkeypatch.setattr(cli_triage.subprocess, "run", fake_run)
    cli_triage._cmd_triage(_args(staged=True))
    assert captured["cmd"] == ["git", "diff", "--cached"]


def test_git_missing_returns_error(monkeypatch, capsys):
    def boom(cmd, **kwargs):
        raise FileNotFoundError

    monkeypatch.setattr(cli_triage.subprocess, "run", boom)
    rc = cli_triage._cmd_triage(_args(against="main"))
    assert rc == 1
    assert "git` not found" in capsys.readouterr().err


def test_triage_markdown_renders_signal():
    md = cli_triage.triage_markdown(_CONFLICT_DIFF)
    assert "prthinker triage —" in md
    assert "merge-conflict marker(s)" in md


def test_triage_markdown_clean_diff():
    md = cli_triage.triage_markdown(_CLEAN_DIFF)
    assert "No triage signals" in md


def test_triage_registered_in_command_handlers():
    from prthinker import cli

    assert cli._COMMAND_HANDLERS["triage"] is cli_triage._cmd_triage


def test_triage_parser_accepts_flags():
    from prthinker.cli_parser import _build_parser

    args = _build_parser().parse_args(
        ["triage", "--against", "origin/main", "--exit-nonzero-on-signal"]
    )
    assert args.command == "triage"
    assert args.against == "origin/main"
    assert args.exit_nonzero_on_signal is True


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

"""Tests for the shared agent-CLI subprocess plumbing."""

from __future__ import annotations

import subprocess
from types import SimpleNamespace

import pytest

from prthinker.backends import agent_cli


def test_validate_workdir_returns_path(tmp_path) -> None:
    assert agent_cli.validate_workdir(str(tmp_path), "Cfg") == tmp_path


def test_validate_workdir_missing_raises() -> None:
    with pytest.raises(ValueError, match="Cfg.working_dir does not exist"):
        agent_cli.validate_workdir("no/such/dir/here", "Cfg")


def test_raise_on_failure_zero_exit_is_noop() -> None:
    agent_cli.raise_on_failure(
        SimpleNamespace(returncode=0, stderr=""), "x CLI"
    )


def test_raise_on_failure_truncates_stderr() -> None:
    completed = SimpleNamespace(returncode=1, stderr="e" * 2000)
    with pytest.raises(RuntimeError) as excinfo:
        agent_cli.raise_on_failure(completed, "x CLI")
    message = str(excinfo.value)
    assert message.startswith("x CLI exited with code 1: ")
    assert len(message) < 600


def test_run_maps_file_not_found(monkeypatch, tmp_path) -> None:
    def _raise(*a, **k):
        raise FileNotFoundError("nope")

    monkeypatch.setattr(agent_cli.subprocess, "run", _raise)
    with pytest.raises(RuntimeError, match="x CLI executable not found: 'exe'"):
        agent_cli.run_print_mode_cli(
            ["exe"], "p", workdir=tmp_path,
            timeout_seconds=1.0, display_name="x CLI",
        )


def test_run_maps_timeout(monkeypatch, tmp_path) -> None:
    def _raise(*a, **k):
        raise subprocess.TimeoutExpired(cmd=["exe"], timeout=1.0)

    monkeypatch.setattr(agent_cli.subprocess, "run", _raise)
    with pytest.raises(RuntimeError, match="x CLI timed out after 1.0s"):
        agent_cli.run_print_mode_cli(
            ["exe"], "p", workdir=tmp_path,
            timeout_seconds=1.0, display_name="x CLI",
        )


def test_run_passes_prompt_and_workdir(monkeypatch, tmp_path) -> None:
    seen = {}

    def _capture(cmd, **kwargs):
        seen.update(cmd=cmd, **kwargs)
        return SimpleNamespace(stdout="", stderr="", returncode=0)

    monkeypatch.setattr(agent_cli.subprocess, "run", _capture)
    agent_cli.run_print_mode_cli(
        ["exe", "-p"], "the prompt", workdir=tmp_path,
        timeout_seconds=5.0, display_name="x CLI",
    )
    assert seen["cmd"] == ["exe", "-p"]
    assert seen["input"] == "the prompt"
    assert seen["cwd"] == str(tmp_path)
    assert seen["timeout"] == 5.0
    # Arg-list invocation only — shell=True is never passed.
    assert "shell" not in seen

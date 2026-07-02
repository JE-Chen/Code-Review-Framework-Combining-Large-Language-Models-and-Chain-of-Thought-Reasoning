"""Tests for the ``codex exec`` subprocess backend.

No real CLI is spawned: ``subprocess.run`` inside the shared agent-CLI
plumbing is monkeypatched with a scripted stand-in, pinning the command
line, the stdin prompt hand-off, and the NDJSON event parsing offline.
"""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from prthinker.backends import agent_cli as agent_cli_mod
from prthinker.backends import create_backend
from prthinker.backends.codex_cli import CodexCliBackend
from prthinker.config import BackendKind, CodexCliConfig, Config


def _completed(
    stdout: str = "", stderr: str = "", returncode: int = 0
) -> SimpleNamespace:
    return SimpleNamespace(
        stdout=stdout, stderr=stderr, returncode=returncode
    )


def _ndjson(*events: dict) -> str:
    return "\n".join(json.dumps(e) for e in events)


def _answer_events(text: str = "looks good") -> str:
    return _ndjson(
        {"type": "thread.started", "thread_id": "t-1"},
        {"type": "item.completed", "item": {"type": "reasoning", "text": "…"}},
        {"type": "item.completed", "item": {"type": "agent_message", "text": text}},
        {"type": "turn.completed", "usage": {"input_tokens": 7, "output_tokens": 9}},
    )


class _ScriptedRun:
    """Stands in for ``subprocess.run``; records every invocation."""

    def __init__(self, outcomes: list[object]) -> None:
        self._outcomes = list(outcomes)
        self.calls: list[dict] = []

    def __call__(self, cmd: list[str], **kwargs: object) -> object:
        self.calls.append({"cmd": cmd, **kwargs})
        outcome = self._outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def _backend(
    monkeypatch: pytest.MonkeyPatch,
    outcomes: list[object],
    **config_kwargs: object,
) -> tuple[CodexCliBackend, _ScriptedRun]:
    scripted = _ScriptedRun(outcomes)
    monkeypatch.setattr(agent_cli_mod.subprocess, "run", scripted)
    backend = CodexCliBackend(CodexCliConfig(**config_kwargs))
    return backend, scripted


# ----- config validation ------------------------------------------------


def test_config_empty_executable_raises() -> None:
    with pytest.raises(ValueError, match="executable is required"):
        CodexCliConfig(executable="")


def test_config_unknown_sandbox_mode_raises() -> None:
    with pytest.raises(ValueError, match="sandbox_mode must be one of"):
        CodexCliConfig(sandbox_mode="yolo")


def test_config_nonpositive_timeout_raises() -> None:
    with pytest.raises(ValueError, match="timeout_seconds must be positive"):
        CodexCliConfig(timeout_seconds=-1)


def test_backend_missing_workdir_raises() -> None:
    with pytest.raises(ValueError, match="working_dir does not exist"):
        CodexCliBackend(CodexCliConfig(working_dir="no/such/dir/here"))


def test_top_level_config_requires_sub_config() -> None:
    with pytest.raises(ValueError, match="codex_cli config required"):
        Config(backend=BackendKind.CODEX_CLI)


# ----- happy path ---------------------------------------------------------


def test_generate_returns_agent_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    backend, _ = _backend(monkeypatch, [_completed(stdout=_answer_events("fine"))])
    assert backend.generate("review this", 128) == "fine"


def test_generate_records_usage(monkeypatch: pytest.MonkeyPatch) -> None:
    backend, _ = _backend(monkeypatch, [_completed(stdout=_answer_events())])
    backend.generate("p", 1)
    usage = backend.last_usage()
    assert usage is not None
    assert (usage.prompt_tokens, usage.completion_tokens) == (7, 9)


def test_last_agent_message_wins(monkeypatch: pytest.MonkeyPatch) -> None:
    stdout = _ndjson(
        {"type": "item.completed", "item": {"type": "agent_message", "text": "draft"}},
        {"type": "item.completed", "item": {"type": "agent_message", "text": "final"}},
    )
    backend, _ = _backend(monkeypatch, [_completed(stdout=stdout)])
    assert backend.generate("p", 1) == "final"


def test_prompt_travels_over_stdin_with_dash_arg(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    backend, scripted = _backend(
        monkeypatch, [_completed(stdout=_answer_events())]
    )
    big_prompt = "diff --git a/x b/x\n" + "x" * 100_000
    backend.generate(big_prompt, 1)
    call = scripted.calls[0]
    assert call["input"] == big_prompt
    assert call["cmd"][-1] == "-"
    assert all(big_prompt not in part for part in call["cmd"])


def test_command_line_shape(
    monkeypatch: pytest.MonkeyPatch, tmp_path,
) -> None:
    backend, scripted = _backend(
        monkeypatch,
        [_completed(stdout=_answer_events())],
        executable="codex",
        model="o4-mini",
        working_dir=str(tmp_path),
        sandbox_mode="workspace-write",
    )
    backend.generate("p", 1)
    cmd = scripted.calls[0]["cmd"]
    assert cmd[:4] == ["codex", "exec", "--json", "--skip-git-repo-check"]
    assert cmd[cmd.index("-C") + 1] == str(tmp_path)
    assert cmd[cmd.index("-c") + 1] == 'sandbox_mode="workspace-write"'
    assert cmd[cmd.index("-m") + 1] == "o4-mini"
    assert scripted.calls[0]["cwd"] == str(tmp_path)


def test_command_line_omits_model_when_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    backend, scripted = _backend(
        monkeypatch, [_completed(stdout=_answer_events())]
    )
    backend.generate("p", 1)
    cmd = scripted.calls[0]["cmd"]
    assert "-m" not in cmd
    assert cmd[cmd.index("-c") + 1] == 'sandbox_mode="read-only"'


# ----- lenient / error parsing ----------------------------------------------


def test_non_json_stdout_returned_verbatim(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    backend, _ = _backend(monkeypatch, [_completed(stdout="  raw text  \n")])
    assert backend.generate("p", 1) == "raw text"


def test_events_without_agent_message_raise(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stdout = _ndjson(
        {"type": "thread.started", "thread_id": "t-1"},
        {"type": "turn.completed", "usage": {}},
    )
    backend, _ = _backend(monkeypatch, [_completed(stdout=stdout)])
    with pytest.raises(RuntimeError, match="no agent_message event"):
        backend.generate("p", 1)


def test_malformed_lines_are_skipped(monkeypatch: pytest.MonkeyPatch) -> None:
    stdout = (
        "not json\n\n"
        + json.dumps(
            {"type": "item.completed",
             "item": {"type": "agent_message", "text": "ok"}}
        )
        + "\n[1, 2]\n"
    )
    backend, _ = _backend(monkeypatch, [_completed(stdout=stdout)])
    assert backend.generate("p", 1) == "ok"


def test_nonzero_exit_raises_with_stderr(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    backend, _ = _backend(
        monkeypatch, [_completed(stderr="boom", returncode=2)]
    )
    with pytest.raises(RuntimeError, match="exited with code 2: boom"):
        backend.generate("p", 1)


def test_missing_executable_raises_runtime_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    backend, _ = _backend(monkeypatch, [FileNotFoundError("codex")])
    with pytest.raises(RuntimeError, match="executable not found"):
        backend.generate("p", 1)


# ----- identity + factory ----------------------------------------------------


def test_backend_kind_and_model_name(monkeypatch: pytest.MonkeyPatch) -> None:
    backend, _ = _backend(monkeypatch, [], model="m-1")
    assert backend.backend_kind() == "codex-cli"
    assert backend.model_name() == "m-1"


def test_factory_builds_codex_cli_backend() -> None:
    config = Config(
        backend=BackendKind.CODEX_CLI, codex_cli=CodexCliConfig()
    )
    backend = create_backend(config)
    assert isinstance(backend, CodexCliBackend)

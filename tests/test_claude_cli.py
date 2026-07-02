"""Tests for the ``claude -p`` subprocess backend.

No real CLI is spawned: ``subprocess.run`` is monkeypatched with a
scripted stand-in (mirroring the ``_ScriptedClient`` posture of the HTTP
backend tests) so the command line, the stdin prompt hand-off, and the
JSON-envelope parsing are pinned offline.
"""

from __future__ import annotations

import json
import subprocess
from types import SimpleNamespace

import pytest

from prthinker.backends import agent_cli as agent_cli_mod
from prthinker.backends import create_backend
from prthinker.backends.claude_cli import ClaudeCliBackend
from prthinker.config import BackendKind, ClaudeCliConfig, Config


def _completed(
    stdout: str = "", stderr: str = "", returncode: int = 0
) -> SimpleNamespace:
    return SimpleNamespace(
        stdout=stdout, stderr=stderr, returncode=returncode
    )


def _envelope(result: str = "looks good", **extra: object) -> str:
    payload: dict[str, object] = {
        "type": "result",
        "result": result,
        "usage": {"input_tokens": 12, "output_tokens": 34},
    }
    payload.update(extra)
    return json.dumps(payload)


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
) -> tuple[ClaudeCliBackend, _ScriptedRun]:
    scripted = _ScriptedRun(outcomes)
    monkeypatch.setattr(agent_cli_mod.subprocess, "run", scripted)
    backend = ClaudeCliBackend(ClaudeCliConfig(**config_kwargs))
    return backend, scripted


# ----- config validation ------------------------------------------------


def test_config_empty_executable_raises() -> None:
    with pytest.raises(ValueError, match="executable is required"):
        ClaudeCliConfig(executable="")


def test_config_nonpositive_timeout_raises() -> None:
    with pytest.raises(ValueError, match="timeout_seconds must be positive"):
        ClaudeCliConfig(timeout_seconds=0)


def test_backend_missing_workdir_raises() -> None:
    with pytest.raises(ValueError, match="working_dir does not exist"):
        ClaudeCliBackend(ClaudeCliConfig(working_dir="no/such/dir/here"))


def test_top_level_config_requires_sub_config() -> None:
    with pytest.raises(ValueError, match="claude_cli config required"):
        Config(backend=BackendKind.CLAUDE_CLI)


# ----- happy path ---------------------------------------------------------


def test_generate_parses_json_envelope(monkeypatch: pytest.MonkeyPatch) -> None:
    backend, scripted = _backend(
        monkeypatch, [_completed(stdout=_envelope("fine"))]
    )
    assert backend.generate("review this", 128) == "fine"
    assert len(scripted.calls) == 1


def test_generate_records_usage(monkeypatch: pytest.MonkeyPatch) -> None:
    backend, _ = _backend(monkeypatch, [_completed(stdout=_envelope())])
    backend.generate("p", 1)
    usage = backend.last_usage()
    assert usage is not None
    assert (usage.prompt_tokens, usage.completion_tokens) == (12, 34)


def test_generate_resets_usage_between_calls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    backend, _ = _backend(
        monkeypatch,
        [_completed(stdout=_envelope()), _completed(stdout="plain text")],
    )
    backend.generate("p", 1)
    backend.generate("p", 1)
    assert backend.last_usage() is None


def test_prompt_travels_over_stdin_not_argv(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    backend, scripted = _backend(
        monkeypatch, [_completed(stdout=_envelope())]
    )
    big_prompt = "diff --git a/x b/x\n" + "x" * 100_000
    backend.generate(big_prompt, 1)
    call = scripted.calls[0]
    assert call["input"] == big_prompt
    assert all(big_prompt not in part for part in call["cmd"])


def test_command_line_shape(monkeypatch: pytest.MonkeyPatch) -> None:
    backend, scripted = _backend(
        monkeypatch,
        [_completed(stdout=_envelope())],
        executable="claude",
        model="some-model",
        allowed_tools="Read,Grep,Glob",
    )
    backend.generate("p", 1)
    cmd = scripted.calls[0]["cmd"]
    assert cmd[:4] == ["claude", "-p", "--output-format", "json"]
    assert cmd[cmd.index("--model") + 1] == "some-model"
    assert cmd[cmd.index("--allowedTools") + 1] == "Read,Grep,Glob"


def test_command_line_omits_optional_flags(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    backend, scripted = _backend(
        monkeypatch, [_completed(stdout=_envelope())]
    )
    backend.generate("p", 1)
    cmd = scripted.calls[0]["cmd"]
    assert "--model" not in cmd
    assert "--allowedTools" not in cmd


def test_runs_in_configured_workdir(
    monkeypatch: pytest.MonkeyPatch, tmp_path,
) -> None:
    backend, scripted = _backend(
        monkeypatch,
        [_completed(stdout=_envelope())],
        working_dir=str(tmp_path),
    )
    backend.generate("p", 1)
    assert scripted.calls[0]["cwd"] == str(tmp_path)


# ----- lenient / fallback parsing -----------------------------------------


def test_non_json_stdout_returned_verbatim(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    backend, _ = _backend(monkeypatch, [_completed(stdout="  raw text  \n")])
    assert backend.generate("p", 1) == "raw text"


def test_json_array_stdout_falls_back_to_raw(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    backend, _ = _backend(monkeypatch, [_completed(stdout='["a", "b"]')])
    assert backend.generate("p", 1) == '["a", "b"]'


def test_empty_result_field_returns_empty_string(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    backend, _ = _backend(
        monkeypatch, [_completed(stdout=json.dumps({"result": None}))]
    )
    assert backend.generate("p", 1) == ""


# ----- error handling -------------------------------------------------------


def test_nonzero_exit_raises_with_stderr(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    backend, _ = _backend(
        monkeypatch, [_completed(stderr="boom", returncode=3)]
    )
    with pytest.raises(RuntimeError, match="exited with code 3: boom"):
        backend.generate("p", 1)


def test_is_error_envelope_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    backend, _ = _backend(
        monkeypatch,
        [_completed(stdout=_envelope("credit exhausted", is_error=True))],
    )
    with pytest.raises(RuntimeError, match="error result: credit exhausted"):
        backend.generate("p", 1)


def test_missing_executable_raises_runtime_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    backend, _ = _backend(monkeypatch, [FileNotFoundError("claude")])
    with pytest.raises(RuntimeError, match="executable not found"):
        backend.generate("p", 1)


def test_timeout_raises_runtime_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    backend, _ = _backend(
        monkeypatch,
        [subprocess.TimeoutExpired(cmd=["claude"], timeout=1.0)],
        timeout_seconds=1.0,
    )
    with pytest.raises(RuntimeError, match="timed out after 1.0s"):
        backend.generate("p", 1)


# ----- identity + factory ----------------------------------------------------


def test_backend_kind_and_model_name(monkeypatch: pytest.MonkeyPatch) -> None:
    backend, _ = _backend(monkeypatch, [], model="m-1")
    assert backend.backend_kind() == "claude-cli"
    assert backend.model_name() == "m-1"


def test_model_name_falls_back_to_executable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    backend, _ = _backend(monkeypatch, [])
    assert backend.model_name() == "claude"


def test_factory_builds_claude_cli_backend() -> None:
    config = Config(
        backend=BackendKind.CLAUDE_CLI, claude_cli=ClaudeCliConfig()
    )
    backend = create_backend(config)
    assert isinstance(backend, ClaudeCliBackend)

"""Subprocess backend for the local ``claude`` CLI (``claude -p``).

Shells out to the locally installed CLI in non-interactive print mode,
one subprocess per :meth:`generate` call. Unlike the HTTP backends, the
CLI can be granted a tool set (``--allowedTools``) so the model may read
the working tree while reviewing — the full local toolchain — instead of
seeing only the prompt text.

Two transport choices the tests pin (shared plumbing lives in
:mod:`prthinker.backends.agent_cli`):

* **Prompt goes over stdin, not argv.** Review prompts embed whole
  diffs; Windows caps a command line at ~32 K characters, so passing
  the prompt as an argument would truncate or fail on large PRs.
* **Response is requested as ``--output-format json``** so the result
  text and token usage can be extracted deterministically, with a
  plain-text fallback when the CLI emits something else.
"""

from __future__ import annotations

import json
import logging

from prthinker.backends.agent_cli import (
    parse_cli_usage,
    raise_on_failure,
    run_print_mode_cli,
    validate_workdir,
)
from prthinker.backends.base import InferenceBackend, Usage
from prthinker.config import ClaudeCliConfig

log = logging.getLogger(__name__)

_ERROR_RESULT_SNIPPET_CHARS = 200
_DISPLAY_NAME = "claude CLI"


class ClaudeCliBackend(InferenceBackend):
    """Run the local ``claude`` CLI in print mode as an inference backend."""

    def __init__(self, config: ClaudeCliConfig) -> None:
        self._config = config
        self._last_usage: Usage | None = None
        self._workdir = validate_workdir(config.working_dir, "ClaudeCliConfig")

    def backend_kind(self) -> str:
        return "claude-cli"

    def model_name(self) -> str:
        return self._config.model or self._config.executable

    def last_usage(self) -> Usage | None:
        return self._last_usage

    def _command(self) -> list[str]:
        cmd = [self._config.executable, "-p", "--output-format", "json"]
        if self._config.model:
            cmd.extend(["--model", self._config.model])
        if self._config.allowed_tools:
            cmd.extend(["--allowedTools", self._config.allowed_tools])
        return cmd

    def generate(
        self,
        prompt: str,
        max_new_tokens: int,
        *,
        cancel_event: "object | None" = None,
    ) -> str:
        # Same accept-and-ignore posture as the network backends: the
        # subprocess run is uninterruptible mid-call. The CLI manages its
        # own generation budget, so max_new_tokens is not forwarded.
        del cancel_event, max_new_tokens
        self._last_usage = None
        completed = run_print_mode_cli(
            self._command(), prompt,
            workdir=self._workdir,
            timeout_seconds=self._config.timeout_seconds,
            display_name=_DISPLAY_NAME,
        )
        raise_on_failure(completed, _DISPLAY_NAME)
        return self._extract_result(completed.stdout or "")

    def _extract_result(self, stdout: str) -> str:
        """Pull the result text (and usage) out of the CLI's JSON envelope.

        Lenient posture: stdout that is not the expected JSON object is
        returned verbatim so an older CLI or a plain-text mode still works.
        """
        try:
            data = json.loads(stdout)
        except json.JSONDecodeError:
            return stdout.strip()
        if not isinstance(data, dict):
            return stdout.strip()
        if data.get("is_error"):
            snippet = str(data.get("result") or "")[:_ERROR_RESULT_SNIPPET_CHARS]
            raise RuntimeError(f"claude CLI reported an error result: {snippet}")
        usage = parse_cli_usage(data.get("usage") or {})
        if usage is not None:
            self._last_usage = usage
        return str(data.get("result") or "")


__all__ = ["ClaudeCliBackend"]

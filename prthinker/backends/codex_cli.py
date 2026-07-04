"""Subprocess backend for the local ``codex`` CLI (``codex exec``).

Runs the locally installed CLI headless, one subprocess per
:meth:`generate` call:

.. code-block:: text

   codex exec --json --skip-git-repo-check -C <workdir> \\
       -c sandbox_mode="<mode>" [-m <model>] -

The trailing ``-`` makes the CLI read the prompt from stdin (argv would
hit platform command-line length caps on a large diff — shared plumbing
in :mod:`prthinker.backends.agent_cli`). ``--json`` output is NDJSON:
the answer is the last ``item.completed`` event whose item type is
``agent_message``; ``turn.completed`` carries the token usage. The
sandbox override goes through ``-c sandbox_mode=...`` rather than the
``--sandbox`` flag so the same shape works for every ``exec`` form, and
defaults to ``read-only`` — the review may read the working tree with
the CLI's full toolchain but never mutate it.
"""

from __future__ import annotations

import json
import logging

from prthinker.backends.agent_cli import (
    raise_on_failure,
    run_print_mode_cli,
    validate_workdir,
)
from prthinker.backends.base import InferenceBackend, Usage
from prthinker.config import CodexCliConfig

log = logging.getLogger(__name__)

_ANSWER_ITEM_TYPE = "agent_message"
_DISPLAY_NAME = "codex CLI"


class CodexCliBackend(InferenceBackend):
    """Run the local ``codex`` CLI headless as an inference backend."""

    def __init__(self, config: CodexCliConfig) -> None:
        self._config = config
        self._last_usage: Usage | None = None
        self._workdir = validate_workdir(config.working_dir, "CodexCliConfig")

    def backend_kind(self) -> str:
        return "codex-cli"

    def model_name(self) -> str:
        return self._config.model or self._config.executable

    def last_usage(self) -> Usage | None:
        return self._last_usage

    def _command(self) -> list[str]:
        cmd = [
            self._config.executable, "exec",
            "--json", "--skip-git-repo-check",
            "-C", str(self._workdir),
            "-c", f'sandbox_mode="{self._config.sandbox_mode}"',
        ]
        if self._config.model:
            cmd.extend(["-m", self._config.model])
        cmd.append("-")
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
        """Walk the NDJSON events; the last agent message is the answer.

        Lenient posture: stdout with no parseable event at all is
        returned verbatim (an older CLI or a plain-text mode); parseable
        events without an agent message mean the turn failed, which is
        an error rather than an empty review.
        """
        answer, saw_event = self._scan_events(stdout)
        if answer is not None:
            return answer
        if not saw_event:
            return stdout.strip()
        raise RuntimeError(
            "codex CLI produced no agent_message event in its output"
        )

    def _scan_events(self, stdout: str) -> tuple[str | None, bool]:
        """Walk NDJSON events, returning (last agent answer, any parsed)."""
        answer: str | None = None
        saw_event = False
        for line in stdout.splitlines():
            event = self._decode_event(line)
            if event is None:
                continue
            saw_event = True
            answer = self._answer_from_event(event, answer)
        return answer, saw_event

    def _answer_from_event(self, event: dict, answer: str | None) -> str | None:
        """Fold one event: update the pending answer or record usage."""
        event_type = event.get("type")
        if event_type == "item.completed":
            item = event.get("item") or {}
            if item.get("type") == _ANSWER_ITEM_TYPE:
                return str(item.get("text") or "")
        elif event_type == "turn.completed":
            self._record_usage(event.get("usage") or {})
        return answer

    @staticmethod
    def _decode_event(line: str) -> dict | None:
        """Parse one NDJSON line, returning None on blank / malformed input."""
        stripped = line.strip()
        if not stripped:
            return None
        try:
            data = json.loads(stripped)
        except json.JSONDecodeError:
            return None
        return data if isinstance(data, dict) else None

    def _record_usage(self, usage: dict) -> None:
        input_tokens = usage.get("input_tokens")
        output_tokens = usage.get("output_tokens")
        if input_tokens is not None and output_tokens is not None:
            self._last_usage = Usage(
                prompt_tokens=int(input_tokens),
                completion_tokens=int(output_tokens),
            )


__all__ = ["CodexCliBackend"]

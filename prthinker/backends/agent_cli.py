"""Shared subprocess plumbing for the local agent-CLI backends.

The ``claude`` and ``codex`` CLIs are driven the same way: the prompt is
piped over stdin (as an argument it would hit the ~32 K Windows
command-line cap on a large diff), the invocation is an arg list (never
``shell=True``), one hard timeout bounds the run, and the same failure
modes map to RuntimeError. The per-CLI pieces — the command line and the
output parsing — stay in their backend modules.
"""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path

log = logging.getLogger(__name__)

STDERR_SNIPPET_CHARS = 500


def validate_workdir(working_dir: str, config_name: str) -> Path:
    """Return the CLI working directory, refusing a path that is not a dir."""
    workdir = Path(working_dir)
    if not workdir.is_dir():
        raise ValueError(
            f"{config_name}.working_dir does not exist: {working_dir!r}"
        )
    return workdir


def run_print_mode_cli(
    cmd: list[str],
    prompt: str,
    *,
    workdir: Path,
    timeout_seconds: float,
    display_name: str,
) -> "subprocess.CompletedProcess[str]":
    """Invoke one agent CLI, mapping subprocess failures to RuntimeError."""
    try:
        return subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=str(workdir),
            timeout=timeout_seconds,
            check=False,
        )
    except FileNotFoundError as err:
        raise RuntimeError(
            f"{display_name} executable not found: {cmd[0]!r}"
        ) from err
    except subprocess.TimeoutExpired as err:
        raise RuntimeError(
            f"{display_name} timed out after {timeout_seconds}s"
        ) from err


def raise_on_failure(
    completed: "subprocess.CompletedProcess[str]", display_name: str
) -> None:
    """Raise RuntimeError with a stderr snippet on a non-zero exit."""
    if completed.returncode == 0:
        return
    stderr_snippet = (completed.stderr or "")[:STDERR_SNIPPET_CHARS]
    raise RuntimeError(
        f"{display_name} exited with code {completed.returncode}: "
        f"{stderr_snippet}"
    )


__all__ = [
    "STDERR_SNIPPET_CHARS",
    "raise_on_failure",
    "run_print_mode_cli",
    "validate_workdir",
]

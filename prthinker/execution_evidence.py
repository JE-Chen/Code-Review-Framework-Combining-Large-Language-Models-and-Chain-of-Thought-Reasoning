"""Safe execution-grounded evidence collection for review findings."""

from __future__ import annotations
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ToolEvidence:
    command: tuple[str, ...]
    exit_code: int | None
    stdout: str
    stderr: str
    timed_out: bool = False


def run_tool(
    command: tuple[str, ...], workdir: Path, timeout: float = 60, max_chars: int = 12000
) -> ToolEvidence:
    if not command:
        raise ValueError("command must not be empty")
    try:
        p = subprocess.run(
            command,
            cwd=workdir,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return ToolEvidence(
            command, p.returncode, p.stdout[-max_chars:], p.stderr[-max_chars:]
        )
    except subprocess.TimeoutExpired as e:
        return ToolEvidence(
            command,
            None,
            (e.stdout or "")[-max_chars:] if isinstance(e.stdout, str) else "",
            (e.stderr or "")[-max_chars:] if isinstance(e.stderr, str) else "",
            True,
        )

"""Sandbox-execute the model's ``suggestion`` blocks.

Most LLM reviewers emit a ``suggestion`` block and hope the human
applies it without breaking the tests. This module turns those
suggestions into *hypotheses with empirical evidence*: given a
suggestion that targets ``(file, start_line, line)``, we apply it in a
disposable copy of the working tree, run a verification command
(typically ``pytest -x``), and return PASS / FAIL / SKIP / ERROR.

Design constraints:

* The sandbox is a fresh ``tempfile.mkdtemp`` directory; the source
  tree is copied in via ``shutil.copytree`` so the original repo is
  never touched. ``.git/`` is skipped — we don't run git in the sandbox.
* The verify command runs under a timeout (default 60 s) and has its
  own working directory; if it exceeds the timeout we return
  ``status="error"``.
* If the suggestion's ``original`` text doesn't match the file at
  ``start_line..line``, we return ``status="skip"`` with a reason —
  applying it blind would corrupt the file.
* The function is pure-data in / pure-data out (returns a dataclass);
  callers do their own logging / formatting. The only side effects are
  the tempdir creation + the subprocess invocation, both fenced.

Per ``paper_rule.md``'s no-fabrication rule: this module makes no claim
about how often verified suggestions are actually correct. The
mechanism is the contribution.
"""

from __future__ import annotations

import logging
import shutil
import subprocess  # noqa: S404 — sandboxed verify command, never shell=True
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from reviewmind.schemas import InlineFinding

log = logging.getLogger(__name__)

VerificationStatus = Literal["pass", "fail", "skip", "error"]


@dataclass(frozen=True)
class VerificationResult:
    """Outcome of one sandboxed verification run.

    ``status`` semantics:

    * ``pass``  — verify_cmd exited 0 after the suggestion was applied.
    * ``fail``  — verify_cmd exited non-zero (tests broke).
    * ``skip``  — couldn't apply the suggestion safely (e.g. ``original``
                  didn't match) or the finding had no suggestion.
    * ``error`` — verify_cmd timed out, was killed, or otherwise crashed.
    """

    status: VerificationStatus
    verify_cmd: str
    duration_ms: int = 0
    reason: str = ""
    stdout_tail: str = ""
    stderr_tail: str = ""


def verify_suggestion(
    finding: InlineFinding,
    *,
    workdir: Path,
    verify_cmd: str,
    timeout_seconds: float = 60.0,
    tail_chars: int = 2000,
) -> VerificationResult:
    """Apply ``finding.suggestion`` in a sandbox and run ``verify_cmd``.

    ``workdir`` is the project root the sandbox is cloned from. It is
    never modified.
    """
    if finding.suggestion is None:
        return VerificationResult(
            status="skip",
            verify_cmd=verify_cmd,
            reason="finding has no suggestion block",
        )

    sandbox_root = Path(tempfile.mkdtemp(prefix="reviewmind-sbx-"))
    try:
        _copy_tree(workdir, sandbox_root)
        target = sandbox_root / finding.path
        if not target.exists():
            return VerificationResult(
                status="skip",
                verify_cmd=verify_cmd,
                reason=f"file {finding.path} not present in workdir",
            )

        ok, why = _apply_suggestion(target, finding)
        if not ok:
            return VerificationResult(
                status="skip", verify_cmd=verify_cmd, reason=why,
            )

        t0 = time.monotonic()
        try:
            proc = subprocess.run(  # noqa: S603 — argv list, never shell=True
                verify_cmd.split(),
                cwd=sandbox_root,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return VerificationResult(
                status="error",
                verify_cmd=verify_cmd,
                reason=f"verify_cmd exceeded {timeout_seconds}s timeout",
                duration_ms=int((time.monotonic() - t0) * 1000),
            )
        except FileNotFoundError as exc:
            return VerificationResult(
                status="error",
                verify_cmd=verify_cmd,
                reason=f"verify_cmd not runnable: {exc}",
            )

        duration = int((time.monotonic() - t0) * 1000)
        return VerificationResult(
            status="pass" if proc.returncode == 0 else "fail",
            verify_cmd=verify_cmd,
            duration_ms=duration,
            reason=f"exit={proc.returncode}",
            stdout_tail=(proc.stdout or "")[-tail_chars:],
            stderr_tail=(proc.stderr or "")[-tail_chars:],
        )
    finally:
        # Best-effort cleanup. Sandboxes are small (text only) but if
        # the verify command spawned a long-running child we still want
        # to drop the dir.
        shutil.rmtree(sandbox_root, ignore_errors=True)


def _copy_tree(src: Path, dst: Path) -> None:
    """Mirror ``src`` into ``dst`` excluding the ``.git`` directory."""
    def _ignore(_dir: str, entries: list[str]) -> list[str]:
        return [e for e in entries if e in {".git", "__pycache__", "node_modules"}]

    # ``copytree`` requires the destination not to exist; mkdtemp gives
    # us an empty dir, so copy contents into it.
    for child in src.iterdir():
        if child.name in {".git", "__pycache__", "node_modules"}:
            continue
        target = dst / child.name
        if child.is_dir():
            shutil.copytree(child, target, ignore=_ignore, symlinks=False)
        else:
            shutil.copy2(child, target)


def _apply_suggestion(target: Path, finding: InlineFinding) -> tuple[bool, str]:
    """Splice ``finding.suggestion`` into ``target`` at the right range.

    Returns ``(True, "")`` on success, ``(False, reason)`` on skip.
    Uses ``finding.original`` (when set) as a guardrail to catch line
    numbers that have drifted since the diff was produced.
    """
    if finding.suggestion is None:
        return False, "no suggestion"

    try:
        text = target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False, "file is not UTF-8 (binary?)"
    lines = text.splitlines(keepends=False)

    start = finding.start_line if finding.start_line is not None else finding.line
    end = finding.line
    if not (1 <= start <= end <= len(lines)):
        return False, (
            f"line range start={start} end={end} out of file "
            f"({len(lines)} lines)"
        )

    if finding.original is not None:
        observed = "\n".join(lines[start - 1: end])
        if observed.strip() != finding.original.strip():
            return False, "original text does not match current file"

    replacement_lines = finding.suggestion.splitlines()
    new_lines = lines[: start - 1] + replacement_lines + lines[end:]
    # Preserve trailing newline iff the original file had one.
    trailing = "\n" if text.endswith("\n") else ""
    target.write_text("\n".join(new_lines) + trailing, encoding="utf-8")
    return True, ""


__all__ = ["VerificationResult", "VerificationStatus", "verify_suggestion"]

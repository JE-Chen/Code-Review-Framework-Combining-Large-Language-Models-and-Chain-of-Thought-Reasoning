"""Standalone ``triage`` command — static review signals, no model.

``prthinker triage`` runs every no-model orientation signal over a diff
and prints the non-empty blocks. Because it never loads a backend, it is
instant and runs anywhere the runner profile installs (``httpx`` +
``pydantic`` + ``PyYAML``) — a pre-push sanity check on a laptop, or a
fast GPU-free gate in CI that catches conflict markers, Trojan-Source
glyphs, swallowed exceptions, and the rest before a full review is even
scheduled.

The diff is read from stdin by default, or from ``--diff-file``,
``git diff --cached`` (``--staged``), or ``git diff REF`` (``--against``).

Runner-safe: composes the pure signal functions; the only I/O is reading
the diff and an optional ``git`` subprocess (arg list, never a shell).
"""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from pathlib import Path

from prthinker.change_stats import compute_change_stats
from prthinker.diff import parse_unified_diff
from prthinker.orientation import build_static_signal_sections

log = logging.getLogger("prthinker")

_GIT_MISSING = "prthinker triage: `git` not found in PATH\n"


def _read_ref_diff(ref: str) -> tuple[str | None, int]:
    """Return ``git diff <ref>`` output, or ``(None, exit_code)`` on failure."""
    try:
        proc = subprocess.run(
            ["git", "diff", ref],
            capture_output=True, text=True, check=True, encoding="utf-8",
        )
    except FileNotFoundError:
        sys.stderr.write(_GIT_MISSING)
        return None, 1
    except subprocess.CalledProcessError as exc:
        sys.stderr.write(f"prthinker triage: `git diff {ref}` failed: {exc}\n")
        return None, 1
    return proc.stdout, 0


def _read_staged_diff() -> tuple[str | None, int]:
    """Return ``git diff --cached`` output, or ``(None, exit_code)``."""
    try:
        proc = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True, text=True, check=True, encoding="utf-8",
        )
    except FileNotFoundError:
        sys.stderr.write(_GIT_MISSING)
        return None, 1
    except subprocess.CalledProcessError as exc:
        sys.stderr.write(f"prthinker triage: `git diff --cached` failed: {exc}\n")
        return None, 1
    return proc.stdout, 0


def _read_file_diff(path: Path) -> tuple[str | None, int]:
    """Return the diff text read from ``path``, or ``(None, 1)`` on error."""
    try:
        return path.read_text(encoding="utf-8"), 0
    except OSError as exc:
        sys.stderr.write(f"prthinker triage: cannot read {path}: {exc}\n")
        return None, 1


def _resolve_diff(args: argparse.Namespace) -> tuple[str | None, int]:
    """Pick the diff source per the flags (staged > against > file > stdin)."""
    if getattr(args, "staged", False):
        return _read_staged_diff()
    ref = getattr(args, "against", None)
    if ref:
        return _read_ref_diff(ref)
    path = getattr(args, "diff_file", None)
    if path is not None:
        return _read_file_diff(path)
    return sys.stdin.read(), 0


def _render_triage(
    diff_text: str, changed: list[str], sections: tuple[str, ...]
) -> str:
    """Render the triage report: a header line plus the signal blocks."""
    stats = compute_change_stats(diff_text)
    added = sum(stat.added for stat in stats.values())
    removed = sum(stat.removed for stat in stats.values())
    header = (
        f"# prthinker triage — {len(changed)} file(s), +{added} −{removed}\n"
    )
    if not sections:
        return (
            header
            + "\n✅ No triage signals — nothing flagged by the static "
            "checks.\n"
        )
    return header + "\n" + "\n\n".join(sections) + "\n"


def triage_markdown(diff_text: str) -> str:
    """Render the full triage report for a diff as markdown.

    The reusable core behind both the ``triage`` command and the MCP
    ``triage_diff`` tool: parse the changed paths, run every no-model
    signal, and format the header + non-empty blocks.
    """
    changed = [file_diff.path for file_diff in parse_unified_diff(diff_text)]
    sections = build_static_signal_sections(diff_text, changed)
    return _render_triage(diff_text, changed, sections)


def _has_signal(diff_text: str) -> bool:
    """True when at least one no-model signal fires for the diff."""
    changed = [file_diff.path for file_diff in parse_unified_diff(diff_text)]
    return bool(build_static_signal_sections(diff_text, changed))


def _cmd_triage(args: argparse.Namespace) -> int:
    """Run the no-model orientation signals over a diff and print them."""
    diff, code = _resolve_diff(args)
    if diff is None:
        return code
    if not diff.strip():
        sys.stdout.write("prthinker triage: empty diff — nothing to check.\n")
        return 0
    sys.stdout.write(triage_markdown(diff))
    if getattr(args, "exit_nonzero_on_signal", False) and _has_signal(diff):
        return 1
    return 0


__all__ = ["_cmd_triage", "triage_markdown"]

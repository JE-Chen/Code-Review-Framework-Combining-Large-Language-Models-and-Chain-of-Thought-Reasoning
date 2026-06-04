"""List files a PR deletes outright.

A whole-file deletion is easy to overlook in a large diff — the reviewer
scrolls past a wall of removed lines — yet it is exactly the change that
silently drops a feature, a test, or a security control. This module
collects the files the PR removes entirely and renders a self-omitting
note so the reviewer can confirm each removal is intentional (dead-code
cleanup) rather than an accident (a test deleted to make CI green).

Runner-safe: reads the ``is_deleted`` flag the diff parser already sets.
"""

from __future__ import annotations

from prthinker.diff import parse_unified_diff

_DELETED_LIMIT = 12


def deleted_files(diff_text: str) -> list[str]:
    """Return the paths of files deleted in the diff, sorted."""
    paths = [fd.path for fd in parse_unified_diff(diff_text) if fd.is_deleted]
    return sorted(paths)


def format_deleted_note(paths: list[str]) -> str:
    """Collapsible 'files deleted' block, or ``""`` when there are none."""
    if not paths:
        return ""
    shown = paths[:_DELETED_LIMIT]
    lines = [
        f"<details><summary>🗑 {len(paths)} file(s) deleted</summary>",
        "",
    ]
    lines += [f"- `{p}`" for p in shown]
    extra = len(paths) - len(shown)
    if extra > 0:
        lines.append(f"- … and {extra} more")
    lines += [
        "",
        "_Confirm each removal is intentional — a dropped test or guard "
        "is easy to miss in a large diff._",
        "",
        "</details>",
    ]
    return "\n".join(lines)


__all__ = ["deleted_files", "format_deleted_note"]

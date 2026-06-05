"""Catch leftover merge-conflict markers a PR adds.

A botched conflict resolution ships lines like ``<<<<<<< HEAD`` or
``>>>>>>> branch`` straight into the source. They break the build at best
and silently corrupt logic at worst, yet they slip past a skimming
reviewer. This module scans the *added* diff lines for the conflict
markers git writes and surfaces each ``path:line`` in a self-omitting
note that, unlike the other orientation blocks, leads with a warning —
this is almost always a real defect.

Only the ``<<<<<<<`` and ``>>>>>>>`` (and diff3 ``|||||||``) markers
trigger it; the ``=======`` separator is deliberately ignored because a
reStructuredText / Markdown section underline can be seven equals signs
and would false-positive.

Runner-safe: pure string parsing over the diff already in hand.
"""

from __future__ import annotations

from dataclasses import dataclass

from prthinker.diff import iter_added_lines, parse_unified_diff

_MARKER_LIMIT = 15
_CONFLICT_PREFIXES = ("<<<<<<<", ">>>>>>>", "|||||||")


@dataclass(frozen=True)
class ConflictMarker:
    """One leftover conflict marker on an added line: path, line, marker."""

    path: str
    line: int
    marker: str


def _conflict_for_line(
    path: str, line_no: int, content: str
) -> ConflictMarker | None:
    """Build a :class:`ConflictMarker` when the line opens a conflict span."""
    for prefix in _CONFLICT_PREFIXES:
        if content.startswith(prefix):
            return ConflictMarker(path=path, line=line_no, marker=prefix)
    return None


def find_conflict_markers(diff_text: str) -> list[ConflictMarker]:
    """Return every leftover conflict marker added on a new-side line."""
    found: list[ConflictMarker] = []
    for file_diff in parse_unified_diff(diff_text):
        for line_no, content in iter_added_lines(file_diff.raw):
            marker = _conflict_for_line(file_diff.path, line_no, content)
            if marker is not None:
                found.append(marker)
    return found


def format_conflict_note(markers: list[ConflictMarker]) -> str:
    """Collapsible 'conflict markers' warning block, or ``""``."""
    if not markers:
        return ""
    shown = markers[:_MARKER_LIMIT]
    lines = [
        f"<details open><summary>⛔ {len(markers)} leftover merge-conflict "
        "marker(s) — likely a bad resolution</summary>",
        "",
    ]
    lines += [
        f"- `{m.path}:{m.line}` — `{m.marker}`" for m in shown
    ]
    extra = len(markers) - len(shown)
    if extra > 0:
        lines.append(f"- … and {extra} more")
    lines += [
        "",
        "_Resolve the conflict before merging — these markers will break "
        "the file._",
        "",
        "</details>",
    ]
    return "\n".join(lines)


__all__ = ["ConflictMarker", "find_conflict_markers", "format_conflict_note"]

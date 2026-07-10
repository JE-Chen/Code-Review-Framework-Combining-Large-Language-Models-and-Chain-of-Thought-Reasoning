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

from prthinker.detector_util import format_details_note, scan_added_lines

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
    return scan_added_lines(diff_text, _conflict_for_line)


def _marker_line(marker: ConflictMarker) -> str:
    """Render one ``path:line — marker`` bullet."""
    return f"- `{marker.path}:{marker.line}` — `{marker.marker}`"


def format_conflict_note(markers: list[ConflictMarker]) -> str:
    """Collapsible 'conflict markers' warning block, or ``""``."""
    return format_details_note(
        markers,
        summary=(
            f"⛔ {len(markers)} leftover merge-conflict "
            "marker(s) — likely a bad resolution"
        ),
        bullet=_marker_line,
        footer=(
            "_Resolve the conflict before merging — these markers will break "
            "the file._"
        ),
        limit=_MARKER_LIMIT,
        open_details=True,
    )


__all__ = ["ConflictMarker", "find_conflict_markers", "format_conflict_note"]

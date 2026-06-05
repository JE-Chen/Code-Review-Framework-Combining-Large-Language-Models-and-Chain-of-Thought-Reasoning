"""Flag deferred-work markers a PR newly introduces.

A diff that adds a ``TODO`` / ``FIXME`` / ``XXX`` / ``HACK`` / ``BUG``
comment is quietly shipping known-incomplete work. Reviewers want to see
those at submission time — to decide whether the marker is acceptable
debt or a blocker — rather than discover it months later. This module
scans only the *added* (new-side) lines of the diff for those markers and
renders a compact, self-omitting orientation note. Context and removed
lines are ignored, so a marker that merely moved or was deleted does not
register; only freshly-added ones do.

Runner-safe: pure string parsing over the diff already in hand.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from prthinker.diff import iter_added_lines, parse_unified_diff

_MARKER_LIMIT = 15
_TEXT_CAP = 80
_MARKER_TOKENS = ("TODO", "FIXME", "XXX", "HACK", "BUG")
_MARKER_RE = re.compile(r"\b(" + "|".join(_MARKER_TOKENS) + r")\b")


@dataclass(frozen=True)
class Marker:
    """One deferred-work marker on an added line: path, line, kind, text."""

    path: str
    line: int
    kind: str
    text: str


def _marker_for_line(path: str, line_no: int, content: str) -> Marker | None:
    """Build a :class:`Marker` for the first marker token on a line, or None."""
    match = _MARKER_RE.search(content)
    if match is None:
        return None
    return Marker(
        path=path,
        line=line_no,
        kind=match.group(1),
        text=content.strip()[:_TEXT_CAP],
    )


def new_markers(diff_text: str) -> list[Marker]:
    """Return every deferred-work marker added on a new-side line."""
    found: list[Marker] = []
    for file_diff in parse_unified_diff(diff_text):
        for line_no, content in iter_added_lines(file_diff.raw):
            marker = _marker_for_line(file_diff.path, line_no, content)
            if marker is not None:
                found.append(marker)
    return found


def _marker_line(marker: Marker) -> str:
    """Render one ``path:line **KIND** — text`` bullet."""
    return f"- `{marker.path}:{marker.line}` **{marker.kind}** — {marker.text}"


def format_new_markers_note(markers: list[Marker]) -> str:
    """Collapsible 'deferred-work markers added' block, or ``""``."""
    if not markers:
        return ""
    shown = markers[:_MARKER_LIMIT]
    lines = [
        f"<details><summary>📌 {len(markers)} deferred-work marker(s) "
        "added (TODO / FIXME / …)</summary>",
        "",
    ]
    lines += [_marker_line(m) for m in shown]
    extra = len(markers) - len(shown)
    if extra > 0:
        lines.append(f"- … and {extra} more")
    lines += [
        "",
        "_Confirm each is acceptable debt, not a blocker shipped by "
        "accident._",
        "",
        "</details>",
    ]
    return "\n".join(lines)


__all__ = ["Marker", "format_new_markers_note", "new_markers"]

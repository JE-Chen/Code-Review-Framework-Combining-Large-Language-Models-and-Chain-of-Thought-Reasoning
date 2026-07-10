"""Flag leftover debug statements a PR introduces.

Interactive-debugger calls and console logging are how a change gets
written, not how it should ship: ``breakpoint()`` halts CI, ``debugger``
freezes a browser, and ``console.log`` / ``pdb.set_trace`` leak noise or
state. They are added on purpose during development and removed on
purpose before merge — except when the second step is forgotten. This
module scans only the *added* diff lines for a curated, high-precision
set of debug constructs and surfaces each ``path:line`` so the reviewer
can confirm none shipped by accident.

The set is deliberately conservative — bare ``print(`` is excluded
because it is legitimate in many CLIs — so the note stays trustworthy
rather than crying wolf.

Runner-safe: pure string parsing over the diff already in hand.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from prthinker.detector_util import format_details_note, scan_added_lines

_DEBUG_LIMIT = 15
_TEXT_CAP = 80
_DEBUG_RE = re.compile(
    r"(breakpoint\s*\(\s*\)"
    r"|(?:i?pdb)\.set_trace\s*\("
    r"|console\.(?:log|debug)\s*\("
    r"|\bdebugger\b"
    r"|var_dump\s*\("
    r"|\bdd\s*\()"
)


@dataclass(frozen=True)
class DebugHit:
    """One leftover debug statement on an added line: path, line, text."""

    path: str
    line: int
    text: str


def _hit_for_line(path: str, line_no: int, content: str) -> DebugHit | None:
    """Build a :class:`DebugHit` when the line carries a debug construct."""
    if _DEBUG_RE.search(content) is None:
        return None
    return DebugHit(path=path, line=line_no, text=content.strip()[:_TEXT_CAP])


def find_debug_statements(diff_text: str) -> list[DebugHit]:
    """Return every leftover debug statement added on a new-side line."""
    return scan_added_lines(diff_text, _hit_for_line)


def _hit_line(hit: DebugHit) -> str:
    """Render one ``path:line — text`` bullet."""
    return f"- `{hit.path}:{hit.line}` — {hit.text}"


def format_debug_note(hits: list[DebugHit]) -> str:
    """Collapsible 'debug statements added' block, or ``""``."""
    return format_details_note(
        hits,
        summary=f"🐞 {len(hits)} leftover debug statement(s) added",
        bullet=_hit_line,
        footer=(
            "_Confirm these are not debugging leftovers that should be "
            "removed before merge._"
        ),
        limit=_DEBUG_LIMIT,
    )


__all__ = ["DebugHit", "find_debug_statements", "format_debug_note"]

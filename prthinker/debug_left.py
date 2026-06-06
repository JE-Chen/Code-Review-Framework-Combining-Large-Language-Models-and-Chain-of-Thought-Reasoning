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

from prthinker.diff import iter_added_lines, parse_unified_diff

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
    found: list[DebugHit] = []
    for file_diff in parse_unified_diff(diff_text):
        for line_no, content in iter_added_lines(file_diff.raw):
            hit = _hit_for_line(file_diff.path, line_no, content)
            if hit is not None:
                found.append(hit)
    return found


def _hit_line(hit: DebugHit) -> str:
    """Render one ``path:line — text`` bullet."""
    return f"- `{hit.path}:{hit.line}` — {hit.text}"


def format_debug_note(hits: list[DebugHit]) -> str:
    """Collapsible 'debug statements added' block, or ``""``."""
    if not hits:
        return ""
    shown = hits[:_DEBUG_LIMIT]
    lines = [
        f"<details><summary>🐞 {len(hits)} leftover debug statement(s) "
        "added</summary>",
        "",
    ]
    lines += [_hit_line(h) for h in shown]
    extra = len(hits) - len(shown)
    if extra > 0:
        lines.append(f"- … and {extra} more")
    lines += [
        "",
        "_Confirm these are not debugging leftovers that should be "
        "removed before merge._",
        "",
        "</details>",
    ]
    return "\n".join(lines)


__all__ = ["DebugHit", "find_debug_statements", "format_debug_note"]

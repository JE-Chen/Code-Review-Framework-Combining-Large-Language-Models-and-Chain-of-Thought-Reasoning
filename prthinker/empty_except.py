"""Flag swallowed exceptions a PR introduces.

An ``except`` clause whose body is just ``pass`` (or ``...``) silently
discards an error: the program limps on in a corrupt state and the bug
surfaces far from its cause. It is one of the highest-signal review
findings, and a purely textual scan of the added lines catches the
common case without a parser. This module pairs an added ``except ...:``
line with the added line that follows it; when that line is a bare
``pass`` / ``...`` it records the location. The single-line form
(``except X: pass``) is matched too.

It is a heuristic hint, not a parser: it never inspects whether the body
re-raises later, so it sticks to the unambiguous ``pass`` / ``...`` body.

Runner-safe: pure string parsing over the diff already in hand.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from prthinker.detector_util import format_details_note, iter_file_added_lines

_EXCEPT_LIMIT = 15
_INLINE_RE = re.compile(r"^except\b.*:\s*(pass|\.\.\.)\s*$")
_CLAUSE_RE = re.compile(r"^except\b.*:\s*$")
_EMPTY_BODIES = ("pass", "...")


@dataclass(frozen=True)
class SwallowedExcept:
    """One swallowed-exception site on an added line: path and line."""

    path: str
    line: int


def _is_empty_body(text: str) -> bool:
    """True when a line's stripped content is just ``pass`` or ``...``."""
    return text.strip() in _EMPTY_BODIES


def _hits_in_file(path: str, added: list[tuple[int, str]]) -> list[SwallowedExcept]:
    """Find swallowed-except sites among one file's added lines."""
    hits: list[SwallowedExcept] = []
    for index, (line_no, content) in enumerate(added):
        stripped = content.strip()
        if _INLINE_RE.match(stripped):
            hits.append(SwallowedExcept(path, line_no))
            continue
        if _CLAUSE_RE.match(stripped) and _next_is_empty(added, index, line_no):
            hits.append(SwallowedExcept(path, line_no))
    return hits


def _next_is_empty(
    added: list[tuple[int, str]], index: int, line_no: int
) -> bool:
    """True when the immediately following added line is an empty body."""
    nxt = index + 1
    if nxt >= len(added):
        return False
    next_line_no, next_content = added[nxt]
    return next_line_no == line_no + 1 and _is_empty_body(next_content)


def find_swallowed_excepts(diff_text: str) -> list[SwallowedExcept]:
    """Return every swallowed-exception site added on a new-side line."""
    found: list[SwallowedExcept] = []
    for path, added in iter_file_added_lines(diff_text):
        found += _hits_in_file(path, added)
    return found


def _hit_line(hit: SwallowedExcept) -> str:
    """Render one ``path:line`` bullet."""
    return f"- `{hit.path}:{hit.line}`"


def format_swallowed_note(hits: list[SwallowedExcept]) -> str:
    """Collapsible 'swallowed exception' block, or ``""``."""
    return format_details_note(
        hits,
        summary=(
            f"🤫 {len(hits)} swallowed exception(s) added "
            "(except: pass)"
        ),
        bullet=_hit_line,
        footer=(
            "_An empty except body hides the error — log it, handle it, or "
            "narrow the caught type._"
        ),
        limit=_EXCEPT_LIMIT,
    )


__all__ = [
    "SwallowedExcept",
    "find_swallowed_excepts",
    "format_swallowed_note",
]

"""Surface files renamed or moved within a PR.

Git emits ``rename from`` / ``rename to`` headers (with a ``similarity
index``) when it detects a file was moved rather than rewritten. A
reviewer who misses that header reads a 100 %-similar move as a brand-new
file plus an unrelated deletion — twice the work and a false "what
changed here?". This module pulls those rename pairs straight from the
diff text and renders a compact, self-omitting orientation note so the
move is obvious at a glance.

Runner-safe: pure string parsing over the diff already in hand.
"""

from __future__ import annotations

from dataclasses import dataclass

_RENAME_LIMIT = 12
_SIMILARITY_PREFIX = "similarity index "
_FROM_PREFIX = "rename from "
_TO_PREFIX = "rename to "


@dataclass(frozen=True)
class Rename:
    """One detected file move: old path, new path, optional similarity %."""

    old_path: str
    new_path: str
    similarity: int | None = None


@dataclass
class _RenameState:
    """Accumulator threaded across the diff's header lines."""

    pending_from: str | None = None
    pending_similarity: int | None = None
    renames: list[Rename] | None = None


def _parse_similarity(line: str) -> int | None:
    """Read the integer percent from a ``similarity index 95%`` line."""
    body = line[len(_SIMILARITY_PREFIX):].strip().rstrip("%")
    return int(body) if body.isdigit() else None


def _fold_line(line: str, state: _RenameState) -> None:
    """Fold one diff line into the rename accumulator, in place."""
    if line.startswith("diff --git "):
        state.pending_from = None
        state.pending_similarity = None
    elif line.startswith(_SIMILARITY_PREFIX):
        state.pending_similarity = _parse_similarity(line)
    elif line.startswith(_FROM_PREFIX):
        state.pending_from = line[len(_FROM_PREFIX):].strip()
    elif line.startswith(_TO_PREFIX) and state.pending_from is not None:
        new_path = line[len(_TO_PREFIX):].strip()
        state.renames.append(
            Rename(state.pending_from, new_path, state.pending_similarity)
        )
        state.pending_from = None
        state.pending_similarity = None


def detect_renames(diff_text: str) -> list[Rename]:
    """Extract every ``rename from`` / ``rename to`` pair in ``diff_text``."""
    state = _RenameState(renames=[])
    for line in diff_text.splitlines():
        _fold_line(line, state)
    return state.renames


def _rename_line(rename: Rename) -> str:
    """Render one ``old → new (NN% similar)`` bullet."""
    sim = (
        f" ({rename.similarity}% similar)"
        if rename.similarity is not None
        else ""
    )
    return f"- `{rename.old_path}` → `{rename.new_path}`{sim}"


def format_rename_note(renames: list[Rename]) -> str:
    """Collapsible 'renamed or moved' block, or ``""`` when there are none."""
    if not renames:
        return ""
    shown = renames[:_RENAME_LIMIT]
    lines = [
        f"<details><summary>🔀 {len(renames)} file(s) renamed or moved"
        "</summary>",
        "",
    ]
    lines += [_rename_line(r) for r in shown]
    extra = len(renames) - len(shown)
    if extra > 0:
        lines.append(f"- … and {extra} more")
    lines += [
        "",
        "_A pure move reads as new + deleted unless flagged — skim, "
        "don't re-review._",
        "",
        "</details>",
    ]
    return "\n".join(lines)


__all__ = ["Rename", "detect_renames", "format_rename_note"]

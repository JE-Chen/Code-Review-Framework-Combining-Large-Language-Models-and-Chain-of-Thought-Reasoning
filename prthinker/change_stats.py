"""Per-file change size from a unified diff.

A reviewer scanning the file menu wants to know *how big* each change is
before expanding it — a one-line tweak reads differently from a 200-line
rewrite. This module derives the added / removed line counts and hunk
count per file straight from the diff text, so the per-file summary can
carry a ``+12 −3 · 2 hunks`` badge with no model call and no extra git
work.

Runner-safe: pure string parsing over the diff already in hand.
"""

from __future__ import annotations

from dataclasses import dataclass

from prthinker.diff import parse_unified_diff


@dataclass(frozen=True)
class ChangeStat:
    """Added / removed / hunk counts for one file in the diff."""

    path: str
    added: int = 0
    removed: int = 0
    hunks: int = 0


def _count_from_raw(raw: str) -> tuple[int, int, int]:
    """Tally (added, removed, hunks) from one file's raw diff body."""
    added = removed = hunks = 0
    for line in raw.splitlines():
        if line.startswith("@@"):
            hunks += 1
        elif line.startswith("+") and not line.startswith("+++"):
            added += 1
        elif line.startswith("-") and not line.startswith("---"):
            removed += 1
    return added, removed, hunks


def compute_change_stats(diff_text: str) -> dict[str, ChangeStat]:
    """Map each file path in ``diff_text`` to its :class:`ChangeStat`."""
    stats: dict[str, ChangeStat] = {}
    for file_diff in parse_unified_diff(diff_text):
        added, removed, hunks = _count_from_raw(file_diff.raw)
        stats[file_diff.path] = ChangeStat(
            path=file_diff.path, added=added, removed=removed, hunks=hunks
        )
    return stats


def change_badge(stat: ChangeStat | None) -> str:
    """Compact ``+12 −3 · 2 hunks`` badge, or ``""`` when unknown/empty.

    The minus uses the U+2212 sign so it never renders as a markdown list
    bullet, and the hunk count is omitted for a single-hunk change to keep
    the common case terse.
    """
    if stat is None or (stat.added == 0 and stat.removed == 0 and stat.hunks == 0):
        return ""
    badge = f"+{stat.added} −{stat.removed}"
    if stat.hunks > 1:
        badge += f" · {stat.hunks} hunks"
    return badge


__all__ = ["ChangeStat", "change_badge", "compute_change_stats"]

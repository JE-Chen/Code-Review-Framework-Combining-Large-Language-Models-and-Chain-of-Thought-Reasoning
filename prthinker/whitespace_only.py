"""Flag files whose diff is whitespace / formatting only.

A reformat — reindentation, a line-length reflow, a tab-to-space sweep —
shows up in the diff as a wall of removed and re-added lines, but it
changes no behaviour. Reading it line by line is wasted reviewer effort.
This module compares each file's added lines against its removed lines
with *all* whitespace stripped: when the two collapse to the same
multiset of content, the file's change is formatting-only and is surfaced
in a self-omitting "formatting only" note so the reviewer can skim it.

A file that adds genuinely new content, or removes content outright, will
not collapse to an equal multiset and is therefore never mis-flagged.

Runner-safe: pure string parsing over the diff already in hand.
"""

from __future__ import annotations

from prthinker.diff import parse_unified_diff

_WS_LIMIT = 12


def _strip_ws(text: str) -> str:
    """Remove every whitespace character from a line of source."""
    return "".join(text.split())


def _added_removed(raw: str) -> tuple[list[str], list[str]]:
    """Collect (added, removed) line bodies for one file's diff."""
    added: list[str] = []
    removed: list[str] = []
    for line in raw.splitlines():
        if line.startswith("+++") or line.startswith("---"):
            continue
        if line.startswith("+"):
            added.append(line[1:])
        elif line.startswith("-"):
            removed.append(line[1:])
    return added, removed


def _is_formatting_only(added: list[str], removed: list[str]) -> bool:
    """True when added and removed lines match once whitespace is dropped."""
    norm_added = sorted(s for line in added if (s := _strip_ws(line)))
    norm_removed = sorted(s for line in removed if (s := _strip_ws(line)))
    if not norm_added and not norm_removed:
        return False
    return norm_added == norm_removed


def whitespace_only_files(diff_text: str) -> list[str]:
    """Return paths whose change is whitespace/formatting only, sorted."""
    out: list[str] = []
    for file_diff in parse_unified_diff(diff_text):
        if file_diff.is_binary:
            continue
        added, removed = _added_removed(file_diff.raw)
        if _is_formatting_only(added, removed):
            out.append(file_diff.path)
    return sorted(out)


def format_whitespace_note(paths: list[str]) -> str:
    """Collapsible 'formatting only' block, or ``""`` when there are none."""
    if not paths:
        return ""
    shown = paths[:_WS_LIMIT]
    lines = [
        f"<details><summary>🎨 {len(paths)} file(s) changed for "
        "formatting only</summary>",
        "",
    ]
    lines += [f"- `{p}`" for p in shown]
    extra = len(paths) - len(shown)
    if extra > 0:
        lines.append(f"- … and {extra} more")
    lines += [
        "",
        "_Whitespace / reindentation only — no behaviour change to "
        "review here._",
        "",
        "</details>",
    ]
    return "\n".join(lines)


__all__ = ["format_whitespace_note", "whitespace_only_files"]

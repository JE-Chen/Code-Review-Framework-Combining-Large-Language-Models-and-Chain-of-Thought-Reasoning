"""Flag files that add a large contiguous block of new lines.

Per-file totals (``+120 −3``) tell a reviewer how much changed, but not
*how* it is shaped: a hundred lines spread over ten small edits reads
very differently from a hundred lines pasted in one unbroken block. The
single big block is the one that hides a copy-paste, a vendored snippet,
or a generated table a human will skim. This module measures the longest
run of consecutive added lines per file and surfaces the files whose
biggest block crosses a threshold, so the reviewer can decide whether
that block deserves a close read or a quick skim.

Runner-safe: pure string parsing over the diff already in hand.
"""

from __future__ import annotations

from dataclasses import dataclass

from prthinker.diff import parse_unified_diff

_BLOCK_THRESHOLD = 80
_BLOCK_LIMIT = 12


@dataclass(frozen=True)
class LargeBlock:
    """One file's largest contiguous added block: path and line count."""

    path: str
    lines: int


def _longest_added_run(raw: str) -> int:
    """Return the longest run of consecutive added lines in a file's diff."""
    longest = 0
    current = 0
    in_hunk = False
    for line in raw.splitlines():
        if line.startswith("@@"):
            in_hunk = True
            current = 0
            continue
        if not in_hunk:
            continue
        if line.startswith("+") and not line.startswith("+++"):
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def large_blocks(
    diff_text: str, threshold: int = _BLOCK_THRESHOLD
) -> list[LargeBlock]:
    """Files whose largest contiguous added block is >= ``threshold``.

    Sorted largest block first so the heaviest paste leads; ties broken by
    path for determinism.
    """
    blocks = [
        LargeBlock(path=fd.path, lines=run)
        for fd in parse_unified_diff(diff_text)
        if (run := _longest_added_run(fd.raw)) >= threshold
    ]
    return sorted(blocks, key=lambda b: (-b.lines, b.path))


def format_large_block_note(blocks: list[LargeBlock]) -> str:
    """Collapsible 'large added block' block, or ``""`` when there are none."""
    if not blocks:
        return ""
    shown = blocks[:_BLOCK_LIMIT]
    lines = [
        f"<details><summary>📜 {len(blocks)} file(s) add a large "
        "contiguous block</summary>",
        "",
    ]
    lines += [
        f"- `{b.path}` — {b.lines} consecutive added lines" for b in shown
    ]
    extra = len(blocks) - len(shown)
    if extra > 0:
        lines.append(f"- … and {extra} more")
    lines += [
        "",
        "_A single big block often hides a copy-paste or generated "
        "content — confirm before a close read._",
        "",
        "</details>",
    ]
    return "\n".join(lines)


__all__ = ["LargeBlock", "format_large_block_note", "large_blocks"]

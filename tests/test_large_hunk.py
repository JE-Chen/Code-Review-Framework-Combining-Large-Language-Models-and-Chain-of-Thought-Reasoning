"""Tests for the large contiguous-block detector."""

from __future__ import annotations

from prthinker.large_hunk import (
    LargeBlock,
    format_large_block_note,
    large_blocks,
)


def _file_diff(path: str, *lines: str) -> str:
    body = "".join(f"{line}\n" for line in lines)
    return (
        f"diff --git a/{path} b/{path}\n"
        f"--- a/{path}\n"
        f"+++ b/{path}\n"
        "@@ -0,0 +1,9 @@\n" + body
    )


def test_block_at_or_above_threshold_flagged():
    diff = _file_diff("a.py", "+l1", "+l2", "+l3", "+l4")
    assert large_blocks(diff, threshold=3) == [LargeBlock("a.py", 4)]


def test_block_below_threshold_ignored():
    diff = _file_diff("a.py", "+l1", "+l2")
    assert large_blocks(diff, threshold=3) == []


def test_run_broken_by_context_resets():
    # 2 + 2 added lines split by a context line → longest run is 2.
    diff = _file_diff("a.py", "+l1", "+l2", " ctx", "+l3", "+l4")
    assert large_blocks(diff, threshold=3) == []


def test_removed_line_breaks_run():
    diff = _file_diff("a.py", "+l1", "+l2", "-old", "+l3")
    assert large_blocks(diff, threshold=3) == []


def test_sorted_largest_first():
    big = _file_diff("big.py", "+1", "+2", "+3", "+4", "+5")
    small = _file_diff("small.py", "+1", "+2", "+3")
    blocks = large_blocks(big + small, threshold=3)
    assert [b.path for b in blocks] == ["big.py", "small.py"]


def test_empty_diff():
    assert large_blocks("") == []


def test_default_threshold_is_high():
    # A modest block does not trip the default (80-line) threshold.
    diff = _file_diff("a.py", *[f"+l{i}" for i in range(10)])
    assert large_blocks(diff) == []


def test_format_note_lists_blocks():
    note = format_large_block_note([LargeBlock("a.py", 120)])
    assert "1 file(s) add a large contiguous block" in note
    assert "`a.py` — 120 consecutive added lines" in note
    assert note.startswith("<details>")


def test_format_note_empty():
    assert format_large_block_note([]) == ""


def test_format_note_caps_overflow():
    blocks = [LargeBlock(f"m{i}.py", 100) for i in range(15)]
    note = format_large_block_note(blocks)
    assert "15 file(s)" in note
    assert "… and 3 more" in note

"""Tests for the formatting-only (whitespace) file detector."""

from __future__ import annotations

from prthinker.whitespace_only import (
    format_whitespace_note,
    whitespace_only_files,
)

_REINDENT = (
    "diff --git a/a.py b/a.py\n"
    "--- a/a.py\n"
    "+++ b/a.py\n"
    "@@ -1,2 +1,2 @@\n"
    "-def f():\n"
    "-  return 1\n"
    "+def f():\n"
    "+    return 1\n"
)

_REAL_CHANGE = (
    "diff --git a/b.py b/b.py\n"
    "--- a/b.py\n"
    "+++ b/b.py\n"
    "@@ -1,1 +1,1 @@\n"
    "-x = 1\n"
    "+x = 2\n"
)

_PURE_ADDITION = (
    "diff --git a/c.py b/c.py\n"
    "--- a/c.py\n"
    "+++ b/c.py\n"
    "@@ -0,0 +1,1 @@\n"
    "+new_line = 1\n"
)


def test_reindent_is_formatting_only():
    assert whitespace_only_files(_REINDENT) == ["a.py"]


def test_real_change_not_flagged():
    assert whitespace_only_files(_REAL_CHANGE) == []


def test_pure_addition_not_flagged():
    # Adding genuinely new content is not a whitespace-only change.
    assert whitespace_only_files(_PURE_ADDITION) == []


def test_empty_diff():
    assert whitespace_only_files("") == []


def test_reordered_lines_same_content_flagged():
    # Same two lines, swapped order → multiset matches → formatting only.
    diff = (
        "diff --git a/d.py b/d.py\n"
        "--- a/d.py\n"
        "+++ b/d.py\n"
        "@@ -1,2 +1,2 @@\n"
        "-a = 1\n"
        "-b = 2\n"
        "+ b = 2\n"
        "+ a = 1\n"
    )
    assert whitespace_only_files(diff) == ["d.py"]


def test_multiple_files_sorted():
    assert whitespace_only_files(_REINDENT + _REAL_CHANGE) == ["a.py"]


def test_format_note_lists_files():
    note = format_whitespace_note(["a.py"])
    assert "1 file(s) changed for formatting only" in note
    assert "`a.py`" in note
    assert note.startswith("<details>")


def test_format_note_empty():
    assert format_whitespace_note([]) == ""


def test_format_note_caps_overflow():
    paths = [f"m{i}.py" for i in range(15)]
    note = format_whitespace_note(paths)
    assert "15 file(s)" in note
    assert "… and 3 more" in note

"""Tests for the binary-change orientation helper."""

from __future__ import annotations

from prthinker.binary_changes import binary_changed_files, format_binary_note

_BINARY = (
    "diff --git a/logo.png b/logo.png\n"
    "index abc1234..def5678 100644\n"
    "Binary files a/logo.png and b/logo.png differ\n"
)

_TEXT = (
    "diff --git a/a.py b/a.py\n"
    "--- a/a.py\n"
    "+++ b/a.py\n"
    "@@ -1 +1 @@\n"
    "-x = 1\n"
    "+x = 2\n"
)


def test_binary_file_detected():
    assert binary_changed_files(_BINARY) == ["logo.png"]


def test_text_file_not_detected():
    assert binary_changed_files(_TEXT) == []


def test_mixed_diff_returns_only_binary():
    assert binary_changed_files(_BINARY + _TEXT) == ["logo.png"]


def test_empty_diff():
    assert binary_changed_files("") == []


def test_multiple_binaries_sorted():
    second = (
        "diff --git a/z/icon.ico b/z/icon.ico\n"
        "index 111..222 100644\n"
        "Binary files a/z/icon.ico and b/z/icon.ico differ\n"
    )
    assert binary_changed_files(second + _BINARY) == ["logo.png", "z/icon.ico"]


def test_format_note_lists_files():
    note = format_binary_note(["logo.png"])
    assert "1 binary file(s) changed" in note
    assert "`logo.png`" in note
    assert note.startswith("<details>")


def test_format_note_empty():
    assert format_binary_note([]) == ""


def test_format_note_caps_overflow():
    paths = [f"asset{i}.png" for i in range(15)]
    note = format_binary_note(paths)
    assert "15 binary file(s)" in note
    assert "… and 3 more" in note

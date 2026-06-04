"""Tests for the deleted-files orientation helper."""

from __future__ import annotations

from prthinker.deleted_files import deleted_files, format_deleted_note

_DELETED = (
    "diff --git a/old.py b/old.py\n"
    "deleted file mode 100644\n"
    "index abc..000\n"
    "--- a/old.py\n"
    "+++ /dev/null\n"
    "@@ -1,2 +0,0 @@\n"
    "-x = 1\n"
    "-y = 2\n"
)

_EDIT = (
    "diff --git a/a.py b/a.py\n"
    "--- a/a.py\n"
    "+++ b/a.py\n"
    "@@ -1 +1 @@\n"
    "-x = 1\n"
    "+x = 2\n"
)


def test_deleted_file_detected():
    assert deleted_files(_DELETED) == ["old.py"]


def test_edit_not_flagged():
    assert deleted_files(_EDIT) == []


def test_mixed_returns_only_deleted():
    assert deleted_files(_DELETED + _EDIT) == ["old.py"]


def test_empty_diff():
    assert deleted_files("") == []


def test_multiple_deletions_sorted():
    second = (
        "diff --git a/z/gone.py b/z/gone.py\n"
        "deleted file mode 100644\n"
        "--- a/z/gone.py\n"
        "+++ /dev/null\n"
        "@@ -1 +0,0 @@\n"
        "-a = 1\n"
    )
    assert deleted_files(second + _DELETED) == ["old.py", "z/gone.py"]


def test_format_note_lists_files():
    note = format_deleted_note(["old.py"])
    assert "1 file(s) deleted" in note
    assert "`old.py`" in note
    assert note.startswith("<details>")


def test_format_note_empty():
    assert format_deleted_note([]) == ""


def test_format_note_caps_overflow():
    paths = [f"m{i}.py" for i in range(15)]
    note = format_deleted_note(paths)
    assert "15 file(s) deleted" in note
    assert "… and 3 more" in note

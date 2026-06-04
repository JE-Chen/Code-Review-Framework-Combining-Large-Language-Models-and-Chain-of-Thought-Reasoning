"""Tests for the rename-map orientation helper."""

from __future__ import annotations

from prthinker.rename_map import Rename, detect_renames, format_rename_note

_PURE_MOVE = (
    "diff --git a/old/foo.py b/new/foo.py\n"
    "similarity index 100%\n"
    "rename from old/foo.py\n"
    "rename to new/foo.py\n"
)

_MOVE_WITH_EDIT = (
    "diff --git a/pkg/a.py b/pkg/b.py\n"
    "similarity index 87%\n"
    "rename from pkg/a.py\n"
    "rename to pkg/b.py\n"
    "index 1234567..89abcde 100644\n"
    "--- a/pkg/a.py\n"
    "+++ b/pkg/b.py\n"
    "@@ -1,2 +1,2 @@\n"
    "-x = 1\n"
    "+x = 2\n"
)

_PLAIN_EDIT = (
    "diff --git a/pkg/c.py b/pkg/c.py\n"
    "index 111..222 100644\n"
    "--- a/pkg/c.py\n"
    "+++ b/pkg/c.py\n"
    "@@ -1 +1 @@\n"
    "-a\n"
    "+b\n"
)


def test_detect_pure_move():
    renames = detect_renames(_PURE_MOVE)
    assert renames == [Rename("old/foo.py", "new/foo.py", 100)]


def test_detect_move_with_edit_keeps_similarity():
    renames = detect_renames(_MOVE_WITH_EDIT)
    assert renames == [Rename("pkg/a.py", "pkg/b.py", 87)]


def test_detect_multiple_renames_in_one_diff():
    renames = detect_renames(_PURE_MOVE + _MOVE_WITH_EDIT)
    assert [r.new_path for r in renames] == ["new/foo.py", "pkg/b.py"]


def test_plain_edit_yields_no_rename():
    assert detect_renames(_PLAIN_EDIT) == []


def test_empty_diff_yields_no_rename():
    assert detect_renames("") == []


def test_rename_without_similarity_index():
    diff = (
        "diff --git a/x b/y\n"
        "rename from x\n"
        "rename to y\n"
    )
    assert detect_renames(diff) == [Rename("x", "y", None)]


def test_dangling_rename_to_without_from_is_ignored():
    # A ``rename to`` with no preceding ``rename from`` must not pair.
    diff = "diff --git a/x b/y\nrename to y\n"
    assert detect_renames(diff) == []


def test_format_note_lists_moves():
    note = format_rename_note([Rename("old/foo.py", "new/foo.py", 100)])
    assert "1 file(s) renamed or moved" in note
    assert "`old/foo.py` → `new/foo.py`" in note
    assert "100% similar" in note
    assert note.startswith("<details>")


def test_format_note_omits_similarity_when_unknown():
    note = format_rename_note([Rename("x", "y", None)])
    assert "`x` → `y`" in note
    assert "% similar" not in note


def test_format_note_empty_is_blank():
    assert format_rename_note([]) == ""


def test_format_note_caps_overflow():
    renames = [Rename(f"a{i}.py", f"b{i}.py", 90) for i in range(15)]
    note = format_rename_note(renames)
    assert "15 file(s) renamed or moved" in note
    assert "… and 3 more" in note

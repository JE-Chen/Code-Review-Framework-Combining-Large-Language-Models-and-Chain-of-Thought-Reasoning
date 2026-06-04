"""Tests for the file-mode change detector."""

from __future__ import annotations

from prthinker.mode_changes import (
    ModeChange,
    detect_mode_changes,
    format_mode_note,
)

_EXEC = (
    "diff --git a/run.sh b/run.sh\n"
    "old mode 100644\n"
    "new mode 100755\n"
)

_UNEXEC = (
    "diff --git a/data.bin b/data.bin\n"
    "old mode 100755\n"
    "new mode 100644\n"
)

_PLAIN_EDIT = (
    "diff --git a/a.py b/a.py\n"
    "index 111..222 100644\n"
    "--- a/a.py\n"
    "+++ b/a.py\n"
    "@@ -1 +1 @@\n"
    "-x = 1\n"
    "+x = 2\n"
)


def test_exec_bit_added_detected():
    changes = detect_mode_changes(_EXEC)
    assert changes == [ModeChange("run.sh", "100644", "100755")]
    assert changes[0].became_executable is True


def test_exec_bit_removed_not_flagged_as_executable():
    changes = detect_mode_changes(_UNEXEC)
    assert changes[0].became_executable is False


def test_plain_edit_has_no_mode_change():
    assert detect_mode_changes(_PLAIN_EDIT) == []


def test_empty_diff():
    assert detect_mode_changes("") == []


def test_multiple_mode_changes():
    changes = detect_mode_changes(_EXEC + _UNEXEC)
    assert [c.path for c in changes] == ["run.sh", "data.bin"]


def test_new_mode_without_old_mode_ignored():
    # A lone ``new mode`` (no preceding ``old mode``) does not pair.
    diff = "diff --git a/x b/x\nnew mode 100755\n"
    assert detect_mode_changes(diff) == []


def test_format_note_flags_executable():
    note = format_mode_note([ModeChange("run.sh", "100644", "100755")])
    assert "1 file mode change(s)" in note
    assert "`run.sh`" in note
    assert "now executable" in note


def test_format_note_no_exec_flag_when_not_executable():
    note = format_mode_note([ModeChange("data.bin", "100755", "100644")])
    assert "now executable" not in note


def test_format_note_empty():
    assert format_mode_note([]) == ""


def test_format_note_caps_overflow():
    changes = [
        ModeChange(f"f{i}.sh", "100644", "100755") for i in range(15)
    ]
    note = format_mode_note(changes)
    assert "15 file mode change(s)" in note
    assert "… and 3 more" in note

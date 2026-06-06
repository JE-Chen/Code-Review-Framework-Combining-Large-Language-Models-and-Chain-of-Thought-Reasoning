"""Tests for the leftover merge-conflict marker scanner."""

from __future__ import annotations

from prthinker.merge_markers import (
    ConflictMarker,
    find_conflict_markers,
    format_conflict_note,
)

_CONFLICT = (
    "diff --git a/a.py b/a.py\n"
    "--- a/a.py\n"
    "+++ b/a.py\n"
    "@@ -1,3 +1,7 @@\n"
    " before\n"
    "+<<<<<<< HEAD\n"
    "+ours = 1\n"
    "+=======\n"
    "+theirs = 1\n"
    "+>>>>>>> branch\n"
    " after\n"
)


def test_conflict_markers_detected():
    markers = find_conflict_markers(_CONFLICT)
    kinds = [(m.line, m.marker) for m in markers]
    # '<<<<<<<' on new line 2, '>>>>>>>' on new line 6.
    assert (2, "<<<<<<<") in kinds
    assert (6, ">>>>>>>") in kinds


def test_separator_alone_not_flagged():
    # A bare seven-equals line (e.g. an RST underline) must not trigger.
    diff = (
        "diff --git a/r.rst b/r.rst\n"
        "--- a/r.rst\n"
        "+++ b/r.rst\n"
        "@@ -0,0 +1,2 @@\n"
        "+Title\n"
        "+=======\n"
    )
    assert find_conflict_markers(diff) == []


def test_diff3_base_marker_detected():
    diff = (
        "diff --git a/b.py b/b.py\n"
        "--- a/b.py\n"
        "+++ b/b.py\n"
        "@@ -0,0 +1,1 @@\n"
        "+||||||| merged common ancestors\n"
    )
    markers = find_conflict_markers(diff)
    assert markers == [ConflictMarker(path="b.py", line=1, marker="|||||||")]


def test_context_marker_not_flagged():
    diff = (
        "diff --git a/c.py b/c.py\n"
        "--- a/c.py\n"
        "+++ b/c.py\n"
        "@@ -1,2 +1,2 @@\n"
        " <<<<<<< pre-existing on context\n"
        "-x = 1\n"
        "+x = 2\n"
    )
    assert find_conflict_markers(diff) == []


def test_empty_diff():
    assert find_conflict_markers("") == []


def test_format_note_lists_markers_and_is_open():
    note = format_conflict_note(find_conflict_markers(_CONFLICT))
    assert "leftover merge-conflict marker(s)" in note
    assert "`a.py:2`" in note
    assert note.startswith("<details open>")


def test_format_note_empty():
    assert format_conflict_note([]) == ""


def test_format_note_caps_overflow():
    markers = [
        ConflictMarker(path="a.py", line=i, marker="<<<<<<<")
        for i in range(20)
    ]
    note = format_conflict_note(markers)
    assert "20 leftover" in note
    assert "… and 5 more" in note

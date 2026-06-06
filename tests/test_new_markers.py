"""Tests for the deferred-work marker scanner."""

from __future__ import annotations

from prthinker.new_markers import (
    Marker,
    format_new_markers_note,
    new_markers,
)

_DIFF_WITH_MARKER = (
    "diff --git a/pkg/a.py b/pkg/a.py\n"
    "--- a/pkg/a.py\n"
    "+++ b/pkg/a.py\n"
    "@@ -1,2 +1,4 @@\n"
    " import os\n"
    "+# TODO: handle the empty case\n"
    "+value = os.getcwd()\n"
    " print(value)\n"
)

_DIFF_CONTEXT_ONLY = (
    "diff --git a/pkg/b.py b/pkg/b.py\n"
    "--- a/pkg/b.py\n"
    "+++ b/pkg/b.py\n"
    "@@ -1,2 +1,2 @@\n"
    " # FIXME: pre-existing marker on a context line\n"
    "-old = 1\n"
    "+old = 2\n"
)

_DIFF_REMOVED_MARKER = (
    "diff --git a/pkg/c.py b/pkg/c.py\n"
    "--- a/pkg/c.py\n"
    "+++ b/pkg/c.py\n"
    "@@ -1,2 +1,1 @@\n"
    "-# XXX: this is being removed\n"
    " keep = 1\n"
)


def test_added_marker_detected_with_line_number():
    markers = new_markers(_DIFF_WITH_MARKER)
    assert markers == [
        Marker(
            path="pkg/a.py",
            line=2,
            kind="TODO",
            text="# TODO: handle the empty case",
        )
    ]


def test_context_line_marker_ignored():
    # A marker on an unchanged context line is pre-existing, not new.
    assert new_markers(_DIFF_CONTEXT_ONLY) == []


def test_removed_marker_ignored():
    # A marker on a removed line is being deleted, not introduced.
    assert new_markers(_DIFF_REMOVED_MARKER) == []


def test_multiple_marker_kinds():
    diff = (
        "diff --git a/m.py b/m.py\n"
        "--- a/m.py\n"
        "+++ b/m.py\n"
        "@@ -0,0 +1,3 @@\n"
        "+# HACK: temporary\n"
        "+# BUG: off-by-one\n"
        "+x = 1  # FIXME later\n"
    )
    kinds = [m.kind for m in new_markers(diff)]
    assert kinds == ["HACK", "BUG", "FIXME"]


def test_word_boundary_avoids_false_positive():
    # ``TODOLIST`` is not the standalone TODO marker.
    diff = (
        "diff --git a/n.py b/n.py\n"
        "--- a/n.py\n"
        "+++ b/n.py\n"
        "@@ -0,0 +1,1 @@\n"
        "+TODOLIST = []\n"
    )
    assert new_markers(diff) == []


def test_text_is_capped():
    long_tail = "x" * 200
    diff = (
        "diff --git a/o.py b/o.py\n"
        "--- a/o.py\n"
        "+++ b/o.py\n"
        "@@ -0,0 +1,1 @@\n"
        f"+# TODO {long_tail}\n"
    )
    marker = new_markers(diff)[0]
    assert len(marker.text) == 80


def test_empty_diff():
    assert new_markers("") == []


def test_format_note_lists_markers():
    note = format_new_markers_note(new_markers(_DIFF_WITH_MARKER))
    assert "1 deferred-work marker(s) added" in note
    assert "`pkg/a.py:2` **TODO**" in note
    assert note.startswith("<details>")


def test_format_note_empty_is_blank():
    assert format_new_markers_note([]) == ""


def test_format_note_caps_overflow():
    markers = [
        Marker(path="a.py", line=i, kind="TODO", text="t") for i in range(20)
    ]
    note = format_new_markers_note(markers)
    assert "20 deferred-work marker(s) added" in note
    assert "… and 5 more" in note

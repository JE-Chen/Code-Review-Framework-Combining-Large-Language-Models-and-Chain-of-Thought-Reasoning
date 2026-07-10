"""Tests for the shared detector scan loop + note renderer."""

from __future__ import annotations

from prthinker.detector_util import (
    format_details_note,
    iter_file_added_lines,
    scan_added_lines,
)


def _diff(path: str, *lines: str) -> str:
    body = "".join(f"+{line}\n" for line in lines)
    return (
        f"diff --git a/{path} b/{path}\n"
        f"--- a/{path}\n"
        f"+++ b/{path}\n"
        f"@@ -0,0 +1,{len(lines)} @@\n" + body
    )


# ----- iter_file_added_lines ---------------------------------------------

def test_iter_file_added_lines_yields_path_and_numbered_lines():
    out = list(iter_file_added_lines(_diff("a.py", "x = 1", "y = 2")))
    assert out == [("a.py", [(1, "x = 1"), (2, "y = 2")])]


def test_iter_file_added_lines_multiple_files():
    diff = _diff("a.py", "one") + _diff("b.py", "two")
    out = list(iter_file_added_lines(diff))
    assert [path for path, _ in out] == ["a.py", "b.py"]


def test_iter_file_added_lines_empty_diff():
    assert list(iter_file_added_lines("")) == []


# ----- scan_added_lines ---------------------------------------------------

def test_scan_added_lines_collects_matcher_hits():
    def matcher(path, line_no, content):
        return (path, line_no, content) if "hit" in content else None

    diff = _diff("a.py", "hit me", "miss", "another hit")
    assert scan_added_lines(diff, matcher) == [
        ("a.py", 1, "hit me"),
        ("a.py", 3, "another hit"),
    ]


def test_scan_added_lines_none_results_are_filtered():
    diff = _diff("a.py", "nothing", "here")
    assert scan_added_lines(diff, lambda *_args: None) == []


def test_scan_added_lines_empty_diff():
    assert scan_added_lines("", lambda *_args: _args) == []


# ----- format_details_note ------------------------------------------------

def test_format_details_note_empty_hits_is_blank():
    assert format_details_note(
        [], summary="s", bullet=str, footer="f", limit=5
    ) == ""


def test_format_details_note_renders_full_block():
    note = format_details_note(
        ["a", "b"],
        summary="2 things",
        bullet=lambda h: f"- {h}",
        footer="_footer._",
        limit=5,
    )
    assert note == (
        "<details><summary>2 things</summary>\n"
        "\n"
        "- a\n"
        "- b\n"
        "\n"
        "_footer._\n"
        "\n"
        "</details>"
    )


def test_format_details_note_open_variant():
    note = format_details_note(
        ["a"], summary="s", bullet=str, footer="f", limit=5, open_details=True
    )
    assert note.startswith("<details open><summary>s</summary>")


def test_format_details_note_caps_overflow():
    note = format_details_note(
        ["a", "b", "c"], summary="s", bullet=str, footer="f", limit=2
    )
    assert "- … and 1 more" in note
    assert "c" not in note.replace("</details>", "")


def test_format_details_note_exactly_at_limit_no_overflow_line():
    note = format_details_note(
        ["a", "b"], summary="s", bullet=str, footer="f", limit=2
    )
    assert "more" not in note

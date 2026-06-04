"""Tests for the leftover-debug-statement scanner."""

from __future__ import annotations

from prthinker.debug_left import (
    DebugHit,
    find_debug_statements,
    format_debug_note,
)


def _added(*lines: str) -> str:
    body = "".join(f"+{line}\n" for line in lines)
    return (
        "diff --git a/a.py b/a.py\n"
        "--- a/a.py\n"
        "+++ b/a.py\n"
        f"@@ -0,0 +1,{len(lines)} @@\n" + body
    )


def test_breakpoint_detected():
    hits = find_debug_statements(_added("    breakpoint()"))
    assert hits == [DebugHit(path="a.py", line=1, text="breakpoint()")]


def test_pdb_set_trace_detected():
    assert find_debug_statements(_added("import pdb; pdb.set_trace()"))


def test_ipdb_set_trace_detected():
    assert find_debug_statements(_added("ipdb.set_trace()"))


def test_console_log_and_debug_detected():
    hits = find_debug_statements(_added("console.log(x)", "console.debug(y)"))
    assert [h.line for h in hits] == [1, 2]


def test_debugger_keyword_detected():
    assert find_debug_statements(_added("debugger;"))


def test_bare_print_not_flagged():
    # Conservative on purpose — print() is legitimate in many CLIs.
    assert find_debug_statements(_added("print('hello')")) == []


def test_console_warn_not_flagged():
    # Only log/debug are treated as leftover noise.
    assert find_debug_statements(_added("console.warn('careful')")) == []


def test_context_and_removed_lines_ignored():
    diff = (
        "diff --git a/a.py b/a.py\n"
        "--- a/a.py\n"
        "+++ b/a.py\n"
        "@@ -1,2 +1,2 @@\n"
        " breakpoint()  # pre-existing on context\n"
        "-console.log('removed')\n"
        "+keep = 1\n"
    )
    assert find_debug_statements(diff) == []


def test_empty_diff():
    assert find_debug_statements("") == []


def test_format_note_lists_hits():
    note = format_debug_note(find_debug_statements(_added("breakpoint()")))
    assert "1 leftover debug statement(s) added" in note
    assert "`a.py:1`" in note
    assert note.startswith("<details>")


def test_format_note_empty():
    assert format_debug_note([]) == ""


def test_format_note_caps_overflow():
    hits = [DebugHit(path="a.py", line=i, text="debugger") for i in range(20)]
    note = format_debug_note(hits)
    assert "20 leftover debug statement(s)" in note
    assert "… and 5 more" in note

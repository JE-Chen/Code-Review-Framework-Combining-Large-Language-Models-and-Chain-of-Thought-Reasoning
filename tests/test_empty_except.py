"""Tests for the swallowed-exception (except: pass) detector."""

from __future__ import annotations

from prthinker.empty_except import (
    SwallowedExcept,
    find_swallowed_excepts,
    format_swallowed_note,
)


def _added(*lines: str) -> str:
    body = "".join(f"+{line}\n" for line in lines)
    return (
        "diff --git a/a.py b/a.py\n"
        "--- a/a.py\n"
        "+++ b/a.py\n"
        f"@@ -0,0 +1,{len(lines)} @@\n" + body
    )


def test_two_line_except_pass_detected():
    diff = _added("try:", "    do()", "except Exception:", "    pass")
    assert find_swallowed_excepts(diff) == [SwallowedExcept("a.py", 3)]


def test_ellipsis_body_detected():
    diff = _added("except ValueError:", "    ...")
    assert find_swallowed_excepts(diff) == [SwallowedExcept("a.py", 1)]


def test_inline_except_pass_detected():
    diff = _added("except KeyError: pass")
    assert find_swallowed_excepts(diff) == [SwallowedExcept("a.py", 1)]


def test_bare_except_pass_detected():
    diff = _added("except:", "    pass")
    assert find_swallowed_excepts(diff) == [SwallowedExcept("a.py", 1)]


def test_handled_except_not_flagged():
    diff = _added("except Exception as exc:", "    log.warning(exc)")
    assert find_swallowed_excepts(diff) == []


def test_pass_not_adjacent_not_flagged():
    # A ``pass`` two lines below the except clause is a different body.
    diff = _added("except Exception:", "    cleanup()", "    pass")
    assert find_swallowed_excepts(diff) == []


def test_empty_diff():
    assert find_swallowed_excepts("") == []


def test_pass_on_context_line_not_flagged():
    diff = (
        "diff --git a/a.py b/a.py\n"
        "--- a/a.py\n"
        "+++ b/a.py\n"
        "@@ -1,2 +1,2 @@\n"
        "+except Exception:\n"
        " pass\n"
    )
    # The ``pass`` is a context (unchanged) line, not part of this change.
    assert find_swallowed_excepts(diff) == []


def test_format_note_lists_hits():
    note = format_swallowed_note([SwallowedExcept("a.py", 3)])
    assert "1 swallowed exception(s) added" in note
    assert "`a.py:3`" in note
    assert note.startswith("<details>")


def test_format_note_empty():
    assert format_swallowed_note([]) == ""


def test_format_note_caps_overflow():
    hits = [SwallowedExcept("a.py", i) for i in range(20)]
    note = format_swallowed_note(hits)
    assert "20 swallowed exception(s)" in note
    assert "… and 5 more" in note

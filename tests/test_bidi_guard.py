"""Tests for the Trojan-Source bidi / invisible-character detector."""

from __future__ import annotations

from prthinker.bidi_guard import BidiHit, find_bidi_hits, format_bidi_note

_RLO = chr(0x202E)
_PDI = chr(0x2069)
_ZWSP = chr(0x200B)


def _added(*lines: str) -> str:
    body = "".join(f"+{line}\n" for line in lines)
    return (
        "diff --git a/a.py b/a.py\n"
        "--- a/a.py\n"
        "+++ b/a.py\n"
        f"@@ -0,0 +1,{len(lines)} @@\n" + body
    )


def test_bidi_override_detected():
    diff = _added(f"x = 1  # {_RLO}harmless")
    hits = find_bidi_hits(diff)
    assert hits == [BidiHit(path="a.py", line=1, markers=("RLO",))]


def test_zero_width_detected():
    diff = _added(f"passwo{_ZWSP}rd = 1")
    hits = find_bidi_hits(diff)
    assert hits == [BidiHit(path="a.py", line=1, markers=("ZWSP",))]


def test_multiple_markers_sorted_and_deduped():
    diff = _added(f"{_RLO}{_PDI}{_RLO}code")
    hits = find_bidi_hits(diff)
    assert hits[0].markers == ("PDI", "RLO")


def test_clean_ascii_not_flagged():
    assert find_bidi_hits(_added("x = 1  # normal comment")) == []


def test_non_ascii_text_not_flagged():
    # Ordinary CJK / accented text is fine — only control chars trip it.
    assert find_bidi_hits(_added("name = '評論'  # café")) == []


def test_context_line_not_flagged():
    diff = (
        "diff --git a/a.py b/a.py\n"
        "--- a/a.py\n"
        "+++ b/a.py\n"
        "@@ -1,2 +1,2 @@\n"
        f" pre = 1  # {_RLO}existing\n"
        "-x = 1\n"
        "+x = 2\n"
    )
    assert find_bidi_hits(diff) == []


def test_empty_diff():
    assert find_bidi_hits("") == []


def test_format_note_is_open_and_lists_hits():
    note = format_bidi_note([BidiHit("a.py", 1, ("RLO",))])
    assert "hidden bidi / invisible characters" in note
    assert "`a.py:1` — RLO" in note
    assert note.startswith("<details open>")
    assert "Trojan Source" in note


def test_format_note_empty():
    assert format_bidi_note([]) == ""


def test_format_note_caps_overflow():
    hits = [BidiHit("a.py", i, ("RLO",)) for i in range(20)]
    note = format_bidi_note(hits)
    assert "20 line(s)" in note
    assert "… and 5 more" in note

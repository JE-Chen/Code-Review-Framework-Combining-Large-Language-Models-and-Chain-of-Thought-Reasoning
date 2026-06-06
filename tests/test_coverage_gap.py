"""Tests for the coverage-gap heuristic (prod changed without a test change)."""

from __future__ import annotations

from prthinker.coverage_gap import coverage_gaps, format_coverage_gap_note


def test_gap_flags_prod_without_matching_test():
    changed = ["prthinker/foo.py", "prthinker/bar.py", "tests/test_foo.py"]
    # foo.py is covered by test_foo.py; bar.py is not.
    assert coverage_gaps(changed) == ["prthinker/bar.py"]


def test_gap_matches_suffix_test_naming():
    changed = ["pkg/widget.py", "pkg/widget_test.py"]
    assert coverage_gaps(changed) == []


def test_gap_ignores_test_and_dunder_files():
    changed = ["tests/test_x.py", "prthinker/__init__.py", "conftest.py"]
    # No production file → no gap.
    assert coverage_gaps(changed) == []


def test_gap_ignores_non_python():
    changed = ["docs/readme.md", "prthinker/x.py", "config.yaml"]
    assert coverage_gaps(changed) == ["prthinker/x.py"]


def test_gap_all_covered_returns_empty():
    changed = ["a/foo.py", "tests/test_foo.py", "b/bar.py", "tests/test_bar.py"]
    assert coverage_gaps(changed) == []


def test_format_gap_note_lists_files():
    note = format_coverage_gap_note(["prthinker/bar.py"])
    assert "1 file(s) changed without a matching test change" in note
    assert "`prthinker/bar.py`" in note
    assert "Heuristic hint" in note


def test_format_gap_note_empty():
    assert format_coverage_gap_note([]) == ""


def test_format_gap_note_caps_overflow():
    gaps = [f"pkg/m{i}.py" for i in range(15)]
    note = format_coverage_gap_note(gaps)
    assert "15 file(s)" in note
    assert "and 5 more" in note

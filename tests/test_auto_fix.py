"""Auto-fix pure transforms — suggestion application + conflict detection.

The git / GitHub side effects in ``reviewmind.auto_fix.open_auto_fix_pr``
are not exercised here (they need a real git repo + GitHub credentials);
the pure functions are what the test suite locks in.
"""

from __future__ import annotations

from reviewmind.auto_fix import apply_suggestions_to_text, detect_conflicts
from reviewmind.schemas import InlineFinding


def _f(
    *, line: int, severity: str = "warning",
    suggestion: str | None = "REPLACED",
    start_line: int | None = None,
    original: str | None = None,
) -> InlineFinding:
    return InlineFinding(
        path="x.py", line=line, severity=severity,
        comment="c", suggestion=suggestion,
        start_line=start_line, original=original,
    )


# ----- single-line replacement ------------------------------------------

def test_single_line_warning_is_applied() -> None:
    text = "a\nb\nc\n"
    findings = [_f(line=2, suggestion="B")]
    new_text, report = apply_suggestions_to_text(text, findings)
    assert new_text == "a\nB\nc\n"
    assert len(report.applied) == 1
    assert report.skipped == []


def test_error_severity_is_NOT_auto_applied() -> None:
    text = "a\nb\nc\n"
    findings = [_f(line=2, severity="error", suggestion="B")]
    new_text, report = apply_suggestions_to_text(text, findings)
    assert new_text == text
    assert report.applied == []


def test_finding_without_suggestion_is_skipped() -> None:
    text = "a\nb\nc\n"
    findings = [_f(line=2, suggestion=None)]
    new_text, report = apply_suggestions_to_text(text, findings)
    assert new_text == text
    assert report.applied == []


# ----- multi-line replacement -------------------------------------------

def test_multiline_replacement_keeps_other_lines() -> None:
    text = "a\nb\nc\nd\ne\n"
    findings = [_f(line=4, start_line=2, suggestion="X\nY\nZ")]
    new_text, report = apply_suggestions_to_text(text, findings)
    # Lines 2..4 (b, c, d) replaced with X, Y, Z.
    assert new_text == "a\nX\nY\nZ\ne\n"
    assert len(report.applied) == 1


# ----- conflict detection -----------------------------------------------

def test_overlapping_edits_keep_first_drop_second() -> None:
    text = "a\nb\nc\nd\ne\n"
    findings = [
        _f(line=3, start_line=2, suggestion="X\nY"),
        _f(line=4, start_line=3, suggestion="Q\nR"),  # overlaps line 3
    ]
    new_text, report = apply_suggestions_to_text(text, findings)
    # First wins; second is skipped.
    assert new_text == "a\nX\nY\nd\ne\n"
    assert len(report.applied) == 1
    assert len(report.skipped) == 1


def test_non_overlapping_edits_both_apply() -> None:
    text = "a\nb\nc\nd\ne\n"
    findings = [
        _f(line=2, suggestion="B"),
        _f(line=4, suggestion="D"),
    ]
    new_text, report = apply_suggestions_to_text(text, findings)
    assert new_text == "a\nB\nc\nD\ne\n"
    assert len(report.applied) == 2
    assert report.skipped == []


def test_bottom_up_application_keeps_line_numbers_stable() -> None:
    # Replace lines 5 and 2 with multi-line content. If we applied
    # top-down the second edit's indices would shift; bottom-up keeps
    # them honest.
    text = "1\n2\n3\n4\n5\n6\n"
    findings = [
        _f(line=2, suggestion="A\nB"),
        _f(line=5, suggestion="C\nD"),
    ]
    new_text, report = apply_suggestions_to_text(text, findings)
    assert new_text == "1\nA\nB\n3\n4\nC\nD\n6\n"
    assert len(report.applied) == 2


# ----- pure ConflictReport behaviour ------------------------------------

def test_detect_conflicts_first_come_priority() -> None:
    from reviewmind.auto_fix import _Edit  # noqa: SLF001

    edits = [
        _Edit(start=10, end=12, replacement="x", finding_index=0),
        _Edit(start=11, end=11, replacement="y", finding_index=1),
        _Edit(start=20, end=22, replacement="z", finding_index=2),
    ]
    report = detect_conflicts(edits)
    assert [e.finding_index for e in report.applied] == [0, 2]
    assert [s.finding_index for s, _ in report.skipped] == [1]


def test_detect_conflicts_no_edges_no_overlap() -> None:
    from reviewmind.auto_fix import _Edit  # noqa: SLF001

    # Touching but not overlapping: edit1 ends at 10, edit2 starts at 11.
    edits = [
        _Edit(start=1, end=10, replacement="a", finding_index=0),
        _Edit(start=11, end=20, replacement="b", finding_index=1),
    ]
    report = detect_conflicts(edits)
    assert len(report.applied) == 2
    assert report.skipped == []

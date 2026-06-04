"""Unit tests for :mod:`prthinker.finding_dedup`."""

from __future__ import annotations

from prthinker.finding_dedup import _normalize_message, dedupe_findings
from prthinker.schemas import InlineFinding


def _finding(path: str, line: int, comment: str, severity: str = "info") -> InlineFinding:
    """Build an :class:`InlineFinding` for tests."""
    return InlineFinding(path=path, line=line, comment=comment, severity=severity)


def test_empty_input() -> None:
    """An empty input list yields an empty output list."""
    assert dedupe_findings([]) == []


def test_exact_dup_collapsed() -> None:
    """Two identical findings collapse into a single entry."""
    finding = _finding("a.py", 3, "Avoid bare except")
    result = dedupe_findings([finding, _finding("a.py", 3, "Avoid bare except")])
    assert len(result) == 1
    assert result[0].comment == "Avoid bare except"


def test_normalized_dup_collapsed() -> None:
    """Comments differing only in case/whitespace/trailing punctuation collapse."""
    result = dedupe_findings(
        [
            _finding("a.py", 3, "Avoid bare except"),
            _finding("a.py", 3, "  avoid   bare   EXCEPT.  "),
        ]
    )
    assert len(result) == 1


def test_same_path_line_different_message_kept() -> None:
    """Same location but a genuinely different message is not collapsed."""
    result = dedupe_findings(
        [
            _finding("a.py", 3, "Avoid bare except"),
            _finding("a.py", 3, "Use a context manager"),
        ]
    )
    assert len(result) == 2


def test_different_path_kept() -> None:
    """Same line+message on a different path is kept separately."""
    result = dedupe_findings(
        [
            _finding("a.py", 3, "Avoid bare except"),
            _finding("b.py", 3, "Avoid bare except"),
        ]
    )
    assert len(result) == 2
    assert {f.path for f in result} == {"a.py", "b.py"}


def test_different_line_kept() -> None:
    """Same path+message on a different line is kept separately."""
    result = dedupe_findings(
        [
            _finding("a.py", 3, "Avoid bare except"),
            _finding("a.py", 9, "Avoid bare except"),
        ]
    )
    assert len(result) == 2
    assert {f.line for f in result} == {3, 9}


def test_severity_preference_on_collapse() -> None:
    """On collapse the most severe finding survives regardless of arrival order."""
    result = dedupe_findings(
        [
            _finding("a.py", 3, "Risky", severity="info"),
            _finding("a.py", 3, "risky.", severity="error"),
            _finding("a.py", 3, "RISKY", severity="warning"),
        ]
    )
    assert len(result) == 1
    assert result[0].severity == "error"


def test_severity_tie_keeps_first_seen() -> None:
    """Equal severity keeps the first-seen finding on collapse."""
    first = _finding("a.py", 3, "Risky", severity="warning")
    second = _finding("a.py", 3, "risky", severity="warning")
    second = second.model_copy(update={"suggestion": "fixed"})
    result = dedupe_findings([first, second])
    assert len(result) == 1
    assert result[0].suggestion is None


def test_order_stability() -> None:
    """Non-duplicate findings preserve their original relative order."""
    findings = [
        _finding("a.py", 1, "first"),
        _finding("b.py", 2, "second"),
        _finding("a.py", 1, "first"),  # duplicate of index 0
        _finding("c.py", 3, "third"),
    ]
    result = dedupe_findings(findings)
    assert [(f.path, f.comment) for f in result] == [
        ("a.py", "first"),
        ("b.py", "second"),
        ("c.py", "third"),
    ]


def test_severe_dup_keeps_position_of_first_seen() -> None:
    """A more-severe later duplicate keeps the slot of the first occurrence."""
    findings = [
        _finding("a.py", 1, "dup", severity="info"),
        _finding("b.py", 2, "other"),
        _finding("a.py", 1, "dup", severity="error"),
    ]
    result = dedupe_findings(findings)
    assert [f.path for f in result] == ["a.py", "b.py"]
    assert result[0].severity == "error"


def test_normalize_message_helper() -> None:
    """The normalizer lowercases, collapses whitespace, and strips trailing punctuation."""
    assert _normalize_message("  Hello   World!! ") == "hello world"
    assert _normalize_message("Same   spacing.") == "same spacing"
    assert _normalize_message("") == ""

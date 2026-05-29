"""Reproducibility labeller — pure logic."""

from __future__ import annotations

from prthinker.reproducibility import label_findings
from prthinker.schemas import InlineFinding


def _f(path: str, line: int, comment: str) -> InlineFinding:
    return InlineFinding(
        path=path, line=line, severity="warning", comment=comment,
    )


def test_finding_in_both_passes_is_stable() -> None:
    a = [_f("x.py", 4, "consider logging")]
    b = [_f("x.py", 4, "Consider logging")]  # same normalised comment
    out = label_findings(a, b)
    assert len(out) == 1
    assert out[0].reproducibility == "stable"


def test_finding_unique_to_first_pass_is_low() -> None:
    a = [_f("x.py", 4, "log")]
    b: list[InlineFinding] = []
    out = label_findings(a, b)
    assert out[0].reproducibility == "low"


def test_finding_unique_to_second_pass_is_low_and_kept() -> None:
    a: list[InlineFinding] = []
    b = [_f("x.py", 4, "log")]
    out = label_findings(a, b)
    assert len(out) == 1
    assert out[0].reproducibility == "low"


def test_normalisation_collapses_whitespace_and_case() -> None:
    a = [_f("x.py", 4, "Consider using logging  module.")]
    b = [_f("x.py", 4, "consider using LOGGING module")]
    out = label_findings(a, b)
    assert out[0].reproducibility == "stable"


def test_different_line_not_matched() -> None:
    a = [_f("x.py", 4, "log")]
    b = [_f("x.py", 5, "log")]
    out = label_findings(a, b)
    assert [f.reproducibility for f in out] == ["low", "low"]


def test_different_path_not_matched() -> None:
    a = [_f("a.py", 4, "log")]
    b = [_f("b.py", 4, "log")]
    out = label_findings(a, b)
    assert all(f.reproducibility == "low" for f in out)


def test_mixed_stable_and_low() -> None:
    a = [
        _f("x.py", 1, "alpha"),
        _f("x.py", 2, "beta"),
        _f("x.py", 3, "gamma"),
    ]
    b = [
        _f("x.py", 2, "beta"),       # stable
        _f("x.py", 99, "delta"),     # new in pass 2 -> low
    ]
    out = label_findings(a, b)
    by_line = {f.line: f.reproducibility for f in out}
    assert by_line[1] == "low"
    assert by_line[2] == "stable"
    assert by_line[3] == "low"
    assert by_line[99] == "low"

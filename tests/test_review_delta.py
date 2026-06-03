"""Tests for cross-run finding delta tracking."""

from __future__ import annotations

from pathlib import Path

from prthinker import review_delta
from prthinker.schemas import InlineFinding


def _f(path: str, comment: str, severity: str = "warning") -> InlineFinding:
    return InlineFinding(path=path, line=1, comment=comment, severity=severity)


def test_fingerprint_is_line_independent():
    a = InlineFinding(path="x.py", line=5, comment="Same issue", severity="warning")
    b = InlineFinding(path="x.py", line=99, comment="same   ISSUE", severity="warning")
    # Different lines + whitespace/case, same identity.
    assert review_delta.fingerprint(a) == review_delta.fingerprint(b)


def test_fingerprint_distinguishes_path_and_severity():
    base = _f("x.py", "msg", "warning")
    assert review_delta.fingerprint(base) != review_delta.fingerprint(_f("y.py", "msg"))
    assert review_delta.fingerprint(base) != review_delta.fingerprint(
        _f("x.py", "msg", "error")
    )


def test_compute_delta_counts_new_resolved_carried():
    prev = set(review_delta.fingerprints([_f("a.py", "old"), _f("b.py", "keep")]))
    current = [_f("b.py", "keep"), _f("c.py", "fresh")]
    delta = review_delta.compute_delta(prev, current)
    assert delta.new == 1       # c.py/fresh
    assert delta.resolved == 1  # a.py/old
    assert delta.carried == 1   # b.py/keep


def test_format_delta():
    delta = review_delta.ReviewDelta(new=2, resolved=3, carried=5)
    assert review_delta.format_delta(delta) == "+2 new · 3 resolved · 5 carried"


def test_load_returns_none_when_missing(tmp_path: Path):
    assert review_delta.load_fingerprints(tmp_path / "nope.json") is None


def test_save_then_load_roundtrip(tmp_path: Path):
    path = tmp_path / "state" / "fp.json"
    findings = [_f("a.py", "one"), _f("b.py", "two")]
    review_delta.save_fingerprints(path, findings)
    loaded = review_delta.load_fingerprints(path)
    assert loaded == set(review_delta.fingerprints(findings))


def test_load_corrupt_file_returns_none(tmp_path: Path):
    path = tmp_path / "fp.json"
    path.write_text("not json{", encoding="utf-8")
    assert review_delta.load_fingerprints(path) is None

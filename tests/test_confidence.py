"""Unit tests for :mod:`prthinker.confidence`."""

from __future__ import annotations

from prthinker.confidence import filter_by_confidence
from prthinker.schemas import InlineFinding, Provenance

_PATH = "src/example.py"


def _finding(confidence: float | None, *, with_provenance: bool = True) -> InlineFinding:
    """Build an InlineFinding with optional provenance confidence."""
    provenance = (
        Provenance(confidence=confidence) if with_provenance else None
    )
    return InlineFinding(
        path=_PATH,
        line=1,
        comment="x",
        provenance=provenance,
    )


def test_below_threshold_dropped() -> None:
    findings = [_finding(0.3)]
    assert filter_by_confidence(findings, 0.7) == []


def test_at_threshold_kept_boundary() -> None:
    findings = [_finding(0.7)]
    assert filter_by_confidence(findings, 0.7) == findings


def test_above_threshold_kept_boundary() -> None:
    findings = [_finding(0.71)]
    assert filter_by_confidence(findings, 0.7) == findings


def test_missing_confidence_in_provenance_kept() -> None:
    findings = [_finding(None)]
    assert filter_by_confidence(findings, 0.7) == findings


def test_no_provenance_kept() -> None:
    findings = [_finding(None, with_provenance=False)]
    assert filter_by_confidence(findings, 0.7) == findings


def test_threshold_zero_keeps_all() -> None:
    findings = [_finding(0.0), _finding(0.5), _finding(None)]
    assert filter_by_confidence(findings, 0.0) == findings


def test_empty_list() -> None:
    assert filter_by_confidence([], 0.7) == []


def test_mixed_keeps_only_qualifying() -> None:
    low = _finding(0.2)
    boundary = _finding(0.7)
    missing = _finding(None)
    no_prov = _finding(None, with_provenance=False)
    result = filter_by_confidence([low, boundary, missing, no_prov], 0.7)
    assert result == [boundary, missing, no_prov]

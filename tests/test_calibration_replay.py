"""Replay-style validation of the calibration merge-gate decisions.

Seeds a :class:`~prthinker.calibration.CalibrationStore` with a realistic
mixed accepted/dismissed history (two categories, two authors, 40 events,
old vs recent timestamps) and asserts the gate decisions that
:func:`prthinker.cli_review_emit._calibration_gate_decision` produces
across a matrix of findings — including stability across a store
close/reopen (persistence round-trip).
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import pytest

from prthinker.calibration import CalibrationStore
from prthinker.cli_review_emit import _calibration_gate_decision
from prthinker.schemas import InlineFinding, Provenance

_REPO = "acme/widgets"
_HALF_LIFE_DAYS = 90.0
_MIN_SAMPLES = 10
_DAY = 86400.0

_EXPECTED = {
    "well_calibrated_high_conf": "publish",
    "well_calibrated_low_conf": "abstain",
    "noisy_low_conf": "abstain",
    "noisy_high_conf": "publish",
    "sparse_category": "request-human-review",
    "decayed_author": "request-human-review",
    "no_confidence": "request-human-review",
}


def _seed_store(path: Path, now: float) -> CalibrationStore:
    """Mixed 40-event history: two categories, two authors, old vs recent."""
    store = CalibrationStore(path)
    recent = now - 60.0
    # Five half-lives back: each event decays to ~3% of its weight.
    old = now - 5 * _HALF_LIFE_DAYS * _DAY
    # alice/security: 12 recent accepted -> well-calibrated, low threshold.
    for i in range(12):
        store.record(_REPO, "alice", "security", True,
                     event_id=f"sec-{i}", timestamp=recent - i)
    # alice/style: 12 recent dismissed -> noisy, raised threshold.
    for i in range(12):
        store.record(_REPO, "alice", "style", False,
                     event_id=f"sty-{i}", timestamp=recent - i)
    # alice/docs: only 4 events -> below the minimum-samples floor.
    for i in range(4):
        store.record(_REPO, "alice", "docs", True,
                     event_id=f"doc-{i}", timestamp=recent - i)
    # bob/security: 12 raw events, but 8 are stale — after half-life
    # decay the effective sample mass (~4.25) falls under the floor.
    for i in range(4):
        store.record(_REPO, "bob", "security", True,
                     event_id=f"bob-new-{i}", timestamp=recent - i)
    for i in range(8):
        store.record(_REPO, "bob", "security", True,
                     event_id=f"bob-old-{i}", timestamp=old - i)
    return store


def _args(author: str) -> argparse.Namespace:
    return argparse.Namespace(
        repo=_REPO,
        calibration_author=author,
        calibration_category="",
        calibration_half_life_days=_HALF_LIFE_DAYS,
        calibration_min_samples=_MIN_SAMPLES,
    )


def _finding(category: str, confidence: float | None) -> InlineFinding:
    provenance = None if confidence is None else Provenance(confidence=confidence)
    return InlineFinding(
        path="src/app.py",
        line=3,
        comment=f"possible {category} issue",
        category=category,
        provenance=provenance,
    )


def _decisions(store: CalibrationStore) -> dict[str, str]:
    alice, bob = _args("alice"), _args("bob")
    return {
        "well_calibrated_high_conf": _calibration_gate_decision(
            alice, store, _finding("security", 0.9)),
        "well_calibrated_low_conf": _calibration_gate_decision(
            alice, store, _finding("security", 0.2)),
        "noisy_low_conf": _calibration_gate_decision(
            alice, store, _finding("style", 0.3)),
        "noisy_high_conf": _calibration_gate_decision(
            alice, store, _finding("style", 0.9)),
        "sparse_category": _calibration_gate_decision(
            alice, store, _finding("docs", 0.99)),
        "decayed_author": _calibration_gate_decision(
            bob, store, _finding("security", 0.9)),
        "no_confidence": _calibration_gate_decision(
            alice, store, _finding("security", None)),
    }


@pytest.fixture()
def seeded(tmp_path: Path) -> CalibrationStore:
    store = _seed_store(tmp_path / "calibration.sqlite", time.time())
    yield store
    store.close()


def test_gate_decision_matrix(seeded: CalibrationStore) -> None:
    assert _decisions(seeded) == _EXPECTED


def test_decay_pushes_stale_author_under_sample_floor(
    seeded: CalibrationStore,
) -> None:
    # Raw (undecayed) counts clear the minimum-samples floor easily...
    raw = seeded.calibration(_REPO, "bob", "security")
    assert raw.accepted + raw.dismissed == 12
    assert raw.accepted + raw.dismissed >= _MIN_SAMPLES
    # ...but the half-life-decayed posterior does not, so the gate asks
    # for a human instead of trusting a stale history.
    posterior = seeded.hierarchical(
        _REPO, "bob", "security", half_life_days=_HALF_LIFE_DAYS
    )
    assert posterior.accepted + posterior.dismissed < _MIN_SAMPLES
    decision = _calibration_gate_decision(
        _args("bob"), seeded, _finding("security", 0.9)
    )
    assert decision == "request-human-review"


def test_thresholds_move_with_category_history(seeded: CalibrationStore) -> None:
    accepted_heavy = seeded.hierarchical(
        _REPO, "alice", "security", half_life_days=_HALF_LIFE_DAYS
    )
    dismissed_heavy = seeded.hierarchical(
        _REPO, "alice", "style", half_life_days=_HALF_LIFE_DAYS
    )
    # A well-received category lowers the publish bar; a noisy one raises it.
    assert accepted_heavy.threshold() < 0.5 < dismissed_heavy.threshold()


def test_decisions_stable_across_close_and_reopen(tmp_path: Path) -> None:
    db = tmp_path / "calibration.sqlite"
    store = _seed_store(db, time.time())
    first = _decisions(store)
    assert first == _EXPECTED
    store.close()

    reopened = CalibrationStore(db)
    try:
        assert _decisions(reopened) == first
    finally:
        reopened.close()

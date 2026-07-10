"""Calibration — threshold sweep regression + shared-connection store."""

from __future__ import annotations

import sqlite3
import threading
from pathlib import Path

from prthinker.calibration import CalibrationStore, _f1_at, select_threshold


# ----- select_threshold ---------------------------------------------------

def _naive_select_threshold(scored_labels) -> float:
    """The pre-rewrite O(unique_scores x n) reference implementation."""
    best = (0.0, -1.0)
    for threshold in sorted({float(s) for s, _ in scored_labels}):
        f = _f1_at(threshold, scored_labels)
        if f > best[1]:
            best = (threshold, f)
    return best[0]


_THRESHOLD_FIXTURES = (
    [],                                        # empty → 0.0 default
    [(0.1, False), (0.9, True)],               # trivially separable
    [(0.5, True)],                             # single positive
    [(0.5, False)],                            # single negative
    [(0.3, True), (0.3, False), (0.3, True)],  # all scores tie
    [(0.2, False), (0.4, True), (0.6, False), (0.8, True)],  # interleaved
    [(0.1, True), (0.2, True), (0.3, True)],   # all positive
    [(0.1, False), (0.2, False)],              # all negative
    [(0.25, True), (0.25, False), (0.75, True), (0.75, True), (0.5, False)],
    [(1.0, True), (0.0, False), (0.5, True), (0.5, False), (0.5, True)],
)


def test_select_threshold_matches_naive_reference() -> None:
    for fixture in _THRESHOLD_FIXTURES:
        assert select_threshold(fixture) == _naive_select_threshold(fixture), (
            fixture
        )


def test_select_threshold_empty_returns_zero() -> None:
    assert select_threshold([]) == 0.0


def test_select_threshold_prefers_smallest_threshold_on_f1_tie() -> None:
    # Both candidate thresholds classify every point as positive-side
    # identically (all labels True) → F1 ties at 1.0 for the smallest
    # threshold; the naive sweep kept the smallest, so must we.
    fixture = [(0.4, True), (0.8, True)]
    assert select_threshold(fixture) == 0.4


def test_select_threshold_all_negative_returns_smallest_score() -> None:
    # No positive labels → every threshold has F1 == 0; historical
    # behaviour returns the smallest observed score.
    assert select_threshold([(0.7, False), (0.2, False)]) == 0.2


# ----- CalibrationStore shared connection ---------------------------------

def test_store_creates_file_and_schema_eagerly(tmp_path: Path) -> None:
    path = tmp_path / "cal.sqlite"
    CalibrationStore(path)
    assert path.exists()
    with sqlite3.connect(path) as conn:
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
    assert {"feedback", "feedback_events"} <= tables


def test_store_reuses_one_connection_across_calls(tmp_path: Path) -> None:
    store = CalibrationStore(tmp_path / "cal.sqlite")
    store.record("r", "a", "c", True, event_id="e1")
    first = store._conn
    store.record("r", "a", "c", False, event_id="e2")
    cal = store.calibration("r", "a", "c")
    assert store._conn is first  # no per-call reconnect
    assert (cal.accepted, cal.dismissed) == (1, 1)


def test_store_close_then_reuse_reopens_lazily(tmp_path: Path) -> None:
    store = CalibrationStore(tmp_path / "cal.sqlite")
    store.record("r", "a", "c", True, event_id="e1")
    store.close()
    assert store._conn is None
    # Reuse after close must transparently reopen, not crash.
    assert store.calibration("r", "a", "c").accepted == 1
    store.close()


def test_store_close_is_idempotent(tmp_path: Path) -> None:
    store = CalibrationStore(tmp_path / "cal.sqlite")
    store.close()
    store.close()  # second close on an already-closed store is a no-op


def test_store_duplicate_event_id_is_ignored(tmp_path: Path) -> None:
    store = CalibrationStore(tmp_path / "cal.sqlite")
    store.record("r", "a", "c", True, event_id="dup")
    store.record("r", "a", "c", True, event_id="dup")
    assert store.calibration("r", "a", "c").accepted == 1


def test_store_records_from_multiple_threads(tmp_path: Path) -> None:
    store = CalibrationStore(tmp_path / "cal.sqlite")

    def worker(index: int) -> None:
        store.record("r", "a", "c", index % 2 == 0, event_id=f"evt-{index}")

    threads = [
        threading.Thread(target=worker, args=(i,)) for i in range(8)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    cal = store.calibration("r", "a", "c")
    assert cal.accepted + cal.dismissed == 8
    store.close()


def test_hierarchical_uses_shared_connection(tmp_path: Path) -> None:
    store = CalibrationStore(tmp_path / "cal.sqlite")
    store.record("r", "a", "c", True, event_id="e1", timestamp=1000.0)
    posterior = store.hierarchical("r", "a", "c", now=1000.0)
    assert posterior.accepted == 1.0
    assert posterior.dismissed == 0.0
    assert store._conn is not None
    store.close()

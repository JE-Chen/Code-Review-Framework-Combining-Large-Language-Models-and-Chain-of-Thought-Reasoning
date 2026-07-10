"""Feedback calibration and embedding-drift primitives."""

from __future__ import annotations

import contextlib
import hashlib
import math
import sqlite3
import threading
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BetaCalibration:
    accepted: float = 0
    dismissed: float = 0

    @property
    def mean(self):
        return (self.accepted + 1) / (self.accepted + self.dismissed + 2)

    def threshold(self, base=0.5):
        return min(0.95, max(0.05, base + (0.5 - self.mean) * 0.25))


def _f1_at(threshold, scored_labels):
    """F1 score treating scores >= threshold as positive predictions."""
    tp = sum(s >= threshold and y for s, y in scored_labels)
    fp = sum(s >= threshold and not y for s, y in scored_labels)
    fn = sum(s < threshold and y for s, y in scored_labels)
    denom = 2 * tp + fp + fn
    return 2 * tp / denom if denom else 0


def _f1(true_pos, false_pos, false_neg):
    """F1 from confusion counts; 0 when there is nothing to score."""
    denom = 2 * true_pos + false_pos + false_neg
    return 2 * true_pos / denom if denom else 0


def _consume_tied_scores(pairs, index, true_pos, false_pos):
    """Fold every pair tied at ``pairs[index]``'s score into tp/fp.

    Returns ``(threshold, next_index, true_pos, false_pos)`` so the sweep
    in :func:`select_threshold` can evaluate F1 once per unique score.
    """
    threshold = pairs[index][0]
    while index < len(pairs) and pairs[index][0] == threshold:
        true_pos += 1 if pairs[index][1] else 0
        false_pos += 0 if pairs[index][1] else 1
        index += 1
    return threshold, index, true_pos, false_pos


def select_threshold(scored_labels):
    """Score threshold maximising F1, smallest such threshold on ties.

    Single descending sweep over the sorted pairs: every item with a score
    equal to the candidate threshold joins the positive-prediction side, so
    tp/fp accumulate and fn derives from the positive total — O(n log n)
    versus the naive O(unique_scores x n) rescan (see ``_f1_at``, kept as
    the reference implementation for the regression test).
    """
    pairs = sorted(
        ((float(s), bool(y)) for s, y in scored_labels), reverse=True
    )
    total_positive = sum(1 for _, y in pairs if y)
    best_threshold, best_f1 = 0.0, -1.0
    true_pos = false_pos = index = 0
    while index < len(pairs):
        threshold, index, true_pos, false_pos = _consume_tied_scores(
            pairs, index, true_pos, false_pos
        )
        f1 = _f1(true_pos, false_pos, total_positive - true_pos)
        if f1 >= best_f1:
            best_threshold, best_f1 = threshold, f1
    return best_threshold


def cosine_drift(reference, current):
    dot = sum(a * b for a, b in zip(reference, current))
    a = math.sqrt(sum(x * x for x in reference))
    b = math.sqrt(sum(x * x for x in current))
    return 1 - dot / (a * b) if a and b else 1.0


_CALIBRATION_SCHEMA = (
    "CREATE TABLE IF NOT EXISTS feedback (repo TEXT, author TEXT, "
    "category TEXT, accepted INTEGER NOT NULL DEFAULT 0, "
    "dismissed INTEGER NOT NULL DEFAULT 0, "
    "PRIMARY KEY(repo,author,category))",
    "CREATE TABLE IF NOT EXISTS feedback_events (event_id TEXT "
    "PRIMARY KEY, repo TEXT NOT NULL, author TEXT NOT NULL, "
    "category TEXT NOT NULL, accepted INTEGER NOT NULL, "
    "ts REAL NOT NULL)",
)


class CalibrationStore:
    """Persistent repository/author/category feedback calibration."""

    def __init__(self, path):
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        self.path = str(target)
        self._lock = threading.Lock()
        self._conn: sqlite3.Connection | None = None
        # Create the database file and schema eagerly (as before) with a
        # short-lived bootstrap connection; the shared read/write
        # connection is opened lazily on first use.
        with contextlib.closing(sqlite3.connect(self.path)) as conn, conn:
            for statement in _CALIBRATION_SCHEMA:
                conn.execute(statement)

    def _connection(self) -> sqlite3.Connection:
        """The lazily-created shared connection; call with ``_lock`` held.

        ``check_same_thread=False`` lets one connection serve every
        caller thread; the lock serialises use because sqlite3 objects
        are shareable but not thread-safe.
        """
        if self._conn is None:
            self._conn = sqlite3.connect(self.path, check_same_thread=False)
        return self._conn

    def close(self) -> None:
        """Close the shared connection; the store reopens lazily if reused."""
        with self._lock:
            if self._conn is not None:
                self._conn.close()
                self._conn = None

    def record(
        self,
        repo: str,
        author: str,
        category: str,
        accepted: bool,
        *,
        event_id: str = "",
        timestamp: float | None = None,
    ) -> None:
        timestamp = time.time() if timestamp is None else timestamp
        event_id = (
            event_id
            or hashlib.sha256(
                f"{repo}:{author}:{category}:{accepted}:{timestamp}".encode()
            ).hexdigest()
        )
        with self._lock, self._connection() as conn:
            inserted = conn.execute(
                "INSERT OR IGNORE INTO feedback_events VALUES(?,?,?,?,?,?)",
                (event_id, repo, author, category, 1 if accepted else 0, timestamp),
            ).rowcount
            if not inserted:
                return
            conn.execute(
                "INSERT INTO feedback VALUES(?,?,?,?,?) "
                "ON CONFLICT(repo,author,category) DO UPDATE SET "
                "accepted=accepted+excluded.accepted,"
                "dismissed=dismissed+excluded.dismissed",
                (repo, author, category, 1 if accepted else 0, 0 if accepted else 1),
            )

    def calibration(self, repo: str, author: str, category: str) -> BetaCalibration:
        with self._lock:
            rows = self._connection().execute(
                "SELECT accepted,dismissed FROM feedback WHERE repo=? AND author IN (?, '') AND category IN (?, '')",
                (repo, author, category),
            ).fetchall()
        accepted = sum(row[0] for row in rows)
        dismissed = sum(row[1] for row in rows)
        return BetaCalibration(accepted, dismissed)

    def hierarchical(
        self,
        repo: str,
        author: str,
        category: str,
        *,
        half_life_days: float = 90,
        now: float | None = None,
    ) -> BetaCalibration:
        """Time-decayed posterior pooling exact and repository-level feedback."""
        now = time.time() if now is None else now
        with self._lock:
            rows = self._connection().execute(
                "SELECT author,category,accepted,ts FROM feedback_events WHERE repo=? AND author IN (?, '') AND category IN (?, '')",
                (repo, author, category),
            ).fetchall()
        yes = no = 0.0
        for row_author, row_category, accepted, ts in rows:
            age = max(0.0, now - ts)
            weight = 0.5 ** (age / (half_life_days * 86400))
            if row_author != author:
                weight *= 0.5
            if row_category != category:
                weight *= 0.5
            if accepted:
                yes += weight
            else:
                no += weight
        return BetaCalibration(yes, no)

    def decision(
        self,
        confidence: float | None,
        repo: str,
        author: str,
        category: str,
        *,
        minimum_samples: int = 10,
        half_life_days: float = 90,
    ) -> str:
        posterior = self.hierarchical(
            repo, author, category, half_life_days=half_life_days
        )
        if posterior.accepted + posterior.dismissed < minimum_samples:
            return "request-human-review"
        if confidence is None:
            return "request-human-review"
        return "publish" if confidence >= posterior.threshold() else "abstain"

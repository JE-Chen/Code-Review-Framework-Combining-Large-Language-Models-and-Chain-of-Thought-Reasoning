"""Feedback calibration and embedding-drift primitives."""

from __future__ import annotations
import math
import sqlite3
import time
from pathlib import Path
from dataclasses import dataclass


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


def select_threshold(scored_labels):
    best = (0.0, -1.0)
    for threshold in sorted({float(s) for s, _ in scored_labels}):
        f = _f1_at(threshold, scored_labels)
        if f > best[1]:
            best = (threshold, f)
    return best[0]


def cosine_drift(reference, current):
    dot = sum(a * b for a, b in zip(reference, current))
    a = math.sqrt(sum(x * x for x in reference))
    b = math.sqrt(sum(x * x for x in current))
    return 1 - dot / (a * b) if a and b else 1.0


class CalibrationStore:
    """Persistent repository/author/category feedback calibration."""

    def __init__(self, path):
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        self.path = str(target)
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS feedback (repo TEXT, author TEXT, "
                "category TEXT, accepted INTEGER NOT NULL DEFAULT 0, "
                "dismissed INTEGER NOT NULL DEFAULT 0, "
                "PRIMARY KEY(repo,author,category))"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS feedback_events (event_id TEXT "
                "PRIMARY KEY, repo TEXT NOT NULL, author TEXT NOT NULL, "
                "category TEXT NOT NULL, accepted INTEGER NOT NULL, "
                "ts REAL NOT NULL)"
            )

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
            or __import__("hashlib")
            .sha256(f"{repo}:{author}:{category}:{accepted}:{timestamp}".encode())
            .hexdigest()
        )
        with sqlite3.connect(self.path) as conn:
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
        with sqlite3.connect(self.path) as conn:
            rows = conn.execute(
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
        with sqlite3.connect(self.path) as conn:
            rows = conn.execute(
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

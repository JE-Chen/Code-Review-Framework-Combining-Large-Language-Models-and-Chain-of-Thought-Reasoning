"""Append-only telemetry of every inference call.

One SQLite row per ``generate()`` invocation. Records what we need to
answer the operator questions:

* How much have we spent this week, broken down by provider?
* p50 / p95 latency per backend? Where are we slow?
* Cache hit rate?
* Which backend is producing the most surviving findings per dollar?

Token counts come from the backend's ``last_usage()`` when available
(OpenAI / Anthropic include them in their response); we estimate from
char counts otherwise. The schema records both so post-hoc analysis can
filter on which call had real numbers.
"""

from __future__ import annotations

import contextlib
import itertools
import logging
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from statistics import median

from prthinker.pricing import estimate_cost

log = logging.getLogger(__name__)


_SCHEMA = """
CREATE TABLE IF NOT EXISTS calls (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp         REAL    NOT NULL,
    backend           TEXT    NOT NULL,
    model             TEXT    NOT NULL,
    prompt_tokens     INTEGER,
    completion_tokens INTEGER,
    tokens_estimated  INTEGER NOT NULL,
    latency_ms        REAL    NOT NULL,
    cost_usd          REAL,
    cache_hit         INTEGER NOT NULL,
    error             TEXT
);
CREATE INDEX IF NOT EXISTS idx_calls_ts ON calls (timestamp);
CREATE INDEX IF NOT EXISTS idx_calls_backend ON calls (backend);
"""


_WHERE_SINCE = "WHERE timestamp >= ?"


@dataclass
class CallRecord:
    backend: str
    model: str
    prompt_tokens: int | None
    completion_tokens: int | None
    tokens_estimated: bool
    latency_ms: float
    cache_hit: bool
    error: str | None = None

    def cost_usd(self) -> float | None:
        if self.prompt_tokens is None or self.completion_tokens is None:
            return None
        return estimate_cost(
            self.backend, self.model, self.prompt_tokens, self.completion_tokens
        )


@dataclass(frozen=True)
class BackendStats:
    backend: str
    model: str
    calls: int
    cache_hits: int
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float
    latency_p50_ms: float
    latency_p95_ms: float


class TelemetrySink:
    def __init__(self, path: Path) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(_SCHEMA)

    @contextlib.contextmanager
    def _connect(self):
        conn = sqlite3.connect(str(self._path), isolation_level=None)
        try:
            yield conn
        finally:
            conn.close()

    def record(self, call: CallRecord) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO calls (timestamp, backend, model, prompt_tokens, "
                "completion_tokens, tokens_estimated, latency_ms, cost_usd, "
                "cache_hit, error) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    time.time(),
                    call.backend,
                    call.model,
                    call.prompt_tokens,
                    call.completion_tokens,
                    1 if call.tokens_estimated else 0,
                    call.latency_ms,
                    call.cost_usd(),
                    1 if call.cache_hit else 0,
                    call.error,
                ),
            )

    def aggregate(self, since_seconds: float | None = None) -> list[BackendStats]:
        clause, params = self._time_filter(since_seconds)
        with self._connect() as conn:
            rows = self._metric_rows(conn, clause, params)
        return [
            _stats_from_rows(backend, model, [row[2:] for row in group])
            for (backend, model), group in itertools.groupby(
                rows, key=lambda row: (row[0], row[1])
            )
        ]

    @staticmethod
    def _time_filter(since_seconds: float | None) -> tuple[str, tuple]:
        """Build the optional ``timestamp >=`` WHERE clause and bound params."""
        if since_seconds is None:
            return "", ()
        return _WHERE_SINCE, (time.time() - since_seconds,)

    @staticmethod
    def _metric_rows(
        conn: sqlite3.Connection, clause: str, params: tuple
    ) -> list[tuple]:
        """Fetch every call's key + metric columns ordered by (backend, model)."""
        # nosec B608 — `clause` is one of two literal strings; the actual
        # user-supplied value goes through a bound parameter.
        return conn.execute(
            f"SELECT backend, model, prompt_tokens, completion_tokens, "  # nosec B608
            f"latency_ms, cost_usd, cache_hit FROM calls {clause} "
            f"ORDER BY backend, model",
            params,
        ).fetchall()


def _sum_int(rows: list[tuple], idx: int) -> int:
    """Sum one integer column, treating ``None`` cells as zero."""
    return sum(int(r[idx] or 0) for r in rows)


def _sum_float(rows: list[tuple], idx: int) -> float:
    """Sum one float column, treating ``None`` cells as zero."""
    return float(sum(float(r[idx] or 0.0) for r in rows))


def _stats_from_rows(
    backend: str, model: str, rows: list[tuple]
) -> BackendStats:
    """Fold one backend/model's metric rows into a ``BackendStats``."""
    latencies = sorted(r[2] for r in rows)
    return BackendStats(
        backend=backend,
        model=model,
        calls=len(rows),
        cache_hits=_sum_int(rows, 4),
        prompt_tokens=_sum_int(rows, 0),
        completion_tokens=_sum_int(rows, 1),
        cost_usd=_sum_float(rows, 3),
        latency_p50_ms=median(latencies),
        latency_p95_ms=_percentile(latencies, 0.95),
    )


def _percentile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        return 0.0
    if len(sorted_values) == 1:
        return float(sorted_values[0])
    idx = max(0, min(len(sorted_values) - 1, int(round(q * (len(sorted_values) - 1)))))
    return float(sorted_values[idx])


def estimate_tokens(text: str) -> int:
    """Crude char-based fallback when the backend gave no usage block.

    ~4 chars/token is the rule-of-thumb for English-heavy text and over-
    estimates for code-heavy text (which has more short tokens). Good
    enough for cost ballparks; not for billing.
    """
    return max(1, len(text) // 4)


__all__ = [
    "CallRecord",
    "BackendStats",
    "TelemetrySink",
    "estimate_tokens",
]

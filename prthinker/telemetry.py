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
        clause = ""
        params: tuple = ()
        if since_seconds is not None:
            clause = "WHERE timestamp >= ?"
            params = (time.time() - since_seconds,)

        out: list[BackendStats] = []
        with self._connect() as conn:
            # nosec B608 — `clause` is one of two literal strings above; the
            # actual user-supplied value goes through a bound parameter.
            keys = conn.execute(
                f"SELECT backend, model FROM calls {clause} "  # nosec B608
                f"GROUP BY backend, model ORDER BY backend, model",
                params,
            ).fetchall()
            for backend, model in keys:
                rows = conn.execute(
                    f"SELECT prompt_tokens, completion_tokens, latency_ms, "  # nosec B608
                    f"cost_usd, cache_hit FROM calls {clause}"
                    + (" AND " if clause else " WHERE ")
                    + "backend = ? AND model = ?",
                    (*params, backend, model),
                ).fetchall()
                if not rows:
                    continue
                latencies = [r[2] for r in rows]
                latencies.sort()
                out.append(
                    BackendStats(
                        backend=backend,
                        model=model,
                        calls=len(rows),
                        cache_hits=sum(int(r[4]) for r in rows),
                        prompt_tokens=sum(int(r[0] or 0) for r in rows),
                        completion_tokens=sum(int(r[1] or 0) for r in rows),
                        cost_usd=float(sum(float(r[3] or 0.0) for r in rows)),
                        latency_p50_ms=median(latencies),
                        latency_p95_ms=_percentile(latencies, 0.95),
                    )
                )
        return out


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

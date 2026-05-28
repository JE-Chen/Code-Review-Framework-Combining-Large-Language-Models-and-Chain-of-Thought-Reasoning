"""SQLite-backed prompt cache.

A single physical store keyed by the SHA-256 of
``backend_kind | model | prompt | max_new_tokens``. The key embeds every
input that can change the response, so prompt-template edits, model
swaps, and token-cap changes all naturally invalidate the cache (no
explicit ``bust`` operation required).

The cache is process-local: SQLite handles concurrent readers fine; we
open a fresh connection per call to avoid sharing a connection across
threads (which sqlite3 forbids by default). Throughput is fine for our
volume — at most a few thousand calls per PR.
"""

from __future__ import annotations

import contextlib
import hashlib
import logging
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path

log = logging.getLogger(__name__)


_SCHEMA = """
CREATE TABLE IF NOT EXISTS prompt_cache (
    key         TEXT PRIMARY KEY,
    response    TEXT NOT NULL,
    created_at  REAL NOT NULL,
    hits        INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_prompt_cache_created
    ON prompt_cache (created_at);
"""


def _hash_key(backend_kind: str, model: str, prompt: str, max_new_tokens: int) -> str:
    payload = f"{backend_kind}|{model}|{max_new_tokens}|{prompt}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class CacheStats:
    total_entries: int
    total_hits: int


class PromptCache:
    """SQLite store of prompt -> response with optional TTL eviction."""

    def __init__(self, path: Path, ttl_seconds: float | None = None) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._ttl_seconds = ttl_seconds
        with self._connect() as conn:
            conn.executescript(_SCHEMA)

    @contextlib.contextmanager
    def _connect(self):
        conn = sqlite3.connect(str(self._path), isolation_level=None)
        try:
            conn.execute("PRAGMA journal_mode=WAL")
            yield conn
        finally:
            conn.close()

    def get(
        self,
        backend_kind: str,
        model: str,
        prompt: str,
        max_new_tokens: int,
    ) -> str | None:
        key = _hash_key(backend_kind, model, prompt, max_new_tokens)
        now = time.time()
        with self._connect() as conn:
            row = conn.execute(
                "SELECT response, created_at FROM prompt_cache WHERE key = ?",
                (key,),
            ).fetchone()
            if row is None:
                return None
            response, created_at = row
            if self._ttl_seconds is not None and now - created_at > self._ttl_seconds:
                conn.execute("DELETE FROM prompt_cache WHERE key = ?", (key,))
                return None
            conn.execute(
                "UPDATE prompt_cache SET hits = hits + 1 WHERE key = ?",
                (key,),
            )
            return str(response)

    def put(
        self,
        backend_kind: str,
        model: str,
        prompt: str,
        max_new_tokens: int,
        response: str,
    ) -> None:
        key = _hash_key(backend_kind, model, prompt, max_new_tokens)
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO prompt_cache (key, response, created_at, hits)"
                " VALUES (?, ?, ?, 0)",
                (key, response, time.time()),
            )

    def stats(self) -> CacheStats:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT COUNT(*), COALESCE(SUM(hits), 0) FROM prompt_cache"
            ).fetchone()
        return CacheStats(total_entries=int(row[0]), total_hits=int(row[1]))

    def prune(self) -> int:
        """Drop entries older than TTL. Returns number removed."""
        if self._ttl_seconds is None:
            return 0
        cutoff = time.time() - self._ttl_seconds
        with self._connect() as conn:
            cur = conn.execute(
                "DELETE FROM prompt_cache WHERE created_at < ?",
                (cutoff,),
            )
            return cur.rowcount


__all__ = ["PromptCache", "CacheStats"]

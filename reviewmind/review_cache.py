"""Per-PR fingerprint store for force-push differential review.

Multiple pushes on the same PR usually leave 60 - 80% of the diff
unchanged. Re-running the model over the unchanged hunks is pure waste:
the prompt is the same so the output is the same (modulo non-zero
temperature). This module caches per-hunk findings keyed on a stable
content hash, so the next push only pays for what is genuinely new.

Schema (SQLite, content-hash key):

    CREATE TABLE findings_cache (
        pr_number       INTEGER NOT NULL,
        repo            TEXT    NOT NULL,
        file_path       TEXT    NOT NULL,
        hunk_sha256     TEXT    NOT NULL,
        findings_json   TEXT    NOT NULL,
        backend         TEXT    NOT NULL,
        model           TEXT    NOT NULL,
        ts              REAL    NOT NULL,
        PRIMARY KEY (pr_number, repo, file_path, hunk_sha256)
    );

Per ``paper_rule.md``'s no-fabrication rule, this module makes no claims
about how much cost / latency this saves in practice — only the
mechanism is shipped. Real measurements come from running with and
without the flag and comparing telemetry.
"""

from __future__ import annotations

import contextlib
import json
import logging
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path

from reviewmind.schemas import InlineFinding

log = logging.getLogger(__name__)


_SCHEMA = """
CREATE TABLE IF NOT EXISTS findings_cache (
    pr_number       INTEGER NOT NULL,
    repo            TEXT    NOT NULL,
    file_path       TEXT    NOT NULL,
    hunk_sha256     TEXT    NOT NULL,
    findings_json   TEXT    NOT NULL,
    backend         TEXT    NOT NULL,
    model           TEXT    NOT NULL,
    ts              REAL    NOT NULL,
    PRIMARY KEY (pr_number, repo, file_path, hunk_sha256)
);
CREATE INDEX IF NOT EXISTS idx_cache_pr
    ON findings_cache (pr_number, repo);
"""


@dataclass(frozen=True)
class CacheKey:
    """Composite key for one cached per-hunk review result."""

    pr_number: int
    repo: str
    file_path: str
    hunk_sha256: str


class ReviewCache:
    """SQLite-backed store of per-hunk findings.

    Per-PR scope means a different PR cannot accidentally read another
    PR's cached findings (the prompt context is PR-specific via dialogue
    + accepted-corpus examples, so cross-PR reuse would silently change
    behaviour).
    """

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

    def get(self, key: CacheKey) -> list[InlineFinding] | None:
        """Return the cached findings for ``key`` or ``None`` on miss."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT findings_json FROM findings_cache "
                "WHERE pr_number = ? AND repo = ? "
                "AND file_path = ? AND hunk_sha256 = ?",
                (key.pr_number, key.repo, key.file_path, key.hunk_sha256),
            ).fetchone()
        if row is None:
            return None
        return _decode_findings(row[0])

    def put(
        self,
        key: CacheKey,
        findings: list[InlineFinding],
        *,
        backend: str,
        model: str,
    ) -> None:
        payload = json.dumps(
            [f.model_dump(exclude_none=True) for f in findings],
            ensure_ascii=False,
        )
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO findings_cache "
                "(pr_number, repo, file_path, hunk_sha256, "
                " findings_json, backend, model, ts) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    key.pr_number, key.repo, key.file_path, key.hunk_sha256,
                    payload, backend, model, time.time(),
                ),
            )

    def evict_pr(self, pr_number: int, repo: str) -> int:
        """Drop all cached findings for one PR. Returns rows deleted.

        Called when the PR is merged or closed — long-term cache
        retention is not the point of this store.
        """
        with self._connect() as conn:
            cur = conn.execute(
                "DELETE FROM findings_cache "
                "WHERE pr_number = ? AND repo = ?",
                (pr_number, repo),
            )
            return cur.rowcount or 0


def _decode_findings(payload: str) -> list[InlineFinding]:
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        log.warning("findings_cache row corrupted: %s", exc)
        return []
    if not isinstance(data, list):
        return []
    out: list[InlineFinding] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        try:
            out.append(InlineFinding.model_validate(item))
        except Exception as exc:  # pydantic ValidationError or similar
            log.debug("Dropped corrupted cached finding: %s", exc)
    return out


__all__ = ["CacheKey", "ReviewCache"]

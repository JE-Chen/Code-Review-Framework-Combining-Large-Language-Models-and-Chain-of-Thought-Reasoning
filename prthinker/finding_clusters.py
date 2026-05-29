"""Cross-PR finding clustering — self-discovered repo rules.

Every inline finding the framework emits is fingerprinted (an
embedding of the normalised comment text) and persisted to a small
SQLite store. On demand the store can be clustered to surface
families of N+ semantically-similar findings, which become candidate
project-level rules: "you've raised this finding N times — would you
like to add it as a permanent rule?"

The vector backend is pluggable but defaults to pure-NumPy brute
force, which keeps the runner profile dependency-thin and is fast
enough for the expected single-repo scale (< 10^5 findings).

Per ``paper_rule.md``'s no-fabrication rule, this module ships the
mechanism only — no claim about how often discovered rules are
actually useful.
"""

from __future__ import annotations

import contextlib
import logging
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np

log = logging.getLogger(__name__)


_SCHEMA = """
CREATE TABLE IF NOT EXISTS findings_index (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    pr_number     INTEGER NOT NULL,
    repo          TEXT    NOT NULL,
    file_path     TEXT    NOT NULL,
    line          INTEGER NOT NULL,
    comment       TEXT    NOT NULL,
    norm_comment  TEXT    NOT NULL,
    embedding     BLOB    NOT NULL,
    ts            REAL    NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_findings_repo
    ON findings_index (repo, pr_number);
CREATE INDEX IF NOT EXISTS idx_findings_norm
    ON findings_index (norm_comment);
"""


@dataclass(frozen=True)
class FindingFingerprint:
    """One persisted finding fingerprint."""

    pr_number: int
    repo: str
    file_path: str
    line: int
    comment: str
    norm_comment: str
    embedding: "np.ndarray"
    ts: float = 0.0


@dataclass(frozen=True)
class FindingCluster:
    """A cluster of semantically-similar findings.

    ``representative`` is the comment from the most-recent member,
    used as the candidate-rule's human-readable label.
    """

    members: list[FindingFingerprint]
    representative: str
    size: int


def _normalise(comment: str) -> str:
    """Same normalisation as :mod:`prthinker.reproducibility` so the
    two layers agree on what "the same comment" means.
    """
    import re
    tokens = re.findall(r"\w+", comment.lower(), flags=re.UNICODE)
    return " ".join(tokens)


class FindingClusterStore:
    """SQLite store of finding fingerprints."""

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

    def add(
        self,
        *,
        pr_number: int,
        repo: str,
        file_path: str,
        line: int,
        comment: str,
        embedding: "np.ndarray",
    ) -> None:
        """Append one fingerprint. No dedup — duplicates *are* the
        signal we're after.
        """
        norm = _normalise(comment)
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO findings_index "
                "(pr_number, repo, file_path, line, comment, "
                " norm_comment, embedding, ts) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    pr_number, repo, file_path, line, comment, norm,
                    embedding.astype("float32").tobytes(),
                    time.time(),
                ),
            )

    def __len__(self) -> int:
        with self._connect() as conn:
            return int(conn.execute(
                "SELECT COUNT(*) FROM findings_index"
            ).fetchone()[0])

    def load(self, *, repo: str | None = None) -> list[FindingFingerprint]:
        """Load every fingerprint, optionally restricted to one repo."""
        import numpy as np
        if repo is not None:
            query = (
                "SELECT pr_number, repo, file_path, line, comment, "
                "norm_comment, embedding, ts FROM findings_index "
                "WHERE repo = ? ORDER BY ts DESC"
            )
            args: tuple = (repo,)
        else:
            query = (
                "SELECT pr_number, repo, file_path, line, comment, "
                "norm_comment, embedding, ts FROM findings_index "
                "ORDER BY ts DESC"
            )
            args = ()
        with self._connect() as conn:
            rows = conn.execute(query, args).fetchall()
        out: list[FindingFingerprint] = []
        for r in rows:
            emb = np.frombuffer(r[6], dtype="float32")
            out.append(FindingFingerprint(
                pr_number=int(r[0]), repo=str(r[1]),
                file_path=str(r[2]), line=int(r[3]),
                comment=str(r[4]), norm_comment=str(r[5]),
                embedding=emb, ts=float(r[7]),
            ))
        return out


def _cosine(a: "np.ndarray", b: "np.ndarray") -> float:
    import numpy as np
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def greedy_cluster(
    fingerprints: list[FindingFingerprint],
    *,
    similarity_threshold: float = 0.85,
    min_cluster_size: int = 5,
) -> list[FindingCluster]:
    """Greedy single-link clustering by cosine similarity.

    O(N²) in the number of fingerprints. Fine for the expected single
    -repo scale (10³–10⁵ findings); upgrade to FAISS / sqlite-vec if
    your repo accumulates beyond that.
    """
    if not fingerprints:
        return []
    centroids: list[list[FindingFingerprint]] = []
    for fp in fingerprints:
        placed = False
        for group in centroids:
            sim = _cosine(group[0].embedding, fp.embedding)
            if sim >= similarity_threshold:
                group.append(fp)
                placed = True
                break
        if not placed:
            centroids.append([fp])

    out: list[FindingCluster] = []
    for group in centroids:
        if len(group) < min_cluster_size:
            continue
        # Most recent first — group[0] is newest because we load
        # ``ORDER BY ts DESC``.
        out.append(FindingCluster(
            members=group, representative=group[0].comment, size=len(group),
        ))
    out.sort(key=lambda c: -c.size)
    return out


def format_clusters_block(clusters: Iterable[FindingCluster]) -> str:
    """Render top-K cluster summaries as PR-comment markdown."""
    items = list(clusters)
    if not items:
        return ""
    out = [
        "### Recurring findings (candidate project rules)",
        "",
        "These finding patterns have recurred across PRs in this",
        "repo — consider adding them to your `--rules-dir` as",
        "permanent project rules so the reviewer raises them",
        "first-class next time.",
        "",
        "| Count | Files touched | Representative comment |",
        "| ---: | --- | --- |",
    ]
    for c in items:
        files = sorted({m.file_path for m in c.members})
        files_display = ", ".join(f"`{p}`" for p in files[:3])
        if len(files) > 3:
            files_display += f", +{len(files) - 3} more"
        rep = c.representative.replace("|", "\\|").strip()
        if len(rep) > 100:
            rep = rep[:99].rstrip() + "..."
        out.append(f"| {c.size} | {files_display} | {rep} |")
    out += ["", ""]
    return "\n".join(out)


__all__ = [
    "FindingCluster",
    "FindingClusterStore",
    "FindingFingerprint",
    "format_clusters_block",
    "greedy_cluster",
]

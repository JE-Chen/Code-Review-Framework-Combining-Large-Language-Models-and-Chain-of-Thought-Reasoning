"""Persisted store of dismissed findings + similarity-based filter.

A *dismissed example* is a past inline finding that the PR author rejected
(thumbs-down reaction, an explicit "false positive" / "wontfix" reply, or
the comment was unresolved when the PR merged).

Storing them lets the next review skip producing the same noise. The store
is a JSON-Lines file — easy to inspect, diff in git, and edit by hand.

At review time the filter embeds each candidate finding's comment, compares
it to every stored dismissed example's comment, and drops the finding when
max cosine similarity ≥ `threshold`. Embedding goes through the same
`codes.util.faiss_util.get_embedding` used by RAG, so similarity space is
consistent.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Iterable

from prthinker.corpora_base import JsonlCorpusStore, embed_store_comments
from prthinker.schemas import InlineFinding

if TYPE_CHECKING:
    import numpy as np

log = logging.getLogger(__name__)


@dataclass
class DismissedExample:
    path: str
    comment: str
    reason: str
    diff_snippet: str = ""

    def to_jsonl(self) -> str:
        return json.dumps(
            {
                "path": self.path,
                "comment": self.comment,
                "reason": self.reason,
                "diff_snippet": self.diff_snippet,
            },
            ensure_ascii=False,
        )

    @classmethod
    def from_dict(cls, data: dict) -> "DismissedExample":
        return cls(
            path=str(data.get("path", "")),
            comment=str(data.get("comment", "")),
            reason=str(data.get("reason", "")),
            diff_snippet=str(data.get("diff_snippet", "")),
        )


class DismissedExamplesStore(JsonlCorpusStore[DismissedExample]):
    """JSONL-backed store of dismissed inline findings."""

    def __init__(self, path: Path) -> None:
        super().__init__(path, DismissedExample.from_dict)

    def _on_malformed(self, raw: str) -> None:
        del raw  # the path, not the payload, is what the operator needs
        log.warning("skipping malformed line in %s", self._path)

    def _on_loaded(self) -> None:
        log.info("Loaded %d dismissed example(s) from %s", len(self), self._path)


class DismissedFilter:
    """Drops candidate findings that look like previously dismissed ones."""

    def __init__(
        self,
        store: DismissedExamplesStore,
        threshold: float = 0.85,
        path_scoped: bool = False,
    ) -> None:
        """`path_scoped=True` only compares against examples on the same file."""
        self._store = store
        self._threshold = threshold
        self._path_scoped = path_scoped
        self._example_embeddings: list[tuple[DismissedExample, np.ndarray]] = []

    def _ensure_embeddings(self) -> None:
        if self._example_embeddings or len(self._store) == 0:
            return
        self._example_embeddings = embed_store_comments(self._store)

    def _best_match(
        self, finding: InlineFinding, candidate: "np.ndarray"
    ) -> tuple[float, str]:
        """Return the max cosine similarity and reason against stored examples."""
        import numpy as np

        best_score = 0.0
        best_reason = ""
        for ex, emb in self._example_embeddings:
            if self._path_scoped and ex.path != finding.path:
                continue
            score = float(np.dot(candidate, emb))
            if score > best_score:
                best_score = score
                best_reason = ex.reason
        return best_score, best_reason

    def filter(self, findings: Iterable[InlineFinding]) -> list[InlineFinding]:
        items = list(findings)
        if not items or len(self._store) == 0:
            return items

        self._ensure_embeddings()
        # Lazy import keeps the runner profile (httpx + pydantic only)
        # importable on machines without numpy / faiss.
        from codes.util.faiss_util import get_embedding

        kept: list[InlineFinding] = []
        for f in items:
            best_score, best_reason = self._best_match(f, get_embedding(f.comment))
            if best_score >= self._threshold:
                log.info(
                    "Dropping finding on %s:%d (sim=%.3f, reason=%s)",
                    f.path, f.line, best_score, best_reason or "n/a",
                )
                continue
            kept.append(f)
        return kept


__all__ = [
    "DismissedExample",
    "DismissedExamplesStore",
    "DismissedFilter",
]

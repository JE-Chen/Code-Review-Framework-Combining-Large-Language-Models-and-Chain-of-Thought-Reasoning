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
from typing import Iterable

import numpy as np

from reviewmind.schemas import InlineFinding

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


class DismissedExamplesStore:
    """JSONL-backed store of dismissed inline findings."""

    def __init__(self, path: Path) -> None:
        self._path = Path(path)
        self._examples: list[DismissedExample] = []
        if self._path.exists():
            self._load()

    def _load(self) -> None:
        for raw in self._path.read_text(encoding="utf-8").splitlines():
            raw = raw.strip()
            if not raw:
                continue
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                log.warning("skipping malformed line in %s", self._path)
                continue
            self._examples.append(DismissedExample.from_dict(data))
        log.info("Loaded %d dismissed example(s) from %s",
                 len(self._examples), self._path)

    def __len__(self) -> int:
        return len(self._examples)

    def __iter__(self):
        return iter(self._examples)

    def append(self, example: DismissedExample) -> None:
        self._examples.append(example)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as fh:
            fh.write(example.to_jsonl() + "\n")


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
        # Lazy import — keeps this module usable in tests without faiss.
        from codes.util.faiss_util import get_embedding

        self._example_embeddings = [
            (ex, get_embedding(ex.comment)) for ex in self._store
        ]

    def filter(self, findings: Iterable[InlineFinding]) -> list[InlineFinding]:
        items = list(findings)
        if not items or len(self._store) == 0:
            return items

        self._ensure_embeddings()
        from codes.util.faiss_util import get_embedding

        kept: list[InlineFinding] = []
        for f in items:
            candidate = get_embedding(f.comment)
            best_score = 0.0
            best_reason = ""
            for ex, emb in self._example_embeddings:
                if self._path_scoped and ex.path != f.path:
                    continue
                score = float(np.dot(candidate, emb))
                if score > best_score:
                    best_score = score
                    best_reason = ex.reason

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

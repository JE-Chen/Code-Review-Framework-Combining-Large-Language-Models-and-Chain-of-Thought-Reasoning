"""Positive-example store: past suggestion comments that PR authors applied.

Symmetric to ``prthinker.dismissed`` but with opposite intent — instead
of filtering out repeats, the in-context pipeline injects the top-K most
similar accepted examples into the inline-findings prompt as exemplars.

Store shape (one JSON object per line)::

    {
      "path":       "<file path of the original comment>",
      "comment":    "<the original advisory comment body>",
      "suggestion": "<the replacement code block that got applied>",
      "pr_number":  <int, where it was applied>
    }
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    import numpy as np

log = logging.getLogger(__name__)


@dataclass
class AcceptedExample:
    path: str
    comment: str
    suggestion: str
    pr_number: int = 0

    def to_jsonl(self) -> str:
        return json.dumps(
            {
                "path": self.path,
                "comment": self.comment,
                "suggestion": self.suggestion,
                "pr_number": self.pr_number,
            },
            ensure_ascii=False,
        )

    @classmethod
    def from_dict(cls, data: dict) -> "AcceptedExample":
        return cls(
            path=str(data.get("path", "")),
            comment=str(data.get("comment", "")),
            suggestion=str(data.get("suggestion", "")),
            pr_number=int(data.get("pr_number", 0) or 0),
        )


class AcceptedExamplesStore:
    """JSONL-backed store of accepted suggestion examples."""

    def __init__(self, path: Path) -> None:
        self._path = Path(path)
        self._examples: list[AcceptedExample] = []
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
                continue
            self._examples.append(AcceptedExample.from_dict(data))

    def __len__(self) -> int:
        return len(self._examples)

    def __iter__(self):
        return iter(self._examples)

    def append(self, example: AcceptedExample) -> None:
        self._examples.append(example)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as fh:
            fh.write(example.to_jsonl() + "\n")


class AcceptedExamplesRetriever:
    """Returns the top-K most similar accepted examples for a given diff."""

    def __init__(
        self,
        store: AcceptedExamplesStore,
        k: int = 3,
        threshold: float = 0.6,
        path_scoped: bool = False,
    ) -> None:
        self._store = store
        self._k = k
        self._threshold = threshold
        self._path_scoped = path_scoped
        self._embeddings: list[tuple[AcceptedExample, np.ndarray]] = []

    def _ensure_embeddings(self) -> None:
        if self._embeddings or len(self._store) == 0:
            return
        from codes.util.faiss_util import get_embedding

        # Embed on `comment` so similarity reflects advisory content, not
        # the suggestion text (which can be repo-specific code).
        self._embeddings = [
            (ex, get_embedding(ex.comment)) for ex in self._store
        ]

    def top_k(self, query: str, path: str | None = None) -> list[AcceptedExample]:
        if len(self._store) == 0:
            return []
        self._ensure_embeddings()
        # Lazy imports keep the runner profile (httpx + pydantic only)
        # importable on machines without numpy / faiss.
        import numpy as np
        from codes.util.faiss_util import get_embedding

        q = get_embedding(query)
        scored: list[tuple[float, AcceptedExample]] = []
        for ex, emb in self._embeddings:
            if self._path_scoped and path is not None and ex.path != path:
                continue
            score = float(np.dot(q, emb))
            if score >= self._threshold:
                scored.append((score, ex))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [ex for _score, ex in scored[: self._k]]


def format_examples_block(examples: Iterable[AcceptedExample]) -> str:
    """Render examples as a prompt-ready few-shot block. Empty list → ''."""
    items = list(examples)
    if not items:
        return ""

    lines = [
        "## Examples of past advice that was accepted in this repo",
        "",
        "Use these as guidance for the style and granularity of your findings.",
        "",
    ]
    for i, ex in enumerate(items, start=1):
        lines += [
            f"### Example {i} — `{ex.path}`",
            "",
            "Comment:",
            "",
            "> " + ex.comment.strip().replace("\n", "\n> "),
            "",
            "Suggested replacement that was applied:",
            "",
            "```",
            ex.suggestion.rstrip("\n"),
            "```",
            "",
        ]
    return "\n".join(lines)


__all__ = [
    "AcceptedExample",
    "AcceptedExamplesStore",
    "AcceptedExamplesRetriever",
    "format_examples_block",
]

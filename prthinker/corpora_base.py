"""Shared JSONL persistence for the append-only corpora stores.

``dismissed.jsonl`` / ``accepted.jsonl`` / ``lessons.jsonl`` share one
storage shape: a JSON object per line, loaded eagerly into an in-memory
cache on construction and appended-to afterwards. The corpora are
APPEND-ONLY — corrections are written as new rows; historical rows are
never rewritten. This module holds that shared skeleton so each store
only supplies its row dataclass and its malformed-row logging policy.

Runner-safe: ``json`` + ``pathlib`` only. The embedding helper keeps its
faiss import lazy so the runner profile (httpx + pydantic + PyYAML)
never pulls numpy / faiss at module load.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Callable,
    Generic,
    Iterable,
    Iterator,
    Protocol,
    TypeVar,
)

if TYPE_CHECKING:
    import numpy as np

log = logging.getLogger(__name__)


class JsonlRow(Protocol):
    """A corpus row that serialises itself to one JSONL line."""

    def to_jsonl(self) -> str:
        """Serialise this row to a single JSONL line."""
        ...


class CommentRow(Protocol):
    """A corpus row carrying an advisory ``comment`` used for retrieval."""

    comment: str


RowT = TypeVar("RowT", bound=JsonlRow)
CommentRowT = TypeVar("CommentRowT", bound=CommentRow)


class JsonlCorpusStore(Generic[RowT]):
    """Append-only JSONL store; rows are built by a ``from_dict`` factory.

    The file is the authoritative state; the in-memory list is a cache
    reloaded on construction. Cross-process appends are safe because
    each row is one ``\\n``-terminated JSON object.
    """

    def __init__(self, path: Path, row_factory: Callable[[dict], RowT]) -> None:
        self._path = Path(path)
        self._row_factory = row_factory
        self._rows: list[RowT] = []
        if self._path.exists():
            self._load()

    def _load(self) -> None:
        with self._path.open(encoding="utf-8") as fh:
            for raw in fh:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    self._on_malformed(raw)
                    continue
                self._rows.append(self._row_factory(data))
        self._on_loaded()

    def _on_malformed(self, raw: str) -> None:
        """Hook: one line failed to JSON-parse. Default skips silently."""

    def _on_loaded(self) -> None:
        """Hook: called once after a load completes. Default is a no-op."""

    def __len__(self) -> int:
        return len(self._rows)

    def __iter__(self) -> Iterator[RowT]:
        return iter(self._rows)

    def append(self, row: RowT) -> None:
        self._rows.append(row)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as fh:
            fh.write(row.to_jsonl() + "\n")


def embed_store_comments(
    rows: Iterable[CommentRowT],
) -> list[tuple[CommentRowT, "np.ndarray"]]:
    """Embed each row's ``comment`` for cosine-similarity retrieval.

    Embedding targets the advisory ``comment`` text — not the suggestion
    or diff snippet, which can be repo-specific code — so similarity
    reflects advisory content. The faiss import stays lazy: the runner
    profile must import this module without numpy / faiss installed.
    """
    from codes.util.faiss_util import get_embedding

    return [(row, get_embedding(row.comment)) for row in rows]


__all__ = [
    "CommentRow",
    "JsonlCorpusStore",
    "JsonlRow",
    "embed_store_comments",
]

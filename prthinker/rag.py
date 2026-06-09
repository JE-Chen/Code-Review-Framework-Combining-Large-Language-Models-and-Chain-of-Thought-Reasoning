"""RAG retrieval — Repository pattern.

Three implementations behind the same interface:
- NoOpRetriever      - skip RAG entirely.
- FaissRAGRetriever  - in-process FAISS via codes.util.faiss_util.
- RemoteRAGRetriever - HTTP call to a remote `/rag` endpoint.

All FAISS calls in the package go through `FaissRAGRetriever`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import httpx

from prthinker.schemas import RagRequest, RagResponse


class RAGRetriever(ABC):
    @abstractmethod
    def retrieve(self, prompt: str) -> list[str]:
        ...


class NoOpRetriever(RAGRetriever):
    """Returns no rules — for runners without the embedding model installed."""

    def retrieve(self, prompt: str) -> list[str]:
        return []


class FaissRAGRetriever(RAGRetriever):
    """Wraps `codes.util.faiss_util.search_docs`.

    The FAISS index is built once at module import time inside `faiss_util`;
    instantiating this class is cheap after the first import.
    """

    def __init__(self, threshold: float = 0.7) -> None:
        # Import the module (not the symbol) so its import-time side effect
        # — building the FAISS index once — runs eagerly at construction.
        # Deferred so callers that pick NoOpRetriever do not pay the
        # embedding-model load cost.
        import codes.util.faiss_util  # noqa: F401

        self._threshold = threshold

    def retrieve(self, prompt: str) -> list[str]:
        from codes.util.faiss_util import search_docs

        docs, _scored = search_docs(query=prompt, threshold=self._threshold)
        return docs


class RemoteRAGRetriever(RAGRetriever):
    """Calls the FastAPI server's `/rag` endpoint — no local embedding model."""

    def __init__(
        self,
        url: str,
        threshold: float = 0.7,
        k: int = 15,
        timeout_seconds: float = 60.0,
        api_key: str | None = None,
    ) -> None:
        if not url:
            raise ValueError("RemoteRAGRetriever requires a base url")
        headers: dict[str, str] = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self._client = httpx.Client(
            base_url=url.rstrip("/"),
            timeout=timeout_seconds,
            headers=headers,
        )
        self._threshold = threshold
        self._k = k

    def retrieve(self, prompt: str) -> list[str]:
        body = RagRequest(query=prompt, threshold=self._threshold, k=self._k)
        response = self._client.post("/rag", json=body.model_dump())
        response.raise_for_status()
        return RagResponse.model_validate_json(response.text).docs

    def close(self) -> None:
        self._client.close()

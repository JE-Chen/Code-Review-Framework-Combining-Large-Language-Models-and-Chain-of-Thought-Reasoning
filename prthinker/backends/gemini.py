"""Google Generative Language (Gemini) REST backend.

Speaks the Generative Language v1beta REST shape::

    POST {base_url}/models/{model}:generateContent?key={api_key}
    {"contents": [{"parts": [{"text": prompt}]}],
     "generationConfig": {"maxOutputTokens": n}}

The response text lives at ``candidates[0].content.parts[0].text``. The
streaming endpoint (``:streamGenerateContent``) returns a JSON array of
``generateContent``-shaped chunks; we concatenate per-chunk part text and
yield each chunk's text as it is decoded.

Model identifiers follow Google's naming, e.g.::

    gemini-2.5-pro
    gemini-2.5-flash
    gemini-1.5-pro

The HTTP client is reused across calls to keep the connection pool warm.
"""

from __future__ import annotations

from typing import Iterator

import httpx

from prthinker.backends.base import InferenceBackend, Usage

_DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
_GENERATE_METHOD = "generateContent"
_STREAM_METHOD = "streamGenerateContent"
_API_KEY_PARAM = "key"


class GeminiBackend(InferenceBackend):
    """Generative Language REST backend (prompt-in / text-out)."""

    def __init__(
        self,
        *,
        model: str,
        api_key: str,
        base_url: str = _DEFAULT_BASE_URL,
        timeout_seconds: float = 600.0,
    ) -> None:
        if not model:
            raise ValueError("GeminiBackend.model is required")
        if not api_key:
            raise ValueError("GeminiBackend.api_key is required")
        if not base_url:
            raise ValueError("GeminiBackend.base_url is required")
        if timeout_seconds <= 0:
            raise ValueError("GeminiBackend.timeout_seconds must be positive")
        self._model = model
        self._api_key = api_key
        self._last_usage: Usage | None = None
        self._client = httpx.Client(
            base_url=base_url.rstrip("/"),
            timeout=timeout_seconds,
            headers={"Content-Type": "application/json"},
        )

    def backend_kind(self) -> str:
        return "gemini"

    def model_name(self) -> str:
        return self._model

    def last_usage(self) -> Usage | None:
        return self._last_usage

    def _endpoint(self, method: str) -> str:
        """Build the ``/models/{model}:{method}`` request path."""
        return f"/models/{self._model}:{method}"

    def _payload(self, prompt: str, max_new_tokens: int) -> dict:
        """Assemble the ``generateContent`` request body."""
        return {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": max_new_tokens},
        }

    @staticmethod
    def _text_from_candidate(body: dict) -> str:
        """Join the part text of the first candidate of a response body."""
        try:
            parts = body["candidates"][0]["content"]["parts"]
            chunks = [p["text"] for p in parts if "text" in p]
            return "".join(str(c) for c in chunks)
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(
                f"Unexpected Gemini response shape: {body!r}"
            ) from exc

    @staticmethod
    def _stream_chunk_text(chunk: dict) -> str:
        """Return a stream chunk's text, or empty when it carries no candidate.

        Stream responses may include a trailing usage-only chunk with no
        ``candidates``; that is not an error, so it yields no text.
        """
        if not chunk.get("candidates"):
            return ""
        return GeminiBackend._text_from_candidate(chunk)

    def _capture_usage(self, body: dict) -> None:
        """Record ``last_usage`` from a ``usageMetadata`` block, if present."""
        usage = body.get("usageMetadata") or {}
        prompt_tokens = usage.get("promptTokenCount")
        completion_tokens = usage.get("candidatesTokenCount")
        if prompt_tokens is not None and completion_tokens is not None:
            self._last_usage = Usage(
                prompt_tokens=int(prompt_tokens),
                completion_tokens=int(completion_tokens),
            )

    def generate(
        self,
        prompt: str,
        max_new_tokens: int,
        *,
        cancel_event: "object | None" = None,
    ) -> str:
        """Generate text for ``prompt`` via a single REST call."""
        # Remote network call; mid-stream cancellation not implemented.
        del cancel_event
        self._last_usage = None
        response = self._client.post(
            self._endpoint(_GENERATE_METHOD),
            params={_API_KEY_PARAM: self._api_key},
            json=self._payload(prompt, max_new_tokens),
        )
        response.raise_for_status()
        body = response.json()
        text = self._text_from_candidate(body)
        self._capture_usage(body)
        return text

    def stream_generate(
        self, prompt: str, max_new_tokens: int
    ) -> Iterator[str]:
        """Yield per-chunk text from the ``streamGenerateContent`` endpoint.

        The endpoint returns a JSON array of ``generateContent``-shaped
        chunks. We decode the whole array, capture usage from the final
        chunk that carries it, and yield each chunk's non-empty text.
        """
        self._last_usage = None
        response = self._client.post(
            self._endpoint(_STREAM_METHOD),
            params={_API_KEY_PARAM: self._api_key},
            json=self._payload(prompt, max_new_tokens),
        )
        response.raise_for_status()
        chunks = response.json()
        if not isinstance(chunks, list):
            chunks = [chunks]
        for chunk in chunks:
            self._capture_usage(chunk)
            text = self._stream_chunk_text(chunk)
            if text:
                yield text

    def close(self) -> None:
        self._client.close()

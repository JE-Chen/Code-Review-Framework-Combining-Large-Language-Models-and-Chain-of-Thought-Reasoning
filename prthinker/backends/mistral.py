"""Mistral Chat Completions backend.

Talks to Mistral's OpenAI-shaped ``POST /chat/completions`` endpoint with
``Authorization: Bearer {api_key}``. Model identifiers follow Mistral's
naming, e.g.::

    mistral-large-latest
    mistral-small-latest
    codestral-latest

Streaming uses SSE ``data:`` lines carrying ``choices[0].delta.content``
deltas, terminated by a ``[DONE]`` sentinel. The HTTP client is reused
across calls to keep the connection pool warm.
"""

from __future__ import annotations

import json
from typing import Iterator

import httpx

from prthinker.backends.base import InferenceBackend, Usage

DEFAULT_BASE_URL = "https://api.mistral.ai/v1"
CHAT_COMPLETIONS_PATH = "/chat/completions"
SSE_DATA_PREFIX = "data:"
SSE_DONE_SENTINEL = "[DONE]"
_BACKEND_KIND = "mistral"


class MistralBackend(InferenceBackend):
    """OpenAI-shaped Mistral Chat Completions inference backend."""

    def __init__(
        self,
        *,
        model: str,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout_seconds: float = 600.0,
    ) -> None:
        if not model:
            raise ValueError("MistralBackend.model is required")
        if not api_key:
            raise ValueError("MistralBackend.api_key is required")
        if not base_url:
            raise ValueError("MistralBackend.base_url is required")
        if timeout_seconds <= 0:
            raise ValueError("MistralBackend.timeout_seconds must be positive")
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._last_usage: Usage | None = None
        self._client = httpx.Client(
            base_url=self._base_url,
            timeout=timeout_seconds,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )

    def backend_kind(self) -> str:
        return _BACKEND_KIND

    def model_name(self) -> str:
        return self._model

    def last_usage(self) -> Usage | None:
        return self._last_usage

    def generate(
        self,
        prompt: str,
        max_new_tokens: int,
        *,
        cancel_event: "object | None" = None,
    ) -> str:
        # Remote network call; mid-stream cancellation not implemented.
        del cancel_event
        self._last_usage = None
        payload = {
            "model": self._model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_new_tokens,
        }
        response = self._client.post(CHAT_COMPLETIONS_PATH, json=payload)
        response.raise_for_status()
        body = response.json()
        try:
            text = str(body["choices"][0]["message"]["content"])
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(
                f"Unexpected Mistral response shape: {body!r}"
            ) from exc

        self._capture_usage(body.get("usage") or {})
        return text

    def _capture_usage(self, usage: dict) -> None:
        """Populate ``last_usage`` when a full usage block is present."""
        prompt_tokens = usage.get("prompt_tokens")
        completion_tokens = usage.get("completion_tokens")
        if prompt_tokens is not None and completion_tokens is not None:
            self._last_usage = Usage(
                prompt_tokens=int(prompt_tokens),
                completion_tokens=int(completion_tokens),
            )

    @staticmethod
    def _sse_payload(line: str) -> str | None:
        """Strip the ``data:`` prefix from one SSE line, or None if not data."""
        if not line or not line.startswith(SSE_DATA_PREFIX):
            return None
        return line[len(SSE_DATA_PREFIX) :].strip()

    @staticmethod
    def _decode_sse_event(data: str) -> dict | None:
        """Parse one SSE payload as JSON, returning None on malformed data."""
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return None

    @staticmethod
    def _extract_delta_content(event: dict) -> str | None:
        """Return the content delta of an event, or None when absent / empty."""
        choices = event.get("choices") or []
        if not choices:
            return None
        delta = (choices[0] or {}).get("delta") or {}
        chunk = delta.get("content")
        return str(chunk) if chunk else None

    def stream_generate(
        self, prompt: str, max_new_tokens: int
    ) -> Iterator[str]:
        """Native SSE streaming via ``stream: true``.

        Yields ``choices[0].delta.content`` deltas until the ``[DONE]``
        sentinel arrives. A final chunk may carry a ``usage`` block, which
        is captured for ``last_usage`` like the non-streaming path.
        """
        self._last_usage = None
        payload = {
            "model": self._model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_new_tokens,
            "stream": True,
        }
        with self._client.stream(
            "POST", CHAT_COMPLETIONS_PATH, json=payload
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                data = self._sse_payload(line)
                if data is None:
                    continue
                if data == SSE_DONE_SENTINEL:
                    break
                event = self._decode_sse_event(data)
                if event is None:
                    continue
                self._capture_usage(event.get("usage") or {})
                chunk = self._extract_delta_content(event)
                if chunk is not None:
                    yield chunk

    def close(self) -> None:
        self._client.close()

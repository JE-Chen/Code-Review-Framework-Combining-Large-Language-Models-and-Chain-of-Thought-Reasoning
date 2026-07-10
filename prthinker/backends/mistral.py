"""Mistral Chat Completions backend.

Talks to Mistral's OpenAI-shaped ``POST /chat/completions`` endpoint with
``Authorization: Bearer {api_key}``. Model identifiers follow Mistral's
naming, e.g.::

    mistral-large-latest
    mistral-small-latest
    codestral-latest

Because the API is OpenAI-shaped, the response / SSE parsing delegates
to the shared helpers in :mod:`prthinker.backends.openai_compat`
(``extract_chat_text`` / ``usage_from_payload`` / ``iter_sse_deltas``);
only the auth, endpoint, and payload construction are Mistral-specific.
The HTTP client is reused across calls to keep the connection pool warm.
"""

from __future__ import annotations

from typing import Iterator

import httpx

from prthinker.backends.base import InferenceBackend, Usage, ThreadLocalUsage
from prthinker.backends.openai_compat import (
    extract_chat_text,
    iter_sse_deltas,
    usage_from_payload,
)

DEFAULT_BASE_URL = "https://api.mistral.ai/v1"
CHAT_COMPLETIONS_PATH = "/chat/completions"
_BACKEND_KIND = "mistral"
_PROVIDER_NAME = "Mistral"


class MistralBackend(InferenceBackend):
    concurrency_limit = 4
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
        self._usage = ThreadLocalUsage()
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
        return self._usage.get()

    def generate(
        self,
        prompt: str,
        max_new_tokens: int,
        *,
        cancel_event: "object | None" = None,
    ) -> str:
        # Remote network call; mid-stream cancellation not implemented.
        del cancel_event
        self._usage.set(None)
        payload = {
            "model": self._model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_new_tokens,
        }
        response = self._client.post(CHAT_COMPLETIONS_PATH, json=payload)
        response.raise_for_status()
        body = response.json()
        text = extract_chat_text(body, _PROVIDER_NAME)
        usage = usage_from_payload(body.get("usage") or {})
        if usage is not None:
            self._usage.set(usage)
        return text

    def stream_generate(self, prompt: str, max_new_tokens: int) -> Iterator[str]:
        """Native SSE streaming via ``stream: true``.

        Yields ``choices[0].delta.content`` deltas until the ``[DONE]``
        sentinel arrives. A final chunk may carry a ``usage`` block, which
        is captured for ``last_usage`` like the non-streaming path.
        """
        self._usage.set(None)
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
            yield from iter_sse_deltas(response.iter_lines(), self._usage.set)

    def close(self) -> None:
        self._client.close()

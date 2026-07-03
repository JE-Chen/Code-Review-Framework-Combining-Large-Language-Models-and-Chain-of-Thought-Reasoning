"""Cohere Chat API v2 backend.

Speaks the Cohere-native ``/v2/chat`` shape. Auth is a bearer token in the
``Authorization`` header. Model identifiers follow Cohere's naming, e.g.::

    command-r-plus
    command-r
    command-a-03-2025

Generated text is read from ``message.content[0].text`` of the response.
The HTTP client is reused across calls to keep the connection pool warm.
"""

from __future__ import annotations

import json
from typing import Iterator

import httpx

from prthinker.backends.base import InferenceBackend, Usage, ThreadLocalUsage

DEFAULT_BASE_URL = "https://api.cohere.com"
_CHAT_PATH = "/v2/chat"
_SSE_DATA_PREFIX = "data:"
_SSE_DONE_SENTINEL = "[DONE]"
_MAX_PROMPT_CHARS = 1_000_000


class CohereBackend(InferenceBackend):
    concurrency_limit = 4
    """Strategy backend for the Cohere Chat API v2."""

    def __init__(
        self,
        *,
        model: str,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout_seconds: float = 600.0,
    ) -> None:
        if not model:
            raise ValueError("model must be a non-empty string")
        if not api_key:
            raise ValueError("api_key must be a non-empty string")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self._model = model
        self._usage = ThreadLocalUsage()
        # ``_client`` is the injection seam: tests replace it with an
        # ``httpx.Client`` bound to a scripted ``MockTransport``.
        self._client = httpx.Client(
            base_url=base_url.rstrip("/"),
            timeout=timeout_seconds,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )

    def backend_kind(self) -> str:
        return "cohere"

    def model_name(self) -> str:
        return self._model

    def last_usage(self) -> Usage | None:
        return self._usage.get()

    def _build_payload(self, prompt: str, max_new_tokens: int, *, stream: bool) -> dict:
        """Assemble a ``/v2/chat`` request body."""
        if len(prompt) > _MAX_PROMPT_CHARS:
            raise ValueError(f"prompt exceeds {_MAX_PROMPT_CHARS} chars: {len(prompt)}")
        if max_new_tokens <= 0:
            raise ValueError("max_new_tokens must be positive")
        return {
            "model": self._model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_new_tokens,
            "stream": stream,
        }

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
        payload = self._build_payload(prompt, max_new_tokens, stream=False)
        response = self._client.post(_CHAT_PATH, json=payload)
        response.raise_for_status()
        body = response.json()
        try:
            blocks = body["message"]["content"]
            chunks = [b["text"] for b in blocks if b.get("type", "text") == "text"]
            text = "".join(chunks)
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"Unexpected Cohere response shape: {body!r}") from exc

        self._capture_usage(body.get("usage"))
        return text

    def stream_generate(self, prompt: str, max_new_tokens: int) -> Iterator[str]:
        """Native SSE streaming via ``stream: true``.

        Cohere emits ``content-delta`` events carrying
        ``delta.message.content.text`` deltas, terminated by ``message-end``
        which carries the final ``usage`` block for ``last_usage``.
        """
        self._usage.set(None)
        payload = self._build_payload(prompt, max_new_tokens, stream=True)
        with self._client.stream("POST", _CHAT_PATH, json=payload) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                event = self._parse_sse_event(line)
                if event is None:
                    continue
                if event.get("type") == "message-end":
                    self._capture_usage(self._usage_from_end(event))
                    break
                text = self._text_from_delta(event)
                if text:
                    yield text

    @staticmethod
    def _parse_sse_event(line: str) -> dict | None:
        """Decode one SSE ``data:`` line, or ``None`` to skip it."""
        if not line or not line.startswith(_SSE_DATA_PREFIX):
            return None
        payload = line[len(_SSE_DATA_PREFIX) :].strip()
        if not payload or payload == _SSE_DONE_SENTINEL:
            return None
        try:
            return json.loads(payload)
        except json.JSONDecodeError:
            return None

    @staticmethod
    def _text_from_delta(event: dict) -> str | None:
        """Return text from a ``content-delta`` event, else ``None``."""
        if event.get("type") != "content-delta":
            return None
        delta = event.get("delta") or {}
        content = (delta.get("message") or {}).get("content") or {}
        text = content.get("text")
        return str(text) if text else None

    @staticmethod
    def _usage_from_end(event: dict) -> dict | None:
        """Read the usage block carried by a ``message-end`` event."""
        delta = event.get("delta") or {}
        return delta.get("usage")

    def _capture_usage(self, usage: dict | None) -> None:
        """Record ``last_usage`` from a Cohere ``usage`` block when complete."""
        tokens = (usage or {}).get("tokens") or {}
        input_tokens = tokens.get("input_tokens")
        output_tokens = tokens.get("output_tokens")
        if input_tokens is not None and output_tokens is not None:
            self._usage.set(Usage(
                prompt_tokens=int(input_tokens),
                completion_tokens=int(output_tokens),
            ))

    def close(self) -> None:
        self._client.close()

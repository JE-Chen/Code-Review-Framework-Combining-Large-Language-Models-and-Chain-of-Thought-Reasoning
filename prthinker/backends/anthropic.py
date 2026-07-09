"""Anthropic Messages API backend.

Speaks the Anthropic-native ``/v1/messages`` shape. Required headers:
``x-api-key`` for auth and ``anthropic-version`` for API versioning
(defaults to the long-supported ``2023-06-01`` release).

Model identifiers follow Anthropic's naming, e.g.::

    claude-opus-4-7
    claude-sonnet-4-6
    claude-haiku-4-5-20251001

The HTTP client is reused across calls.
"""

from __future__ import annotations

import json
from typing import Iterator

import httpx

from prthinker.backends.base import InferenceBackend, Usage, ThreadLocalUsage
from prthinker.config import AnthropicConfig


class AnthropicBackend(InferenceBackend):
    concurrency_limit = 4

    def __init__(self, config: AnthropicConfig) -> None:
        self._config = config
        self._usage = ThreadLocalUsage()
        self._client = httpx.Client(
            base_url=config.base_url.rstrip("/"),
            timeout=config.timeout_seconds,
            headers={
                "x-api-key": config.api_key,
                "anthropic-version": config.anthropic_version,
                "Content-Type": "application/json",
            },
        )

    def backend_kind(self) -> str:
        return "anthropic"

    def model_name(self) -> str:
        return self._config.model

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
            "model": self._config.model,
            "max_tokens": max_new_tokens,
            "temperature": self._config.temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        response = self._client.post("/v1/messages", json=payload)
        response.raise_for_status()
        body = response.json()
        try:
            blocks = body["content"]
            chunks = [b["text"] for b in blocks if b.get("type") == "text"]
            text = "".join(chunks)
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(
                f"Unexpected Anthropic response shape: {body!r}"
            ) from exc

        usage = body.get("usage") or {}
        input_tokens = usage.get("input_tokens")
        output_tokens = usage.get("output_tokens")
        if input_tokens is not None and output_tokens is not None:
            self._usage.set(Usage(
                prompt_tokens=int(input_tokens),
                completion_tokens=int(output_tokens),
            ))

        return text

    def stream_generate(self, prompt: str, max_new_tokens: int) -> Iterator[str]:
        """Native SSE streaming via ``stream: true``.

        Anthropic emits ``content_block_delta`` events with ``delta.text``
        deltas. The terminating ``message_delta`` event carries the final
        ``usage`` block; we capture it for ``last_usage``.
        """
        self._usage.set(None)
        prompt_tokens: int | None = None
        payload = self._build_stream_payload(prompt, max_new_tokens)
        with self._client.stream("POST", "/v1/messages", json=payload) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                event = self._parse_sse_event(line)
                if event is None:
                    continue
                event_type = event.get("type")

                if event_type == "message_start":
                    prompt_tokens = self._prompt_tokens_from_start(event)
                elif event_type == "content_block_delta":
                    text = self._text_from_delta(event)
                    if text:
                        yield text
                elif event_type == "message_delta":
                    self._capture_stream_usage(event, prompt_tokens)
                elif event_type == "message_stop":
                    break

    def _build_stream_payload(self, prompt: str, max_new_tokens: int) -> dict:
        """Assemble the streaming ``/v1/messages`` request body."""
        return {
            "model": self._config.model,
            "max_tokens": max_new_tokens,
            "temperature": self._config.temperature,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True,
        }

    @staticmethod
    def _parse_sse_event(line: str) -> dict | None:
        """Decode one SSE ``data:`` line, or ``None`` to skip it."""
        if not line or not line.startswith("data:"):
            return None
        try:
            return json.loads(line[5:].strip())
        except json.JSONDecodeError:
            return None

    @staticmethod
    def _prompt_tokens_from_start(event: dict) -> int | None:
        """Read ``input_tokens`` from a ``message_start`` event."""
        msg = event.get("message", {}) or {}
        tokens = (msg.get("usage") or {}).get("input_tokens")
        return int(tokens) if tokens is not None else None

    @staticmethod
    def _text_from_delta(event: dict) -> str | None:
        """Return text from a ``content_block_delta`` text delta, else None."""
        delta = event.get("delta") or {}
        if delta.get("type") != "text_delta":
            return None
        text = delta.get("text")
        return str(text) if text else None

    def _capture_stream_usage(self, event: dict, prompt_tokens: int | None) -> None:
        """Record ``last_usage`` from a ``message_delta`` usage block."""
        output = (event.get("usage") or {}).get("output_tokens")
        if output is not None and prompt_tokens is not None:
            self._usage.set(Usage(prompt_tokens, int(output)))

    def close(self) -> None:
        self._client.close()

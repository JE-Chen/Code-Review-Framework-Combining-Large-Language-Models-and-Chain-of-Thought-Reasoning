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

from prthinker.backends.base import InferenceBackend, Usage
from prthinker.config import AnthropicConfig


class AnthropicBackend(InferenceBackend):
    def __init__(self, config: AnthropicConfig) -> None:
        self._config = config
        self._last_usage: Usage | None = None
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
            self._last_usage = Usage(
                prompt_tokens=int(input_tokens),
                completion_tokens=int(output_tokens),
            )

        return text

    def stream_generate(
        self, prompt: str, max_new_tokens: int
    ) -> Iterator[str]:
        """Native SSE streaming via ``stream: true``.

        Anthropic emits ``content_block_delta`` events with ``delta.text``
        deltas. The terminating ``message_delta`` event carries the final
        ``usage`` block; we capture it for ``last_usage``.
        """
        self._last_usage = None
        prompt_tokens: int | None = None
        payload = {
            "model": self._config.model,
            "max_tokens": max_new_tokens,
            "temperature": self._config.temperature,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True,
        }
        with self._client.stream("POST", "/v1/messages", json=payload) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line or not line.startswith("data:"):
                    continue
                try:
                    event = json.loads(line[5:].strip())
                except json.JSONDecodeError:
                    continue
                event_type = event.get("type")

                if event_type == "message_start":
                    msg = event.get("message", {}) or {}
                    p = (msg.get("usage") or {}).get("input_tokens")
                    if p is not None:
                        prompt_tokens = int(p)

                elif event_type == "content_block_delta":
                    delta = event.get("delta") or {}
                    if delta.get("type") == "text_delta":
                        text = delta.get("text")
                        if text:
                            yield str(text)

                elif event_type == "message_delta":
                    output = (event.get("usage") or {}).get("output_tokens")
                    if output is not None and prompt_tokens is not None:
                        self._last_usage = Usage(prompt_tokens, int(output))

                elif event_type == "message_stop":
                    break

    def close(self) -> None:
        self._client.close()

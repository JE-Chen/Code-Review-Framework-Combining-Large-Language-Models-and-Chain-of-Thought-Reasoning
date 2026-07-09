"""OpenAI-Chat-Completions-compatible backend.

Talks to any service that implements ``POST /chat/completions`` with the
OpenAI request/response shape. Tested compatibility list:

- OpenAI (``https://api.openai.com/v1``)
- Azure OpenAI (set ``base_url`` to your resource's ``/v1`` path)
- vLLM (``http://host:8000/v1``)
- LM Studio (``http://localhost:1234/v1``)
- llama.cpp server (``http://localhost:8080/v1``)
- Ollama (``http://localhost:11434/v1``)
- Together AI (``https://api.together.xyz/v1``)
- Groq (``https://api.groq.com/openai/v1``)
- DeepInfra (``https://api.deepinfra.com/v1/openai``)
- OpenRouter (``https://openrouter.ai/api/v1``)

The HTTP client is reused across calls to keep the connection pool warm.
"""

from __future__ import annotations

import json
from typing import Iterator

import httpx

from prthinker.backends.base import InferenceBackend, Usage, ThreadLocalUsage
from prthinker.config import OpenAICompatConfig

SSE_DATA_PREFIX = "data:"
SSE_DONE_SENTINEL = "[DONE]"


class OpenAICompatBackend(InferenceBackend):
    concurrency_limit = 4

    def __init__(self, config: OpenAICompatConfig) -> None:
        self._config = config
        self._usage = ThreadLocalUsage()
        headers: dict[str, str] = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        }
        if config.organization:
            headers["OpenAI-Organization"] = config.organization
        self._client = httpx.Client(
            base_url=config.base_url.rstrip("/"),
            timeout=config.timeout_seconds,
            headers=headers,
        )

    def backend_kind(self) -> str:
        return "openai"

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
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_new_tokens,
            "temperature": self._config.temperature,
            "stream": False,
        }
        response = self._client.post("/chat/completions", json=payload)
        response.raise_for_status()
        body = response.json()
        try:
            text = str(body["choices"][0]["message"]["content"])
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(
                f"Unexpected OpenAI-compat response shape: {body!r}"
            ) from exc

        usage = body.get("usage") or {}
        prompt_tokens = usage.get("prompt_tokens")
        completion_tokens = usage.get("completion_tokens")
        if prompt_tokens is not None and completion_tokens is not None:
            self._usage.set(Usage(
                prompt_tokens=int(prompt_tokens),
                completion_tokens=int(completion_tokens),
            ))

        return text

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

    def _record_stream_usage(self, event: dict) -> None:
        """Populate ``last_usage`` when an event carries a full usage block."""
        usage = event.get("usage") or {}
        prompt_tokens = usage.get("prompt_tokens")
        completion_tokens = usage.get("completion_tokens")
        if prompt_tokens is not None and completion_tokens is not None:
            self._usage.set(Usage(int(prompt_tokens), int(completion_tokens)))

    @staticmethod
    def _extract_delta_content(event: dict) -> str | None:
        """Return the content delta of an event, or None when absent / empty."""
        choices = event.get("choices") or []
        if not choices:
            return None
        delta = (choices[0] or {}).get("delta") or {}
        chunk = delta.get("content")
        return str(chunk) if chunk else None

    def stream_generate(self, prompt: str, max_new_tokens: int) -> Iterator[str]:
        """Native SSE streaming via ``stream: true``.

        The server's ``usage`` block typically only arrives in the final
        chunk (with ``stream_options: {include_usage: true}``); request
        it so ``last_usage`` is populated like the non-streaming path.
        """
        self._usage.set(None)
        payload = {
            "model": self._config.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_new_tokens,
            "temperature": self._config.temperature,
            "stream": True,
            "stream_options": {"include_usage": True},
        }
        with self._client.stream("POST", "/chat/completions", json=payload) as response:
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
                self._record_stream_usage(event)
                chunk = self._extract_delta_content(event)
                if chunk is not None:
                    yield chunk

    def close(self) -> None:
        self._client.close()

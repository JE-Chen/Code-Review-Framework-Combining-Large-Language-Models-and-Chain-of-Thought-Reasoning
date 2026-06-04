"""Behaviour tests for the OpenAI-compatible streaming backend."""

from __future__ import annotations

import httpx

from prthinker.backends.base import Usage
from prthinker.backends.openai_compat import OpenAICompatBackend
from prthinker.config import OpenAICompatConfig


def _make_backend(handler: httpx.MockTransport) -> OpenAICompatBackend:
    config = OpenAICompatConfig(model="m", api_key="k", base_url="https://x/v1")
    backend = OpenAICompatBackend(config)
    backend._client = httpx.Client(
        base_url=config.base_url.rstrip("/"),
        transport=handler,
    )
    return backend


def _sse(lines: list[str]) -> bytes:
    return ("\n".join(lines) + "\n").encode("utf-8")


def test_stream_generate_yields_content_chunks() -> None:
    body = _sse(
        [
            'data: {"choices":[{"delta":{"content":"Hel"}}]}',
            'data: {"choices":[{"delta":{"content":"lo"}}]}',
            "data: [DONE]",
        ]
    )
    transport = httpx.MockTransport(lambda req: httpx.Response(200, content=body))
    backend = _make_backend(transport)

    out = list(backend.stream_generate("hi", 16))

    assert out == ["Hel", "lo"]


def test_stream_generate_populates_usage() -> None:
    body = _sse(
        [
            'data: {"choices":[{"delta":{"content":"x"}}]}',
            'data: {"choices":[],"usage":{"prompt_tokens":3,"completion_tokens":5}}',
            "data: [DONE]",
        ]
    )
    transport = httpx.MockTransport(lambda req: httpx.Response(200, content=body))
    backend = _make_backend(transport)

    out = list(backend.stream_generate("hi", 16))

    assert out == ["x"]
    assert backend.last_usage() == Usage(3, 5)


def test_stream_generate_skips_non_data_and_bad_json() -> None:
    body = _sse(
        [
            ": comment line",
            "",
            "data: not-json",
            'data: {"choices":[{"delta":{"content":"ok"}}]}',
            'data: {"choices":[{"delta":{}}]}',
            'data: {"choices":[{"delta":{"content":""}}]}',
            "data: [DONE]",
        ]
    )
    transport = httpx.MockTransport(lambda req: httpx.Response(200, content=body))
    backend = _make_backend(transport)

    out = list(backend.stream_generate("hi", 16))

    assert out == ["ok"]
    assert backend.last_usage() is None


def test_stream_generate_partial_usage_ignored() -> None:
    body = _sse(
        [
            'data: {"usage":{"prompt_tokens":3}}',
            'data: {"choices":[{"delta":{"content":"y"}}]}',
            "data: [DONE]",
        ]
    )
    transport = httpx.MockTransport(lambda req: httpx.Response(200, content=body))
    backend = _make_backend(transport)

    out = list(backend.stream_generate("hi", 16))

    assert out == ["y"]
    assert backend.last_usage() is None


def test_stream_generate_handles_null_choice_entry() -> None:
    body = _sse(
        [
            'data: {"choices":[null]}',
            'data: {"choices":[{"delta":{"content":"z"}}]}',
            "data: [DONE]",
        ]
    )
    transport = httpx.MockTransport(lambda req: httpx.Response(200, content=body))
    backend = _make_backend(transport)

    out = list(backend.stream_generate("hi", 16))

    assert out == ["z"]

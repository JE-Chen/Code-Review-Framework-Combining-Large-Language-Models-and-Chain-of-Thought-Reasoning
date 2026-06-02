"""Behaviour tests for the Mistral Chat Completions backend."""

from __future__ import annotations

import json

import httpx
import pytest

from prthinker.backends.base import Usage
from prthinker.backends.mistral import MistralBackend

_BASE_URL = "https://api.mistral.ai/v1"


def _make_backend(handler: httpx.MockTransport) -> MistralBackend:
    backend = MistralBackend(
        model="mistral-large-latest",
        api_key="sk-test",
        base_url=_BASE_URL,
    )
    backend._client.close()
    backend._client = httpx.Client(
        base_url=_BASE_URL,
        transport=handler,
        headers={
            "Authorization": "Bearer sk-test",
            "Content-Type": "application/json",
        },
    )
    return backend


def _sse(lines: list[str]) -> bytes:
    return ("\n".join(lines) + "\n").encode("utf-8")


def test_generate_returns_parsed_text() -> None:
    body = {"choices": [{"message": {"content": "Hello world"}}]}
    transport = httpx.MockTransport(
        lambda req: httpx.Response(200, json=body)
    )
    backend = _make_backend(transport)

    assert backend.generate("hi", 64) == "Hello world"


def test_generate_request_url_method_headers_body() -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["method"] = request.method
        captured["url"] = str(request.url)
        captured["auth"] = request.headers.get("Authorization")
        captured["content_type"] = request.headers.get("Content-Type")
        captured["body"] = json.loads(request.content)
        return httpx.Response(
            200, json={"choices": [{"message": {"content": "ok"}}]}
        )

    backend = _make_backend(httpx.MockTransport(handler))
    backend.generate("the prompt", 128)

    assert captured["method"] == "POST"
    assert captured["url"] == f"{_BASE_URL}/chat/completions"
    assert captured["auth"] == "Bearer sk-test"
    assert captured["content_type"] == "application/json"
    body = captured["body"]
    assert body["model"] == "mistral-large-latest"
    assert body["max_tokens"] == 128
    assert body["messages"] == [{"role": "user", "content": "the prompt"}]


def test_generate_populates_usage() -> None:
    body = {
        "choices": [{"message": {"content": "x"}}],
        "usage": {"prompt_tokens": 7, "completion_tokens": 3},
    }
    transport = httpx.MockTransport(
        lambda req: httpx.Response(200, json=body)
    )
    backend = _make_backend(transport)

    backend.generate("hi", 16)

    assert backend.last_usage() == Usage(7, 3)


def test_generate_partial_usage_left_none() -> None:
    body = {
        "choices": [{"message": {"content": "x"}}],
        "usage": {"prompt_tokens": 7},
    }
    transport = httpx.MockTransport(
        lambda req: httpx.Response(200, json=body)
    )
    backend = _make_backend(transport)

    backend.generate("hi", 16)

    assert backend.last_usage() is None


def test_generate_raises_on_http_error() -> None:
    transport = httpx.MockTransport(
        lambda req: httpx.Response(401, json={"error": "unauthorized"})
    )
    backend = _make_backend(transport)

    with pytest.raises(httpx.HTTPStatusError):
        backend.generate("hi", 16)


def test_generate_raises_on_unexpected_shape() -> None:
    transport = httpx.MockTransport(
        lambda req: httpx.Response(200, json={"unexpected": True})
    )
    backend = _make_backend(transport)

    with pytest.raises(RuntimeError, match="Unexpected Mistral response shape"):
        backend.generate("hi", 16)


def test_stream_generate_yields_content_chunks() -> None:
    body = _sse(
        [
            'data: {"choices":[{"delta":{"content":"Hel"}}]}',
            'data: {"choices":[{"delta":{"content":"lo"}}]}',
            "data: [DONE]",
        ]
    )
    transport = httpx.MockTransport(
        lambda req: httpx.Response(200, content=body)
    )
    backend = _make_backend(transport)

    assert list(backend.stream_generate("hi", 16)) == ["Hel", "lo"]


def test_stream_generate_populates_usage_and_skips_junk() -> None:
    body = _sse(
        [
            ": comment line",
            "",
            "data: not-json",
            'data: {"choices":[{"delta":{"content":"ok"}}]}',
            'data: {"choices":[{"delta":{}}]}',
            'data: {"choices":[],"usage":{"prompt_tokens":3,"completion_tokens":5}}',
            "data: [DONE]",
            'data: {"choices":[{"delta":{"content":"after-done"}}]}',
        ]
    )
    transport = httpx.MockTransport(
        lambda req: httpx.Response(200, content=body)
    )
    backend = _make_backend(transport)

    assert list(backend.stream_generate("hi", 16)) == ["ok"]
    assert backend.last_usage() == Usage(3, 5)


def test_stream_generate_raises_on_http_error() -> None:
    transport = httpx.MockTransport(
        lambda req: httpx.Response(500, content=b"data: [DONE]\n")
    )
    backend = _make_backend(transport)

    with pytest.raises(httpx.HTTPStatusError):
        list(backend.stream_generate("hi", 16))


def test_constructor_validates_required_fields() -> None:
    with pytest.raises(ValueError, match="model is required"):
        MistralBackend(model="", api_key="k")
    with pytest.raises(ValueError, match="api_key is required"):
        MistralBackend(model="m", api_key="")
    with pytest.raises(ValueError, match="timeout_seconds must be positive"):
        MistralBackend(model="m", api_key="k", timeout_seconds=0)


def test_backend_kind_and_model_name() -> None:
    transport = httpx.MockTransport(
        lambda req: httpx.Response(200, json={})
    )
    backend = _make_backend(transport)

    assert backend.backend_kind() == "mistral"
    assert backend.model_name() == "mistral-large-latest"

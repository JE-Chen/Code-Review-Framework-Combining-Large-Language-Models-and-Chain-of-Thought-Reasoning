"""Behaviour tests for the Gemini Generative Language REST backend."""

from __future__ import annotations

import json

import httpx
import pytest

from prthinker.backends.base import Usage
from prthinker.backends.gemini import GeminiBackend

_MODEL = "gemini-2.5-flash"
_API_KEY = "k-secret"
_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"


def _make_backend(handler: httpx.MockTransport) -> GeminiBackend:
    backend = GeminiBackend(model=_MODEL, api_key=_API_KEY, base_url=_BASE_URL)
    backend._client = httpx.Client(
        base_url=_BASE_URL.rstrip("/"),
        transport=handler,
        headers={"Content-Type": "application/json"},
    )
    return backend


def _candidate(text: str) -> dict:
    return {"candidates": [{"content": {"parts": [{"text": text}]}}]}


def test_generate_returns_parsed_text() -> None:
    body = _candidate("Hello world")
    transport = httpx.MockTransport(lambda req: httpx.Response(200, json=body))
    backend = _make_backend(transport)

    assert backend.generate("hi", 32) == "Hello world"


def test_generate_request_shape() -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["method"] = request.method
        captured["url"] = str(request.url)
        captured["path"] = request.url.path
        captured["key"] = request.url.params.get("key")
        captured["content_type"] = request.headers.get("Content-Type")
        captured["json"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(200, json=_candidate("ok"))

    backend = _make_backend(httpx.MockTransport(handler))
    backend.generate("the prompt", 128)

    assert captured["method"] == "POST"
    assert captured["path"] == f"/v1beta/models/{_MODEL}:generateContent"
    assert captured["key"] == _API_KEY
    assert captured["content_type"] == "application/json"
    assert captured["json"] == {
        "contents": [{"parts": [{"text": "the prompt"}]}],
        "generationConfig": {"maxOutputTokens": 128},
    }


def test_generate_populates_usage() -> None:
    body = _candidate("x")
    body["usageMetadata"] = {
        "promptTokenCount": 7,
        "candidatesTokenCount": 4,
    }
    transport = httpx.MockTransport(lambda req: httpx.Response(200, json=body))
    backend = _make_backend(transport)

    assert backend.generate("hi", 16) == "x"
    assert backend.last_usage() == Usage(7, 4)


def test_generate_partial_usage_ignored() -> None:
    body = _candidate("y")
    body["usageMetadata"] = {"promptTokenCount": 3}
    transport = httpx.MockTransport(lambda req: httpx.Response(200, json=body))
    backend = _make_backend(transport)

    backend.generate("hi", 16)
    assert backend.last_usage() is None


def test_generate_unexpected_shape_raises() -> None:
    transport = httpx.MockTransport(
        lambda req: httpx.Response(200, json={"candidates": []})
    )
    backend = _make_backend(transport)

    with pytest.raises(RuntimeError, match="Unexpected Gemini response shape"):
        backend.generate("hi", 16)


def test_generate_http_error_raises() -> None:
    transport = httpx.MockTransport(
        lambda req: httpx.Response(429, json={"error": "rate limited"})
    )
    backend = _make_backend(transport)

    with pytest.raises(httpx.HTTPStatusError):
        backend.generate("hi", 16)


def test_stream_generate_yields_chunk_text() -> None:
    chunks = [_candidate("Hel"), _candidate("lo")]
    transport = httpx.MockTransport(
        lambda req: httpx.Response(200, json=chunks)
    )
    backend = _make_backend(transport)

    assert list(backend.stream_generate("hi", 16)) == ["Hel", "lo"]


def test_stream_generate_captures_usage_and_skips_usage_only_chunk() -> None:
    usage_chunk = {
        "usageMetadata": {
            "promptTokenCount": 5,
            "candidatesTokenCount": 9,
        }
    }
    chunks = [_candidate("a"), usage_chunk]
    transport = httpx.MockTransport(
        lambda req: httpx.Response(200, json=chunks)
    )
    backend = _make_backend(transport)

    assert list(backend.stream_generate("hi", 16)) == ["a"]
    assert backend.last_usage() == Usage(5, 9)


def test_stream_generate_wraps_single_object() -> None:
    transport = httpx.MockTransport(
        lambda req: httpx.Response(200, json=_candidate("solo"))
    )
    backend = _make_backend(transport)

    assert list(backend.stream_generate("hi", 16)) == ["solo"]


def test_stream_generate_http_error_raises() -> None:
    transport = httpx.MockTransport(
        lambda req: httpx.Response(500, json={"error": "boom"})
    )
    backend = _make_backend(transport)

    with pytest.raises(httpx.HTTPStatusError):
        list(backend.stream_generate("hi", 16))


def test_backend_kind_and_model_name() -> None:
    transport = httpx.MockTransport(lambda req: httpx.Response(200, json={}))
    backend = _make_backend(transport)

    assert backend.backend_kind() == "gemini"
    assert backend.model_name() == _MODEL


def test_constructor_rejects_empty_model() -> None:
    with pytest.raises(ValueError, match="model is required"):
        GeminiBackend(model="", api_key=_API_KEY)


def test_constructor_rejects_empty_api_key() -> None:
    with pytest.raises(ValueError, match="api_key is required"):
        GeminiBackend(model=_MODEL, api_key="")


def test_constructor_rejects_nonpositive_timeout() -> None:
    with pytest.raises(ValueError, match="timeout_seconds must be positive"):
        GeminiBackend(model=_MODEL, api_key=_API_KEY, timeout_seconds=0)

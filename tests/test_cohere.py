"""Behaviour tests for the Cohere Chat API v2 backend."""

from __future__ import annotations

import json

import httpx
import pytest

from prthinker.backends.base import Usage
from prthinker.backends.cohere import DEFAULT_BASE_URL, CohereBackend


def _make_backend(handler: httpx.MockTransport) -> CohereBackend:
    backend = CohereBackend(
        model="command-r-plus", api_key="co-test", base_url=DEFAULT_BASE_URL
    )
    backend._client.close()
    backend._client = httpx.Client(
        base_url=DEFAULT_BASE_URL,
        transport=handler,
        headers={"Authorization": "Bearer co-test"},
    )
    return backend


def _sse(lines: list[str]) -> bytes:
    return ("\n".join(lines) + "\n").encode("utf-8")


def test_generate_returns_parsed_text() -> None:
    body = {
        "message": {"content": [{"type": "text", "text": "Hello world"}]},
        "usage": {"tokens": {"input_tokens": 7, "output_tokens": 3}},
    }
    transport = httpx.MockTransport(lambda req: httpx.Response(200, json=body))
    backend = _make_backend(transport)

    assert backend.generate("hi", 64) == "Hello world"
    assert backend.last_usage() == Usage(7, 3)


def test_generate_request_url_method_headers_and_body() -> None:
    captured: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        captured["method"] = req.method
        captured["url"] = str(req.url)
        captured["auth"] = req.headers.get("Authorization")
        captured["body"] = json.loads(req.content)
        return httpx.Response(
            200, json={"message": {"content": [{"type": "text", "text": "x"}]}}
        )

    backend = _make_backend(httpx.MockTransport(handler))
    backend.generate("the prompt", 128)

    assert captured["method"] == "POST"
    assert captured["url"] == f"{DEFAULT_BASE_URL}/v2/chat"
    assert captured["auth"] == "Bearer co-test"
    body = captured["body"]
    assert body["model"] == "command-r-plus"
    assert body["max_tokens"] == 128
    assert body["stream"] is False
    assert body["messages"] == [{"role": "user", "content": "the prompt"}]


def test_generate_raises_on_http_error() -> None:
    transport = httpx.MockTransport(
        lambda req: httpx.Response(401, json={"message": "unauthorized"})
    )
    backend = _make_backend(transport)

    with pytest.raises(httpx.HTTPStatusError):
        backend.generate("hi", 16)


def test_generate_raises_on_unexpected_shape() -> None:
    transport = httpx.MockTransport(
        lambda req: httpx.Response(200, json={"nope": True})
    )
    backend = _make_backend(transport)

    with pytest.raises(RuntimeError):
        backend.generate("hi", 16)
    assert backend.last_usage() is None


def test_stream_generate_yields_content_deltas_and_usage() -> None:
    body = _sse(
        [
            'data: {"type":"content-delta",'
            '"delta":{"message":{"content":{"text":"Hel"}}}}',
            'data: {"type":"content-delta",'
            '"delta":{"message":{"content":{"text":"lo"}}}}',
            'data: {"type":"message-end",'
            '"delta":{"usage":{"tokens":{"input_tokens":4,"output_tokens":2}}}}',
        ]
    )
    transport = httpx.MockTransport(lambda req: httpx.Response(200, content=body))
    backend = _make_backend(transport)

    out = list(backend.stream_generate("hi", 16))

    assert out == ["Hel", "lo"]
    assert backend.last_usage() == Usage(4, 2)


def test_stream_generate_skips_blank_done_and_bad_json() -> None:
    body = _sse(
        [
            "",
            ": comment",
            "data: not-json",
            'data: {"type":"content-delta",'
            '"delta":{"message":{"content":{"text":"ok"}}}}',
            "data: [DONE]",
        ]
    )
    transport = httpx.MockTransport(lambda req: httpx.Response(200, content=body))
    backend = _make_backend(transport)

    assert list(backend.stream_generate("p", 8)) == ["ok"]


def test_stream_generate_stops_on_message_end() -> None:
    body = _sse(
        [
            'data: {"type":"content-delta",'
            '"delta":{"message":{"content":{"text":"a"}}}}',
            'data: {"type":"message-end","delta":{}}',
            'data: {"type":"content-delta",'
            '"delta":{"message":{"content":{"text":"after"}}}}',
        ]
    )
    transport = httpx.MockTransport(lambda req: httpx.Response(200, content=body))
    backend = _make_backend(transport)

    assert list(backend.stream_generate("p", 8)) == ["a"]


def test_constructor_rejects_empty_model_and_key() -> None:
    with pytest.raises(ValueError):
        CohereBackend(model="", api_key="k")
    with pytest.raises(ValueError):
        CohereBackend(model="m", api_key="")
    with pytest.raises(ValueError):
        CohereBackend(model="m", api_key="k", timeout_seconds=0)


def test_generate_rejects_bad_token_budget() -> None:
    transport = httpx.MockTransport(lambda req: httpx.Response(200, json={}))
    backend = _make_backend(transport)
    with pytest.raises(ValueError):
        backend.generate("hi", 0)


def test_backend_kind_and_model_name() -> None:
    backend = _make_backend(
        httpx.MockTransport(lambda req: httpx.Response(200, json={}))
    )
    assert backend.backend_kind() == "cohere"
    assert backend.model_name() == "command-r-plus"

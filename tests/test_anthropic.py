"""Tests for the Anthropic Messages API streaming backend."""

from __future__ import annotations

import contextlib
import json

from prthinker.backends.anthropic import AnthropicBackend
from prthinker.config import AnthropicConfig


def _sse(event: dict) -> str:
    return f"data: {json.dumps(event)}"


class _ScriptedStreamResponse:
    """Stand-in for the streaming ``httpx.Response`` context manager."""

    def __init__(self, lines: list[str]) -> None:
        self._lines = lines

    def __enter__(self) -> "_ScriptedStreamResponse":
        return self

    def __exit__(self, *_exc: object) -> bool:
        return False

    def raise_for_status(self) -> None:
        return None

    def iter_lines(self):
        yield from self._lines


class _ScriptedClient:
    """Captures the streamed payload and replays scripted SSE lines."""

    def __init__(self, lines: list[str]) -> None:
        self._lines = lines
        self.calls: list[dict] = []

    def stream(self, method: str, url: str, *, json: dict):
        self.calls.append({"method": method, "url": url, "json": json})
        return _ScriptedStreamResponse(self._lines)

    def close(self) -> None:
        return None


class _ScriptedPostResponse:
    """Stand-in for a non-streaming ``httpx.Response``."""

    def __init__(self, body: dict) -> None:
        self._body = body

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._body


class _ScriptedPostClient:
    """Captures the posted payload and replays a scripted JSON body."""

    def __init__(self, body: dict) -> None:
        self._body = body
        self.calls: list[dict] = []

    def post(self, url: str, *, json: dict) -> _ScriptedPostResponse:
        self.calls.append({"url": url, "json": json})
        return _ScriptedPostResponse(self._body)

    def close(self) -> None:
        return None


def _make_backend(lines: list[str]) -> AnthropicBackend:
    config = AnthropicConfig(model="claude-opus-4-7", api_key="sk-test")
    backend = AnthropicBackend(config)
    with contextlib.suppress(Exception):
        backend._client.close()
    backend._client = _ScriptedClient(lines)
    return backend


def _make_post_backend(body: dict) -> AnthropicBackend:
    config = AnthropicConfig(model="claude-opus-4-7", api_key="sk-test")
    backend = AnthropicBackend(config)
    with contextlib.suppress(Exception):
        backend._client.close()
    backend._client = _ScriptedPostClient(body)
    return backend


_LONG_PROMPT = "x" * 4096
_OK_BODY: dict = {"content": [{"type": "text", "text": "ok"}], "usage": {}}


def test_stream_yields_text_deltas_and_usage() -> None:
    lines = [
        _sse({"type": "message_start",
              "message": {"usage": {"input_tokens": 11}}}),
        _sse({"type": "content_block_delta",
              "delta": {"type": "text_delta", "text": "Hello "}}),
        _sse({"type": "content_block_delta",
              "delta": {"type": "text_delta", "text": "world"}}),
        _sse({"type": "message_delta", "usage": {"output_tokens": 5}}),
        _sse({"type": "message_stop"}),
    ]
    backend = _make_backend(lines)
    out = list(backend.stream_generate("hi", 64))
    assert out == ["Hello ", "world"]
    usage = backend.last_usage()
    assert usage is not None
    assert usage.prompt_tokens == 11
    assert usage.completion_tokens == 5


def test_stream_request_payload_shape() -> None:
    backend = _make_backend([_sse({"type": "message_stop"})])
    list(backend.stream_generate("the prompt", 128))
    call = backend._client.calls[0]
    assert call["method"] == "POST"
    assert call["url"] == "/v1/messages"
    body = call["json"]
    assert body["model"] == "claude-opus-4-7"
    assert body["max_tokens"] == 128
    assert body["stream"] is True
    assert body["messages"] == [{"role": "user", "content": "the prompt"}]


def test_stream_skips_blank_and_non_data_lines() -> None:
    lines = [
        "",
        "event: ping",
        _sse({"type": "content_block_delta",
              "delta": {"type": "text_delta", "text": "x"}}),
    ]
    backend = _make_backend(lines)
    assert list(backend.stream_generate("p", 8)) == ["x"]


def test_stream_skips_malformed_json() -> None:
    lines = [
        "data: {not valid json",
        _sse({"type": "content_block_delta",
              "delta": {"type": "text_delta", "text": "ok"}}),
    ]
    backend = _make_backend(lines)
    assert list(backend.stream_generate("p", 8)) == ["ok"]


def test_stream_ignores_non_text_delta() -> None:
    lines = [
        _sse({"type": "content_block_delta",
              "delta": {"type": "input_json_delta", "partial_json": "{}"}}),
        _sse({"type": "content_block_delta",
              "delta": {"type": "text_delta", "text": ""}}),
        _sse({"type": "content_block_delta",
              "delta": {"type": "text_delta", "text": "real"}}),
    ]
    backend = _make_backend(lines)
    assert list(backend.stream_generate("p", 8)) == ["real"]


def test_stream_usage_none_without_prompt_tokens() -> None:
    lines = [
        _sse({"type": "message_delta", "usage": {"output_tokens": 5}}),
        _sse({"type": "message_stop"}),
    ]
    backend = _make_backend(lines)
    list(backend.stream_generate("p", 8))
    assert backend.last_usage() is None


def test_stream_usage_none_without_output_tokens() -> None:
    lines = [
        _sse({"type": "message_start",
              "message": {"usage": {"input_tokens": 3}}}),
        _sse({"type": "message_delta", "usage": {}}),
        _sse({"type": "message_stop"}),
    ]
    backend = _make_backend(lines)
    list(backend.stream_generate("p", 8))
    assert backend.last_usage() is None


def test_stream_stops_on_message_stop() -> None:
    lines = [
        _sse({"type": "content_block_delta",
              "delta": {"type": "text_delta", "text": "a"}}),
        _sse({"type": "message_stop"}),
        _sse({"type": "content_block_delta",
              "delta": {"type": "text_delta", "text": "after-stop"}}),
    ]
    backend = _make_backend(lines)
    assert list(backend.stream_generate("p", 8)) == ["a"]


def test_backend_kind_and_model_name() -> None:
    backend = _make_backend([])
    assert backend.backend_kind() == "anthropic"
    assert backend.model_name() == "claude-opus-4-7"


def test_generate_short_prompt_keeps_plain_string_content() -> None:
    backend = _make_post_backend(_OK_BODY)
    backend.generate("short prompt", 64)
    body = backend._client.calls[0]["json"]
    assert body["messages"] == [{"role": "user", "content": "short prompt"}]


def test_generate_long_prompt_gets_cache_control_block() -> None:
    backend = _make_post_backend(_OK_BODY)
    backend.generate(_LONG_PROMPT, 64)
    content = backend._client.calls[0]["json"]["messages"][0]["content"]
    assert isinstance(content, list) and len(content) == 1
    block = content[0]
    assert block["type"] == "text"
    assert block["text"] == _LONG_PROMPT
    assert block["cache_control"] == {"type": "ephemeral"}


def test_cache_control_threshold_boundary() -> None:
    just_below = "y" * 4095
    backend = _make_post_backend(_OK_BODY)
    backend.generate(just_below, 64)
    body = backend._client.calls[0]["json"]
    assert body["messages"][0]["content"] == just_below

    backend = _make_post_backend(_OK_BODY)
    backend.generate("y" * 4096, 64)
    content = backend._client.calls[0]["json"]["messages"][0]["content"]
    assert content[0]["cache_control"] == {"type": "ephemeral"}


def test_stream_long_prompt_gets_cache_control_block() -> None:
    backend = _make_backend([_sse({"type": "message_stop"})])
    list(backend.stream_generate(_LONG_PROMPT, 8))
    content = backend._client.calls[0]["json"]["messages"][0]["content"]
    assert content[0]["cache_control"] == {"type": "ephemeral"}


def test_generate_usage_without_cache_fields_unchanged() -> None:
    body = {
        "content": [{"type": "text", "text": "ok"}],
        "usage": {"input_tokens": 10, "output_tokens": 5},
    }
    backend = _make_post_backend(body)
    backend.generate("p", 8)
    usage = backend.last_usage()
    assert usage is not None
    assert usage.prompt_tokens == 10
    assert usage.completion_tokens == 5


def test_generate_usage_folds_cache_tokens_into_prompt_tokens() -> None:
    body = {
        "content": [{"type": "text", "text": "ok"}],
        "usage": {
            "input_tokens": 10,
            "output_tokens": 5,
            "cache_creation_input_tokens": 100,
            "cache_read_input_tokens": 200,
        },
    }
    backend = _make_post_backend(body)
    backend.generate("p", 8)
    usage = backend.last_usage()
    assert usage is not None
    assert usage.prompt_tokens == 310
    assert usage.completion_tokens == 5


def test_generate_usage_none_when_input_tokens_missing() -> None:
    body = {
        "content": [{"type": "text", "text": "ok"}],
        "usage": {"output_tokens": 5, "cache_read_input_tokens": 200},
    }
    backend = _make_post_backend(body)
    backend.generate("p", 8)
    assert backend.last_usage() is None


def test_stream_usage_folds_cache_tokens_into_prompt_tokens() -> None:
    lines = [
        _sse({"type": "message_start",
              "message": {"usage": {"input_tokens": 3,
                                    "cache_creation_input_tokens": 4,
                                    "cache_read_input_tokens": 5}}}),
        _sse({"type": "message_delta", "usage": {"output_tokens": 2}}),
        _sse({"type": "message_stop"}),
    ]
    backend = _make_backend(lines)
    list(backend.stream_generate("p", 8))
    usage = backend.last_usage()
    assert usage is not None
    assert usage.prompt_tokens == 12
    assert usage.completion_tokens == 2

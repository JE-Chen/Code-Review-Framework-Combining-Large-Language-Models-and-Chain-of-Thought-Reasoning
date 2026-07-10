"""Behaviour tests for the OpenAI-compatible streaming backend."""

from __future__ import annotations

import httpx
import pytest

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


# --------------------------------------------------------------------------
# shared OpenAI-shaped parsing helpers (reused by the Mistral backend)
# --------------------------------------------------------------------------


def test_extract_chat_text_happy_path() -> None:
    from prthinker.backends.openai_compat import extract_chat_text

    body = {"choices": [{"message": {"content": "hi"}}]}
    assert extract_chat_text(body, "OpenAI-compat") == "hi"


def test_extract_chat_text_bad_shape_names_provider() -> None:
    from prthinker.backends.openai_compat import extract_chat_text

    with pytest.raises(RuntimeError, match="Unexpected Mistral response shape"):
        extract_chat_text({"unexpected": True}, "Mistral")


def test_extract_chat_text_empty_choices() -> None:
    from prthinker.backends.openai_compat import extract_chat_text

    with pytest.raises(RuntimeError, match="response shape"):
        extract_chat_text({"choices": []}, "OpenAI-compat")


def test_usage_from_payload_full_block() -> None:
    from prthinker.backends.openai_compat import usage_from_payload

    assert usage_from_payload(
        {"prompt_tokens": 7, "completion_tokens": 3}
    ) == Usage(7, 3)


def test_usage_from_payload_partial_or_empty_is_none() -> None:
    from prthinker.backends.openai_compat import usage_from_payload

    assert usage_from_payload({"prompt_tokens": 7}) is None
    assert usage_from_payload({"completion_tokens": 3}) is None
    assert usage_from_payload({}) is None


def test_iter_sse_deltas_yields_until_done_and_records_usage() -> None:
    from prthinker.backends.openai_compat import iter_sse_deltas

    recorded: list[Usage] = []
    lines = [
        ": comment",
        "",
        "data: not-json",
        'data: {"choices":[{"delta":{"content":"Hel"}}]}',
        'data: {"choices":[{"delta":{}}]}',
        'data: {"choices":[],"usage":{"prompt_tokens":3,"completion_tokens":5}}',
        'data: {"choices":[{"delta":{"content":"lo"}}]}',
        "data: [DONE]",
        'data: {"choices":[{"delta":{"content":"after-done"}}]}',
    ]
    chunks = list(iter_sse_deltas(lines, recorded.append))
    assert chunks == ["Hel", "lo"]
    assert recorded == [Usage(3, 5)]


def test_iter_sse_deltas_empty_input() -> None:
    from prthinker.backends.openai_compat import iter_sse_deltas

    assert list(iter_sse_deltas([], lambda _u: None)) == []

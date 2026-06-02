"""Unit tests for the RouterBackend fallback meta-backend."""

from __future__ import annotations

from typing import Iterator

import pytest

from prthinker.backends.base import InferenceBackend
from prthinker.backends.router import RouterBackend


class _StubBackend(InferenceBackend):
    """Tiny fake backend that returns a fixed text or raises on generate."""

    def __init__(
        self,
        kind: str,
        model: str,
        *,
        text: str = "",
        error: Exception | None = None,
    ) -> None:
        self._kind = kind
        self._model = model
        self._text = text
        self._error = error
        self.generate_calls = 0
        self.stream_calls = 0

    def backend_kind(self) -> str:
        return self._kind

    def model_name(self) -> str:
        return self._model

    def generate(
        self,
        prompt: str,
        max_new_tokens: int,
        *,
        cancel_event: "object | None" = None,
    ) -> str:
        self.generate_calls += 1
        if self._error is not None:
            raise self._error
        return self._text

    def stream_generate(
        self, prompt: str, max_new_tokens: int
    ) -> Iterator[str]:
        self.stream_calls += 1
        yield self._text


def test_primary_success_uses_primary() -> None:
    primary = _StubBackend("primary", "model-a", text="ok")
    fallback = _StubBackend("fallback", "model-b", text="nope")
    router = RouterBackend(primary, (fallback,))

    assert router.generate("p", 16) == "ok"
    assert primary.generate_calls == 1
    assert fallback.generate_calls == 0


def test_primary_failure_uses_first_healthy_fallback() -> None:
    primary = _StubBackend("primary", "model-a", error=RuntimeError("boom"))
    bad = _StubBackend("bad", "model-b", error=ValueError("also boom"))
    good = _StubBackend("good", "model-c", text="recovered")
    router = RouterBackend(primary, (bad, good))

    assert router.generate("p", 16) == "recovered"
    assert primary.generate_calls == 1
    assert bad.generate_calls == 1
    assert good.generate_calls == 1


def test_all_fail_propagates_last_exception() -> None:
    primary = _StubBackend("primary", "model-a", error=RuntimeError("first"))
    last_error = ValueError("last")
    fallback = _StubBackend("fallback", "model-b", error=last_error)
    router = RouterBackend(primary, (fallback,))

    with pytest.raises(ValueError) as excinfo:
        router.generate("p", 16)
    assert excinfo.value is last_error


def test_no_fallbacks_propagates_primary_exception() -> None:
    primary = _StubBackend("primary", "model-a", error=KeyError("only"))
    router = RouterBackend(primary)

    with pytest.raises(KeyError):
        router.generate("p", 16)


def test_backend_kind_and_model_name() -> None:
    primary = _StubBackend("primary", "model-a", text="ok")
    fallback = _StubBackend("fallback", "model-b", text="nope")
    router = RouterBackend(primary, (fallback,))

    assert router.backend_kind() == "router"
    assert router.model_name() == "model-a"


def test_stream_delegates_to_primary() -> None:
    primary = _StubBackend("primary", "model-a", text="streamed")
    fallback = _StubBackend("fallback", "model-b", text="nope")
    router = RouterBackend(primary, (fallback,))

    chunks = list(router.stream_generate("p", 16))

    assert chunks == ["streamed"]
    assert primary.stream_calls == 1
    assert fallback.stream_calls == 0

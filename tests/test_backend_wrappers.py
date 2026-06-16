"""Tests for SerializingBackend — the single-GPU generation serialiser."""

from __future__ import annotations

import threading
import time

from prthinker.backends.base import InferenceBackend, Usage
from prthinker.backends.wrappers import SerializingBackend


class _ConcurrencyProbe(InferenceBackend):
    """Backend stub that records the peak number of overlapping generates."""

    def __init__(self) -> None:
        self._counter_lock = threading.Lock()
        self.current = 0
        self.max_seen = 0
        self.calls = 0
        self.last_cancel: object = "unset"
        self.closed = False
        self._usage: Usage | None = None
        # An attribute the server reads directly off the backend; the wrapper
        # must delegate it through __getattr__.
        self._tokenizer = object()

    def backend_kind(self) -> str:
        return "probe"

    def model_name(self) -> str:
        return "probe-model"

    def last_usage(self) -> Usage | None:
        return self._usage

    def generate(
        self,
        prompt: str,
        max_new_tokens: int,
        *,
        cancel_event: "object | None" = None,
    ) -> str:
        with self._counter_lock:
            self.current += 1
            self.max_seen = max(self.max_seen, self.current)
            self.calls += 1
            self.last_cancel = cancel_event
        time.sleep(0.03)  # widen the window where overlap could be observed
        with self._counter_lock:
            self.current -= 1
        return f"out:{prompt}:{max_new_tokens}"

    def close(self) -> None:
        self.closed = True


def test_concurrent_generates_never_overlap():
    probe = _ConcurrencyProbe()
    backend = SerializingBackend(probe)
    results: list[str] = []
    results_lock = threading.Lock()

    def worker(i: int) -> None:
        out = backend.generate(f"p{i}", 16)
        with results_lock:
            results.append(out)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert probe.max_seen == 1  # the lock held generations strictly serial
    assert probe.calls == 8
    assert len(results) == 8


def test_generate_returns_inner_result_and_passes_cancel_event():
    probe = _ConcurrencyProbe()
    backend = SerializingBackend(probe)
    sentinel = object()
    out = backend.generate("hello", 32, cancel_event=sentinel)
    assert out == "out:hello:32"
    assert probe.last_cancel is sentinel


def test_getattr_delegates_to_inner():
    probe = _ConcurrencyProbe()
    backend = SerializingBackend(probe)
    # The server reads ``_tokenizer`` straight off the backend object.
    assert backend._tokenizer is probe._tokenizer


def test_missing_attribute_raises():
    backend = SerializingBackend(_ConcurrencyProbe())
    try:
        _ = backend.does_not_exist
    except AttributeError:
        pass
    else:  # pragma: no cover - guard
        raise AssertionError("expected AttributeError")


def test_proxies_metadata_and_close():
    probe = _ConcurrencyProbe()
    backend = SerializingBackend(probe)
    assert backend.backend_kind() == "probe"
    assert backend.model_name() == "probe-model"
    assert backend.last_usage() is None
    backend.close()
    assert probe.closed is True


def test_stream_generate_yields_inner_chunks():
    probe = _ConcurrencyProbe()
    backend = SerializingBackend(probe)
    chunks = list(backend.stream_generate("x", 8))
    # Default stream falls back to a single full-response chunk.
    assert chunks == ["out:x:8"]


def test_explicit_shared_lock_is_used():
    lock = threading.Lock()
    backend = SerializingBackend(_ConcurrencyProbe(), lock=lock)
    assert backend._lock is lock

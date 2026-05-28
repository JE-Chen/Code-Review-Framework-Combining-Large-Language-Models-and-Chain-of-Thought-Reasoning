"""Composable wrappers over an ``InferenceBackend``.

Two Decorators that can be stacked at the factory level:

- ``CachingBackend(inner, cache)`` — looks up the prompt in the cache
  before delegating; writes the response back on miss. Honors the cache's
  TTL config (set when the ``PromptCache`` was constructed).
- ``InstrumentedBackend(inner, telemetry)`` — records every call's tokens,
  latency, cache-hit status, and estimated cost.

A common usage pattern is ``InstrumentedBackend(CachingBackend(real, cache),
telemetry)`` so the telemetry layer sees the cache outcome via the inner
wrapper's ``last_cache_hit`` flag.
"""

from __future__ import annotations

import logging
import time
from typing import Iterator

from prthinker.backends.base import InferenceBackend, Usage
from prthinker.cache import PromptCache
from prthinker.telemetry import CallRecord, TelemetrySink, estimate_tokens

log = logging.getLogger(__name__)


class CachingBackend(InferenceBackend):
    """Read-through cache wrapper."""

    def __init__(self, inner: InferenceBackend, cache: PromptCache) -> None:
        self._inner = inner
        self._cache = cache
        self._last_cache_hit = False

    @property
    def last_cache_hit(self) -> bool:
        return self._last_cache_hit

    def backend_kind(self) -> str:
        return self._inner.backend_kind()

    def model_name(self) -> str:
        return self._inner.model_name()

    def last_usage(self) -> Usage | None:
        return self._inner.last_usage()

    def generate(self, prompt: str, max_new_tokens: int) -> str:
        kind = self._inner.backend_kind()
        model = self._inner.model_name()
        cached = self._cache.get(kind, model, prompt, max_new_tokens)
        if cached is not None:
            self._last_cache_hit = True
            return cached

        self._last_cache_hit = False
        text = self._inner.generate(prompt, max_new_tokens)
        self._cache.put(kind, model, prompt, max_new_tokens, text)
        return text

    def stream_generate(
        self, prompt: str, max_new_tokens: int
    ) -> Iterator[str]:
        """Stream from the inner backend, then write the full text to cache.

        Cache hits short-circuit to a single chunk so the caller does not
        need to special-case the hit path.
        """
        kind = self._inner.backend_kind()
        model = self._inner.model_name()
        cached = self._cache.get(kind, model, prompt, max_new_tokens)
        if cached is not None:
            self._last_cache_hit = True
            yield cached
            return

        self._last_cache_hit = False
        chunks: list[str] = []
        for chunk in self._inner.stream_generate(prompt, max_new_tokens):
            chunks.append(chunk)
            yield chunk
        self._cache.put(kind, model, prompt, max_new_tokens, "".join(chunks))

    def close(self) -> None:
        self._inner.close()


class InstrumentedBackend(InferenceBackend):
    """Record one telemetry row per ``generate()`` call."""

    def __init__(
        self,
        inner: InferenceBackend,
        telemetry: TelemetrySink,
    ) -> None:
        self._inner = inner
        self._telemetry = telemetry

    def backend_kind(self) -> str:
        return self._inner.backend_kind()

    def model_name(self) -> str:
        return self._inner.model_name()

    def last_usage(self) -> Usage | None:
        return self._inner.last_usage()

    def generate(self, prompt: str, max_new_tokens: int) -> str:
        start = time.perf_counter()
        error: str | None = None
        text = ""
        try:
            text = self._inner.generate(prompt, max_new_tokens)
            return text
        except Exception as exc:
            error = repr(exc)
            raise
        finally:
            self._record(prompt, text, start, error)

    def stream_generate(
        self, prompt: str, max_new_tokens: int
    ) -> Iterator[str]:
        start = time.perf_counter()
        error: str | None = None
        chunks: list[str] = []
        try:
            for chunk in self._inner.stream_generate(prompt, max_new_tokens):
                chunks.append(chunk)
                yield chunk
        except Exception as exc:
            error = repr(exc)
            raise
        finally:
            self._record(prompt, "".join(chunks), start, error)

    def _record(
        self, prompt: str, text: str, start: float, error: str | None
    ) -> None:
        latency_ms = (time.perf_counter() - start) * 1000.0
        cache_hit = bool(
            isinstance(self._inner, CachingBackend)
            and self._inner.last_cache_hit
        )
        usage = self._inner.last_usage()
        if usage is not None:
            prompt_tokens: int | None = usage.prompt_tokens
            completion_tokens: int | None = usage.completion_tokens
            estimated = False
        else:
            prompt_tokens = estimate_tokens(prompt)
            completion_tokens = estimate_tokens(text)
            estimated = True
        try:
            self._telemetry.record(CallRecord(
                backend=self._inner.backend_kind(),
                model=self._inner.model_name(),
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                tokens_estimated=estimated,
                latency_ms=latency_ms,
                cache_hit=cache_hit,
                error=error,
            ))
        except Exception as telemetry_exc:  # never let telemetry break a review
            log.warning("Telemetry write failed: %s", telemetry_exc)

    def close(self) -> None:
        self._inner.close()


__all__ = ["CachingBackend", "InstrumentedBackend"]

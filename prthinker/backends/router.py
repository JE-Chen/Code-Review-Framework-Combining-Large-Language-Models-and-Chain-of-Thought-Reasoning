"""Fallback / escalation meta-backend over an ``InferenceBackend`` chain."""

from __future__ import annotations

import logging
from typing import Iterator

from prthinker.backends.base import InferenceBackend, Usage

log = logging.getLogger(__name__)

_BACKEND_KIND = "router"


class RouterBackend(InferenceBackend):
    """Try a primary backend, then fall over to ordered fallbacks.

    ``generate`` calls the primary first; on any ``Exception`` it walks the
    fallbacks in order, logging each failover, and re-raises the LAST
    exception if every backend fails. ``stream_generate`` delegates to the
    primary only — there is no failover mid-stream because chunks may
    already have been yielded to the caller. This is pure composition: it
    holds no transport of its own and is runner-safe.
    """

    def __init__(
        self,
        primary: InferenceBackend,
        fallbacks: tuple[InferenceBackend, ...] = (),
    ) -> None:
        self._primary = primary
        self._fallbacks = fallbacks

    def backend_kind(self) -> str:
        """Return the static router identifier for telemetry / cache keys."""
        return _BACKEND_KIND

    def model_name(self) -> str:
        """Return the primary backend's model name."""
        return self._primary.model_name()

    def last_usage(self) -> Usage | None:
        """Return the primary backend's most recent usage, if any."""
        return self._primary.last_usage()

    def generate(
        self,
        prompt: str,
        max_new_tokens: int,
        *,
        cancel_event: "object | None" = None,
    ) -> str:
        """Generate via the primary, falling over to each fallback in turn."""
        last_exc: Exception | None = None
        for index, backend in enumerate((self._primary, *self._fallbacks)):
            try:
                return backend.generate(
                    prompt, max_new_tokens, cancel_event=cancel_event
                )
            except Exception as exc:
                last_exc = exc
                log.warning(
                    "Backend %s (position %d) failed: %s; trying next",
                    backend.backend_kind(),
                    index,
                    exc,
                )
        if last_exc is not None:
            raise last_exc
        raise RuntimeError("RouterBackend has no backends to call")

    def stream_generate(
        self, prompt: str, max_new_tokens: int
    ) -> Iterator[str]:
        """Stream from the primary only; no mid-stream failover is attempted."""
        return self._primary.stream_generate(prompt, max_new_tokens)

    def close(self) -> None:
        """Close the primary and every fallback backend."""
        for backend in (self._primary, *self._fallbacks):
            backend.close()


__all__ = ["RouterBackend"]

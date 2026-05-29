"""Inference backend Strategy interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterator


@dataclass(frozen=True)
class Usage:
    """Token-count side channel populated by backends that report it.

    Set by ``OpenAICompatBackend`` and ``AnthropicBackend`` from the
    provider's ``usage`` block. ``LocalHFBackend`` and ``RemoteHttpBackend``
    leave it as ``None`` — the telemetry layer estimates from char counts.
    """

    prompt_tokens: int
    completion_tokens: int


class InferenceBackend(ABC):
    """A single-method interface for prompt-in / text-out generation.

    Implementations may run in-process (loading a local model) or proxy
    requests to a remote service. The pipeline depends only on this ABC.

    Backends that have authoritative token counts override
    ``last_usage`` to return the most recent ``Usage`` (cleared per call).
    """

    @abstractmethod
    def generate(
        self,
        prompt: str,
        max_new_tokens: int,
        *,
        cancel_event: "object | None" = None,
    ) -> str:
        """Generate text for ``prompt``.

        ``cancel_event`` is an optional threading.Event-like object that
        backends supporting mid-stream cancellation (the local HF
        backend) install as a stopping criterion checked between
        tokens. Remote / OpenAI / Anthropic backends accept and ignore
        the argument — the network call itself is uninterruptible.
        """

    def stream_generate(
        self, prompt: str, max_new_tokens: int
    ) -> Iterator[str]:
        """Yield incremental text chunks as they arrive.

        Default implementation falls back to a single full-response chunk
        — backends override when the underlying API supports streaming
        (OpenAI / Anthropic SSE). The pipeline can call this without
        worrying about whether streaming is genuinely incremental.
        """
        yield self.generate(prompt, max_new_tokens)

    def last_usage(self) -> Usage | None:
        return None

    def backend_kind(self) -> str:
        """Short identifier used for telemetry + cache keys."""
        return self.__class__.__name__

    def model_name(self) -> str:
        return ""

    def close(self) -> None:
        """Release any held resources. Default is a no-op."""
        return None

    def __enter__(self) -> "InferenceBackend":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

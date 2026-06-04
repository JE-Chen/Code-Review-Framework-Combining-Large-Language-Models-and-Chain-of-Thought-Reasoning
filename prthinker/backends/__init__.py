"""Backend factory — single entry point for instantiating inference backends.

Concrete backends are lazy-imported so that the runner profile
(``pip install -e ".[runner]"``) does not need torch / transformers when
the user picks an online backend.

The factory transparently stacks caching and telemetry wrappers around
the concrete backend whenever ``config.cache.enabled`` or
``config.telemetry.enabled`` is set.
"""

from __future__ import annotations

from pathlib import Path

from prthinker.backends.base import InferenceBackend
from prthinker.config import BackendKind, Config


def create_backend(config: Config) -> InferenceBackend:
    inner = _create_inner_backend(config)
    return _wrap(inner, config)


def _create_inner_backend(config: Config) -> InferenceBackend:
    if config.backend is BackendKind.LOCAL:
        from prthinker.backends.local import LocalHFBackend

        assert config.local is not None
        return LocalHFBackend(config.local)

    if config.backend is BackendKind.REMOTE:
        from prthinker.backends.remote import RemoteHttpBackend

        assert config.remote is not None
        return RemoteHttpBackend(config.remote)

    if config.backend is BackendKind.OPENAI:
        from prthinker.backends.openai_compat import OpenAICompatBackend

        assert config.openai is not None
        return OpenAICompatBackend(config.openai)

    if config.backend is BackendKind.ANTHROPIC:
        from prthinker.backends.anthropic import AnthropicBackend

        assert config.anthropic is not None
        return AnthropicBackend(config.anthropic)

    if config.backend is BackendKind.GEMINI:
        from prthinker.backends.gemini import GeminiBackend

        assert config.gemini is not None
        return GeminiBackend(
            model=config.gemini.model, api_key=config.gemini.api_key,
            base_url=config.gemini.base_url,
            timeout_seconds=config.gemini.timeout_seconds,
        )

    if config.backend is BackendKind.COHERE:
        from prthinker.backends.cohere import CohereBackend

        assert config.cohere is not None
        return CohereBackend(
            model=config.cohere.model, api_key=config.cohere.api_key,
            base_url=config.cohere.base_url,
            timeout_seconds=config.cohere.timeout_seconds,
        )

    if config.backend is BackendKind.MISTRAL:
        from prthinker.backends.mistral import MistralBackend

        assert config.mistral is not None
        return MistralBackend(
            model=config.mistral.model, api_key=config.mistral.api_key,
            base_url=config.mistral.base_url,
            timeout_seconds=config.mistral.timeout_seconds,
        )

    raise ValueError(f"Unsupported backend: {config.backend!r}")


def _wrap(inner: InferenceBackend, config: Config) -> InferenceBackend:
    wrapped: InferenceBackend = inner

    if config.cache.enabled:
        from prthinker.backends.wrappers import CachingBackend
        from prthinker.cache import PromptCache

        ttl = (
            None
            if config.cache.ttl_days is None
            else config.cache.ttl_days * 86400.0
        )
        cache = PromptCache(Path(config.cache.path), ttl_seconds=ttl)
        wrapped = CachingBackend(wrapped, cache)

    if config.telemetry.enabled:
        from prthinker.backends.wrappers import InstrumentedBackend
        from prthinker.telemetry import TelemetrySink

        sink = TelemetrySink(Path(config.telemetry.path))
        wrapped = InstrumentedBackend(wrapped, sink)

    return wrapped


__all__ = ["InferenceBackend", "create_backend"]

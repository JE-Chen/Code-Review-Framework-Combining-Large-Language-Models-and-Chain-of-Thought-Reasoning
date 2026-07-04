"""Backend factory — single entry point for instantiating inference backends.

Concrete backends are lazy-imported so that the runner profile
(``pip install -e ".[runner]"``) does not need torch / transformers when
the user picks an online backend.

The factory transparently stacks caching and telemetry wrappers around
the concrete backend whenever ``config.cache.enabled`` or
``config.telemetry.enabled`` is set.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from prthinker.backends.base import InferenceBackend
from prthinker.config import BackendKind, Config


def create_backend(config: Config) -> InferenceBackend:
    inner = _create_inner_backend(config)
    return _wrap(inner, config)


def _build_local(config: Config) -> InferenceBackend:
    """Instantiate the local Hugging Face backend."""
    from prthinker.backends.local import LocalHFBackend

    assert config.local is not None
    return LocalHFBackend(config.local)


def _build_remote(config: Config) -> InferenceBackend:
    """Instantiate the remote HTTP backend."""
    from prthinker.backends.remote import RemoteHttpBackend

    assert config.remote is not None
    return RemoteHttpBackend(config.remote)


def _build_openai(config: Config) -> InferenceBackend:
    """Instantiate the OpenAI-compatible backend."""
    from prthinker.backends.openai_compat import OpenAICompatBackend

    assert config.openai is not None
    return OpenAICompatBackend(config.openai)


def _build_anthropic(config: Config) -> InferenceBackend:
    """Instantiate the Anthropic backend."""
    from prthinker.backends.anthropic import AnthropicBackend

    assert config.anthropic is not None
    return AnthropicBackend(config.anthropic)


def _build_gemini(config: Config) -> InferenceBackend:
    """Instantiate the Gemini backend."""
    from prthinker.backends.gemini import GeminiBackend

    assert config.gemini is not None
    return GeminiBackend(
        model=config.gemini.model, api_key=config.gemini.api_key,
        base_url=config.gemini.base_url,
        timeout_seconds=config.gemini.timeout_seconds,
    )


def _build_cohere(config: Config) -> InferenceBackend:
    """Instantiate the Cohere backend."""
    from prthinker.backends.cohere import CohereBackend

    assert config.cohere is not None
    return CohereBackend(
        model=config.cohere.model, api_key=config.cohere.api_key,
        base_url=config.cohere.base_url,
        timeout_seconds=config.cohere.timeout_seconds,
    )


def _build_mistral(config: Config) -> InferenceBackend:
    """Instantiate the Mistral backend."""
    from prthinker.backends.mistral import MistralBackend

    assert config.mistral is not None
    return MistralBackend(
        model=config.mistral.model, api_key=config.mistral.api_key,
        base_url=config.mistral.base_url,
        timeout_seconds=config.mistral.timeout_seconds,
    )


def _build_claude_cli(config: Config) -> InferenceBackend:
    """Instantiate the Claude CLI backend."""
    from prthinker.backends.claude_cli import ClaudeCliBackend

    assert config.claude_cli is not None
    return ClaudeCliBackend(config.claude_cli)


def _build_codex_cli(config: Config) -> InferenceBackend:
    """Instantiate the codex CLI backend."""
    from prthinker.backends.codex_cli import CodexCliBackend

    assert config.codex_cli is not None
    return CodexCliBackend(config.codex_cli)


# Factory dispatch: one builder per backend kind. Each builder lazy-imports
# its concrete backend so the runner profile never pulls heavy deps for a
# backend the user did not select.
_BACKEND_BUILDERS: dict[BackendKind, Callable[[Config], InferenceBackend]] = {
    BackendKind.LOCAL: _build_local,
    BackendKind.REMOTE: _build_remote,
    BackendKind.OPENAI: _build_openai,
    BackendKind.ANTHROPIC: _build_anthropic,
    BackendKind.GEMINI: _build_gemini,
    BackendKind.COHERE: _build_cohere,
    BackendKind.MISTRAL: _build_mistral,
    BackendKind.CLAUDE_CLI: _build_claude_cli,
    BackendKind.CODEX_CLI: _build_codex_cli,
}


def _create_inner_backend(config: Config) -> InferenceBackend:
    """Dispatch to the builder registered for ``config.backend``."""
    try:
        builder = _BACKEND_BUILDERS[config.backend]
    except KeyError:
        raise ValueError(f"Unsupported backend: {config.backend!r}") from None
    return builder(config)


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

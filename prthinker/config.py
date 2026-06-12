"""Runtime configuration for PRThinker.

Configuration is loaded from CLI arguments first, then environment
variables. Fails fast on missing values that are required for the chosen
backend.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum


class BackendKind(str, Enum):
    LOCAL = "local"
    REMOTE = "remote"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    COHERE = "cohere"
    MISTRAL = "mistral"


@dataclass(frozen=True)
class LocalBackendConfig:
    """Local in-process HF causal-LM. Works with any chat-tuned HF id."""

    model_name: str = "Qwen/Qwen3-Coder-30B-A3B-Instruct"
    lora_path: str | None = None
    quantization: bool = True


def _normalize_remote_url(url: str) -> str:
    """Return ``url`` with an http(s) scheme, defaulting to https when absent.

    httpx requires an explicit scheme; a bare host (``PRTHINKER_REMOTE_URL=
    "host:9000"``) otherwise dies deep in httpx with "Request URL is missing
    an 'http://' or 'https://' protocol". An explicit ``http://`` or
    ``https://`` is respected (``http://`` covers a no-TLS tunnel); any other
    scheme is rejected per the HTTPS-only outbound rule.
    """
    cleaned = (url or "").strip()
    if not cleaned:
        raise ValueError("RemoteBackendConfig.url is required")
    if cleaned.lower().startswith(("http://", "https://")):
        return cleaned
    scheme_sep = cleaned.find("://")
    if scheme_sep != -1:
        scheme = cleaned[:scheme_sep]
        raise ValueError(
            f"RemoteBackendConfig.url scheme must be http or https, got {scheme!r}"
        )
    return f"https://{cleaned}"


@dataclass(frozen=True)
class RemoteBackendConfig:
    """Self-hosted FastAPI server (the project's own /ask + /review)."""

    url: str
    timeout_seconds: float = 3600.0
    api_key: str | None = None

    def __post_init__(self) -> None:
        # Normalise the URL at the boundary so every downstream httpx client
        # gets a scheme-qualified value (frozen dataclass -> object.__setattr__).
        object.__setattr__(self, "url", _normalize_remote_url(self.url))


@dataclass(frozen=True)
class OpenAICompatConfig:
    """Any OpenAI-Chat-Completions-compatible endpoint.

    Covers OpenAI, Azure OpenAI, vLLM, LM Studio, llama.cpp server's /v1,
    Ollama /v1, Together AI, Groq, DeepInfra, OpenRouter, etc.
    """

    model: str
    api_key: str
    base_url: str = "https://api.openai.com/v1"
    organization: str | None = None
    timeout_seconds: float = 3600.0
    temperature: float = 0.0

    def __post_init__(self) -> None:
        if not self.model:
            raise ValueError("OpenAICompatConfig.model is required")
        if not self.api_key:
            raise ValueError("OpenAICompatConfig.api_key is required")
        if not self.base_url:
            raise ValueError("OpenAICompatConfig.base_url is required")


@dataclass(frozen=True)
class AnthropicConfig:
    """Anthropic Messages API."""

    model: str
    api_key: str
    base_url: str = "https://api.anthropic.com"
    anthropic_version: str = "2023-06-01"
    timeout_seconds: float = 3600.0
    temperature: float = 0.0

    def __post_init__(self) -> None:
        if not self.model:
            raise ValueError("AnthropicConfig.model is required")
        if not self.api_key:
            raise ValueError("AnthropicConfig.api_key is required")


@dataclass(frozen=True)
class GeminiConfig:
    """Google Generative Language (Gemini) REST API."""

    model: str
    api_key: str
    base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    timeout_seconds: float = 3600.0

    def __post_init__(self) -> None:
        if not self.model:
            raise ValueError("GeminiConfig.model is required")
        if not self.api_key:
            raise ValueError("GeminiConfig.api_key is required")


@dataclass(frozen=True)
class CohereConfig:
    """Cohere Chat API v2."""

    model: str
    api_key: str
    base_url: str = "https://api.cohere.com"
    timeout_seconds: float = 3600.0

    def __post_init__(self) -> None:
        if not self.model:
            raise ValueError("CohereConfig.model is required")
        if not self.api_key:
            raise ValueError("CohereConfig.api_key is required")


@dataclass(frozen=True)
class MistralConfig:
    """Mistral chat-completions API (OpenAI-shaped)."""

    model: str
    api_key: str
    base_url: str = "https://api.mistral.ai/v1"
    timeout_seconds: float = 3600.0

    def __post_init__(self) -> None:
        if not self.model:
            raise ValueError("MistralConfig.model is required")
        if not self.api_key:
            raise ValueError("MistralConfig.api_key is required")


@dataclass(frozen=True)
class GitHubConfig:
    repo: str
    pr_number: int
    token: str
    comment_marker: str = "<!-- prthinker:summary -->"

    def __post_init__(self) -> None:
        if "/" not in self.repo:
            raise ValueError(
                f"GitHubConfig.repo must be 'owner/name', got {self.repo!r}"
            )
        if not self.token:
            raise ValueError("GitHubConfig.token is required")


@dataclass(frozen=True)
class CacheConfig:
    enabled: bool = False
    path: str = ".prthinker/cache.sqlite"
    ttl_days: float | None = 7.0


@dataclass(frozen=True)
class TelemetryConfig:
    enabled: bool = False
    path: str = ".prthinker/telemetry.sqlite"


@dataclass(frozen=True)
class Config:
    backend: BackendKind
    local: LocalBackendConfig | None = None
    remote: RemoteBackendConfig | None = None
    openai: OpenAICompatConfig | None = None
    anthropic: AnthropicConfig | None = None
    gemini: GeminiConfig | None = None
    cohere: CohereConfig | None = None
    mistral: MistralConfig | None = None
    rag_enabled: bool = True
    # None = resolve per context: the local FAISS retriever picks the
    # calibrated threshold for the active embedding model; remote calls
    # send the historical 0.7 (the server pins the qwen-era index).
    rag_threshold: float | None = None
    max_new_tokens: int = 32768
    steps: tuple[str, ...] = field(default_factory=tuple)
    cache: CacheConfig = field(default_factory=CacheConfig)
    telemetry: TelemetryConfig = field(default_factory=TelemetryConfig)

    def __post_init__(self) -> None:
        required = {
            BackendKind.LOCAL: ("local", self.local),
            BackendKind.REMOTE: ("remote", self.remote),
            BackendKind.OPENAI: ("openai", self.openai),
            BackendKind.ANTHROPIC: ("anthropic", self.anthropic),
            BackendKind.GEMINI: ("gemini", self.gemini),
            BackendKind.COHERE: ("cohere", self.cohere),
            BackendKind.MISTRAL: ("mistral", self.mistral),
        }
        name, value = required[self.backend]
        if value is None:
            raise ValueError(f"{name} config required when backend={self.backend.value}")


def env_str(name: str, default: str | None = None) -> str | None:
    value = os.environ.get(name)
    return value if value else default


def env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}

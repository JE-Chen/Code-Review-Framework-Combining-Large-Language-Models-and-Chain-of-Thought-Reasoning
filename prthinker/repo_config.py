"""Repo-level ``.prthinker.yaml`` schema and loader.

A YAML file at the repo root that pins every prthinker setting except
secrets — those still come from environment variables so a config that
gets committed never leaks an API key.

Resolution order (highest priority last):

1. Package defaults.
2. Values from ``.prthinker.yaml`` (or the path passed to ``--config``).
3. Environment variables.
4. Command-line arguments.

The loader returns plain dictionaries that the CLI merges into argparse
defaults — it does not bypass argparse, so ``--help`` still reflects
every option.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field

log = logging.getLogger(__name__)

REPO_CONFIG_FILENAME = ".prthinker.yaml"


class _RagSection(BaseModel):
    enabled: bool = True
    threshold: float = 0.7
    rules_dir: str | None = None
    remote: bool = False

    model_config = ConfigDict(extra="forbid")


class _GateSection(BaseModel):
    # ``severity`` not ``on`` to avoid YAML 1.1's implicit booleans
    # (``on: error`` is parsed as ``True: error``).
    severity: str = "none"  # "none" | "warning" | "error"

    model_config = ConfigDict(extra="forbid")


class _CISignalsSection(BaseModel):
    enabled: bool = False
    max_jobs: int = 5
    tail_chars: int = 4000

    model_config = ConfigDict(extra="forbid")


class _CacheSection(BaseModel):
    enabled: bool = False
    path: str = ".prthinker/cache.sqlite"
    ttl_days: float | None = 7.0

    model_config = ConfigDict(extra="forbid")


class _TelemetrySection(BaseModel):
    enabled: bool = False
    path: str = ".prthinker/telemetry.sqlite"

    model_config = ConfigDict(extra="forbid")


class _StoresSection(BaseModel):
    dismissed: str | None = None
    accepted: str | None = None

    model_config = ConfigDict(extra="forbid")


class _LocalSection(BaseModel):
    model: str = "Qwen/Qwen3-Coder-30B-A3B-Instruct"
    lora_path: str | None = None

    model_config = ConfigDict(extra="forbid")


class _OpenAISection(BaseModel):
    model: str = "gpt-4o-mini"
    base_url: str = "https://api.openai.com/v1"
    organization: str | None = None

    model_config = ConfigDict(extra="forbid")


class _AnthropicSection(BaseModel):
    model: str = "claude-opus-4-7"
    base_url: str = "https://api.anthropic.com"
    version: str = "2023-06-01"

    model_config = ConfigDict(extra="forbid")


class _RemoteSection(BaseModel):
    url: str | None = None
    timeout_seconds: float = 600.0
    use_pipeline_endpoint: bool = True

    model_config = ConfigDict(extra="forbid")


class RepoConfig(BaseModel):
    """The full ``.prthinker.yaml`` schema."""

    backend: str = "remote"  # local | remote | openai | anthropic
    max_new_tokens: int = 16384
    per_file: bool = False
    inline_review: bool = False
    max_findings_per_file: int = 10

    rag: _RagSection = Field(default_factory=_RagSection)
    gate: _GateSection = Field(default_factory=_GateSection)
    ci_signals: _CISignalsSection = Field(default_factory=_CISignalsSection)
    cache: _CacheSection = Field(default_factory=_CacheSection)
    telemetry: _TelemetrySection = Field(default_factory=_TelemetrySection)
    stores: _StoresSection = Field(default_factory=_StoresSection)

    local: _LocalSection = Field(default_factory=_LocalSection)
    openai: _OpenAISection = Field(default_factory=_OpenAISection)
    anthropic: _AnthropicSection = Field(default_factory=_AnthropicSection)
    remote: _RemoteSection = Field(default_factory=_RemoteSection)

    model_config = ConfigDict(extra="forbid")


@dataclass
class FlattenedDefaults:
    """argparse-friendly dict of defaults derived from a ``RepoConfig``."""

    values: dict[str, Any] = field(default_factory=dict)


def find_config_file(explicit: Path | None = None) -> Path | None:
    """Resolve which YAML to load.

    ``explicit`` (from ``--config``) wins; otherwise look for
    ``.prthinker.yaml`` in the current working directory.
    """
    if explicit is not None:
        if not explicit.exists():
            raise FileNotFoundError(explicit)
        return explicit
    default = Path.cwd() / REPO_CONFIG_FILENAME
    return default if default.exists() else None


def load_repo_config(path: Path) -> RepoConfig:
    raw = path.read_text(encoding="utf-8")
    data = yaml.safe_load(raw) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path}: top-level YAML must be a mapping")
    return RepoConfig.model_validate(data)


def to_argparse_defaults(cfg: RepoConfig) -> dict[str, Any]:
    """Map a ``RepoConfig`` to the dict of argparse ``--flag`` defaults.

    Keys match argparse ``dest`` (``--max-new-tokens`` → ``max_new_tokens``).
    The CLI calls ``set_defaults(**values)`` so user args still win.
    """
    flat: dict[str, Any] = {
        "backend": cfg.backend,
        "max_new_tokens": cfg.max_new_tokens,
        "per_file": cfg.per_file,
        "inline_review": cfg.inline_review,
        "max_findings_per_file": cfg.max_findings_per_file,
        "no_rag": not cfg.rag.enabled,
        "rag_threshold": cfg.rag.threshold,
        "remote_rag": cfg.rag.remote,
        "gate_on": cfg.gate.severity,
        "include_ci_signals": cfg.ci_signals.enabled,
        "ci_signal_max_jobs": cfg.ci_signals.max_jobs,
        "ci_signal_tail_chars": cfg.ci_signals.tail_chars,
        "cache_enabled": cfg.cache.enabled,
        "cache_path": cfg.cache.path,
        "cache_ttl_days": cfg.cache.ttl_days,
        "telemetry_enabled": cfg.telemetry.enabled,
        "telemetry_path": cfg.telemetry.path,
        "model_name": cfg.local.model,
        "lora_path": cfg.local.lora_path,
        "openai_model": cfg.openai.model,
        "openai_base_url": cfg.openai.base_url,
        "openai_organization": cfg.openai.organization,
        "anthropic_model": cfg.anthropic.model,
        "anthropic_base_url": cfg.anthropic.base_url,
        "anthropic_version": cfg.anthropic.version,
        "remote_url": cfg.remote.url,
        "remote_timeout": cfg.remote.timeout_seconds,
        "use_remote_pipeline": cfg.remote.use_pipeline_endpoint,
    }
    if cfg.rag.rules_dir is not None:
        flat["rules_dir"] = Path(cfg.rag.rules_dir)
    # Strip Nones so argparse keeps its own defaults for unset YAML keys.
    return {k: v for k, v in flat.items() if v is not None}


__all__ = [
    "REPO_CONFIG_FILENAME",
    "RepoConfig",
    "find_config_file",
    "load_repo_config",
    "to_argparse_defaults",
]

"""Backend sub-config builders and dialogue-block assembly for ``cli_review``.

Imported only by ``prthinker.cli_review``; split out to keep that module
under the per-file line cap.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from prthinker.config import (
    AnthropicConfig,
    BackendKind,
    CacheConfig,
    CohereConfig,
    GeminiConfig,
    LocalBackendConfig,
    MistralConfig,
    OpenAICompatConfig,
    RemoteBackendConfig,
    TelemetryConfig,
)
from prthinker.repo_kg import (
    KnowledgeGraphStore,
    format_kg_block,
)

log = logging.getLogger("prthinker")


def _local_backend_config(
    args: argparse.Namespace,
) -> tuple[str, LocalBackendConfig]:
    """Build the LOCAL backend sub-config from CLI args."""
    return "local", LocalBackendConfig(
        model_name=args.model_name,
        lora_path=args.lora_path,
    )


def _remote_backend_config(
    args: argparse.Namespace,
) -> tuple[str, RemoteBackendConfig]:
    """Build the REMOTE backend sub-config; raise on missing URL."""
    if not args.remote_url:
        raise SystemExit(
            "remote backend requires --remote-url or PRTHINKER_REMOTE_URL"
        )
    return "remote", RemoteBackendConfig(
        url=args.remote_url,
        timeout_seconds=args.remote_timeout,
        api_key=args.remote_api_key,
    )


def _openai_backend_config(
    args: argparse.Namespace,
) -> tuple[str, OpenAICompatConfig]:
    """Build the OPENAI backend sub-config; raise on missing API key."""
    if not args.openai_api_key:
        raise SystemExit(
            "openai backend requires --openai-api-key or "
            "$PRTHINKER_OPENAI_API_KEY / $OPENAI_API_KEY"
        )
    return "openai", OpenAICompatConfig(
        model=args.openai_model,
        api_key=args.openai_api_key,
        base_url=args.openai_base_url,
        organization=args.openai_organization,
        timeout_seconds=args.remote_timeout,
    )


def _anthropic_backend_config(
    args: argparse.Namespace,
) -> tuple[str, AnthropicConfig]:
    """Build the ANTHROPIC backend sub-config; raise on missing API key."""
    if not args.anthropic_api_key:
        raise SystemExit(
            "anthropic backend requires --anthropic-api-key or "
            "$PRTHINKER_ANTHROPIC_API_KEY / $ANTHROPIC_API_KEY"
        )
    return "anthropic", AnthropicConfig(
        model=args.anthropic_model,
        api_key=args.anthropic_api_key,
        base_url=args.anthropic_base_url,
        anthropic_version=args.anthropic_version,
        timeout_seconds=args.remote_timeout,
    )


def _gemini_backend_config(
    args: argparse.Namespace,
) -> tuple[str, GeminiConfig]:
    """Build the GEMINI backend sub-config; raise on missing API key."""
    if not args.gemini_api_key:
        raise SystemExit(
            "gemini backend requires --gemini-api-key or "
            "$PRTHINKER_GEMINI_API_KEY / $GEMINI_API_KEY / $GOOGLE_API_KEY"
        )
    return "gemini", GeminiConfig(
        model=args.gemini_model,
        api_key=args.gemini_api_key,
        base_url=args.gemini_base_url,
        timeout_seconds=args.remote_timeout,
    )


def _cohere_backend_config(
    args: argparse.Namespace,
) -> tuple[str, CohereConfig]:
    """Build the COHERE backend sub-config; raise on missing API key."""
    if not args.cohere_api_key:
        raise SystemExit(
            "cohere backend requires --cohere-api-key or "
            "$PRTHINKER_COHERE_API_KEY / $COHERE_API_KEY"
        )
    return "cohere", CohereConfig(
        model=args.cohere_model,
        api_key=args.cohere_api_key,
        base_url=args.cohere_base_url,
        timeout_seconds=args.remote_timeout,
    )


def _mistral_backend_config(
    args: argparse.Namespace,
) -> tuple[str, MistralConfig]:
    """Build the MISTRAL backend sub-config; raise on missing API key."""
    if not args.mistral_api_key:
        raise SystemExit(
            "mistral backend requires --mistral-api-key or "
            "$PRTHINKER_MISTRAL_API_KEY / $MISTRAL_API_KEY"
        )
    return "mistral", MistralConfig(
        model=args.mistral_model,
        api_key=args.mistral_api_key,
        base_url=args.mistral_base_url,
        timeout_seconds=args.remote_timeout,
    )


BACKEND_CONFIG_BUILDERS = {
    BackendKind.LOCAL: _local_backend_config,
    BackendKind.REMOTE: _remote_backend_config,
    BackendKind.OPENAI: _openai_backend_config,
    BackendKind.ANTHROPIC: _anthropic_backend_config,
    BackendKind.GEMINI: _gemini_backend_config,
    BackendKind.COHERE: _cohere_backend_config,
    BackendKind.MISTRAL: _mistral_backend_config,
}


def build_cache_telemetry(
    args: argparse.Namespace,
) -> tuple[CacheConfig, TelemetryConfig]:
    """Build the CacheConfig / TelemetryConfig pair from CLI args."""
    cache_cfg = CacheConfig(
        enabled=bool(getattr(args, "cache_enabled", False)),
        path=str(getattr(args, "cache_path", ".prthinker/cache.sqlite")),
        ttl_days=(
            None
            if getattr(args, "cache_ttl_days", 7.0) in (None, 0, 0.0)
            else float(getattr(args, "cache_ttl_days", 7.0))
        ),
    )
    telemetry_cfg = TelemetryConfig(
        enabled=bool(getattr(args, "telemetry_enabled", False)),
        path=str(getattr(args, "telemetry_path", ".prthinker/telemetry.sqlite")),
    )
    return cache_cfg, telemetry_cfg


def _dialogue_from_replies(adapter: object) -> str:
    """Render the author-reply dialogue block; tolerate fetch failure."""
    try:
        replies = adapter.fetch_author_replies()
    except Exception as exc:
        log.warning("Failed to fetch author replies (%s); skipping dialogue", exc)
        return ""
    if not replies:
        return ""
    from prthinker.dialogue import render_dialogue_block
    log.info("Injecting %d author reply(ies) into inline-findings prompt", len(replies))
    return render_dialogue_block(replies)


def _dialogue_from_lessons(args: argparse.Namespace) -> str:
    """Render the derived-lessons block from the lessons store."""
    lessons_path = Path(getattr(args, "lessons_path", "") or ".prthinker/lessons.jsonl")
    if not lessons_path.exists():
        return ""
    from prthinker.lessons import LessonsStore, format_lessons_block
    top_k = int(getattr(args, "lessons_top_k", 5) or 5)
    recent = list(LessonsStore(lessons_path))[-top_k:]
    block = format_lessons_block(recent)
    if block:
        log.info("Injecting %d derived lesson(s) into inline-findings prompt", len(recent))
    return block


def _dialogue_from_kg(args: argparse.Namespace) -> str:
    """Render the repo knowledge-graph symbol block."""
    kg_store_path = Path(getattr(args, "kg_store", "") or ".prthinker/repo-kg.sqlite")
    if not kg_store_path.exists():
        return ""
    kg_workdir = Path(getattr(args, "kg_workdir", "") or ".")
    symbols = KnowledgeGraphStore(kg_store_path).all_symbols(kg_workdir)
    block = format_kg_block(symbols)
    if block:
        log.info("Injecting %d known symbol(s) into inline-findings prompt", len(symbols))
    return block


def build_dialogue_block(args: argparse.Namespace, adapter: object) -> str:
    """Assemble the inline-findings context from replies, lessons, and KG."""
    if not args.inline_review:
        return ""
    block = _dialogue_from_replies(adapter) if getattr(args, "reply_to_author", False) else ""
    if getattr(args, "lessons", False):
        lessons = _dialogue_from_lessons(args)
        if lessons:
            block = (lessons + "\n\n" + block).strip()
    if getattr(args, "kg_ground", False):
        kg = _dialogue_from_kg(args)
        if kg:
            block = (kg + "\n\n" + block).strip()
    return block

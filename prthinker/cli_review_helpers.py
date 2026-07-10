"""Backend sub-config builders and dialogue-block assembly for ``cli_review``.

Imported only by ``prthinker.cli_review``; split out to keep that module
under the per-file line cap.
"""

from __future__ import annotations

import argparse
import logging
from collections import deque
from pathlib import Path

from prthinker.arbitration import (
    FindingArbitrator,
    create_arbitration_strategy,
)
from prthinker.backends import InferenceBackend, create_backend
from prthinker.config import (
    CACHE_DEFAULT,
    KG_STORE_DEFAULT,
    LESSONS_DEFAULT,
    TELEMETRY_DEFAULT,
    AnthropicConfig,
    BackendKind,
    CacheConfig,
    ClaudeCliConfig,
    CodexCliConfig,
    CohereConfig,
    Config,
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


def _claude_cli_backend_config(
    args: argparse.Namespace,
) -> tuple[str, ClaudeCliConfig]:
    """Build the CLAUDE_CLI backend sub-config from CLI args."""
    return "claude_cli", ClaudeCliConfig(
        executable=args.claude_cli_path,
        model=args.claude_cli_model,
        working_dir=args.claude_cli_workdir,
        allowed_tools=args.claude_cli_allowed_tools,
        timeout_seconds=args.claude_cli_timeout,
    )


def _codex_cli_backend_config(
    args: argparse.Namespace,
) -> tuple[str, CodexCliConfig]:
    """Build the CODEX_CLI backend sub-config from CLI args."""
    return "codex_cli", CodexCliConfig(
        executable=args.codex_cli_path,
        model=args.codex_cli_model,
        working_dir=args.codex_cli_workdir,
        sandbox_mode=args.codex_cli_sandbox,
        timeout_seconds=args.codex_cli_timeout,
    )


BACKEND_CONFIG_BUILDERS = {
    BackendKind.LOCAL: _local_backend_config,
    BackendKind.REMOTE: _remote_backend_config,
    BackendKind.OPENAI: _openai_backend_config,
    BackendKind.ANTHROPIC: _anthropic_backend_config,
    BackendKind.GEMINI: _gemini_backend_config,
    BackendKind.COHERE: _cohere_backend_config,
    BackendKind.MISTRAL: _mistral_backend_config,
    BackendKind.CLAUDE_CLI: _claude_cli_backend_config,
    BackendKind.CODEX_CLI: _codex_cli_backend_config,
}


def build_cache_telemetry(
    args: argparse.Namespace,
) -> tuple[CacheConfig, TelemetryConfig]:
    """Build the CacheConfig / TelemetryConfig pair from CLI args."""
    cache_cfg = CacheConfig(
        enabled=bool(getattr(args, "cache_enabled", False)),
        path=str(getattr(args, "cache_path", CACHE_DEFAULT)),
        ttl_days=(
            None
            if getattr(args, "cache_ttl_days", 7.0) in (None, 0, 0.0)
            else float(getattr(args, "cache_ttl_days", 7.0))
        ),
    )
    telemetry_cfg = TelemetryConfig(
        enabled=bool(getattr(args, "telemetry_enabled", False)),
        path=str(getattr(args, "telemetry_path", TELEMETRY_DEFAULT)),
    )
    return cache_cfg, telemetry_cfg


def build_platform_adapter(args: argparse.Namespace) -> object:
    """Create the forge adapter every PR-facing command shares.

    Imported lazily so tests can monkeypatch
    ``prthinker.platforms.create_platform_adapter`` and so the platforms
    package stays off the import path of non-PR commands.
    """
    from prthinker.platforms import PlatformKind, create_platform_adapter

    return create_platform_adapter(
        PlatformKind(args.platform),
        repo=args.repo,
        token=args.github_token,
        pr_number=args.pr_number,
        comment_marker=args.marker,
        base_url=args.platform_base_url,
    )


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
    lessons_path = Path(getattr(args, "lessons_path", "") or LESSONS_DEFAULT)
    if not lessons_path.exists():
        return ""
    from prthinker.lessons import LessonsStore, format_lessons_block
    top_k = int(getattr(args, "lessons_top_k", 5) or 5)
    # deque(maxlen=k) keeps only the corpus tail without materializing the
    # whole append-only store in memory.
    recent = list(deque(LessonsStore(lessons_path), maxlen=top_k))
    block = format_lessons_block(recent)
    if block:
        log.info("Injecting %d derived lesson(s) into inline-findings prompt", len(recent))
    return block


def _dialogue_from_kg(args: argparse.Namespace) -> str:
    """Render the repo knowledge-graph symbol block."""
    kg_store_path = Path(getattr(args, "kg_store", "") or KG_STORE_DEFAULT)
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


# --- multi-model arbitration wiring ---------------------------------------


def _split_arbiter_kinds(raw: str) -> list[BackendKind]:
    """Parse the comma-separated --arbitration-backends value."""
    kinds: list[BackendKind] = []
    for token in (raw or "").split(","):
        name = token.strip()
        if not name:
            continue
        try:
            kinds.append(BackendKind(name))
        except ValueError:
            raise SystemExit(
                f"unknown arbitration backend kind: {name!r}"
            ) from None
    return kinds


def _build_arbiter_backends(args: argparse.Namespace) -> list[InferenceBackend]:
    """Instantiate one backend per --arbitration-backends entry.

    Each arbiter reuses the same flags / env vars it would use as the
    primary backend; cache and telemetry wrappers stay off so votes are
    never memoized against a stale diff.
    """
    backends: list[InferenceBackend] = []
    for kind in _split_arbiter_kinds(getattr(args, "arbitration_backends", "")):
        field_name, sub_config = BACKEND_CONFIG_BUILDERS[kind](args)
        config = Config(backend=kind, **{field_name: sub_config})
        backends.append(create_backend(config))
    return backends


def _filter_per_file_findings(result: object, kept: list) -> None:
    """Restrict every per-file finding list to the arbitration survivors."""
    kept_ids = {id(f) for f in kept}
    for file_result in result.per_file:
        file_result.inline_findings = [
            f for f in file_result.inline_findings if id(f) in kept_ids
        ]


def apply_arbitration(args: argparse.Namespace, result: object) -> None:
    """Run the opt-in multi-model arbitration pass over ``result`` in place.

    No-op unless ``--arbitration`` is set and the review produced
    findings. Arbiter backends are built fresh per run and always closed.
    """
    if not getattr(args, "arbitration", False) or not result.inline_findings:
        return
    backends = _build_arbiter_backends(args)
    if not backends:
        log.warning(
            "--arbitration set but --arbitration-backends is empty; skipping"
        )
        return
    strategy = create_arbitration_strategy(
        getattr(args, "arbitration_strategy", "majority")
    )
    arbitrator = FindingArbitrator(
        backends, strategy,
        max_new_tokens=int(getattr(args, "arbitration_max_new_tokens", 4096)),
    )
    try:
        outcome = arbitrator.arbitrate(result.inline_findings, result.code_diff)
    finally:
        for backend in backends:
            backend.close()
    result.inline_findings = outcome.kept
    _filter_per_file_findings(result, outcome.kept)
    log.info(
        "Arbitration kept %d and dropped %d finding(s) "
        "[strategy=%s, arbiters=%d]",
        len(outcome.kept), len(outcome.dropped),
        strategy.name, len(backends),
    )

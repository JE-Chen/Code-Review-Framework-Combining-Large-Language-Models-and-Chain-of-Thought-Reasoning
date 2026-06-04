"""Model Context Protocol (MCP) server adapter.

Exposes the prthinker pipeline as MCP tools so any MCP-compatible
client — Claude Desktop, Cursor, Continue, Cline, Zed, etc. — can drive
reviews from inside the IDE.

The server is a stdio process: clients launch ``prthinker mcp``,
exchange JSON-RPC over the subprocess's stdin/stdout, and the LLM
inside the client decides when to invoke a tool.

Backend configuration is read from the same environment variables the
CLI uses (``PRTHINKER_BACKEND``, ``OPENAI_API_KEY``, …) — there is no
MCP-specific config layer, so docs and ``.prthinker.yaml`` apply.

The ``mcp`` SDK is an optional dependency; install with
``pip install -e ".[mcp]"``.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from prthinker.config import (
    AnthropicConfig,
    BackendKind,
    CacheConfig,
    Config,
    LocalBackendConfig,
    OpenAICompatConfig,
    RemoteBackendConfig,
    TelemetryConfig,
    env_bool,
    env_str,
)

log = logging.getLogger(__name__)

_DEFAULT_OPENAI_BASE_URL = "https://api.openai.com/v1"
_DEFAULT_ANTHROPIC_BASE_URL = "https://api.anthropic.com"


def _read_timeout() -> float:
    """Resolve the shared remote/provider request timeout in seconds."""
    return float(env_str("PRTHINKER_REMOTE_TIMEOUT", "600") or 600)


def _local_config() -> LocalBackendConfig:
    """Build the local-backend config from environment variables."""
    return LocalBackendConfig(
        model_name=env_str("PRTHINKER_MODEL_NAME",
                            "Qwen/Qwen3-Coder-30B-A3B-Instruct") or "",
        lora_path=env_str("PRTHINKER_LORA_PATH"),
    )


def _remote_config(timeout: float) -> RemoteBackendConfig:
    """Build the remote-backend config; require an explicit URL."""
    url = env_str("PRTHINKER_REMOTE_URL")
    if not url:
        raise RuntimeError("PRTHINKER_REMOTE_URL is required for remote backend")
    return RemoteBackendConfig(
        url=url, timeout_seconds=timeout,
        api_key=env_str("PRTHINKER_REMOTE_API_KEY"),
    )


def _openai_config(timeout: float) -> OpenAICompatConfig:
    """Build the OpenAI-compatible backend config; require an API key."""
    key = env_str("PRTHINKER_OPENAI_API_KEY") or env_str("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is required for openai backend")
    return OpenAICompatConfig(
        model=env_str("PRTHINKER_OPENAI_MODEL", "gpt-4o-mini") or "gpt-4o-mini",
        api_key=key,
        base_url=env_str("PRTHINKER_OPENAI_BASE_URL",
                          _DEFAULT_OPENAI_BASE_URL) or _DEFAULT_OPENAI_BASE_URL,
        organization=env_str("PRTHINKER_OPENAI_ORGANIZATION")
                          or env_str("OPENAI_ORG_ID"),
        timeout_seconds=timeout,
    )


def _anthropic_config(timeout: float) -> AnthropicConfig:
    """Build the Anthropic backend config; require an API key."""
    key = env_str("PRTHINKER_ANTHROPIC_API_KEY") or env_str("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY is required for anthropic backend")
    return AnthropicConfig(
        model=env_str("PRTHINKER_ANTHROPIC_MODEL", "claude-opus-4-7")
                   or "claude-opus-4-7",
        api_key=key,
        base_url=env_str("PRTHINKER_ANTHROPIC_BASE_URL",
                          _DEFAULT_ANTHROPIC_BASE_URL) or _DEFAULT_ANTHROPIC_BASE_URL,
        anthropic_version=env_str("PRTHINKER_ANTHROPIC_VERSION",
                                   "2023-06-01") or "2023-06-01",
        timeout_seconds=timeout,
    )


def _cache_config() -> CacheConfig:
    """Build the prompt-cache config from environment variables."""
    return CacheConfig(
        enabled=env_bool("PRTHINKER_CACHE_ENABLED", False),
        path=env_str("PRTHINKER_CACHE_PATH", ".prthinker/cache.sqlite")
              or ".prthinker/cache.sqlite",
    )


def _telemetry_config() -> TelemetryConfig:
    """Build the telemetry config from environment variables."""
    return TelemetryConfig(
        enabled=env_bool("PRTHINKER_TELEMETRY_ENABLED", False),
        path=env_str("PRTHINKER_TELEMETRY_PATH", ".prthinker/telemetry.sqlite")
              or ".prthinker/telemetry.sqlite",
    )


def _config_from_env() -> Config:
    """Replicate the CLI's environment-driven Config construction.

    Intentionally separate from ``cli._build_config`` because MCP has no
    argparse layer — only env vars (and, transitively, ``.prthinker.yaml``
    if the runner pre-sourced it).
    """
    backend_str = env_str("PRTHINKER_BACKEND", BackendKind.REMOTE.value) or "remote"
    backend = BackendKind(backend_str)
    timeout = _read_timeout()

    builders = {
        BackendKind.LOCAL: lambda: ("local", _local_config()),
        BackendKind.REMOTE: lambda: ("remote", _remote_config(timeout)),
        BackendKind.OPENAI: lambda: ("openai", _openai_config(timeout)),
        BackendKind.ANTHROPIC: lambda: ("anthropic", _anthropic_config(timeout)),
    }
    kwargs: dict[str, object] = {
        "local": None, "remote": None, "openai": None, "anthropic": None,
    }
    builder = builders.get(backend)
    if builder is not None:
        field, cfg = builder()
        kwargs[field] = cfg

    return Config(
        backend=backend,
        local=kwargs["local"],
        remote=kwargs["remote"],
        openai=kwargs["openai"],
        anthropic=kwargs["anthropic"],
        rag_enabled=env_bool("PRTHINKER_RAG_ENABLED", True),
        rag_threshold=float(env_str("PRTHINKER_RAG_THRESHOLD", "0.7") or 0.7),
        max_new_tokens=int(env_str("PRTHINKER_MAX_NEW_TOKENS", "32768") or 32768),
        cache=_cache_config(),
        telemetry=_telemetry_config(),
    )


def run() -> int:
    """Entry point for ``prthinker mcp``. Blocks until the client disconnects."""
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:  # pragma: no cover — guarded by the dep
        sys.stderr.write(
            "The `mcp` package is not installed. Install with\n"
            "    pip install -e \".[mcp]\"\n"
            f"Original error: {exc}\n"
        )
        return 1

    from prthinker.backends import create_backend
    from prthinker.formatters import format_pr_comment
    from prthinker.pipeline import CoTPipeline
    from prthinker.rag import NoOpRetriever
    from prthinker.redaction import redact

    config = _config_from_env()
    backend = create_backend(config)
    retriever = NoOpRetriever()  # RAG over local FAISS isn't sensible from an IDE call

    pipeline = CoTPipeline(
        backend=backend,
        retriever=retriever,
        max_new_tokens=config.max_new_tokens,
    )

    mcp = FastMCP("prthinker")

    @mcp.tool()
    def review_diff(
        diff: str,
        file_path: str | None = None,
        redact_secrets: bool = True,
    ) -> str:
        """Run the CoT pipeline against a unified diff.

        Args:
            diff: The unified diff text (output of ``git diff``).
            file_path: Optional hint for inline-findings context.
            redact_secrets: If True (default), scrub well-known secret
                patterns before any backend call. Strongly recommended
                when the backend is a paid third-party API.

        Returns:
            A markdown review (the same body that would land in the PR
            comment) — collapsible sections per step, plus a per-file
            block when ``file_path`` is set.
        """
        if redact_secrets:
            diff, report = redact(diff)
            if report:
                log.warning("MCP redaction: %s", report.summary())
        if file_path:
            result = pipeline.run_per_file(diff, inline_review=False)
        else:
            from prthinker.pipeline import ReviewResult
            inner = pipeline.run(diff)
            result = ReviewResult(
                code_diff=inner.code_diff,
                rag_docs=inner.rag_docs,
                step_outputs=inner.step_outputs,
            )
        return format_pr_comment(result, marker="<!-- prthinker:mcp -->")

    @mcp.tool()
    def stats(since_days: float | None = 7.0) -> str:
        """Aggregate recent inference telemetry as markdown.

        Args:
            since_days: Window in days; ``None`` reports all-time.

        Returns:
            A short markdown table — calls, cache hit rate, p50/p95
            latency, estimated USD cost — per (backend, model). Reads
            from the configured telemetry SQLite path; returns a notice
            if telemetry has never been recorded.
        """
        from prthinker.telemetry import TelemetrySink

        path = Path(config.telemetry.path)
        if not path.exists():
            return (
                "No telemetry recorded yet. Set "
                "`PRTHINKER_TELEMETRY_ENABLED=true` and run a review first."
            )
        sink = TelemetrySink(path)
        window = None if since_days is None else float(since_days) * 86400.0
        rows = sink.aggregate(since_seconds=window)
        if not rows:
            return "No calls in the selected window."

        label = "all-time" if since_days is None else f"last {since_days:g} day(s)"
        out = [f"# prthinker stats — {label}", ""]
        out.append("| backend | model | calls | hit | in-tok | out-tok | USD | p50 ms | p95 ms |")
        out.append("|---|---|---:|---:|---:|---:|---:|---:|---:|")
        for r in rows:
            out.append(
                f"| {r.backend} | {r.model} | {r.calls} | {r.cache_hits} | "
                f"{r.prompt_tokens} | {r.completion_tokens} | "
                f"${r.cost_usd:.4f} | {r.latency_p50_ms:.0f} | "
                f"{r.latency_p95_ms:.0f} |"
            )
        return "\n".join(out)

    log.info("prthinker MCP server starting on stdio (backend=%s)", config.backend.value)
    mcp.run()
    return 0


__all__ = ["run"]

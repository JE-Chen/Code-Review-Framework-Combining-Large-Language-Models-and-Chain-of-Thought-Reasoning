"""Backend- and hosted-provider argument groups for the prthinker CLI parser.

Split out of :mod:`prthinker.cli_parser_groups` to keep that module under the
file-length limit. :mod:`prthinker.cli_parser_groups` re-exports the public
``add_backend_args`` / ``add_provider_args`` builders from here, so callers and
tests continue to reach them through ``prthinker.cli_parser_groups``.
"""

from __future__ import annotations

import argparse

from prthinker.config import BackendKind, env_bool, env_str


def add_backend_args(common: argparse.ArgumentParser) -> None:
    """Add backend selection + local-model arguments to the shared parser."""
    common.add_argument(
        "--backend",
        choices=[b.value for b in BackendKind],
        default=env_str("PRTHINKER_BACKEND", BackendKind.REMOTE.value),
    )
    common.add_argument(
        "--remote-url",
        default=env_str("PRTHINKER_REMOTE_URL"),
    )
    common.add_argument(
        "--remote-api-key",
        default=env_str("PRTHINKER_REMOTE_API_KEY"),
    )
    common.add_argument(
        "--remote-timeout",
        type=float,
        default=float(env_str("PRTHINKER_REMOTE_TIMEOUT", "600") or 600),
    )
    common.add_argument(
        "--use-remote-pipeline",
        action="store_true",
        default=env_bool("PRTHINKER_USE_REMOTE_PIPELINE", False),
        help="Call /review once instead of /ask per step. Implies --backend remote.",
    )
    common.add_argument(
        "--model-name",
        default=env_str("PRTHINKER_MODEL_NAME", "Qwen/Qwen3-Coder-30B-A3B-Instruct"),
    )
    common.add_argument(
        "--lora-path",
        default=env_str("PRTHINKER_LORA_PATH"),
    )


def add_provider_args(common: argparse.ArgumentParser) -> None:
    """Add hosted-provider (OpenAI / Anthropic / Gemini / Cohere / Mistral) arguments."""
    _add_openai_anthropic_args(common)
    _add_gemini_cohere_mistral_args(common)
    _add_claude_cli_args(common)
    _add_codex_cli_args(common)


def _add_claude_cli_args(common: argparse.ArgumentParser) -> None:
    """Add local claude-CLI subprocess backend arguments."""
    common.add_argument(
        "--claude-cli-path",
        default=env_str("PRTHINKER_CLAUDE_CLI_PATH", "claude"),
        help="Executable for --backend claude-cli (name on PATH or full "
        "path). The CLI runs in non-interactive print mode (-p).",
    )
    common.add_argument(
        "--claude-cli-model",
        default=env_str("PRTHINKER_CLAUDE_CLI_MODEL"),
        help="Optional model override passed to the CLI via --model.",
    )
    common.add_argument(
        "--claude-cli-workdir",
        default=env_str("PRTHINKER_CLAUDE_CLI_WORKDIR", "."),
        help="Working directory the CLI (and its tools) runs in.",
    )
    common.add_argument(
        "--claude-cli-allowed-tools",
        default=env_str("PRTHINKER_CLAUDE_CLI_ALLOWED_TOOLS", ""),
        help="Tool allowlist forwarded as --allowedTools (e.g. "
        "'Read,Grep,Glob'), so the review can consult the working "
        "tree with the full local toolchain. Empty (default) leaves "
        "the CLI's own tool policy in place.",
    )
    common.add_argument(
        "--claude-cli-timeout",
        type=float,
        default=float(env_str("PRTHINKER_CLAUDE_CLI_TIMEOUT", "3600") or 3600),
        help="Seconds before one CLI invocation is killed.",
    )


def _add_codex_cli_args(common: argparse.ArgumentParser) -> None:
    """Add local codex-CLI subprocess backend arguments."""
    common.add_argument(
        "--codex-cli-path",
        default=env_str("PRTHINKER_CODEX_CLI_PATH", "codex"),
        help="Executable for --backend codex-cli (name on PATH or full "
        "path). The CLI runs headless via `codex exec --json`.",
    )
    common.add_argument(
        "--codex-cli-model",
        default=env_str("PRTHINKER_CODEX_CLI_MODEL"),
        help="Optional model override passed to the CLI via -m.",
    )
    common.add_argument(
        "--codex-cli-workdir",
        default=env_str("PRTHINKER_CODEX_CLI_WORKDIR", "."),
        help="Working directory the CLI (and its tools) runs in (-C).",
    )
    common.add_argument(
        "--codex-cli-sandbox",
        choices=["read-only", "workspace-write", "danger-full-access"],
        default=env_str("PRTHINKER_CODEX_CLI_SANDBOX", "read-only"),
        help="Sandbox mode forwarded as `-c sandbox_mode=...`. read-only "
        "(default) lets the review consult the working tree without "
        "mutating it.",
    )
    common.add_argument(
        "--codex-cli-timeout",
        type=float,
        default=float(env_str("PRTHINKER_CODEX_CLI_TIMEOUT", "3600") or 3600),
        help="Seconds before one CLI invocation is killed.",
    )


def _add_openai_anthropic_args(common: argparse.ArgumentParser) -> None:
    """Add OpenAI-compatible and Anthropic Messages API provider arguments."""
    # --- OpenAI-compatible provider --------------------------------------
    common.add_argument(
        "--openai-model",
        default=env_str("PRTHINKER_OPENAI_MODEL", "gpt-4o-mini"),
        help="Model id for --backend openai (e.g. gpt-4o-mini, "
        "qwen-coder-30b on vLLM, llama3.1:8b on Ollama)",
    )
    common.add_argument(
        "--openai-api-key",
        default=env_str("PRTHINKER_OPENAI_API_KEY") or env_str("OPENAI_API_KEY"),
    )
    common.add_argument(
        "--openai-base-url",
        default=env_str("PRTHINKER_OPENAI_BASE_URL", "https://api.openai.com/v1"),
        help="Override for OpenAI-compatible servers "
        "(vLLM, Ollama /v1, LM Studio, Together, Groq, …)",
    )
    common.add_argument(
        "--openai-organization",
        default=env_str("PRTHINKER_OPENAI_ORGANIZATION") or env_str("OPENAI_ORG_ID"),
    )

    # --- Anthropic Messages API ------------------------------------------
    common.add_argument(
        "--anthropic-model",
        default=env_str("PRTHINKER_ANTHROPIC_MODEL", "claude-opus-4-7"),
    )
    common.add_argument(
        "--anthropic-api-key",
        default=env_str("PRTHINKER_ANTHROPIC_API_KEY") or env_str("ANTHROPIC_API_KEY"),
    )
    common.add_argument(
        "--anthropic-base-url",
        default=env_str("PRTHINKER_ANTHROPIC_BASE_URL", "https://api.anthropic.com"),
    )
    common.add_argument(
        "--anthropic-version",
        default=env_str("PRTHINKER_ANTHROPIC_VERSION", "2023-06-01"),
    )


def _add_gemini_cohere_mistral_args(common: argparse.ArgumentParser) -> None:
    """Add Google Gemini, Cohere, and Mistral provider arguments."""
    # --- Google Gemini ---------------------------------------------------
    common.add_argument(
        "--gemini-model",
        default=env_str("PRTHINKER_GEMINI_MODEL", "gemini-1.5-pro"),
    )
    common.add_argument(
        "--gemini-api-key",
        default=env_str("PRTHINKER_GEMINI_API_KEY")
        or env_str("GEMINI_API_KEY")
        or env_str("GOOGLE_API_KEY"),
    )
    common.add_argument(
        "--gemini-base-url",
        default=env_str(
            "PRTHINKER_GEMINI_BASE_URL",
            "https://generativelanguage.googleapis.com/v1beta",
        ),
    )

    # --- Cohere ----------------------------------------------------------
    common.add_argument(
        "--cohere-model",
        default=env_str("PRTHINKER_COHERE_MODEL", "command-r-plus"),
    )
    common.add_argument(
        "--cohere-api-key",
        default=env_str("PRTHINKER_COHERE_API_KEY") or env_str("COHERE_API_KEY"),
    )
    common.add_argument(
        "--cohere-base-url",
        default=env_str("PRTHINKER_COHERE_BASE_URL", "https://api.cohere.com"),
    )

    # --- Mistral ---------------------------------------------------------
    common.add_argument(
        "--mistral-model",
        default=env_str("PRTHINKER_MISTRAL_MODEL", "mistral-large-latest"),
    )
    common.add_argument(
        "--mistral-api-key",
        default=env_str("PRTHINKER_MISTRAL_API_KEY") or env_str("MISTRAL_API_KEY"),
    )
    common.add_argument(
        "--mistral-base-url",
        default=env_str("PRTHINKER_MISTRAL_BASE_URL", "https://api.mistral.ai/v1"),
    )

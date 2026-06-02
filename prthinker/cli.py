"""Command-line interface for prthinker.

Subcommands:
    review-pr    Pull a PR diff from GitHub, run the pipeline, post a comment
                 (and optionally inline-comment review).
    review-file  Run the pipeline against a local file or '-' for stdin.

Backend selection:
    --backend local                     in-process Hugging Face causal-LM
    --backend remote                    the project's own FastAPI server
    --backend openai                    any OpenAI-Chat-Completions endpoint
                                        (OpenAI, Azure, vLLM, Ollama /v1, …)
    --backend anthropic                 Anthropic Messages API

RAG selection:
    --no-rag         skip RAG entirely
    --remote-rag     call /rag instead of loading FAISS locally
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from collections.abc import Callable

from prthinker.cli_commands import (
    _cmd_adversarial_eval,
    _cmd_aggregate,
    _cmd_build_kg,
    _cmd_derive_lessons,
    _cmd_discover_rules,
    _cmd_harvest,
    _cmd_harvest_accepted,
    _cmd_hook,
    _cmd_mcp,
    _cmd_report,
    _cmd_review_commits,
    _cmd_stats,
    _cmd_visualize_kg,
    _kg_html_path,
    merge_partial_reviews,
)
from prthinker.cli_parser import _apply_repo_defaults, _build_parser
from prthinker.plugins import load_plugin_steps
from prthinker.cli_review import _build_config, _cmd_review_file, _cmd_review_pr

log = logging.getLogger("prthinker")


_COMMAND_HANDLERS: dict[str, Callable[[argparse.Namespace], int]] = {
    "review-file": _cmd_review_file,
    "review-pr": _cmd_review_pr,
    "aggregate": _cmd_aggregate,
    "stats": _cmd_stats,
    "report": _cmd_report,
    "adversarial-eval": _cmd_adversarial_eval,
    "derive-lessons": _cmd_derive_lessons,
    "discover-rules": _cmd_discover_rules,
    "build-kg": _cmd_build_kg,
    "visualize-kg": _cmd_visualize_kg,
    "mcp": _cmd_mcp,
    "hook": _cmd_hook,
    "review-commits": _cmd_review_commits,
    "harvest-dismissed": _cmd_harvest,
    "harvest-accepted": _cmd_harvest_accepted,
}


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    # Peek at --config without forcing a parse, so YAML defaults apply
    # before argparse fixes the rest of the namespace.
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--config", type=Path, default=None)
    pre_args, _ = pre.parse_known_args(argv)
    try:
        _apply_repo_defaults(parser, pre_args.config)
    except (FileNotFoundError, ValueError) as exc:
        sys.stderr.write(f"Config error: {exc}\n")
        return 2

    args = parser.parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    # Discover third-party review steps (entry-point group "prthinker.steps")
    # so they self-register before any pipeline resolves its step sequence.
    load_plugin_steps()

    handler = _COMMAND_HANDLERS.get(args.command)
    if handler is None:
        parser.error(f"unknown command: {args.command}")
        return 2
    return handler(args)


__all__ = [
    "main",
    "_build_parser",
    "_apply_repo_defaults",
    "_build_config",
    "_kg_html_path",
    "merge_partial_reviews",
]

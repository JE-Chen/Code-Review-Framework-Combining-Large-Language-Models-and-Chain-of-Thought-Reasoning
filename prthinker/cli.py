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

from prthinker.backends import create_backend
from prthinker.backends.remote import RemotePipelineClient
from prthinker.config import (
    AnthropicConfig,
    BackendKind,
    Config,
    GitHubConfig,
    LocalBackendConfig,
    OpenAICompatConfig,
    RemoteBackendConfig,
    env_bool,
    env_str,
)
from prthinker.accepted import AcceptedExamplesStore
from prthinker.checks import (
    evaluate_gate,
)
from prthinker.ci_signals import (
    fetch_ci_failure_signals,
    format_signals_block,
)
from prthinker.diff import parse_unified_diff
from prthinker.dismissed import DismissedExamplesStore
from prthinker.formatters import format_pr_comment
from prthinker.harvest import harvest, harvest_accepted
from prthinker.pipeline import (
    CoTPipeline,
    FileReviewResult,
    ReviewResult,
)
from prthinker.rag import (
    FaissRAGRetriever,
    NoOpRetriever,
    RAGRetriever,
    RemoteRAGRetriever,
)
from prthinker.repo_config import (
    find_config_file,
    load_repo_config,
    to_argparse_defaults,
)
from prthinker.rules import load_rules_dir
from prthinker.schemas import InlineFinding, ReviewRequest

log = logging.getLogger("prthinker")


def _apply_repo_defaults(parser: argparse.ArgumentParser, config_path: Path | None) -> None:
    """Layer ``.prthinker.yaml`` defaults under argparse's own defaults.

    Called before ``parse_args`` so user flags still override the YAML.
    ``set_defaults`` does not propagate from a parent parser into its
    subparsers, so we walk the subparser action and apply to each child.
    """
    resolved = find_config_file(config_path)
    if resolved is None:
        return
    log.info("Loading repo config from %s", resolved)
    cfg = load_repo_config(resolved)
    defaults = to_argparse_defaults(cfg)
    parser.set_defaults(**defaults)
    for action in parser._actions:  # noqa: SLF001 — argparse exposes no public iterator
        if isinstance(action, argparse._SubParsersAction):
            for sub in action.choices.values():
                sub.set_defaults(**defaults)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="prthinker")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(env_str("PRTHINKER_CONFIG") or "") if env_str("PRTHINKER_CONFIG") else None,
        help="Path to a .prthinker.yaml (default: ./.prthinker.yaml if present)",
    )
    parser.add_argument(
        "--log-level",
        default=env_str("PRTHINKER_LOG_LEVEL", "INFO"),
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )

    sub = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
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
    common.add_argument(
        "--no-rag",
        action="store_true",
        default=not env_bool("PRTHINKER_RAG_ENABLED", True),
    )
    common.add_argument(
        "--remote-rag",
        action="store_true",
        default=env_bool("PRTHINKER_REMOTE_RAG", False),
        help="Use /rag instead of loading FAISS locally",
    )
    common.add_argument(
        "--rag-threshold",
        type=float,
        default=float(env_str("PRTHINKER_RAG_THRESHOLD", "0.7") or 0.7),
    )
    common.add_argument(
        "--max-new-tokens",
        type=int,
        default=int(env_str("PRTHINKER_MAX_NEW_TOKENS", "32768") or 32768),
    )
    common.add_argument(
        "--steps",
        default="",
    )
    common.add_argument(
        "--per-file",
        action="store_true",
        default=env_bool("PRTHINKER_PER_FILE", False),
        help="Run the pipeline once per file in the diff",
    )
    common.add_argument(
        "--inline-review",
        action="store_true",
        default=env_bool("PRTHINKER_INLINE_REVIEW", False),
        help="Collect JSON findings per file and submit a GitHub review",
    )
    common.add_argument(
        "--max-findings-per-file",
        type=int,
        default=int(env_str("PRTHINKER_MAX_FINDINGS_PER_FILE", "10") or 10),
    )
    common.add_argument(
        "--reply-to-author",
        action="store_true",
        default=env_bool("PRTHINKER_REPLY_TO_AUTHOR", False),
        help=(
            "Fetch author replies to the previous prthinker summary "
            "comment and inject them as 'Prior dialogue' context into "
            "the inline-findings prompt (closed-loop multi-turn review)."
        ),
    )
    common.add_argument(
        "--counterfactual",
        action="store_true",
        default=env_bool("PRTHINKER_COUNTERFACTUAL", False),
        help=(
            "After inline findings, run a counterfactual / mutation-style "
            "step that surfaces competing alternative implementations and "
            "an explicit trade-off matrix for each design-choice finding. "
            "Requires --inline-review."
        ),
    )
    common.add_argument(
        "--provenance",
        action="store_true",
        default=env_bool("PRTHINKER_PROVENANCE", False),
        help=(
            "Ask the model to cite the RAG rule / accepted-example / diff "
            "evidence that informed each finding, and surface those "
            "citations as an audit-trail footer under the finding in the "
            "PR comment. Requires --inline-review."
        ),
    )
    common.add_argument(
        "--rules-dir",
        type=Path,
        default=Path(env_str("PRTHINKER_RULES_DIR") or "") if env_str("PRTHINKER_RULES_DIR") else None,
        help="Directory of *.md files containing per-repo coding rules",
    )

    # --- Cache + telemetry ------------------------------------------------
    common.add_argument(
        "--cache",
        dest="cache_enabled",
        action="store_true",
        default=env_bool("PRTHINKER_CACHE_ENABLED", False),
        help="Memoize backend.generate() calls by (model, prompt) in SQLite",
    )
    common.add_argument(
        "--cache-path",
        default=env_str("PRTHINKER_CACHE_PATH", ".prthinker/cache.sqlite"),
    )
    common.add_argument(
        "--cache-ttl-days",
        type=float,
        default=float(env_str("PRTHINKER_CACHE_TTL_DAYS", "7") or 7),
        help="Drop cache entries older than this many days; set to 0 to disable TTL",
    )
    common.add_argument(
        "--telemetry",
        dest="telemetry_enabled",
        action="store_true",
        default=env_bool("PRTHINKER_TELEMETRY_ENABLED", False),
        help="Record tokens / latency / estimated cost per generate() call",
    )
    common.add_argument(
        "--telemetry-path",
        default=env_str("PRTHINKER_TELEMETRY_PATH", ".prthinker/telemetry.sqlite"),
    )

    common.add_argument(
        "--stream",
        action="store_true",
        default=env_bool("PRTHINKER_STREAM", False),
        help="Stream generated tokens to stderr as they arrive. Native "
             "for OpenAI and Anthropic; local + remote fall back to a "
             "single chunk per step.",
    )
    common.add_argument(
        "--judge",
        action="store_true",
        default=env_bool("PRTHINKER_JUDGE", False),
        help="Add a per-file judge step that emits a JSON verdict; "
             "review-pr aggregates verdicts into one APPROVE / "
             "REQUEST_CHANGES / COMMENT event on the GitHub review.",
    )
    common.add_argument(
        "--self-correct",
        action="store_true",
        default=env_bool("PRTHINKER_SELF_CORRECT", False),
        help="Add a second-pass noise filter — after inline findings are "
             "parsed and dismissed-filtered, the model is asked to flag "
             "noise / duplicate / over-picky entries which the runner "
             "then drops.",
    )
    common.add_argument(
        "--redact-secrets",
        action="store_true",
        default=env_bool("PRTHINKER_REDACT_SECRETS", False),
        help="Scrub well-known secret patterns (AWS / GitHub / OpenAI / "
             "Anthropic / Stripe / Slack / JWT / PEM keys) from the diff "
             "before any backend call. Strongly recommended for paid backends.",
    )

    p_pr = sub.add_parser("review-pr", parents=[common])
    p_pr.add_argument(
        "--platform",
        choices=["github", "gitlab"],
        default=env_str("PRTHINKER_PLATFORM", "github"),
        help="Which forge to talk to. GitHub uses /pulls + Check Runs; "
             "GitLab uses /merge_requests + commit statuses.",
    )
    p_pr.add_argument(
        "--platform-base-url",
        default=env_str("PRTHINKER_PLATFORM_BASE_URL"),
        help="Override for self-hosted instances (e.g. GitHub Enterprise "
             "or self-hosted GitLab). Default: each platform's public API.",
    )
    p_pr.add_argument(
        "--repo",
        default=env_str("GITHUB_REPOSITORY") or env_str("CI_PROJECT_PATH"),
        help="GitHub `owner/name` or GitLab `group/project`.",
    )
    p_pr.add_argument(
        "--pr-number",
        type=int,
        default=int(
            env_str("PRTHINKER_PR_NUMBER")
            or env_str("CI_MERGE_REQUEST_IID", "0")
            or 0
        ),
        help="GitHub PR number or GitLab MR iid.",
    )
    p_pr.add_argument(
        "--github-token",
        default=env_str("GITHUB_TOKEN") or env_str("GITLAB_TOKEN"),
        help="Platform API token. Reads GITHUB_TOKEN for GitHub, "
             "GITLAB_TOKEN for GitLab.",
    )
    p_pr.add_argument(
        "--marker",
        default=env_str("PRTHINKER_COMMENT_MARKER", "<!-- prthinker:summary -->"),
    )
    p_pr.add_argument(
        "--dry-run",
        action="store_true",
    )
    p_pr.add_argument(
        "--auto-fix-threshold",
        type=int,
        default=int(env_str("PRTHINKER_AUTO_FIX_THRESHOLD", "0") or 0),
        help="When ≥ N warning-severity findings carry a `suggestion` "
             "block, auto-apply them on a fresh branch and open a draft "
             "PR pointed at the original PR's base. Set to 0 to disable.",
    )
    p_pr.add_argument(
        "--auto-fix-base-branch",
        default=env_str("PRTHINKER_AUTO_FIX_BASE_BRANCH"),
        help="Base branch for the auto-fix PR (defaults to the original "
             "PR's base branch, fetched from the GitHub API).",
    )
    p_pr.add_argument(
        "--gate-on",
        choices=["none", "warning", "error"],
        default=env_str("PRTHINKER_GATE_ON", "none"),
        help="Open a Check Run; conclude as 'failure' when findings of this "
             "severity or higher exist. Required for branch-protection gating.",
    )
    p_pr.add_argument(
        "--include-ci-signals",
        action="store_true",
        default=env_bool("PRTHINKER_INCLUDE_CI_SIGNALS", False),
        help="Prepend failed-job tail logs from the PR head to the diff",
    )
    p_pr.add_argument(
        "--ci-signal-max-jobs",
        type=int,
        default=int(env_str("PRTHINKER_CI_SIGNAL_MAX_JOBS", "5") or 5),
    )
    p_pr.add_argument(
        "--ci-signal-tail-chars",
        type=int,
        default=int(env_str("PRTHINKER_CI_SIGNAL_TAIL_CHARS", "4000") or 4000),
    )

    p_file = sub.add_parser("review-file", parents=[common])
    p_file.add_argument("path", help="Path to a code/diff file, or '-' for stdin")
    p_file.add_argument("--output-dir", type=Path, default=None)

    p_harvest = sub.add_parser(
        "harvest-dismissed",
        help="Scan PR review comments for dismissed findings; append to JSONL",
    )
    p_harvest.add_argument(
        "--repo",
        default=env_str("GITHUB_REPOSITORY"),
    )
    p_harvest.add_argument(
        "--github-token",
        default=env_str("GITHUB_TOKEN"),
    )
    p_harvest.add_argument(
        "--pr-number",
        type=int,
        default=None,
        help="Single PR to harvest (omit to scan recent closed PRs)",
    )
    p_harvest.add_argument(
        "--max-prs",
        type=int,
        default=50,
    )
    p_harvest.add_argument(
        "--out",
        type=Path,
        default=Path(env_str("PRTHINKER_DISMISSED_PATH", ".prthinker/dismissed.jsonl") or
                     ".prthinker/dismissed.jsonl"),
    )

    p_acc = sub.add_parser(
        "harvest-accepted",
        help="Scan PRs for applied suggestions; append to JSONL",
    )
    p_acc.add_argument("--repo", default=env_str("GITHUB_REPOSITORY"))
    p_acc.add_argument("--github-token", default=env_str("GITHUB_TOKEN"))
    p_acc.add_argument("--pr-number", type=int, default=None)
    p_acc.add_argument("--max-prs", type=int, default=50)
    p_acc.add_argument(
        "--out",
        type=Path,
        default=Path(env_str("PRTHINKER_ACCEPTED_PATH", ".prthinker/accepted.jsonl") or
                     ".prthinker/accepted.jsonl"),
    )

    p_stats = sub.add_parser(
        "stats",
        help="Aggregate telemetry: tokens, cost, latency, cache hit rate",
    )
    p_stats.add_argument(
        "--telemetry-path",
        default=env_str("PRTHINKER_TELEMETRY_PATH", ".prthinker/telemetry.sqlite"),
    )
    p_stats.add_argument(
        "--since-days",
        type=float,
        default=None,
        help="Restrict to calls within the last N days (default: all-time)",
    )
    p_stats.add_argument(
        "--cache-path",
        default=env_str("PRTHINKER_CACHE_PATH", ".prthinker/cache.sqlite"),
        help="Also report cache fill / hit counters if the file exists",
    )

    p_report = sub.add_parser(
        "report",
        help="Cross-store longitudinal report — telemetry + cache + "
             "dismissed + accepted. Renders to markdown / HTML / JSON.",
    )
    p_report.add_argument(
        "--since-days",
        type=float,
        default=None,
        help="Restrict to entries within the last N days (default: all-time)",
    )
    p_report.add_argument(
        "--format",
        choices=["markdown", "html", "json"],
        default="markdown",
    )
    p_report.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Write to file instead of stdout.",
    )
    p_report.add_argument(
        "--telemetry-path",
        type=Path,
        default=Path(env_str("PRTHINKER_TELEMETRY_PATH", ".prthinker/telemetry.sqlite")
                     or ".prthinker/telemetry.sqlite"),
    )
    p_report.add_argument(
        "--cache-path",
        type=Path,
        default=Path(env_str("PRTHINKER_CACHE_PATH", ".prthinker/cache.sqlite")
                     or ".prthinker/cache.sqlite"),
    )
    p_report.add_argument(
        "--dismissed-path",
        type=Path,
        default=Path(env_str("PRTHINKER_DISMISSED_PATH", ".prthinker/dismissed.jsonl")
                     or ".prthinker/dismissed.jsonl"),
    )
    p_report.add_argument(
        "--accepted-path",
        type=Path,
        default=Path(env_str("PRTHINKER_ACCEPTED_PATH", ".prthinker/accepted.jsonl")
                     or ".prthinker/accepted.jsonl"),
    )

    sub.add_parser(
        "mcp",
        help="Run the Model Context Protocol stdio server (for Claude "
             "Desktop / Cursor / Continue / Cline / Zed integration). "
             "Reads PRTHINKER_* env vars for backend config.",
    )

    p_adv = sub.add_parser(
        "adversarial-eval",
        parents=[common],
        help="Run a corpus of attack diffs through the configured backend "
             "and record per-case bypass outcomes into SQLite. Does NOT "
             "emit aggregate detection-rate numbers — compute those from "
             "the raw output table.",
    )
    p_adv.add_argument(
        "--corpus",
        type=Path,
        default=Path("prthinker/adversarial_corpus/seed.jsonl"),
        help="JSONL corpus to evaluate.",
    )
    p_adv.add_argument(
        "--outcomes-path",
        type=Path,
        default=Path(env_str("PRTHINKER_ADV_OUTCOMES_PATH",
                              ".prthinker/adversarial-outcomes.sqlite") or
                     ".prthinker/adversarial-outcomes.sqlite"),
    )

    p_hook = sub.add_parser(
        "hook",
        parents=[common],
        help="Read `git diff --cached`, run the pipeline, exit non-zero "
             "on error-severity findings. Intended as a pre-commit hook.",
    )
    p_hook.add_argument(
        "--advisory",
        action="store_true",
        default=env_bool("PRTHINKER_HOOK_ADVISORY", False),
        help="Always exit 0; print findings to stderr but never block the "
             "commit. Useful as a soft introduction.",
    )
    p_hook.add_argument(
        "--block-on",
        choices=["none", "warning", "error"],
        default=env_str("PRTHINKER_HOOK_BLOCK_ON", "error"),
        help="Severity floor that blocks the commit. Ignored when "
             "--advisory is set.",
    )

    return parser


def _build_config(args: argparse.Namespace) -> Config:
    if args.use_remote_pipeline and args.backend != BackendKind.REMOTE.value:
        log.info("--use-remote-pipeline forces --backend remote")
        args.backend = BackendKind.REMOTE.value

    backend = BackendKind(args.backend)
    local_cfg: LocalBackendConfig | None = None
    remote_cfg: RemoteBackendConfig | None = None
    openai_cfg: OpenAICompatConfig | None = None
    anthropic_cfg: AnthropicConfig | None = None

    if backend is BackendKind.LOCAL:
        local_cfg = LocalBackendConfig(
            model_name=args.model_name,
            lora_path=args.lora_path,
        )
    elif backend is BackendKind.REMOTE:
        if not args.remote_url:
            raise SystemExit(
                "remote backend requires --remote-url or PRTHINKER_REMOTE_URL"
            )
        remote_cfg = RemoteBackendConfig(
            url=args.remote_url,
            timeout_seconds=args.remote_timeout,
            api_key=args.remote_api_key,
        )
    elif backend is BackendKind.OPENAI:
        if not args.openai_api_key:
            raise SystemExit(
                "openai backend requires --openai-api-key or "
                "$PRTHINKER_OPENAI_API_KEY / $OPENAI_API_KEY"
            )
        openai_cfg = OpenAICompatConfig(
            model=args.openai_model,
            api_key=args.openai_api_key,
            base_url=args.openai_base_url,
            organization=args.openai_organization,
            timeout_seconds=args.remote_timeout,
        )
    elif backend is BackendKind.ANTHROPIC:
        if not args.anthropic_api_key:
            raise SystemExit(
                "anthropic backend requires --anthropic-api-key or "
                "$PRTHINKER_ANTHROPIC_API_KEY / $ANTHROPIC_API_KEY"
            )
        anthropic_cfg = AnthropicConfig(
            model=args.anthropic_model,
            api_key=args.anthropic_api_key,
            base_url=args.anthropic_base_url,
            anthropic_version=args.anthropic_version,
            timeout_seconds=args.remote_timeout,
        )

    steps = tuple(s.strip() for s in args.steps.split(",") if s.strip())
    from prthinker.config import CacheConfig, TelemetryConfig

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

    return Config(
        backend=backend,
        local=local_cfg,
        remote=remote_cfg,
        openai=openai_cfg,
        anthropic=anthropic_cfg,
        rag_enabled=not args.no_rag,
        rag_threshold=args.rag_threshold,
        max_new_tokens=args.max_new_tokens,
        steps=steps,
        cache=cache_cfg,
        telemetry=telemetry_cfg,
    )


def _build_retriever(args: argparse.Namespace, config: Config) -> RAGRetriever:
    if not config.rag_enabled:
        return NoOpRetriever()
    if args.remote_rag:
        if not args.remote_url:
            raise SystemExit("--remote-rag needs --remote-url")
        return RemoteRAGRetriever(
            url=args.remote_url,
            threshold=config.rag_threshold,
            timeout_seconds=args.remote_timeout,
            api_key=args.remote_api_key,
        )
    return FaissRAGRetriever(threshold=config.rag_threshold)


def _read_stdin_or_file(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


# ----------------------------------------------------------------------------
# Server-orchestrated path: call /review per file.
# ----------------------------------------------------------------------------

def _review_via_server(
    args: argparse.Namespace, config: Config, diff_text: str
) -> ReviewResult:
    assert config.remote is not None
    extra_rules = load_rules_dir(args.rules_dir)
    client = RemotePipelineClient(config.remote)
    try:
        if not args.per_file:
            response = client.review(
                ReviewRequest(
                    code_diff=diff_text,
                    rag_enabled=config.rag_enabled,
                    rag_threshold=config.rag_threshold,
                    max_new_tokens=config.max_new_tokens,
                    steps=list(config.steps) or None,
                    extra_rules=extra_rules,
                )
            )
            return ReviewResult(
                code_diff=diff_text,
                rag_docs=response.rag_docs,
                step_outputs=response.step_map(),
                inline_findings=list(response.inline_findings),
            )

        files = parse_unified_diff(diff_text)
        all_findings: list[InlineFinding] = []
        aggregated_steps: dict[str, str] = {}
        per_file: list[FileReviewResult] = []
        for fd in files:
            if fd.is_binary or fd.is_deleted:
                continue
            response = client.review(
                ReviewRequest(
                    code_diff=fd.raw,
                    file_path=fd.path,
                    rag_enabled=config.rag_enabled,
                    rag_threshold=config.rag_threshold,
                    max_new_tokens=config.max_new_tokens,
                    steps=list(config.steps) or None,
                    extra_rules=extra_rules,
                )
            )
            sm = response.step_map()
            for name, output in sm.items():
                aggregated_steps[f"{fd.path}::{name}"] = output
            findings = list(response.inline_findings)
            all_findings.extend(findings)
            per_file.append(
                FileReviewResult(
                    path=fd.path,
                    rag_docs=response.rag_docs,
                    step_outputs=sm,
                    inline_findings=findings,
                    is_binary=fd.is_binary,
                    is_deleted=fd.is_deleted,
                )
            )
        return ReviewResult(
            code_diff=diff_text,
            rag_docs=[],
            step_outputs=aggregated_steps,
            inline_findings=all_findings,
            per_file=per_file,
        )
    finally:
        client.close()


# ----------------------------------------------------------------------------
# Runner-orchestrated path: build a CoTPipeline locally.
# ----------------------------------------------------------------------------

def _review_via_pipeline(
    args: argparse.Namespace,
    config: Config,
    diff_text: str,
    output_dir: Path | None = None,
    *,
    dialogue_block: str = "",
) -> ReviewResult:
    backend = create_backend(config)
    retriever = _build_retriever(args, config)
    extra_rules = load_rules_dir(args.rules_dir)
    pipeline = CoTPipeline(
        backend=backend,
        retriever=retriever,
        steps=config.steps,
        max_new_tokens=config.max_new_tokens,
        extra_rules=tuple(extra_rules),
        stream=bool(getattr(args, "stream", False)),
    )
    try:
        if args.per_file:
            return pipeline.run_per_file(
                diff_text,
                inline_review=args.inline_review,
                judge=bool(getattr(args, "judge", False)),
                self_correct=bool(getattr(args, "self_correct", False)),
                counterfactual=bool(getattr(args, "counterfactual", False)),
                provenance=bool(getattr(args, "provenance", False)),
                max_findings_per_file=args.max_findings_per_file,
                output_dir=output_dir,
                dialogue_block=dialogue_block,
            )
        return pipeline.run(diff_text, output_dir=output_dir)
    finally:
        backend.close()
        if isinstance(retriever, RemoteRAGRetriever):
            retriever.close()


def _run_review(
    args: argparse.Namespace,
    config: Config,
    diff_text: str,
    output_dir: Path | None = None,
    *,
    dialogue_block: str = "",
) -> ReviewResult:
    if getattr(args, "redact_secrets", False):
        from prthinker.redaction import redact
        diff_text, report = redact(diff_text)
        if report:
            log.warning(
                "Redacted secrets from diff before backend call: %s",
                report.summary(),
            )
    if args.use_remote_pipeline:
        return _review_via_server(args, config, diff_text)
    return _review_via_pipeline(
        args, config, diff_text,
        output_dir=output_dir,
        dialogue_block=dialogue_block,
    )


# ----------------------------------------------------------------------------
# Subcommand handlers
# ----------------------------------------------------------------------------

def _cmd_review_file(args: argparse.Namespace) -> int:
    config = _build_config(args)
    code = _read_stdin_or_file(args.path)
    result = _run_review(args, config, code, output_dir=args.output_dir)
    sys.stdout.write(
        format_pr_comment(result, marker="<!-- prthinker:summary -->")
    )
    if result.inline_findings:
        sys.stdout.write(
            f"\n[{len(result.inline_findings)} inline findings parsed]\n"
        )
    return 0


def _cmd_review_pr(args: argparse.Namespace) -> int:
    config = _build_config(args)
    if not args.repo:
        raise SystemExit("--repo or $GITHUB_REPOSITORY / $CI_PROJECT_PATH is required")
    if not args.pr_number:
        raise SystemExit("--pr-number is required")
    if not args.github_token:
        raise SystemExit("--github-token / $GITHUB_TOKEN / $GITLAB_TOKEN is required")

    from prthinker.platforms import PlatformKind, create_platform_adapter

    platform_kind = PlatformKind(args.platform)
    adapter = create_platform_adapter(
        platform_kind,
        repo=args.repo,
        token=args.github_token,
        pr_number=args.pr_number,
        comment_marker=args.marker,
        base_url=args.platform_base_url,
    )

    log.info("Fetching diff for %s %s#%d",
             platform_kind.value, args.repo, args.pr_number)
    diff = adapter.fetch_diff()
    if not diff.strip():
        log.warning("Empty diff — skipping review")
        return 0

    head_sha: str | None = None
    needs_head_sha = (
        (args.gate_on != "none" and not args.dry_run)
        or args.include_ci_signals
    )
    if needs_head_sha:
        head_sha = adapter.fetch_head_sha()

    if args.include_ci_signals and head_sha is not None:
        # CI signals are currently GitHub-specific; on GitLab we'd want
        # /projects/:id/jobs which has a different shape. Skip silently
        # on non-GitHub platforms for now.
        if platform_kind is PlatformKind.GITHUB:
            signals = fetch_ci_failure_signals(
                args.repo, head_sha, args.github_token,
                max_jobs=args.ci_signal_max_jobs,
                log_tail_chars=args.ci_signal_tail_chars,
            )
            block = format_signals_block(signals)
            if block:
                diff = block + diff
                log.info("Prepended %d CI failure signal(s) to diff", len(signals))
        else:
            log.info("CI signals not yet supported on %s — skipping",
                     platform_kind.value)

    gate_handle = None
    if args.gate_on != "none" and not args.dry_run and head_sha is not None:
        gate_handle = adapter.open_gate(head_sha)

    dialogue_block = ""
    if getattr(args, "reply_to_author", False) and args.inline_review:
        try:
            replies = adapter.fetch_author_replies()
        except Exception as exc:
            log.warning("Failed to fetch author replies (%s); skipping dialogue", exc)
            replies = []
        if replies:
            from prthinker.dialogue import render_dialogue_block
            dialogue_block = render_dialogue_block(replies)
            log.info("Injecting %d author reply(ies) into inline-findings prompt",
                     len(replies))

    try:
        result = _run_review(args, config, diff, dialogue_block=dialogue_block)
    except Exception:
        if gate_handle is not None:
            from prthinker.checks import CheckResult
            adapter.close_gate(gate_handle, CheckResult(
                conclusion="failure",
                title="Reviewer crashed",
                summary="The CoT reviewer raised an exception. Check workflow logs.",
                error_count=0, warning_count=0, info_count=0,
            ))
        raise

    body = format_pr_comment(result, marker=args.marker)
    if args.dry_run:
        sys.stdout.write(body)
        if result.inline_findings:
            sys.stdout.write(
                f"\n[would post {len(result.inline_findings)} inline findings]\n"
            )
        return 0

    comment_id = adapter.upsert_summary_comment(body)
    log.info("Posted summary comment id=%d", comment_id)

    review_event = "COMMENT"
    if args.judge and result.per_file:
        from prthinker.judge import aggregate, to_github_event
        verdicts = [fr.verdict for fr in result.per_file if fr.verdict is not None]
        if verdicts:
            review_event = to_github_event(aggregate(verdicts))
            log.info("Judge verdict aggregated → %s", review_event)

    if args.inline_review and result.inline_findings:
        review_id = adapter.submit_inline_review(
            result.inline_findings,
            summary_body="prthinker — inline findings",
            event=review_event,
        )
        log.info("Posted inline review id=%s (event=%s)", review_id, review_event)

    if gate_handle is not None:
        gate_result = evaluate_gate(result.inline_findings, gate_on=args.gate_on)
        adapter.close_gate(gate_handle, gate_result)
        log.info(
            "Gate conclusion=%s (errors=%d warnings=%d info=%d, floor=%s)",
            gate_result.conclusion,
            gate_result.error_count, gate_result.warning_count,
            gate_result.info_count, args.gate_on,
        )

    if args.auto_fix_threshold and not args.dry_run:
        # auto-fix opens a draft PR — currently GitHub-only.
        if platform_kind is PlatformKind.GITHUB:
            gh = GitHubConfig(
                repo=args.repo, pr_number=args.pr_number,
                token=args.github_token, comment_marker=args.marker,
            )
            _maybe_open_auto_fix_pr(gh, args, result)
        else:
            log.info("Auto-fix not yet supported on %s — skipping",
                     platform_kind.value)

    return 0


def _maybe_open_auto_fix_pr(
    gh: GitHubConfig,
    args: argparse.Namespace,
    result: ReviewResult,
) -> None:
    """Apply ``--auto-fix-threshold`` to surviving warning suggestions."""
    eligible = [
        f for f in result.inline_findings
        if f.severity == "warning" and f.suggestion is not None
    ]
    if len(eligible) < args.auto_fix_threshold:
        log.info(
            "Auto-fix: %d eligible suggestion(s) below threshold %d — skipped",
            len(eligible), args.auto_fix_threshold,
        )
        return

    from prthinker.auto_fix import open_auto_fix_pr

    findings_by_file: dict[str, list[InlineFinding]] = {}
    for f in eligible:
        findings_by_file.setdefault(f.path, []).append(f)

    base_branch = args.auto_fix_base_branch
    if not base_branch:
        from prthinker.github_api import fetch_pr_base_branch
        try:
            base_branch = fetch_pr_base_branch(gh)
        except Exception as exc:
            log.warning("Auto-fix: could not fetch base branch: %s", exc)
            return

    repo_root = Path.cwd()
    try:
        auto_result = open_auto_fix_pr(
            config=gh,
            findings_by_file=findings_by_file,
            base_pr_number=gh.pr_number,
            base_branch=base_branch,
            repo_root=repo_root,
        )
    except Exception as exc:
        log.error("Auto-fix failed: %s", exc)
        return

    if auto_result is None:
        log.info("Auto-fix: no edits applied (every suggestion conflicted or "
                 "the target files did not exist)")
        return

    log.info(
        "Auto-fix PR #%s opened: %s (applied=%d skipped=%d files=%d)",
        auto_result.pr_number, auto_result.pr_url,
        auto_result.total_findings_applied,
        auto_result.total_findings_skipped,
        len(auto_result.files_changed),
    )


def _cmd_harvest(args: argparse.Namespace) -> int:
    if not args.repo:
        raise SystemExit("--repo or $GITHUB_REPOSITORY is required")
    if not args.github_token:
        raise SystemExit("--github-token or $GITHUB_TOKEN is required")

    store = DismissedExamplesStore(args.out)
    stats = harvest(
        repo=args.repo,
        token=args.github_token,
        store=store,
        pr_number=args.pr_number,
        max_prs=args.max_prs,
    )
    sys.stdout.write(
        f"PRs scanned: {stats.prs_scanned}\n"
        f"Comments scanned: {stats.comments_scanned}\n"
        f"Dismissed appended: {stats.dismissed_found}\n"
        f"Store: {args.out}\n"
    )
    return 0


def _cmd_harvest_accepted(args: argparse.Namespace) -> int:
    if not args.repo:
        raise SystemExit("--repo or $GITHUB_REPOSITORY is required")
    if not args.github_token:
        raise SystemExit("--github-token or $GITHUB_TOKEN is required")

    store = AcceptedExamplesStore(args.out)
    stats = harvest_accepted(
        repo=args.repo,
        token=args.github_token,
        store=store,
        pr_number=args.pr_number,
        max_prs=args.max_prs,
    )
    sys.stdout.write(
        f"PRs scanned: {stats.prs_scanned}\n"
        f"Comments scanned: {stats.comments_scanned}\n"
        f"Accepted appended: {stats.accepted_found}\n"
        f"Store: {args.out}\n"
    )
    return 0


def _cmd_adversarial_eval(args: argparse.Namespace) -> int:
    from prthinker.adversarial_eval import run_eval

    config = _build_config(args)
    backend = create_backend(config)
    try:
        stats = run_eval(
            backend=backend,
            corpus_path=args.corpus,
            out_path=args.outcomes_path,
            max_new_tokens=config.max_new_tokens,
        )
    finally:
        backend.close()
    sys.stdout.write(
        f"adversarial-eval: ran {stats.total} case(s), {stats.errors} error(s). "
        f"Raw outcomes written to {args.outcomes_path}.\n"
        f"Per the no-fabrication rule, no aggregate detection-rate is "
        f"reported here — query the `outcomes` table directly.\n"
    )
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    from prthinker.report import (
        ReportInputs,
        render_html,
        render_json,
        render_markdown,
    )

    inputs = ReportInputs(
        telemetry_path=args.telemetry_path,
        cache_path=args.cache_path,
        dismissed_path=args.dismissed_path,
        accepted_path=args.accepted_path,
        since_seconds=(
            None if args.since_days is None
            else float(args.since_days) * 86400.0
        ),
    )
    renderer = {
        "markdown": render_markdown,
        "html": render_html,
        "json": render_json,
    }[args.format]
    body = renderer(inputs)

    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(body, encoding="utf-8")
        log.info("Wrote %s report to %s", args.format, args.out)
    else:
        sys.stdout.write(body)
    return 0


def _cmd_hook(args: argparse.Namespace) -> int:
    """Pre-commit hook entry point.

    Reads ``git diff --cached`` and runs the per-file pipeline. Exits 0 if
    no finding at or above ``--block-on`` survives the dismissed filter;
    otherwise exits 1 with a short stderr summary so the developer sees
    exactly what blocked the commit.
    """
    import subprocess

    if args.advisory:
        # Force gate to none + override the block floor regardless.
        args.gate_on = "none"
    args.per_file = True
    args.inline_review = True

    try:
        proc = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True, text=True, check=True, encoding="utf-8",
        )
    except FileNotFoundError:
        sys.stderr.write("prthinker hook: `git` not found in PATH\n")
        return 0 if args.advisory else 1
    except subprocess.CalledProcessError as exc:
        sys.stderr.write(f"prthinker hook: `git diff --cached` failed: {exc}\n")
        return 0 if args.advisory else 1

    diff = proc.stdout
    if not diff.strip():
        # Nothing staged → nothing to review. Don't fail the commit.
        return 0

    config = _build_config(args)
    result = _run_review(args, config, diff)

    from prthinker.checks import evaluate_gate

    gate_result = evaluate_gate(
        result.inline_findings,
        gate_on=("none" if args.advisory else args.block_on),
    )

    if not result.inline_findings:
        sys.stderr.write("prthinker hook: no findings.\n")
        return 0

    sys.stderr.write(
        f"prthinker hook: {gate_result.error_count} error(s), "
        f"{gate_result.warning_count} warning(s), "
        f"{gate_result.info_count} info finding(s):\n"
    )
    for finding in result.inline_findings:
        sys.stderr.write(
            f"  {finding.severity:>7} {finding.path}:{finding.line} — "
            f"{finding.comment.splitlines()[0][:120]}\n"
        )

    if args.advisory or gate_result.conclusion == "success":
        return 0
    sys.stderr.write(
        f"\nCommit blocked: at least one finding at severity ≥ "
        f"'{args.block_on}'. Address the findings or rerun with "
        f"`git commit --no-verify` to bypass.\n"
    )
    return 1


def _cmd_stats(args: argparse.Namespace) -> int:
    from prthinker.cache import PromptCache
    from prthinker.telemetry import TelemetrySink

    telemetry_path = Path(args.telemetry_path)
    if not telemetry_path.exists():
        sys.stderr.write(
            f"No telemetry file at {telemetry_path}. Re-run a review with "
            f"--telemetry first.\n"
        )
        return 1
    sink = TelemetrySink(telemetry_path)
    window = None if args.since_days is None else args.since_days * 86400.0
    stats = sink.aggregate(since_seconds=window)
    if not stats:
        sys.stdout.write("No calls recorded in the selected window.\n")
        return 0

    range_label = (
        "all-time" if args.since_days is None
        else f"last {args.since_days:g} day(s)"
    )
    sys.stdout.write(f"# prthinker stats — {range_label}\n\n")

    fmt = "{backend:<10} {model:<35} {calls:>6} {hits:>5} {ptok:>9} {ctok:>9} {cost:>9} {p50:>8} {p95:>8}\n"
    sys.stdout.write(fmt.format(
        backend="backend", model="model", calls="calls", hits="hits",
        ptok="in-tok", ctok="out-tok", cost="USD",
        p50="p50 ms", p95="p95 ms",
    ))
    sys.stdout.write("-" * 110 + "\n")
    total_cost = 0.0
    total_calls = 0
    total_hits = 0
    for s in stats:
        total_cost += s.cost_usd
        total_calls += s.calls
        total_hits += s.cache_hits
        sys.stdout.write(fmt.format(
            backend=s.backend,
            model=(s.model[:33] + "..") if len(s.model) > 35 else s.model,
            calls=s.calls,
            hits=s.cache_hits,
            ptok=s.prompt_tokens,
            ctok=s.completion_tokens,
            cost=f"${s.cost_usd:.4f}",
            p50=f"{s.latency_p50_ms:.0f}",
            p95=f"{s.latency_p95_ms:.0f}",
        ))
    sys.stdout.write("-" * 110 + "\n")
    hit_rate = (total_hits / total_calls * 100) if total_calls else 0.0
    sys.stdout.write(
        f"Total: {total_calls} call(s), {total_hits} cache hits "
        f"({hit_rate:.1f}%), ${total_cost:.4f}\n"
    )

    cache_path = Path(args.cache_path)
    if cache_path.exists():
        cache = PromptCache(cache_path)
        cstats = cache.stats()
        sys.stdout.write(
            f"\nCache: {cstats.total_entries} entries stored, "
            f"{cstats.total_hits} lifetime hits at {cache_path}\n"
        )
    return 0


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

    if args.command == "review-file":
        return _cmd_review_file(args)
    if args.command == "review-pr":
        return _cmd_review_pr(args)
    if args.command == "stats":
        return _cmd_stats(args)
    if args.command == "report":
        return _cmd_report(args)
    if args.command == "adversarial-eval":
        return _cmd_adversarial_eval(args)
    if args.command == "mcp":
        from prthinker.mcp_server import run as run_mcp
        return run_mcp()
    if args.command == "hook":
        return _cmd_hook(args)
    if args.command == "harvest-dismissed":
        return _cmd_harvest(args)
    if args.command == "harvest-accepted":
        return _cmd_harvest_accepted(args)
    parser.error(f"unknown command: {args.command}")
    return 2


__all__ = ["main"]

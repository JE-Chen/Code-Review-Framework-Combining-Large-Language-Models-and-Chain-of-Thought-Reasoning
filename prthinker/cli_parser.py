"""Argument-parser construction for the prthinker CLI.

Split out of ``cli`` so neither the parser builders nor the command
handlers push a single module past the file-length limit.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from prthinker.config import BackendKind, env_bool, env_str
from prthinker.repo_config import (
    find_config_file,
    load_repo_config,
    to_argparse_defaults,
)

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


def _build_common_parser() -> argparse.ArgumentParser:
    """Build the parser of arguments shared by every subcommand."""
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
        "--exclude-globs",
        default=env_str("PRTHINKER_EXCLUDE_GLOBS", ""),
        help=(
            "Comma-separated fnmatch patterns; files in the PR diff that "
            "match any pattern are skipped in --per-file mode. Useful for "
            "noisy paths (IDE config, generated data, *.md). Example: "
            "'.idea/*,datas/*,*.md,*.lock'."
        ),
    )
    common.add_argument(
        "--target-file",
        default=env_str("PRTHINKER_TARGET_FILE", ""),
        help=(
            "When set, --per-file mode reviews only this exact diff path "
            "and skips every other file. Lets a CI matrix runner own a "
            "single file's review so each file gets its own job timeout."
        ),
    )
    common.add_argument(
        "--output-json",
        default=env_str("PRTHINKER_OUTPUT_JSON", ""),
        help=(
            "Write a JSON-encoded partial ReviewResult to this path and "
            "skip posting to GitHub. Lets a matrix runner stash its "
            "findings as an artifact for a later `aggregate` job to merge."
        ),
    )
    common.add_argument(
        "--incremental-save-dir",
        default=env_str("PRTHINKER_INCREMENTAL_SAVE_DIR", ""),
        help=(
            "Persist each per-file review to <dir>/files/<slug>.json as the "
            "file finishes, plus a final <dir>/review.json once the run "
            "completes. If the run is cancelled or crashes mid-PR the "
            "files written so far are still on disk for inspection. "
            "Local pipeline only; takes effect with --per-file."
        ),
    )
    common.add_argument(
        "--aggregate-from",
        default=env_str("PRTHINKER_AGGREGATE_FROM", ""),
        help=(
            "Directory of partial-review JSONs (produced by --output-json) "
            "to merge and post as a single summary + inline review. Used "
            "by the `aggregate` subcommand only."
        ),
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
        "--kg-ground",
        action="store_true",
        default=env_bool("PRTHINKER_KG_GROUND", False),
        help=(
            "Inject the workdir's Known-symbols table (built via "
            "`prthinker build-kg`) into the inline-findings prompt, "
            "so the model cannot hallucinate symbol names. Read-only "
            "lookup; safe-failure if the store is empty or missing."
        ),
    )
    common.add_argument(
        "--kg-store",
        type=Path,
        default=Path(env_str("PRTHINKER_KG_STORE",
                              ".prthinker/repo-kg.sqlite") or
                     ".prthinker/repo-kg.sqlite"),
    )
    common.add_argument(
        "--kg-workdir",
        type=Path,
        default=Path(env_str("PRTHINKER_KG_WORKDIR") or "."),
        help="Workdir scope the KG was built against.",
    )
    common.add_argument(
        "--lessons",
        action="store_true",
        default=env_bool("PRTHINKER_LESSONS", False),
        help=(
            "Inject the top-K derived review rules from "
            "`--lessons-path` (default `.prthinker/lessons.jsonl`) "
            "into the inline-findings prompt as 'Repo-derived review "
            "lessons'. Populate the store via `prthinker derive-lessons`."
        ),
    )
    common.add_argument(
        "--lessons-top-k",
        type=int,
        default=int(env_str("PRTHINKER_LESSONS_TOP_K", "5") or 5),
        help="Number of lessons to inject per file (most recent first).",
    )
    common.add_argument(
        "--diff-since-last",
        action="store_true",
        default=env_bool("PRTHINKER_DIFF_SINCE_LAST", False),
        help=(
            "Force-push differential review: hash each file's post-change "
            "content and look up cached findings keyed on "
            "(pr_number, repo, file, hash). Cache hits are reused; only "
            "files whose hash changed re-enter the model. Requires "
            "--inline-review."
        ),
    )
    common.add_argument(
        "--diff-cache-path",
        default=env_str("PRTHINKER_DIFF_CACHE_PATH", ".prthinker/diff-cache.sqlite"),
        help="SQLite file for the differential-review cache.",
    )
    common.add_argument(
        "--verify-suggestions",
        action="store_true",
        default=env_bool("REVIEWMIND_VERIFY_SUGGESTIONS", False),
        help=(
            "Apply each finding's ``suggestion`` block in a sandboxed copy "
            "of the working tree, run --verify-cmd, and badge the result "
            "(pass/fail/skip/error) in the PR comment. Requires "
            "--inline-review and a clean working tree."
        ),
    )
    common.add_argument(
        "--verify-cmd",
        default=env_str("REVIEWMIND_VERIFY_CMD", "pytest -x"),
        help="Command run inside the sandbox to verify each suggestion.",
    )
    common.add_argument(
        "--verify-timeout",
        type=float,
        default=float(env_str("REVIEWMIND_VERIFY_TIMEOUT", "60") or 60),
        help="Seconds before the verify command is killed.",
    )
    common.add_argument(
        "--verify-workdir",
        type=Path,
        default=Path(env_str("REVIEWMIND_VERIFY_WORKDIR") or "."),
        help="Source tree the sandbox is cloned from (default: cwd).",
    )
    common.add_argument(
        "--api-consistency",
        action="store_true",
        default=env_bool("REVIEWMIND_API_CONSISTENCY", False),
        help=(
            "When the PR touches both backend (.py) and frontend "
            "(.ts/.tsx/.js/.jsx) files, run an extra cross-language step "
            "that flags request/response shape drift (renamed fields, "
            "removed routes, type changes)."
        ),
    )
    common.add_argument(
        "--pr-classify",
        action="store_true",
        default=env_bool("REVIEWMIND_PR_CLASSIFY", False),
        help=(
            "Classify the PR (bugfix / feature / refactor / docs / chore "
            "/ unknown) before reviewing, then adapt review depth + "
            "focus to the type. Docs-only PRs skip inline findings; "
            "bugfix PRs use a focused prompt with smaller budget."
        ),
    )
    common.add_argument(
        "--reproducibility-check",
        action="store_true",
        default=env_bool("REVIEWMIND_REPRODUCIBILITY_CHECK", False),
        help=(
            "Run the inline-findings step twice per file and label each "
            "finding stable / low-reproducibility based on whether it "
            "appeared in both passes. Backend-agnostic uncertainty "
            "proxy; costs one extra backend call per file."
        ),
    )
    common.add_argument(
        "--dep-upgrade-check",
        action="store_true",
        default=env_bool("REVIEWMIND_DEP_UPGRADE_CHECK", False),
        help=(
            "Detect dependency version bumps in lock files "
            "(requirements / pyproject / package.json / etc.) and "
            "ask the model whether breaking changes between the old and "
            "new versions affect this codebase's actual usage."
        ),
    )
    common.add_argument(
        "--personas",
        default=env_str("REVIEWMIND_PERSONAS", ""),
        help=(
            "Comma-separated list of review personas to run against "
            "the diff (security, performance, readability, api_stability, "
            "maintainability) — or 'all' for every persona. After the "
            "per-persona passes a conflict-finder step surfaces "
            "disagreements between them. Empty (default) disables."
        ),
    )
    common.add_argument(
        "--risk-weighted",
        action="store_true",
        default=env_bool("REVIEWMIND_RISK_WEIGHTED", False),
        help=(
            "Compute a per-file risk score (churn + complexity + bug "
            "history over the last 90 days) and scale the inline "
            "findings budget proportional to the score. Requires a git "
            "working directory."
        ),
    )
    common.add_argument(
        "--risk-workdir",
        type=Path,
        default=Path(env_str("REVIEWMIND_RISK_WORKDIR") or "."),
        help="Git working directory used to compute risk scores (default: cwd).",
    )
    common.add_argument(
        "--diff-entropy",
        action="store_true",
        default=env_bool("REVIEWMIND_DIFF_ENTROPY", False),
        help=(
            "Compute the diff's size + dispersion entropy and surface a "
            "'split this PR' warning at the top of the comment when the "
            "score crosses the 'bomb' threshold."
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
    common.add_argument(
        "--sarif-out",
        default=env_str("PRTHINKER_SARIF_OUT"),
        help="Write findings as a SARIF 2.1.0 file to this path "
             "(for GitHub code-scanning or any SARIF viewer).",
    )
    common.add_argument(
        "--html-report",
        default=env_str("PRTHINKER_HTML_REPORT"),
        help="Write a standalone HTML review report to this path.",
    )
    common.add_argument(
        "--ignore-file",
        default=env_str("PRTHINKER_IGNORE_FILE", ".prthinkerignore"),
        help="Path to a .prthinkerignore file (glob / rule: / severity: "
             "suppression rules). Missing file is a no-op.",
    )
    common.add_argument(
        "--dedupe-findings",
        action="store_true",
        default=env_bool("PRTHINKER_DEDUPE_FINDINGS", False),
        help="Collapse near-duplicate findings (same path+line, "
             "equivalent message) before submission.",
    )
    common.add_argument(
        "--api-impact",
        action="store_true",
        default=env_bool("PRTHINKER_API_IMPACT", False),
        help="Append a public-API semver-impact line "
             "(major/minor/patch) to the summary comment.",
    )
    common.add_argument(
        "--review-modes",
        default=env_str("PRTHINKER_REVIEW_MODES", ""),
        help="Comma-separated focused review passes to run over the whole "
             "diff (e.g. security,performance,iac). Each appends its output "
             "to the summary. Unknown names are skipped.",
    )
    return common


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

    common = _build_common_parser()

    p_pr = sub.add_parser("review-pr", parents=[common])
    p_pr.add_argument(
        "--platform",
        choices=["github", "gitlab", "gitea"],
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

    p_agg = sub.add_parser(
        "aggregate",
        parents=[common],
        help=(
            "Merge partial review JSONs (from `review-pr --output-json` "
            "runners in a matrix) and post a single summary + inline "
            "review + gate close to the PR."
        ),
    )
    p_agg.add_argument(
        "--platform",
        choices=["github", "gitlab", "gitea"],
        default=env_str("PRTHINKER_PLATFORM", "github"),
    )
    p_agg.add_argument(
        "--platform-base-url",
        default=env_str("PRTHINKER_PLATFORM_BASE_URL"),
    )
    p_agg.add_argument(
        "--repo",
        default=env_str("GITHUB_REPOSITORY") or env_str("CI_PROJECT_PATH"),
    )
    p_agg.add_argument(
        "--pr-number",
        type=int,
        default=int(
            env_str("PRTHINKER_PR_NUMBER")
            or env_str("CI_MERGE_REQUEST_IID", "0")
            or 0
        ),
    )
    p_agg.add_argument(
        "--github-token",
        default=env_str("GITHUB_TOKEN") or env_str("GITLAB_TOKEN"),
    )
    p_agg.add_argument(
        "--marker",
        default=env_str("PRTHINKER_COMMENT_MARKER", "<!-- prthinker:summary -->"),
    )
    p_agg.add_argument(
        "--dry-run",
        action="store_true",
    )
    p_agg.add_argument(
        "--gate-on",
        choices=["none", "warning", "error"],
        default=env_str("PRTHINKER_GATE_ON", "none"),
        help="Open a Check Run; conclude as 'failure' when findings of this "
             "severity or higher exist. Required for branch-protection gating.",
    )

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

    sub.add_parser(
        "review-commits",
        parents=[common],
        help="Review commit-message quality (messages read from stdin, one per line)",
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

    p_build_kg = sub.add_parser(
        "build-kg",
        help="Walk the repo and persist a {symbol: file:line} table to "
             "SQLite. Run once per repo (or when symbol surface drifts) "
             "before using --kg-ground on review-pr / review-file.",
    )
    p_build_kg.add_argument(
        "--workdir",
        type=Path,
        default=Path(env_str("PRTHINKER_KG_WORKDIR") or "."),
    )
    p_build_kg.add_argument(
        "--kg-store",
        type=Path,
        default=Path(env_str("PRTHINKER_KG_STORE",
                              ".prthinker/repo-kg.sqlite") or
                     ".prthinker/repo-kg.sqlite"),
    )

    p_viz_kg = sub.add_parser(
        "visualize-kg",
        help="Render the per-repo knowledge graph as a self-contained "
             "D3 force-directed HTML page. Opens in any browser; no "
             "server. Run `build-kg` first if the store is empty.",
    )
    p_viz_kg.add_argument(
        "--workdir",
        type=Path,
        default=Path(env_str("PRTHINKER_KG_WORKDIR") or "."),
    )
    p_viz_kg.add_argument(
        "--kg-store",
        type=Path,
        default=Path(env_str("PRTHINKER_KG_STORE",
                              ".prthinker/repo-kg.sqlite") or
                     ".prthinker/repo-kg.sqlite"),
    )
    p_viz_kg.add_argument(
        "--output",
        type=Path,
        default=Path(env_str("PRTHINKER_KG_HTML",
                              ".prthinker/repo-kg.html") or
                     ".prthinker/repo-kg.html"),
    )
    p_viz_kg.add_argument(
        "--name",
        default=env_str("PRTHINKER_KG_NAME", "") or "",
        help="Per-repo label. When set, the page is written to "
             "repo-kg-<name>.html next to --output, so one server can host "
             "many repos' graphs (nginx routes /kg/<name>/ to each).",
    )
    p_viz_kg.add_argument(
        "--auto-build",
        action="store_true",
        default=env_bool("PRTHINKER_KG_AUTO_BUILD", False),
        help="If the store is empty, run build-kg first instead of "
             "exiting with an error.",
    )

    p_discover = sub.add_parser(
        "discover-rules",
        parents=[common],
        help="Cluster persisted finding fingerprints across PRs and "
             "print the families that recur ≥ N times. Use to identify "
             "candidate rules for --rules-dir.",
    )
    p_discover.add_argument(
        "--cluster-store",
        type=Path,
        default=Path(env_str("PRTHINKER_CLUSTER_STORE",
                              ".prthinker/findings-index.sqlite") or
                     ".prthinker/findings-index.sqlite"),
    )
    p_discover.add_argument(
        "--similarity-threshold",
        type=float,
        default=float(env_str("PRTHINKER_CLUSTER_THRESHOLD", "0.85") or 0.85),
    )
    p_discover.add_argument(
        "--min-cluster-size",
        type=int,
        default=int(env_str("PRTHINKER_CLUSTER_MIN_SIZE", "5") or 5),
    )
    p_discover.add_argument(
        "--repo",
        default=env_str("GITHUB_REPOSITORY", ""),
        help="Filter to one repo. Empty (default) clusters across all.",
    )

    p_lessons = sub.add_parser(
        "derive-lessons",
        parents=[common],
        help="Batch recent dismissed + accepted examples and ask the "
             "model to distil general review rules; append to "
             "lessons.jsonl. Run weekly via cron or GHA schedule.",
    )
    p_lessons.add_argument(
        "--dismissed-path",
        type=Path,
        default=Path(env_str("PRTHINKER_DISMISSED_PATH",
                              ".prthinker/dismissed.jsonl") or
                     ".prthinker/dismissed.jsonl"),
    )
    p_lessons.add_argument(
        "--accepted-path",
        type=Path,
        default=Path(env_str("PRTHINKER_ACCEPTED_PATH",
                              ".prthinker/accepted.jsonl") or
                     ".prthinker/accepted.jsonl"),
    )
    p_lessons.add_argument(
        "--lessons-path",
        type=Path,
        default=Path(env_str("PRTHINKER_LESSONS_PATH",
                              ".prthinker/lessons.jsonl") or
                     ".prthinker/lessons.jsonl"),
    )
    p_lessons.add_argument(
        "--lookback-recent",
        type=int,
        default=int(env_str("PRTHINKER_LESSONS_LOOKBACK", "200") or 200),
        help="Take the most recent N entries from each corpus.",
    )
    p_lessons.add_argument(
        "--max-rules",
        type=int,
        default=int(env_str("PRTHINKER_LESSONS_MAX_RULES", "5") or 5),
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

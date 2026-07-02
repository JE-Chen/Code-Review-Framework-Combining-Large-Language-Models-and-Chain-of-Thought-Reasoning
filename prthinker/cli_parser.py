"""Argument-parser construction for the prthinker CLI.

Split out of ``cli`` so neither the parser builders nor the command
handlers push a single module past the file-length limit.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from prthinker.cli_parser_groups import (
    add_analysis_args,
    add_arbitration_args,
    add_backend_args,
    add_cache_telemetry_args,
    add_diff_cache_args,
    add_output_args,
    add_per_file_args,
    add_provider_args,
    add_rag_args,
    add_review_feature_args,
)
from prthinker.config import env_bool, env_str
from prthinker.repo_config import (
    find_config_file,
    load_repo_config,
    to_argparse_defaults,
)

log = logging.getLogger("prthinker")

_SUMMARY_MARKER = "<!-- prthinker:summary -->"
_GATE_HELP = (
    "Open a Check Run; conclude as 'failure' when findings of this "
    "severity or higher exist. Required for branch-protection gating."
)
_KG_STORE_DEFAULT = ".prthinker/repo-kg.sqlite"
_DISMISSED_DEFAULT = ".prthinker/dismissed.jsonl"
_ACCEPTED_DEFAULT = ".prthinker/accepted.jsonl"
_TELEMETRY_DEFAULT = ".prthinker/telemetry.sqlite"
_CACHE_DEFAULT = ".prthinker/cache.sqlite"


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
    add_backend_args(common)
    add_provider_args(common)
    add_arbitration_args(common)
    add_rag_args(common)
    add_per_file_args(common)
    add_review_feature_args(common)
    add_diff_cache_args(common)
    add_analysis_args(common)
    add_cache_telemetry_args(common)
    add_output_args(common)
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

    add_review_pr_parser(sub, common)
    add_pr_summary_parser(sub, common)
    add_review_file_parser(sub, common)
    add_aggregate_parser(sub, common)
    add_harvest_parsers(sub)
    add_stats_parser(sub)
    sub.add_parser(
        "review-commits",
        parents=[common],
        help="Review commit-message quality (messages read from stdin, one per line)",
    )
    add_report_parser(sub)
    sub.add_parser(
        "mcp",
        help="Run the Model Context Protocol stdio server (for Claude "
             "Desktop / Cursor / Continue / Cline / Zed integration). "
             "Reads PRTHINKER_* env vars for backend config.",
    )
    add_adversarial_parser(sub, common)
    add_kg_parsers(sub)
    add_discover_rules_parser(sub, common)
    add_derive_lessons_parser(sub, common)
    add_hook_parser(sub, common)
    add_triage_parser(sub)

    return parser


def add_triage_parser(sub) -> None:
    """Register the ``triage`` subcommand (no-model static signals)."""
    p_triage = sub.add_parser(
        "triage",
        help="Run all no-model orientation signals over a diff (no backend, "
             "no GPU). Reads stdin by default; or --diff-file / --staged / "
             "--against REF.",
    )
    source = p_triage.add_argument_group("diff source")
    source.add_argument(
        "--diff-file",
        type=Path,
        default=None,
        help="Read the unified diff from this file (default: stdin).",
    )
    source.add_argument(
        "--staged",
        action="store_true",
        help="Use `git diff --cached` (staged changes) instead of stdin.",
    )
    source.add_argument(
        "--against",
        default=None,
        metavar="REF",
        help="Use `git diff REF` (e.g. origin/main) instead of stdin.",
    )
    p_triage.add_argument(
        "--exit-nonzero-on-signal",
        action="store_true",
        help="Exit 1 if any signal fires, so the command can gate CI.",
    )


def add_review_pr_parser(sub, common: argparse.ArgumentParser) -> None:
    """Register the ``review-pr`` subcommand."""
    p_pr = sub.add_parser("review-pr", parents=[common])
    _add_review_pr_platform_args(p_pr)
    _add_review_pr_gate_args(p_pr)


def add_pr_summary_parser(sub, common: argparse.ArgumentParser) -> None:
    """Register the ``pr-summary`` subcommand."""
    p_sum = sub.add_parser(
        "pr-summary",
        parents=[common],
        help=(
            "Generate a Copilot-style PR summary from the PR title, "
            "description, commit messages, and diff, then upsert it as a "
            "dedicated PR comment. Designed to run before the per-file "
            "review starts (e.g. the enumerate job)."
        ),
    )
    _add_review_pr_platform_args(p_sum)


def _add_review_pr_platform_args(p_pr: argparse.ArgumentParser) -> None:
    """Add platform / repo / token / marker arguments to ``review-pr``."""
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
        default=env_str("PRTHINKER_COMMENT_MARKER", _SUMMARY_MARKER),
    )
    p_pr.add_argument(
        "--dry-run",
        action="store_true",
    )


def _add_review_pr_gate_args(p_pr: argparse.ArgumentParser) -> None:
    """Add auto-fix / gate / CI-signal arguments to ``review-pr``."""
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
        help=_GATE_HELP,
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


def add_review_file_parser(sub, common: argparse.ArgumentParser) -> None:
    """Register the ``review-file`` subcommand."""
    p_file = sub.add_parser("review-file", parents=[common])
    p_file.add_argument("path", help="Path to a code/diff file, or '-' for stdin")
    p_file.add_argument("--output-dir", type=Path, default=None)


def add_aggregate_parser(sub, common: argparse.ArgumentParser) -> None:
    """Register the ``aggregate`` subcommand."""
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
    _add_aggregate_target_args(p_agg)

    p_status = sub.add_parser(
        "post-status",
        help=(
            "Upsert a 'review in progress' placeholder comment so reviewers "
            "see the review has started before the full result is posted."
        ),
    )
    p_status.add_argument(
        "--platform",
        choices=["github", "gitlab", "gitea"],
        default=env_str("PRTHINKER_PLATFORM", "github"),
    )
    p_status.add_argument(
        "--platform-base-url",
        default=env_str("PRTHINKER_PLATFORM_BASE_URL"),
    )
    _add_aggregate_target_args(p_status)


def _add_aggregate_target_args(p_agg: argparse.ArgumentParser) -> None:
    """Add repo / PR / token / marker / gate arguments to ``aggregate``."""
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
        default=env_str("PRTHINKER_COMMENT_MARKER", _SUMMARY_MARKER),
    )
    p_agg.add_argument(
        "--dry-run",
        action="store_true",
    )
    p_agg.add_argument(
        "--gate-on",
        choices=["none", "warning", "error"],
        default=env_str("PRTHINKER_GATE_ON", "none"),
        help=_GATE_HELP,
    )


def add_harvest_parsers(sub) -> None:
    """Register the ``harvest-dismissed`` and ``harvest-accepted`` subcommands."""
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
        default=Path(env_str("PRTHINKER_DISMISSED_PATH", _DISMISSED_DEFAULT) or
                     _DISMISSED_DEFAULT),
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
        default=Path(env_str("PRTHINKER_ACCEPTED_PATH", _ACCEPTED_DEFAULT) or
                     _ACCEPTED_DEFAULT),
    )


def add_stats_parser(sub) -> None:
    """Register the ``stats`` subcommand."""
    p_stats = sub.add_parser(
        "stats",
        help="Aggregate telemetry: tokens, cost, latency, cache hit rate",
    )
    p_stats.add_argument(
        "--telemetry-path",
        default=env_str("PRTHINKER_TELEMETRY_PATH", _TELEMETRY_DEFAULT),
    )
    p_stats.add_argument(
        "--since-days",
        type=float,
        default=None,
        help="Restrict to calls within the last N days (default: all-time)",
    )
    p_stats.add_argument(
        "--cache-path",
        default=env_str("PRTHINKER_CACHE_PATH", _CACHE_DEFAULT),
        help="Also report cache fill / hit counters if the file exists",
    )


def add_report_parser(sub) -> None:
    """Register the ``report`` subcommand."""
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
        default=Path(env_str("PRTHINKER_TELEMETRY_PATH", _TELEMETRY_DEFAULT)
                     or _TELEMETRY_DEFAULT),
    )
    p_report.add_argument(
        "--cache-path",
        type=Path,
        default=Path(env_str("PRTHINKER_CACHE_PATH", _CACHE_DEFAULT)
                     or _CACHE_DEFAULT),
    )
    p_report.add_argument(
        "--dismissed-path",
        type=Path,
        default=Path(env_str("PRTHINKER_DISMISSED_PATH", _DISMISSED_DEFAULT)
                     or _DISMISSED_DEFAULT),
    )
    p_report.add_argument(
        "--accepted-path",
        type=Path,
        default=Path(env_str("PRTHINKER_ACCEPTED_PATH", _ACCEPTED_DEFAULT)
                     or _ACCEPTED_DEFAULT),
    )


def add_adversarial_parser(sub, common: argparse.ArgumentParser) -> None:
    """Register the ``adversarial-eval`` subcommand."""
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


def add_kg_parsers(sub) -> None:
    """Register the ``build-kg`` and ``visualize-kg`` subcommands."""
    _add_build_kg_parser(sub)
    _add_visualize_kg_parser(sub)


def _add_build_kg_parser(sub) -> None:
    """Register the ``build-kg`` subcommand."""
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
                              _KG_STORE_DEFAULT) or
                     _KG_STORE_DEFAULT),
    )


def _add_visualize_kg_parser(sub) -> None:
    """Register the ``visualize-kg`` subcommand."""
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
                              _KG_STORE_DEFAULT) or
                     _KG_STORE_DEFAULT),
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


def add_discover_rules_parser(sub, common: argparse.ArgumentParser) -> None:
    """Register the ``discover-rules`` subcommand."""
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


def add_derive_lessons_parser(sub, common: argparse.ArgumentParser) -> None:
    """Register the ``derive-lessons`` subcommand."""
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
                              _DISMISSED_DEFAULT) or
                     _DISMISSED_DEFAULT),
    )
    p_lessons.add_argument(
        "--accepted-path",
        type=Path,
        default=Path(env_str("PRTHINKER_ACCEPTED_PATH",
                              _ACCEPTED_DEFAULT) or
                     _ACCEPTED_DEFAULT),
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


def add_hook_parser(sub, common: argparse.ArgumentParser) -> None:
    """Register the ``hook`` subcommand."""
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

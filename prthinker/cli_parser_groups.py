"""Shared-parser argument-group helpers for the prthinker CLI parser.

Extracted from ``cli_parser`` so the shared-parser builder does not push
a single module past the file-length and cyclomatic-complexity limits.
Imported only by ``cli_parser``.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from prthinker.arbitration import STRATEGY_NAMES
from prthinker.config import (
    CACHE_DEFAULT,
    KG_STORE_DEFAULT,
    TELEMETRY_DEFAULT,
    env_bool,
    env_float,
    env_int,
    env_path,
    env_str,
)
from prthinker.cli_parser_provider_groups import (
    add_backend_args,
    add_provider_args,
)

__all__ = ["add_backend_args", "add_provider_args"]

_REPO_CONTEXT_STRATEGIES = (
    "none",
    "lexical",
    "semantic",
    "structural",
    "graph",
    "rerank",
    "block_rerank",
    "iterative",
    "query_rewrite",
)


def _env_str_compat(
    primary: str, legacy: str, default: str | None = None
) -> str | None:
    """Read a PRTHINKER_* env var, falling back to the legacy REVIEWMIND_*."""
    return env_str(primary, env_str(legacy, default))


def _env_bool_compat(primary: str, legacy: str, default: bool) -> bool:
    """Boolean env reader with PRTHINKER_* precedence and REVIEWMIND_* fallback."""
    if env_str(primary) is not None:
        return env_bool(primary, default)
    return env_bool(legacy, default)


def add_arbitration_args(common: argparse.ArgumentParser) -> None:
    """Add the opt-in multi-model finding-arbitration arguments."""
    common.add_argument(
        "--arbitration",
        action="store_true",
        default=env_bool("PRTHINKER_ARBITRATION", False),
        help="After the review, have extra model backends vote "
        "confirm/reject on each inline finding and drop the "
        "off-voted ones. Fail-open: arbiter failures keep findings.",
    )
    common.add_argument(
        "--arbitration-backends",
        default=env_str("PRTHINKER_ARBITRATION_BACKENDS", ""),
        help="Comma-separated backend kinds acting as arbiters (e.g. "
        "'openai,anthropic,claude-cli'). Each is configured by the "
        "same flags / env vars as when used as the primary backend.",
    )
    common.add_argument(
        "--arbitration-strategy",
        choices=list(STRATEGY_NAMES),
        default=env_str("PRTHINKER_ARBITRATION_STRATEGY", "majority"),
        help="How votes combine: majority (rejects must outnumber "
        "confirms to drop), unanimous (any reject drops), any "
        "(one confirm keeps).",
    )
    common.add_argument(
        "--arbitration-max-new-tokens",
        type=int,
        default=env_int("PRTHINKER_ARBITRATION_MAX_NEW_TOKENS", 4096),
        help="Generation budget for each arbiter's vote call.",
    )


def add_rag_args(common: argparse.ArgumentParser) -> None:
    """Add RAG + generation-budget arguments to the shared parser."""
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
    rag_threshold_env = env_str("PRTHINKER_RAG_THRESHOLD", "")
    common.add_argument(
        "--rag-threshold",
        type=float,
        default=float(rag_threshold_env) if rag_threshold_env else None,
        help=(
            "Cosine cutoff for RAG rules. Default: the calibrated value "
            "for the local embedding model; 0.7 on remote calls."
        ),
    )
    common.add_argument(
        "--max-new-tokens",
        type=int,
        default=env_int("PRTHINKER_MAX_NEW_TOKENS", 32768),
    )
    common.add_argument(
        "--steps",
        default="",
    )
    _add_repo_context_args(common)


def _add_repo_context_args(common: argparse.ArgumentParser) -> None:
    """Add the cross-file repository-context retrieval arguments."""
    common.add_argument(
        "--repo-context-strategy",
        choices=_REPO_CONTEXT_STRATEGIES,
        default=env_str("PRTHINKER_REPO_CONTEXT_STRATEGY", "none"),
        help=(
            "Cross-file repository context strategy for local per-file review. "
            "'none' preserves the existing prompt; lexical/semantic/structural/"
            "graph/rerank/block_rerank/iterative/query_rewrite inject related "
            "files into each file prompt."
        ),
    )
    common.add_argument(
        "--repo-context-workdir",
        type=Path,
        default=env_path("PRTHINKER_REPO_CONTEXT_WORKDIR", "."),
        help="Work tree used by --repo-context-strategy and import-graph context.",
    )
    common.add_argument(
        "--repo-context-top-k",
        type=int,
        default=env_int("PRTHINKER_REPO_CONTEXT_TOP_K", 10),
        help="Maximum files considered by file-level repository context retrieval.",
    )
    common.add_argument(
        "--repo-context-keep-ratio",
        type=float,
        default=env_float("PRTHINKER_REPO_CONTEXT_KEEP_RATIO", 0.0),
        help=(
            "Lexical keep-ratio cutoff for repo-context retrieval; 0 keeps the "
            "fixed top-k tail."
        ),
    )
    _add_repo_context_tuning_args(common)


def _add_repo_context_tuning_args(common: argparse.ArgumentParser) -> None:
    """Add the block / vote / round / focus tuning knobs for repo context."""
    common.add_argument(
        "--repo-context-block-candidates",
        type=int,
        default=env_int("PRTHINKER_REPO_CONTEXT_BLOCK_CANDIDATES", 6),
        help="Candidate blocks per file for block_rerank/iterative strategies.",
    )
    common.add_argument(
        "--repo-context-votes",
        type=int,
        default=env_int("PRTHINKER_REPO_CONTEXT_VOTES", 1),
        help="Self-consistency votes for model-in-the-loop repo retrieval.",
    )
    common.add_argument(
        "--repo-context-rounds",
        type=int,
        default=env_int("PRTHINKER_REPO_CONTEXT_ROUNDS", 3),
        help="Maximum rounds for the iterative repo-context strategy.",
    )
    common.add_argument(
        "--repo-context-focus-lines",
        type=int,
        default=env_int("PRTHINKER_REPO_CONTEXT_FOCUS_LINES", 0),
        help="Optional line-window focus for block context; 0 disables.",
    )


def add_per_file_args(common: argparse.ArgumentParser) -> None:
    """Add per-file / inline-review / matrix-runner arguments to the shared parser."""
    _add_per_file_mode_args(common)
    _add_matrix_output_args(common)
    common.add_argument(
        "--step-dag",
        default="",
        help="JSON object mapping step names to dependency lists",
    )
    common.add_argument(
        "--trajectory-out",
        default="",
        help="Append content-safe review trajectory JSONL",
    )


def _add_per_file_mode_args(common: argparse.ArgumentParser) -> None:
    """Add per-file mode + inline-review selection arguments."""
    _add_per_file_toggle_args(common)
    _add_pr_presentation_args(common)
    _add_per_file_summary_args(common)
    _add_per_file_scope_args(common)


def _add_per_file_toggle_args(common: argparse.ArgumentParser) -> None:
    """Add the per-file / inline-review toggle flags."""
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
        "--parallelism",
        type=int,
        default=1,
        help="Bounded per-file workers; capped by backend capability.",
    )
    common.add_argument(
        "--step-plan",
        choices=["full", "adaptive"],
        default=env_str("PRTHINKER_STEP_PLAN", "full"),
        help=(
            "Per-file review depth. 'full' runs every configured step on "
            "every file; 'adaptive' scales the CoT chain to each file — "
            "docs/config/tiny diffs skip the analysis chain, mid-size "
            "changes drop the per-file PR summary, large or high-risk "
            "files keep the full sweep."
        ),
    )
    _add_summary_display_args(common)


def _add_summary_display_args(common: argparse.ArgumentParser) -> None:
    """Add the summary display-filtering flags."""
    common.add_argument(
        "--findings-only",
        action="store_true",
        default=env_bool("PRTHINKER_FINDINGS_ONLY", False),
        help=(
            "Summary lists only files that have findings; clean files are "
            "collapsed into a count. A PR with zero findings collapses to a "
            "one-line confirmation instead of a full empty result."
        ),
    )
    common.add_argument(
        "--hide-info",
        action="store_true",
        default=env_bool("PRTHINKER_HIDE_INFO", False),
        help=(
            "Omit info-severity findings from the rendered summary (display "
            "only; the inline review and merge gate still see them)."
        ),
    )


def _add_pr_presentation_args(common: argparse.ArgumentParser) -> None:
    """Add the PR overview / labels / check-annotation flags."""
    common.add_argument(
        "--pr-overview",
        action="store_true",
        default=env_bool("PRTHINKER_PR_OVERVIEW", False),
        help=(
            "Pin a model-free 'what this PR does' overview (built from the "
            "commit messages and changed files) to the top of the summary."
        ),
    )
    common.add_argument(
        "--pr-labels",
        action="store_true",
        default=env_bool("PRTHINKER_PR_LABELS", False),
        help=(
            "Apply prthinker-managed PR labels (size bucket + review status); "
            "human-applied labels are left untouched."
        ),
    )
    common.add_argument(
        "--check-annotations",
        action="store_true",
        default=env_bool("PRTHINKER_CHECK_ANNOTATIONS", False),
        help=(
            "Attach per-line Check Run annotations to the gate — a robust "
            "parallel channel to inline comments (a bad line cannot 422 the "
            "whole batch)."
        ),
    )


def _add_per_file_summary_args(common: argparse.ArgumentParser) -> None:
    """Add the delta / summary-rendering arguments for per-file mode."""
    common.add_argument(
        "--review-delta",
        action="store_true",
        default=env_bool("PRTHINKER_REVIEW_DELTA", False),
        help=(
            "Show a 'since last review' new/resolved tally in the digest, "
            "comparing against fingerprints persisted in the per-PR state."
        ),
    )
    common.add_argument(
        "--delta-state",
        default=env_str(
            "PRTHINKER_DELTA_STATE", ".prthinker/pr-state/findings-fp.json"
        ),
        help="Path to the persisted finding-fingerprint file for --review-delta.",
    )
    common.add_argument(
        "--summary-min-confidence",
        type=float,
        default=env_float("PRTHINKER_SUMMARY_MIN_CONFIDENCE", 0.0),
        help=(
            "Drop findings whose model confidence is below this floor (0–1) "
            "from the rendered summary; findings without a score are kept. "
            "Display only — the inline review and gate are unaffected."
        ),
    )
    common.add_argument(
        "--summary-table",
        action="store_true",
        default=env_bool("PRTHINKER_SUMMARY_TABLE", False),
        help=(
            "Render findings as one compact table (severity | location | "
            "finding) instead of per-file collapsible blocks."
        ),
    )
    common.add_argument(
        "--max-findings-per-file",
        type=int,
        default=env_int("PRTHINKER_MAX_FINDINGS_PER_FILE", 10),
    )


def _add_per_file_scope_args(common: argparse.ArgumentParser) -> None:
    """Add the file-scoping arguments (exclude globs, single target file)."""
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


def _add_matrix_output_args(common: argparse.ArgumentParser) -> None:
    """Add matrix-runner JSON-output / aggregation arguments."""
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


def add_review_feature_args(common: argparse.ArgumentParser) -> None:
    """Add optional review-augmentation feature flags to the shared parser."""
    _add_dialogue_feature_args(common)
    _add_kg_lessons_args(common)


def _add_dialogue_feature_args(common: argparse.ArgumentParser) -> None:
    """Add reply / counterfactual / provenance review-augmentation flags."""
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
        "--walkthrough",
        action="store_true",
        default=env_bool("PRTHINKER_WALKTHROUGH", False),
        help=(
            "Generate a short model-written narrative of what each file "
            "change does and why, pinned to the top of that file's block — "
            "the inference-backed counterpart to the commit-message PR "
            "overview. Independent of --inline-review."
        ),
    )


def _add_kg_lessons_args(common: argparse.ArgumentParser) -> None:
    """Add knowledge-graph grounding and repo-lessons injection flags."""
    _add_kg_grounding_args(common)
    _add_kg_map_lessons_args(common)


def _add_kg_grounding_args(common: argparse.ArgumentParser) -> None:
    """Add the knowledge-graph store / grounding configuration flags."""
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
        default=env_path("PRTHINKER_KG_STORE", KG_STORE_DEFAULT),
    )
    common.add_argument(
        "--kg-workdir",
        type=Path,
        default=env_path("PRTHINKER_KG_WORKDIR", "."),
        help="Workdir scope the KG was built against.",
    )


def _add_kg_map_lessons_args(common: argparse.ArgumentParser) -> None:
    """Add the impact/order/change-map and repo-lessons injection flags."""
    _add_kg_map_args(common)
    _add_lessons_args(common)


def _add_kg_map_args(common: argparse.ArgumentParser) -> None:
    """Add the full-scan / body-summary / impact / order / change-map flags."""
    common.add_argument(
        "--require-full-scan",
        action="store_true",
        default=env_bool("PRTHINKER_REQUIRE_FULL_SCAN", False),
        help=(
            "Withhold the report (post only a progress notice) until every "
            "PR file has been reviewed — never publish a partial result."
        ),
    )
    common.add_argument(
        "--pr-body-summary",
        action="store_true",
        default=env_bool("PRTHINKER_PR_BODY_SUMMARY", False),
        help=(
            "Upsert the at-a-glance digest into the PR description (body) "
            "between markers, so the verdict shows at the top of the PR."
        ),
    )
    common.add_argument(
        "--impact-map",
        action="store_true",
        default=env_bool("PRTHINKER_IMPACT_MAP", False),
        help=(
            "Add an 'Impacted areas' note to the overview listing downstream "
            "importers of the changed files (from the repo knowledge graph)."
        ),
    )
    common.add_argument(
        "--review-order",
        action="store_true",
        default=env_bool("PRTHINKER_REVIEW_ORDER", False),
        help=(
            "Add a 'Suggested review order' note that ranks the changed files "
            "most-depended-upon first (from the repo knowledge graph), so the "
            "reviewer reads foundational changes before their call sites."
        ),
    )
    common.add_argument(
        "--change-map",
        action="store_true",
        default=env_bool("PRTHINKER_CHANGE_MAP", False),
        help=(
            "Embed a small Mermaid graph of the import edges between the "
            "changed files (from the repo knowledge graph) so the shape of "
            "the change is visible inline."
        ),
    )


def _add_lessons_args(common: argparse.ArgumentParser) -> None:
    """Add the repo-derived lessons injection flags."""
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
        default=env_int("PRTHINKER_LESSONS_TOP_K", 5),
        help="Number of lessons to inject per file (most recent first).",
    )


def add_diff_cache_args(common: argparse.ArgumentParser) -> None:
    """Add differential-review + suggestion-verification arguments to the shared parser."""
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
    _add_verify_args(common)


def _add_verify_args(common: argparse.ArgumentParser) -> None:
    """Add the sandboxed suggestion-verification arguments."""
    common.add_argument(
        "--verify-suggestions",
        action="store_true",
        default=_env_bool_compat(
            "PRTHINKER_VERIFY_SUGGESTIONS",
            "REVIEWMIND_VERIFY_SUGGESTIONS",
            False,
        ),
        help=(
            "Apply each finding's ``suggestion`` block in a sandboxed copy "
            "of the working tree, run --verify-cmd, and badge the result "
            "(pass/fail/skip/error) in the PR comment. Requires "
            "--inline-review and a clean working tree."
        ),
    )
    common.add_argument(
        "--verify-cmd",
        default=_env_str_compat(
            "PRTHINKER_VERIFY_CMD", "REVIEWMIND_VERIFY_CMD", "pytest -x"
        ),
        help="Command run inside the sandbox to verify each suggestion.",
    )
    common.add_argument(
        "--verify-timeout",
        type=float,
        default=float(
            _env_str_compat(
                "PRTHINKER_VERIFY_TIMEOUT", "REVIEWMIND_VERIFY_TIMEOUT", "60"
            )
            or 60
        ),
        help="Seconds before the verify command is killed.",
    )
    common.add_argument(
        "--verify-workdir",
        type=Path,
        default=Path(
            _env_str_compat("PRTHINKER_VERIFY_WORKDIR", "REVIEWMIND_VERIFY_WORKDIR")
            or "."
        ),
        help="Source tree the sandbox is cloned from (default: cwd).",
    )


def add_analysis_args(common: argparse.ArgumentParser) -> None:
    """Add cross-cutting analysis feature flags to the shared parser."""
    _add_classification_args(common)
    _add_risk_args(common)


def _add_classification_args(common: argparse.ArgumentParser) -> None:
    """Add API-consistency / classification / reproducibility / dependency flags."""
    _add_pr_classification_args(common)
    _add_change_audit_args(common)


def _add_pr_classification_args(common: argparse.ArgumentParser) -> None:
    """Add the API-consistency and PR-classification flags."""
    common.add_argument(
        "--api-consistency",
        action="store_true",
        default=_env_bool_compat(
            "PRTHINKER_API_CONSISTENCY", "REVIEWMIND_API_CONSISTENCY", False
        ),
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
        default=_env_bool_compat(
            "PRTHINKER_PR_CLASSIFY", "REVIEWMIND_PR_CLASSIFY", False
        ),
        help=(
            "Classify the PR (bugfix / feature / refactor / docs / chore "
            "/ unknown) before reviewing, then adapt review depth + "
            "focus to the type. Docs-only PRs skip inline findings; "
            "bugfix PRs use a focused prompt with smaller budget."
        ),
    )


def _add_change_audit_args(common: argparse.ArgumentParser) -> None:
    """Add the reproducibility and dependency-upgrade audit flags."""
    common.add_argument(
        "--reproducibility-check",
        action="store_true",
        default=_env_bool_compat(
            "PRTHINKER_REPRODUCIBILITY_CHECK",
            "REVIEWMIND_REPRODUCIBILITY_CHECK",
            False,
        ),
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
        default=_env_bool_compat(
            "PRTHINKER_DEP_UPGRADE_CHECK", "REVIEWMIND_DEP_UPGRADE_CHECK", False
        ),
        help=(
            "Detect dependency version bumps in lock files "
            "(requirements / pyproject / package.json / etc.) and "
            "ask the model whether breaking changes between the old and "
            "new versions affect this codebase's actual usage."
        ),
    )


def _add_risk_args(common: argparse.ArgumentParser) -> None:
    """Add persona / risk-weighting / diff-entropy / rules-dir flags."""
    _add_persona_risk_args(common)
    _add_diff_signal_args(common)


def _add_persona_risk_args(common: argparse.ArgumentParser) -> None:
    """Add the persona and risk-weighted budget flags."""
    common.add_argument(
        "--personas",
        default=_env_str_compat("PRTHINKER_PERSONAS", "REVIEWMIND_PERSONAS", ""),
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
        default=_env_bool_compat(
            "PRTHINKER_RISK_WEIGHTED", "REVIEWMIND_RISK_WEIGHTED", False
        ),
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
        default=Path(
            _env_str_compat("PRTHINKER_RISK_WORKDIR", "REVIEWMIND_RISK_WORKDIR")
            or "."
        ),
        help="Git working directory used to compute risk scores (default: cwd).",
    )


def _add_diff_signal_args(common: argparse.ArgumentParser) -> None:
    """Add the diff-entropy and per-repo rules-dir flags."""
    common.add_argument(
        "--diff-entropy",
        action="store_true",
        default=_env_bool_compat(
            "PRTHINKER_DIFF_ENTROPY", "REVIEWMIND_DIFF_ENTROPY", False
        ),
        help=(
            "Compute the diff's size + dispersion entropy and surface a "
            "'split this PR' warning at the top of the comment when the "
            "score crosses the 'bomb' threshold."
        ),
    )
    common.add_argument(
        "--rules-dir",
        type=Path,
        default=Path(env_str("PRTHINKER_RULES_DIR") or "")
        if env_str("PRTHINKER_RULES_DIR")
        else None,
        help="Directory of *.md files containing per-repo coding rules",
    )


def add_cache_telemetry_args(common: argparse.ArgumentParser) -> None:
    """Add cache + telemetry arguments to the shared parser."""
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
        default=env_str("PRTHINKER_CACHE_PATH", CACHE_DEFAULT),
    )
    common.add_argument(
        "--cache-ttl-days",
        type=float,
        default=env_float("PRTHINKER_CACHE_TTL_DAYS", 7.0),
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
        default=env_str("PRTHINKER_TELEMETRY_PATH", TELEMETRY_DEFAULT),
    )


def add_output_args(common: argparse.ArgumentParser) -> None:
    """Add streaming, judging, and report-output arguments to the shared parser."""
    _add_generation_output_args(common)
    _add_report_output_args(common)


def _add_generation_output_args(common: argparse.ArgumentParser) -> None:
    """Add streaming / judge / self-correct / redaction generation flags."""
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


def _add_report_output_args(common: argparse.ArgumentParser) -> None:
    """Add SARIF / HTML / ignore-file / dedupe / confidence report-output flags."""
    _add_report_format_args(common)
    _add_report_extra_format_args(common)
    _add_report_filter_args(common)


def _add_report_format_args(common: argparse.ArgumentParser) -> None:
    """Add the SARIF / HTML / Code Quality / JUnit / CSV report flags."""
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
        "--codequality-out",
        default=env_str("PRTHINKER_CODEQUALITY_OUT"),
        help="Write findings + signals as a GitLab Code Quality "
        "(CodeClimate) JSON report to this path.",
    )
    common.add_argument(
        "--junit-out",
        default=env_str("PRTHINKER_JUNIT_OUT"),
        help="Write findings + signals as a JUnit XML report to this path "
        "(for CI test-report viewers).",
    )
    common.add_argument(
        "--csv-out",
        default=env_str("PRTHINKER_CSV_OUT"),
        help="Write findings + signals as a flat CSV to this path "
        "(spreadsheet / awk triage).",
    )


def _add_report_extra_format_args(common: argparse.ArgumentParser) -> None:
    """Add the metrics / Markdown / Sonar / report-dir / annotation flags."""
    common.add_argument(
        "--metrics-out",
        default=env_str("PRTHINKER_METRICS_OUT"),
        help="Write a machine-readable metrics-rollup JSON (counts by "
        "severity / signal, diff totals) to this path.",
    )
    common.add_argument(
        "--markdown-out",
        default=env_str("PRTHINKER_MARKDOWN_OUT"),
        help="Write a standalone Markdown review report to this path.",
    )
    common.add_argument(
        "--sonar-out",
        default=env_str("PRTHINKER_SONAR_OUT"),
        help="Write findings + signals as SonarQube Generic Issue Data "
        "JSON to this path.",
    )
    common.add_argument(
        "--report-dir",
        default=env_str("PRTHINKER_REPORT_DIR"),
        help="Write every file-based report format (SARIF / HTML / "
        "Markdown / Code Quality / Sonar / JUnit / CSV / metrics) "
        "into this directory with standard filenames.",
    )
    common.add_argument(
        "--gha-annotations",
        action="store_true",
        default=env_bool("PRTHINKER_GHA_ANNOTATIONS", False),
        help="Emit findings + signals as GitHub Actions workflow commands "
        "on stdout (inline ::error / ::warning / ::notice annotations).",
    )


def _add_report_filter_args(common: argparse.ArgumentParser) -> None:
    """Add ignore-file / dedupe / confidence / review-mode flags."""
    _add_finding_filter_args(common)
    _add_calibration_args(common)
    _add_review_mode_args(common)


def _add_finding_filter_args(common: argparse.ArgumentParser) -> None:
    """Add the ignore-file / dedupe / impact / confidence filter flags."""
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
        "--min-confidence",
        type=float,
        default=env_float("PRTHINKER_MIN_CONFIDENCE", 0.0),
        help="Drop findings whose provenance confidence is below this "
        "threshold (0 keeps all; findings without a confidence are "
        "always kept). Use with --provenance.",
    )


def _add_calibration_args(common: argparse.ArgumentParser) -> None:
    """Add the confidence-calibration store flags."""
    common.add_argument("--calibration-store", default="", help="SQLite feedback calibration store")
    common.add_argument("--calibration-author", default="", help="Author key for confidence calibration")
    common.add_argument("--calibration-category", default="", help="Finding category key for calibration")
    common.add_argument("--calibration-min-samples", type=int, default=10)
    common.add_argument("--calibration-half-life-days", type=float, default=90)
    common.add_argument(
        "--calibration-gate",
        action="store_true",
        default=env_bool("PRTHINKER_CALIBRATION_GATE", False),
        help=(
            "Apply the calibration store to merge-gate scoring. Low-confidence "
            "findings may still appear in reports, but calibrated abstentions "
            "do not block the gate."
        ),
    )


def _add_review_mode_args(common: argparse.ArgumentParser) -> None:
    """Add the review-preset and focused review-mode flags."""
    common.add_argument(
        "--review-preset",
        choices=["none", "backend", "frontend", "security", "release"],
        default=env_str("PRTHINKER_REVIEW_PRESET", "none"),
        help="Enable a focused bundle of review modes and safety checks.",
    )
    common.add_argument(
        "--review-modes",
        default=env_str("PRTHINKER_REVIEW_MODES", ""),
        help="Comma-separated focused review passes to run over the whole "
        "diff (e.g. security,performance,iac). Each appends its output "
        "to the summary. Unknown names are skipped.",
    )

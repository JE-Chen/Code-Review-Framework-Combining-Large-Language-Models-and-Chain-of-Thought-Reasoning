"""Auto-fix PR / MR orchestration for ``review-pr``.

Split out of :mod:`prthinker.cli_review` to keep that module under the
file-length bar. These helpers group threshold-passing warning suggestions
per file and open a draft auto-fix pull request (GitHub, Gitea) or merge
request (GitLab) for them.

Every step here is best-effort: a missing base branch, an unreachable API,
or a failed apply logs and returns rather than failing the surrounding
review. The module imports only lower layers (config, pipeline, schemas, and
the lazily-imported ``auto_fix`` / ``github_api`` / ``platforms`` helpers); it
never imports :mod:`prthinker.cli_review`, so the dependency edge runs one way
(``cli_review`` -> ``cli_review_autofix``).
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from prthinker.config import GitHubConfig
from prthinker.pipeline import ReviewResult
from prthinker.schemas import InlineFinding

log = logging.getLogger("prthinker")


def _maybe_autofix(
    args: argparse.Namespace,
    result: ReviewResult,
    platform_kind: object,
    adapter: object,
) -> None:
    """Open a draft auto-fix PR / MR when the threshold is set."""
    from prthinker.platforms import PlatformKind

    if not (args.auto_fix_threshold and not args.dry_run):
        return
    if platform_kind is PlatformKind.GITHUB:
        gh = GitHubConfig(
            repo=args.repo,
            pr_number=args.pr_number,
            token=args.github_token,
            comment_marker=args.marker,
        )
        _maybe_open_auto_fix_pr(gh, args, result)
        return
    if platform_kind is PlatformKind.GITLAB:
        _maybe_open_auto_fix_mr(args, result, adapter)
        return
    if platform_kind is PlatformKind.GITEA:
        _maybe_open_auto_fix_gitea_pr(args, result, adapter)
        return
    log.info("Auto-fix not yet supported on %s — skipping", platform_kind.value)


def _resolve_auto_fix_base_branch(
    gh: GitHubConfig, args: argparse.Namespace
) -> str | None:
    """Return the auto-fix base branch, fetching it from the PR if unset."""
    base_branch = args.auto_fix_base_branch
    if base_branch:
        return base_branch

    from prthinker.github_api import fetch_pr_base_branch

    try:
        return fetch_pr_base_branch(gh)
    except Exception as exc:
        log.warning("Auto-fix: could not fetch base branch: %s", exc)
        return None


def _report_auto_fix_outcome(auto_result: object | None, ref_prefix: str) -> None:
    """Log the auto-fix outcome uniformly for the PR and MR paths."""
    if auto_result is None:
        log.info(
            "Auto-fix: no edits applied (every suggestion conflicted or "
            "the target files did not exist)"
        )
        return
    log.info(
        "Auto-fix %s%s opened: %s (applied=%d skipped=%d files=%d)",
        ref_prefix,
        auto_result.pr_number,
        auto_result.pr_url,
        auto_result.total_findings_applied,
        auto_result.total_findings_skipped,
        len(auto_result.files_changed),
    )


def _open_auto_fix_pr_and_report(
    gh: GitHubConfig,
    findings_by_file: dict[str, list[InlineFinding]],
    base_branch: str,
) -> None:
    """Open the auto-fix PR for the collected findings and log the outcome."""
    from prthinker.auto_fix import open_auto_fix_pr

    try:
        auto_result = open_auto_fix_pr(
            config=gh,
            findings_by_file=findings_by_file,
            base_pr_number=gh.pr_number,
            base_branch=base_branch,
            repo_root=Path.cwd(),
        )
    except Exception as exc:
        log.error("Auto-fix failed: %s", exc)
        return

    _report_auto_fix_outcome(auto_result, "PR #")


def _collect_auto_fix_findings(
    args: argparse.Namespace, result: ReviewResult
) -> dict[str, list[InlineFinding]] | None:
    """Group threshold-passing warning suggestions per file, or None to skip."""
    eligible = [
        f
        for f in result.inline_findings
        if f.severity == "warning" and f.suggestion is not None
    ]
    if len(eligible) < args.auto_fix_threshold:
        log.info(
            "Auto-fix: %d eligible suggestion(s) below threshold %d — skipped",
            len(eligible),
            args.auto_fix_threshold,
        )
        return None
    findings_by_file: dict[str, list[InlineFinding]] = {}
    for f in eligible:
        findings_by_file.setdefault(f.path, []).append(f)
    return findings_by_file


def _maybe_open_auto_fix_pr(
    gh: GitHubConfig,
    args: argparse.Namespace,
    result: ReviewResult,
) -> None:
    """Apply ``--auto-fix-threshold`` to surviving warning suggestions."""
    findings_by_file = _collect_auto_fix_findings(args, result)
    if findings_by_file is None:
        return

    base_branch = _resolve_auto_fix_base_branch(gh, args)
    if base_branch is None:
        return

    _open_auto_fix_pr_and_report(gh, findings_by_file, base_branch)


def _resolve_mr_base_branch(args: argparse.Namespace, adapter: object) -> str | None:
    """Return the auto-fix target branch, asking the adapter when unset.

    Shared by the GitLab (MR) and Gitea (PR) paths — both resolve the
    base through the platform adapter's ``fetch_base_branch``.
    """
    if args.auto_fix_base_branch:
        return args.auto_fix_base_branch
    try:
        return adapter.fetch_base_branch() or None
    except Exception as exc:  # noqa: BLE001 — auto-fix is best-effort
        log.warning("Auto-fix: could not fetch base branch: %s", exc)
        return None


def _maybe_open_auto_fix_mr(
    args: argparse.Namespace,
    result: ReviewResult,
    adapter: object,
) -> None:
    """GitLab twin of ``_maybe_open_auto_fix_pr``: open a draft MR."""
    findings_by_file = _collect_auto_fix_findings(args, result)
    if findings_by_file is None:
        return

    base_branch = _resolve_mr_base_branch(args, adapter)
    if base_branch is None:
        return

    from prthinker.auto_fix import GitLabMRTarget, open_auto_fix_mr

    target = GitLabMRTarget(
        project=args.repo,
        token=args.github_token,
        mr_iid=int(args.pr_number),
        base_url=getattr(adapter, "base_url", "https://gitlab.com/api/v4"),
    )
    try:
        auto_result = open_auto_fix_mr(
            target, findings_by_file, base_branch, Path.cwd()
        )
    except Exception as exc:  # noqa: BLE001 — auto-fix must never fail the review
        log.error("Auto-fix failed: %s", exc)
        return
    _report_auto_fix_outcome(auto_result, "MR !")


def _maybe_open_auto_fix_gitea_pr(
    args: argparse.Namespace,
    result: ReviewResult,
    adapter: object,
) -> None:
    """Gitea twin of ``_maybe_open_auto_fix_pr``: open a WIP draft PR."""
    findings_by_file = _collect_auto_fix_findings(args, result)
    if findings_by_file is None:
        return

    base_branch = _resolve_mr_base_branch(args, adapter)
    if base_branch is None:
        return

    from prthinker.auto_fix import GiteaPRTarget, open_auto_fix_gitea_pr

    target = GiteaPRTarget(
        repo=args.repo,
        token=args.github_token,
        pr_number=int(args.pr_number),
        base_url=getattr(adapter, "base_url", "https://gitea.com/api/v1"),
    )
    try:
        auto_result = open_auto_fix_gitea_pr(
            target, findings_by_file, base_branch, Path.cwd()
        )
    except Exception as exc:  # noqa: BLE001 — auto-fix must never fail the review
        log.error("Auto-fix failed: %s", exc)
        return
    _report_auto_fix_outcome(auto_result, "PR #")

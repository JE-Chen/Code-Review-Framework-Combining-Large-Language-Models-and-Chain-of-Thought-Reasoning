"""Auto-file review findings as tracker issues, for ``review-pr``.

Split out of :mod:`prthinker.cli_review` the same way as
:mod:`prthinker.cli_review_autofix`: this module owns the
``--auto-file-issues`` behaviour — picking which findings deserve a tracker
issue (those falling outside the diff hunks, or all of them) and handing
them to :mod:`prthinker.issue_autofile` through the platform's
:class:`~prthinker.issue_tracker.IssueTracker` strategy (GitHub, GitLab,
and Gitea). Best-effort throughout: an API failure logs a warning and never
fails the surrounding review. The dependency edge runs one way
(``cli_review`` -> ``cli_review_issues``).
"""

from __future__ import annotations

import argparse
import logging

import httpx

from prthinker.pipeline import ReviewResult

log = logging.getLogger("prthinker")

_MODE_OFF = "none"
_MODE_OFF_DIFF = "off-diff"


def _selected_findings(mode: str, result: ReviewResult) -> list:
    """The findings the chosen mode files: off-diff only, or every finding."""
    if mode == _MODE_OFF_DIFF:
        from prthinker.github_api import findings_off_diff

        return list(findings_off_diff(result.inline_findings, result.code_diff))
    return list(result.inline_findings)


def _issue_labels(args: argparse.Namespace) -> tuple[str, ...]:
    """Parse the comma-separated --issue-labels value into a label tuple."""
    raw = getattr(args, "issue_labels", "") or ""
    return tuple(label.strip() for label in raw.split(",") if label.strip())


def _tracker_for(args: argparse.Namespace, platform_kind: object,
                 adapter: object):
    """The platform's issue-tracker strategy, or None when unsupported."""
    from prthinker.issue_tracker import create_issue_tracker
    from prthinker.platforms import PlatformKind

    supported = (PlatformKind.GITHUB, PlatformKind.GITLAB, PlatformKind.GITEA)
    if platform_kind not in supported:
        log.info("Auto-file issues not yet supported on %s — skipping",
                 getattr(platform_kind, "value", platform_kind))
        return None
    return create_issue_tracker(
        str(getattr(platform_kind, "value", platform_kind)),
        repo=args.repo, token=args.github_token,
        base_url=str(getattr(adapter, "base_url", "") or ""))


def _maybe_file_issues(
    args: argparse.Namespace, result: ReviewResult,
    platform_kind: object, adapter: object,
) -> None:
    """File findings as tracker issues when ``--auto-file-issues`` asks for it."""
    mode = getattr(args, "auto_file_issues", _MODE_OFF)
    if mode == _MODE_OFF or args.dry_run:
        return
    tracker = _tracker_for(args, platform_kind, adapter)
    if tracker is None:
        return
    findings = _selected_findings(mode, result)
    if not findings:
        return
    from prthinker.issue_autofile import file_findings_as_issues

    try:
        created = file_findings_as_issues(
            tracker, findings, labels=_issue_labels(args))
    except (httpx.HTTPError, ValueError) as exc:
        log.warning("Auto-file issues failed: %s", exc)
        return
    log.info("Auto-filed %d issue(s): %s",
             len(created), [issue.number for issue in created])

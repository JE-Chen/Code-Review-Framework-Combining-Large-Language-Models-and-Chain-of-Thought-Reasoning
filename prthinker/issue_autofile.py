"""Auto-file review findings as issues — draft, fingerprint, dedup, create.

Findings that fall outside a PR's diff hunks cannot be posted as inline
comments (GitHub 422s the whole review); today they only survive in the
summary text. This module turns them into tracker issues instead, so real
problems spotted near — but not on — the changed lines get a durable home.

Two layers, mirroring :mod:`prthinker.auto_fix`:

1. Pure transforms — :func:`finding_fingerprint`, :func:`draft_from_finding`,
   :func:`known_fingerprints` build deterministic issue drafts and parse the
   dedup markers back out of existing issue bodies. Unit-testable without
   any network.
2. Glue — :func:`file_findings_as_issues` lists open issues, skips any
   finding whose fingerprint is already filed, and creates the rest through
   an injected :class:`~prthinker.issue_tracker.IssueTracker` strategy
   (GitHub or GitLab). Each create is best-effort: an API failure logs and
   moves on rather than aborting the batch.

Dedup is content-based, not exact: the fingerprint hashes the finding's
path, category, and whitespace-normalised comment, so re-reviews of the
same problem usually map to the same open issue. A reworded model comment
defeats it; that is accepted best-effort behaviour, not a bug.

Runner-safe: ``httpx`` (via issue_tracker) + stdlib.
"""

from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass
from typing import Iterable, Sequence

import httpx

from prthinker.issue_tracker import Issue, IssueTracker
from prthinker.schemas import InlineFinding

log = logging.getLogger(__name__)

_MARKER_TEMPLATE = "<!-- prthinker:auto-issue:{fingerprint} -->"
_MARKER_RE = re.compile(r"<!-- prthinker:auto-issue:([0-9a-f]{16}) -->")
_FINGERPRINT_HEX_CHARS = 16
_TITLE_COMMENT_CAP = 72
_DEFAULT_LABELS = ("prthinker",)
_DEFAULT_MAX_NEW_ISSUES = 10
_DEDUP_SCAN_LIMIT = 100


@dataclass(frozen=True)
class IssueDraft:
    """A ready-to-create issue derived from one finding."""

    title: str
    body: str
    fingerprint: str


def finding_fingerprint(finding: InlineFinding) -> str:
    """A short stable hash identifying a finding across review runs.

    Hashes path + category + normalised comment; the line number is left
    out on purpose so unrelated edits shifting the file do not re-file the
    same problem as a "new" issue.
    """
    comment = " ".join(finding.comment.lower().split())
    key = f"{finding.path}|{finding.category or ''}|{comment}"
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return digest[:_FINGERPRINT_HEX_CHARS]


def _draft_title(finding: InlineFinding) -> str:
    """One-line issue title: severity, location, and the comment's head."""
    head = " ".join(finding.comment.split())[:_TITLE_COMMENT_CAP]
    return f"[prthinker] {finding.severity}: {finding.path}:{finding.line} {head}"


def _draft_body(finding: InlineFinding, fingerprint: str) -> str:
    """Markdown body carrying the dedup marker and the full finding."""
    lines = [
        _MARKER_TEMPLATE.format(fingerprint=fingerprint),
        "",
        f"**File:** `{finding.path}` (line {finding.line})",
        f"**Severity:** {finding.severity}",
    ]
    if finding.category:
        lines.append(f"**Category:** {finding.category}")
    lines += ["", finding.comment]
    if finding.suggestion:
        lines += ["", "Proposed replacement:", "", "```", finding.suggestion, "```"]
    lines += ["", "_Filed automatically from a code review finding._"]
    return "\n".join(lines)


def draft_from_finding(finding: InlineFinding) -> IssueDraft:
    """Build the title/body/fingerprint draft for one finding."""
    fingerprint = finding_fingerprint(finding)
    return IssueDraft(_draft_title(finding), _draft_body(finding, fingerprint), fingerprint)


def known_fingerprints(issues: Iterable[Issue]) -> set[str]:
    """Every auto-issue fingerprint present in the given issues' bodies."""
    found: set[str] = set()
    for issue in issues:
        found.update(_MARKER_RE.findall(issue.body))
    return found


def _create_one(tracker: IssueTracker, draft: IssueDraft,
                labels: tuple[str, ...]) -> Issue | None:
    """Create one issue, logging and returning None on an API failure."""
    try:
        return tracker.create_issue(
            title=draft.title, body=draft.body, labels=labels)
    except httpx.HTTPError as exc:
        log.warning("Auto-file: could not create issue %r: %s", draft.title, exc)
        return None


def file_findings_as_issues(
    tracker: IssueTracker,
    findings: Sequence[InlineFinding],
    *,
    labels: tuple[str, ...] = _DEFAULT_LABELS,
    max_new_issues: int = _DEFAULT_MAX_NEW_ISSUES,
) -> list[Issue]:
    """Create an issue per not-yet-filed finding; return the created issues.

    Dedup scans the first :data:`_DEDUP_SCAN_LIMIT` open issues for
    fingerprint markers (older filings past that page can be re-filed —
    accepted best-effort behaviour). ``max_new_issues`` caps one run so a
    noisy review cannot flood the tracker; the overflow count is logged.
    """
    seen = known_fingerprints(tracker.list_open_issues(limit=_DEDUP_SCAN_LIMIT))
    created: list[Issue] = []
    skipped_over_cap = 0
    for finding in findings:
        draft = draft_from_finding(finding)
        if draft.fingerprint in seen:
            continue
        if len(created) >= max_new_issues:
            skipped_over_cap += 1
            continue
        seen.add(draft.fingerprint)
        issue = _create_one(tracker, draft, labels)
        if issue is not None:
            created.append(issue)
    if skipped_over_cap:
        log.warning(
            "Auto-file: %d finding(s) beyond the max-new-issues cap (%d) were "
            "not filed this run", skipped_over_cap, max_new_issues)
    return created


__all__ = [
    "IssueDraft",
    "draft_from_finding",
    "file_findings_as_issues",
    "finding_fingerprint",
    "known_fingerprints",
]

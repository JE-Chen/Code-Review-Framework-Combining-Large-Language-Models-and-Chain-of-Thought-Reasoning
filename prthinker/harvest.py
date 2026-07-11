"""Harvest dismissed inline-review comments from GitHub PRs.

A comment is treated as "dismissed" when at least one of:
  - it carries a 👎 (`-1`) reaction
  - it has a reply whose body matches one of the dismissal keywords below
  - the comment is on a merged PR but remains unresolved (we approximate
    this as: PR is merged AND we could not find a positive resolution)

The harvested examples are appended to a JSONL store; downstream the
DismissedFilter will load and embed them to drop similar future findings.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from itertools import islice
from typing import Iterable, Iterator

import httpx

from prthinker.accepted import AcceptedExample, AcceptedExamplesStore
from prthinker.dismissed import DismissedExample, DismissedExamplesStore
from prthinker.github_api import _client, paginate

log = logging.getLogger(__name__)

# Substrings (case-insensitive) in any reply that mark the parent as dismissed.
_DISMISS_KEYWORDS_EN = [
    "false positive",
    "wontfix",
    "won't fix",
    "not relevant",
    "not applicable",
    "ignore this",
    "intentional",
    "by design",
    "as designed",
]
_DISMISS_KEYWORDS_ZH = [
    "誤判",
    "不是問題",
    "不修",
    "已討論",
    "故意",
    "預期",
    "本來就是",
]
_DISMISS_RE = re.compile(
    "|".join(re.escape(k) for k in _DISMISS_KEYWORDS_EN + _DISMISS_KEYWORDS_ZH),
    re.IGNORECASE,
)


@dataclass
class HarvestStats:
    prs_scanned: int = 0
    comments_scanned: int = 0
    dismissed_found: int = 0
    accepted_found: int = 0


_SUGGESTION_RE = re.compile(
    r"```suggestion\s*\n(?P<body>.*?)```", re.DOTALL
)
_APPLY_COMMIT_RE = re.compile(
    r"^Apply suggestions? from code review", re.MULTILINE
)


def _extract_suggestion_block(body: str) -> str | None:
    match = _SUGGESTION_RE.search(body or "")
    return match.group("body").rstrip("\n") if match else None


def _reply_dismissal_reason(replies: Iterable[dict]) -> str | None:
    """Reason string when any reply body matches the dismissal keywords.

    Shared with the GitLab / Gitea harvesters so every platform reads
    the same reviewer signals.
    """
    for reply in replies:
        text = reply.get("body") or ""
        match = _DISMISS_RE.search(text)
        if match:
            return f"reply matched: {match.group(0)!r}"
    return None


def _accepted_comment_text(body: str) -> str:
    """Advisory text with the ```suggestion block stripped out.

    The embedding should reflect the reviewer's advice, not the patch;
    a suggestion-only comment gets a placeholder. Shared across the
    platform harvesters.
    """
    return _SUGGESTION_RE.sub("", body).strip() or "(suggestion only)"


def harvest(
    repo: str,
    token: str,
    *,
    store: DismissedExamplesStore,
    pr_number: int | None = None,
    max_prs: int = 50,
) -> HarvestStats:
    """Harvest dismissed comments. If `pr_number` is set, harvest just that PR."""
    if "/" not in repo:
        raise ValueError(f"repo must be 'owner/name', got {repo!r}")

    stats = HarvestStats()
    with _client(token) as client:
        if pr_number is not None:
            stats.prs_scanned = 1
            _harvest_one_pr(client, repo, pr_number, store, stats)
        else:
            for n in _iter_recent_closed_prs(client, repo, max_prs):
                stats.prs_scanned += 1
                try:
                    _harvest_one_pr(client, repo, n, store, stats)
                except httpx.HTTPStatusError as exc:
                    log.warning("PR #%d failed: %s", n, exc)
                    continue

    log.info(
        "Harvest done: scanned %d PR(s), %d comment(s), kept %d dismissed",
        stats.prs_scanned, stats.comments_scanned, stats.dismissed_found,
    )
    return stats


def _iter_recent_closed_prs(
    client: httpx.Client, repo: str, max_prs: int
) -> Iterator[int]:
    """Yield the numbers of the ``max_prs`` most recently updated closed PRs."""
    pages = paginate(
        client,
        f"/repos/{repo}/pulls",
        params={"state": "closed", "sort": "updated", "direction": "desc"},
    )
    for pr in islice(pages, max_prs):
        yield int(pr["number"])


def _harvest_one_pr(
    client: httpx.Client,
    repo: str,
    pr_number: int,
    store: DismissedExamplesStore,
    stats: HarvestStats,
) -> None:
    comments = _fetch_review_comments(client, repo, pr_number)
    by_parent = _index_replies_by_parent(comments)
    for c in comments:
        stats.comments_scanned += 1
        if c.get("in_reply_to_id"):
            # Replies themselves aren't candidate parents.
            continue
        replies = by_parent.get(int(c["id"]), [])
        _harvest_dismissed_comment(client, repo, c, replies, store, stats)


def _index_replies_by_parent(comments: list[dict]) -> dict[int, list[dict]]:
    """Group reply comments by their parent comment id."""
    by_parent: dict[int, list[dict]] = {}
    for c in comments:
        parent = c.get("in_reply_to_id")
        if parent:
            by_parent.setdefault(int(parent), []).append(c)
    return by_parent


def _harvest_dismissed_comment(
    client: httpx.Client,
    repo: str,
    comment: dict,
    replies: Iterable[dict],
    store: DismissedExamplesStore,
    stats: HarvestStats,
) -> None:
    """Append the comment as a dismissed example when it is dismissed and non-empty."""
    reason = _dismissal_reason(client, repo, comment, replies)
    if reason is None:
        return
    body = (comment.get("body") or "").strip()
    if not body:
        return
    store.append(
        DismissedExample(
            path=comment.get("path") or "",
            comment=body,
            reason=reason,
            diff_snippet=(comment.get("diff_hunk") or "").strip(),
        )
    )
    stats.dismissed_found += 1


def _fetch_review_comments(
    client: httpx.Client, repo: str, pr_number: int
) -> list[dict]:
    return list(paginate(client, f"/repos/{repo}/pulls/{pr_number}/comments"))


def _dismissal_reason(
    client: httpx.Client,
    repo: str,
    comment: dict,
    replies: Iterable[dict],
) -> str | None:
    """Return a short reason string if this comment is dismissed, else None."""
    if _has_thumbs_down(client, repo, comment):
        return "thumbs-down reaction"
    return _reply_dismissal_reason(replies)


def _has_thumbs_down(
    client: httpx.Client, repo: str, comment: dict
) -> bool:
    """Whether the comment carries a 👎 reaction.

    The review-comments list payload already ships a ``reactions``
    rollup with per-emoji counts; using it avoids one request per
    comment (N+1). Only when the rollup key is absent (older payloads,
    minimal fixtures) does the per-comment reactions endpoint get hit.
    """
    rollup = comment.get("reactions")
    if isinstance(rollup, dict) and "-1" in rollup:
        return int(rollup.get("-1") or 0) > 0
    response = client.get(
        f"/repos/{repo}/pulls/comments/{int(comment['id'])}/reactions",
        params={"content": "-1", "per_page": 1},
    )
    if response.status_code == 404:
        return False
    response.raise_for_status()
    return bool(response.json())


def harvest_accepted(
    repo: str,
    token: str,
    *,
    store: AcceptedExamplesStore,
    pr_number: int | None = None,
    max_prs: int = 50,
) -> HarvestStats:
    """Harvest accepted suggestion examples.

    Heuristic: a PR has accepted suggestions if any of its commits has a
    message matching `^Apply suggestions? from code review`. For each such
    PR we keep every review comment that contains a ```suggestion``` block
    — best-effort, with no per-suggestion attribution.
    """
    if "/" not in repo:
        raise ValueError(f"repo must be 'owner/name', got {repo!r}")

    stats = HarvestStats()
    with _client(token) as client:
        pr_numbers: Iterable[int]
        if pr_number is not None:
            pr_numbers = [pr_number]
        else:
            pr_numbers = list(_iter_recent_closed_prs(client, repo, max_prs))

        for n in pr_numbers:
            stats.prs_scanned += 1
            try:
                _harvest_accepted_one_pr(client, repo, n, store, stats)
            except httpx.HTTPStatusError as exc:
                log.warning("PR #%d failed: %s", n, exc)
                continue

    log.info(
        "Accepted harvest done: scanned %d PR(s), %d comment(s), kept %d accepted",
        stats.prs_scanned, stats.comments_scanned, stats.accepted_found,
    )
    return stats


def _harvest_accepted_one_pr(
    client: httpx.Client,
    repo: str,
    pr_number: int,
    store: AcceptedExamplesStore,
    stats: HarvestStats,
) -> None:
    if not _pr_has_apply_commit(client, repo, pr_number):
        return

    for c in _fetch_review_comments(client, repo, pr_number):
        stats.comments_scanned += 1
        body = c.get("body") or ""
        suggestion = _extract_suggestion_block(body)
        if not suggestion:
            continue

        comment_text = _accepted_comment_text(body)

        store.append(
            AcceptedExample(
                path=str(c.get("path") or ""),
                comment=comment_text,
                suggestion=suggestion,
                pr_number=pr_number,
            )
        )
        stats.accepted_found += 1


def _pr_has_apply_commit(
    client: httpx.Client, repo: str, pr_number: int
) -> bool:
    for commit in paginate(client, f"/repos/{repo}/pulls/{pr_number}/commits"):
        message = (commit.get("commit") or {}).get("message") or ""
        if _APPLY_COMMIT_RE.search(message):
            return True
    return False


__all__ = ["harvest", "harvest_accepted", "HarvestStats"]

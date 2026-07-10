"""Harvest dismissed / accepted review comments from Gitea pull requests.

Gitea counterpart of :mod:`prthinker.harvest`, feeding the same
learned-corpora stores with the same dismissal / acceptance semantics —
both forges see the same reviewer habits. Gitea's PR review API is
GitHub-shaped with two deviations this module absorbs:

  - inline review comments hang off each review
    (``GET /pulls/{index}/reviews`` then ``.../reviews/{id}/comments``)
    instead of one flat ``/pulls/{index}/comments`` list, and they carry
    no ``in_reply_to_id`` — replies are approximated as the later
    comments of the same ``(path, position)`` thread;
  - reactions are read from the GitHub-shaped issue-comment endpoint
    (``GET /repos/{repo}/issues/comments/{id}/reactions`` — Gitea's
    review comments share the comment id space), each row carrying a
    ``content`` field where ``"-1"`` is the thumbs-down.
"""

from __future__ import annotations

import logging
from itertools import islice
from typing import Iterable, Iterator

import httpx

from prthinker.accepted import AcceptedExample, AcceptedExamplesStore
from prthinker.dismissed import DismissedExample, DismissedExamplesStore
from prthinker.github_api import paginate
# The dismissal keywords, suggestion-block grammar, and applied-commit
# heuristic are shared with the GitHub harvester so both platforms learn
# from the same signals.
from prthinker.harvest import (
    HarvestStats,
    _accepted_comment_text,
    _APPLY_COMMIT_RE,
    _extract_suggestion_block,
    _reply_dismissal_reason,
)

log = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://gitea.com/api/v1"
_USER_AGENT = "prthinker-harvester/0.1"
# Gitea caps list endpoints at the instance's max page size (default 50).
_PER_PAGE = 50


def harvest(
    repo: str,
    token: str,
    *,
    store: DismissedExamplesStore,
    pr_number: int | None = None,
    max_prs: int = 50,
    base_url: str = DEFAULT_BASE_URL,
) -> HarvestStats:
    """Harvest dismissed comments. If ``pr_number`` is set, harvest just that PR."""
    _validate_repo(repo)
    stats = HarvestStats()
    with _client(token, base_url) as client:
        if pr_number is not None:
            stats.prs_scanned = 1
            _harvest_one_pr(client, repo, pr_number, store, stats)
        else:
            for number in _iter_recent_closed_prs(client, repo, max_prs):
                stats.prs_scanned += 1
                try:
                    _harvest_one_pr(client, repo, number, store, stats)
                except httpx.HTTPStatusError as exc:
                    log.warning("PR #%d failed: %s", number, exc)
                    continue

    log.info(
        "Gitea harvest done: scanned %d PR(s), %d comment(s), kept %d dismissed",
        stats.prs_scanned, stats.comments_scanned, stats.dismissed_found,
    )
    return stats


def harvest_accepted(
    repo: str,
    token: str,
    *,
    store: AcceptedExamplesStore,
    pr_number: int | None = None,
    max_prs: int = 50,
    base_url: str = DEFAULT_BASE_URL,
) -> HarvestStats:
    """Harvest accepted suggestion examples from Gitea PRs.

    Heuristic mirror of the GitHub harvester: a PR has accepted
    suggestions when one of its commits matches the applied-suggestion
    message; every review comment containing a ```suggestion``` block on
    such a PR is kept — best-effort, with no per-suggestion attribution.
    """
    _validate_repo(repo)
    stats = HarvestStats()
    with _client(token, base_url) as client:
        numbers: Iterable[int]
        if pr_number is not None:
            numbers = [pr_number]
        else:
            numbers = list(_iter_recent_closed_prs(client, repo, max_prs))

        for number in numbers:
            stats.prs_scanned += 1
            try:
                _harvest_accepted_one_pr(client, repo, number, store, stats)
            except httpx.HTTPStatusError as exc:
                log.warning("PR #%d failed: %s", number, exc)
                continue

    log.info(
        "Gitea accepted harvest done: scanned %d PR(s), %d comment(s), "
        "kept %d accepted",
        stats.prs_scanned, stats.comments_scanned, stats.accepted_found,
    )
    return stats


def _validate_repo(repo: str) -> None:
    if "/" not in repo:
        raise ValueError(f"repo must be 'owner/name', got {repo!r}")


def _client(token: str, base_url: str) -> httpx.Client:
    return httpx.Client(
        base_url=base_url.rstrip("/"),
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/json",
            "User-Agent": _USER_AGENT,
        },
        timeout=30.0,
    )


def _iter_recent_closed_prs(
    client: httpx.Client, repo: str, max_prs: int
) -> Iterator[int]:
    """Yield the numbers of the ``max_prs`` most recently updated closed PRs."""
    pages = paginate(
        client,
        f"/repos/{repo}/pulls",
        params={"state": "closed", "sort": "recentupdate"},
        per_page=_PER_PAGE,
        size_param="limit",
    )
    for pr in islice(pages, max_prs):
        yield int(pr["number"])


def _fetch_review_comments(
    client: httpx.Client, repo: str, pr_number: int
) -> list[dict]:
    """Every inline comment across the PR's reviews.

    Gitea has no flat per-PR review-comments list; each review's
    comments are fetched separately and concatenated.
    """
    comments: list[dict] = []
    for review in paginate(
        client, f"/repos/{repo}/pulls/{pr_number}/reviews",
        per_page=_PER_PAGE, size_param="limit",
    ):
        response = client.get(
            f"/repos/{repo}/pulls/{pr_number}"
            f"/reviews/{int(review['id'])}/comments",
        )
        response.raise_for_status()
        comments.extend(response.json() or [])
    return comments


def _threads_by_position(comments: list[dict]) -> list[list[dict]]:
    """Group comments into ``(path, position)`` threads, each ordered by id.

    Gitea review comments carry no reply linkage; a reply to an inline
    finding lands on the same file position, so the oldest comment of a
    position group is the candidate parent and the rest are treated as
    its replies.
    """
    threads: dict[tuple[str, int], list[dict]] = {}
    for comment in comments:
        key = (
            str(comment.get("path") or ""),
            int(comment.get("position") or comment.get("original_position") or 0),
        )
        threads.setdefault(key, []).append(comment)
    return [
        sorted(thread, key=lambda c: int(c.get("id") or 0))
        for thread in threads.values()
    ]


def _harvest_one_pr(
    client: httpx.Client,
    repo: str,
    pr_number: int,
    store: DismissedExamplesStore,
    stats: HarvestStats,
) -> None:
    comments = _fetch_review_comments(client, repo, pr_number)
    for thread in _threads_by_position(comments):
        stats.comments_scanned += 1
        _harvest_dismissed_comment(
            client, repo, thread[0], thread[1:], store, stats,
        )


def _harvest_dismissed_comment(
    client: httpx.Client,
    repo: str,
    comment: dict,
    replies: list[dict],
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
            path=str(comment.get("path") or ""),
            comment=body,
            reason=reason,
            diff_snippet=(comment.get("diff_hunk") or "").strip(),
        )
    )
    stats.dismissed_found += 1


def _dismissal_reason(
    client: httpx.Client,
    repo: str,
    comment: dict,
    replies: list[dict],
) -> str | None:
    """Return a short reason string if this comment is dismissed, else None."""
    if _has_thumbs_down(client, repo, int(comment["id"])):
        return "thumbs-down reaction"
    return _reply_dismissal_reason(replies)


def _has_thumbs_down(
    client: httpx.Client, repo: str, comment_id: int
) -> bool:
    """Whether the comment carries a 👎 reaction.

    Gitea's review comments share the comment id space with issue
    comments, so the GitHub-shaped issue-comment reactions endpoint
    serves them. A 404 (comment gone, reactions disabled) means no.
    """
    response = client.get(
        f"/repos/{repo}/issues/comments/{comment_id}/reactions",
    )
    if response.status_code == 404:
        return False
    response.raise_for_status()
    return any(
        str(reaction.get("content")) == "-1"
        for reaction in (response.json() or [])
    )


def _harvest_accepted_one_pr(
    client: httpx.Client,
    repo: str,
    pr_number: int,
    store: AcceptedExamplesStore,
    stats: HarvestStats,
) -> None:
    if not _pr_has_apply_commit(client, repo, pr_number):
        return

    for comment in _fetch_review_comments(client, repo, pr_number):
        stats.comments_scanned += 1
        body = comment.get("body") or ""
        suggestion = _extract_suggestion_block(body)
        if not suggestion:
            continue
        store.append(
            AcceptedExample(
                path=str(comment.get("path") or ""),
                comment=_accepted_comment_text(body),
                suggestion=suggestion,
                pr_number=pr_number,
            )
        )
        stats.accepted_found += 1


def _pr_has_apply_commit(
    client: httpx.Client, repo: str, pr_number: int
) -> bool:
    """Whether any PR commit message looks like an applied suggestion.

    Gitea's PR commits payload is GitHub-shaped (``commit.message``).
    """
    for commit in paginate(
        client, f"/repos/{repo}/pulls/{pr_number}/commits",
        per_page=_PER_PAGE, size_param="limit",
    ):
        message = str((commit.get("commit") or {}).get("message") or "")
        if _APPLY_COMMIT_RE.search(message):
            return True
    return False


__all__ = ["DEFAULT_BASE_URL", "harvest", "harvest_accepted"]

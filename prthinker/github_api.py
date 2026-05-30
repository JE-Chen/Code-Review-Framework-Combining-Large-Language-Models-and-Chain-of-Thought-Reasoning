"""GitHub REST helpers — fetch PR diffs, upsert summary comment, submit
inline-comment reviews.

- Summary comment: a single PR conversation comment, upserted by marker.
- Inline review:  posts a `POST /pulls/:n/reviews` with `comments[]` keyed
                  by `path` + `line` (GitHub's new-side line number).

We use only the GitHub REST API via httpx to avoid pulling in PyGithub.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable

import httpx

from prthinker.config import GitHubConfig
from prthinker.schemas import InlineFinding

log = logging.getLogger(__name__)

_API_ROOT = "https://api.github.com"
_USER_AGENT = "prthinker/0.1"


@dataclass
class _Comment:
    id: int
    body: str


def _client(token: str) -> httpx.Client:
    return httpx.Client(
        base_url=_API_ROOT,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": _USER_AGENT,
        },
        timeout=30.0,
    )


def fetch_pr_diff(config: GitHubConfig) -> str:
    """Return the unified diff for the PR. Empty PRs return ''."""
    with _client(config.token) as client:
        response = client.get(
            f"/repos/{config.repo}/pulls/{config.pr_number}",
            headers={"Accept": "application/vnd.github.v3.diff"},
        )
        response.raise_for_status()
        return response.text


def fetch_pr_head_sha(config: GitHubConfig) -> str:
    """Return the HEAD commit SHA of the PR — required by the Checks API."""
    with _client(config.token) as client:
        response = client.get(
            f"/repos/{config.repo}/pulls/{config.pr_number}",
        )
        response.raise_for_status()
        return str(response.json()["head"]["sha"])


def fetch_pr_base_branch(config: GitHubConfig) -> str:
    """Return the PR's base branch name — used as the target for auto-fix PRs."""
    with _client(config.token) as client:
        response = client.get(
            f"/repos/{config.repo}/pulls/{config.pr_number}",
        )
        response.raise_for_status()
        return str(response.json()["base"]["ref"])


def _iter_existing_comments(
    client: httpx.Client, config: GitHubConfig
) -> list[_Comment]:
    comments: list[_Comment] = []
    page = 1
    while True:
        response = client.get(
            f"/repos/{config.repo}/issues/{config.pr_number}/comments",
            params={"per_page": 100, "page": page},
        )
        response.raise_for_status()
        batch = response.json()
        if not batch:
            break
        comments.extend(_Comment(id=int(c["id"]), body=c.get("body") or "") for c in batch)
        if len(batch) < 100:
            break
        page += 1
    return comments


def upsert_pr_comment(config: GitHubConfig, body: str) -> int:
    """Create or update the marker-tagged PR comment. Returns its id."""
    if config.comment_marker not in body:
        raise ValueError("body must contain the configured comment marker")

    with _client(config.token) as client:
        existing = next(
            (c for c in _iter_existing_comments(client, config)
             if config.comment_marker in c.body),
            None,
        )
        if existing is not None:
            log.info("Updating existing PR comment %d", existing.id)
            response = client.patch(
                f"/repos/{config.repo}/issues/comments/{existing.id}",
                json={"body": body},
            )
            response.raise_for_status()
            return existing.id

        log.info("Creating new PR comment")
        response = client.post(
            f"/repos/{config.repo}/issues/{config.pr_number}/comments",
            json={"body": body},
        )
        response.raise_for_status()
        return int(response.json()["id"])


# Hidden marker embedded in every prthinker inline review's summary
# body so the NEXT run can identify and clean up its own predecessors.
# Distinct from the summary-comment marker so the two never collide.
_INLINE_REVIEW_MARKER = "<!-- prthinker:inline -->"


def _collect_our_review_ids(client: httpx.Client, config: GitHubConfig) -> set[int]:
    """Page through PR reviews and collect those carrying our marker."""
    our_review_ids: set[int] = set()
    page = 1
    while True:
        resp = client.get(
            f"/repos/{config.repo}/pulls/{config.pr_number}/reviews",
            params={"per_page": 100, "page": page},
        )
        resp.raise_for_status()
        reviews = resp.json()
        if not reviews:
            return our_review_ids
        for r in reviews:
            if _INLINE_REVIEW_MARKER in (r.get("body") or ""):
                our_review_ids.add(int(r["id"]))
        if len(reviews) < 100:
            return our_review_ids
        page += 1


def _delete_inline_comments_for_reviews(
    client: httpx.Client,
    config: GitHubConfig,
    review_ids: set[int],
) -> int:
    """Page through PR review comments and delete those owned by review_ids."""
    deleted = 0
    page = 1
    while True:
        resp = client.get(
            f"/repos/{config.repo}/pulls/{config.pr_number}/comments",
            params={"per_page": 100, "page": page},
        )
        resp.raise_for_status()
        comments = resp.json()
        if not comments:
            return deleted
        for c in comments:
            if c.get("pull_request_review_id") in review_ids:
                deleted += _delete_one_inline_comment(client, config, int(c["id"]))
        if len(comments) < 100:
            return deleted
        page += 1


def _delete_one_inline_comment(
    client: httpx.Client, config: GitHubConfig, comment_id: int
) -> int:
    del_resp = client.delete(
        f"/repos/{config.repo}/pulls/comments/{comment_id}",
    )
    if del_resp.status_code < 400:
        return 1
    log.warning(
        "Failed to delete inline comment %d (%d)",
        comment_id, del_resp.status_code,
    )
    return 0


def _dismiss_stale_inline_reviews(config: GitHubConfig) -> None:
    """Delete the inline comments left by previous prthinker reviews.

    GitHub's review-dismissal endpoint refuses ``COMMENT``-state reviews
    (which is what prthinker posts by default), so we can't strike the
    review wrappers themselves. Deleting each review's child comments
    is the next best thing — the wrapper stays on the PR timeline as a
    stub but the noisy inline annotations disappear from the diff.

    Identification is by ``_INLINE_REVIEW_MARKER`` in the review body,
    not by author. Filtering by the bot user would catch reviews from
    every other workflow that uses ``GITHUB_TOKEN`` too.
    """
    with _client(config.token) as client:
        our_review_ids = _collect_our_review_ids(client, config)
        if not our_review_ids:
            log.info("No prior prthinker inline reviews to clean up")
            return
        deleted = _delete_inline_comments_for_reviews(
            client, config, our_review_ids
        )
        log.info(
            "Cleaned up %d inline comment(s) from %d prior review(s)",
            deleted, len(our_review_ids),
        )


def submit_inline_review(
    config: GitHubConfig,
    findings: Iterable[InlineFinding],
    summary_body: str | None = None,
    event: str = "COMMENT",
) -> int | None:
    """Post a PR review containing one inline comment per finding.

    Returns the new review id, or None if there were no findings (we skip
    creating an empty review).

    `event` is one of GitHub's review states: COMMENT, APPROVE, REQUEST_CHANGES.

    Before posting, deletes inline comments from every previous prthinker
    review on this PR (identified by ``_INLINE_REVIEW_MARKER`` in their
    body) so the diff doesn't accumulate duplicates across re-pushes.
    """
    items = list(findings)
    if not items:
        log.info("No inline findings — skipping review submission")
        return None

    try:
        _dismiss_stale_inline_reviews(config)
    except Exception as exc:  # noqa: BLE001 — cleanup failure must not block posting
        log.warning("Inline-review cleanup failed (%s); continuing", exc)

    base_body = summary_body or "prthinker — inline findings"
    marked_body = f"{base_body}\n\n{_INLINE_REVIEW_MARKER}"

    comments = [_build_inline_comment(f) for f in items]

    payload: dict[str, object] = {
        "event": event,
        "comments": comments,
        "body": marked_body,
    }

    with _client(config.token) as client:
        response = client.post(
            f"/repos/{config.repo}/pulls/{config.pr_number}/reviews",
            json=payload,
        )
        if response.status_code >= 400:
            log.error(
                "Review submission failed (%d): %s",
                response.status_code, response.text,
            )
        response.raise_for_status()
        review_id = int(response.json()["id"])
        log.info("Submitted review %d with %d inline comments",
                 review_id, len(comments))
        return review_id


_SEVERITY_BADGE: dict[str, str] = {
    "error": "🔴 **error**",
    "warning": "🟡 **warning**",
    "info": "🔵 _info_",
}


def _build_inline_comment(finding: InlineFinding) -> dict[str, object]:
    """Build the JSON payload for one entry in `comments[]` of a Review.

    For multi-line suggestions, GitHub requires `start_line` + `start_side`
    in addition to `line` + `side`.
    """
    payload: dict[str, object] = {
        "path": finding.path,
        "line": finding.line,
        "side": "RIGHT",
        "body": _format_inline_body(finding),
    }
    if finding.is_multiline and finding.start_line is not None:
        payload["start_line"] = finding.start_line
        payload["start_side"] = "RIGHT"
    return payload


def _format_inline_body(finding: InlineFinding) -> str:
    badge = _SEVERITY_BADGE.get(finding.severity, finding.severity)
    body = f"{badge} — {finding.comment.strip()}"
    if finding.suggestion is not None:
        # GitHub renders ```suggestion blocks as a one-click "Apply" button.
        body += "\n\n```suggestion\n" + finding.suggestion.rstrip("\n") + "\n```"
    return body


__all__ = [
    "fetch_pr_diff",
    "fetch_pr_head_sha",
    "fetch_pr_base_branch",
    "upsert_pr_comment",
    "submit_inline_review",
]

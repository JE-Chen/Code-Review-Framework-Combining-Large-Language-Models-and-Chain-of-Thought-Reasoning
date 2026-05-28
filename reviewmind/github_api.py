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

from reviewmind.config import GitHubConfig
from reviewmind.schemas import InlineFinding

log = logging.getLogger(__name__)

_API_ROOT = "https://api.github.com"
_USER_AGENT = "reviewmind/0.1"


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
    """
    items = list(findings)
    if not items:
        log.info("No inline findings — skipping review submission")
        return None

    comments = [_build_inline_comment(f) for f in items]

    payload: dict[str, object] = {
        "event": event,
        "comments": comments,
    }
    if summary_body is not None:
        payload["body"] = summary_body

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

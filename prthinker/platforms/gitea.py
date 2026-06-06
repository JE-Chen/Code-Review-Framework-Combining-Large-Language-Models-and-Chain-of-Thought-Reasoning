"""Gitea :class:`PlatformAdapter`.

Maps the same small five-method API the pipeline uses for GitHub onto
Gitea's REST endpoints under ``/api/v1/repos/{owner}/{repo}/...``.

Gitea deliberately mirrors GitHub's PR / issue model, so the mapping is
close to one-to-one:

* **Diff** — ``GET /repos/{owner}/{repo}/pulls/{index}.diff`` returns the
  raw unified diff body (no special ``Accept`` header needed).
* **Summary comment** — the PR conversation comments live on the *issue*
  resource (``issues/{index}/comments``); we upsert the marker-tagged
  comment there. Updates go to ``issues/comments/{id}`` (no index segment).
* **Inline review** — ``POST /pulls/{index}/reviews`` with a ``comments``
  array keyed by ``path`` + ``new_position`` (Gitea's new-side line).
* **Gate** — Gitea has no Check Run API; commit statuses via
  ``POST /statuses/{sha}`` play the role. ``pending`` for open,
  ``success`` / ``failure`` for closed. We map our
  :class:`prthinker.checks.CheckResult.conclusion` onto these.

The constructor signature mirrors :class:`prthinker.platforms.github.GitHubAdapter`
(``repo`` / ``token`` / ``pr_number`` / ``comment_marker`` / ``base_url``)
so the factory can construct either interchangeably.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import httpx

from prthinker.checks import CheckResult
from prthinker.conventional import format_inline_body
from prthinker.dialogue import AuthorReply
from prthinker.platforms.base import PlatformAdapter
from prthinker.schemas import InlineFinding

log = logging.getLogger(__name__)

_USER_AGENT = "prthinker/0.1"
_COMMENTS_PER_PAGE = 50
_STATUS_DESCRIPTION_MAX = 255

# Gitea review verbs differ from GitHub's; map our platform-neutral
# vocabulary onto Gitea's ``type`` field for ``POST .../reviews``.
_EVENT_TO_GITEA: dict[str, str] = {
    "APPROVE":         "APPROVE",
    "REQUEST_CHANGES": "REQUEST_CHANGES",
    "COMMENT":         "COMMENT",
}



@dataclass
class GiteaAdapter(PlatformAdapter):
    """Single Gitea PR worth of state behind the platform-neutral API."""

    repo: str                # "owner/repo"
    token: str
    pr_number: int
    comment_marker: str = "<!-- prthinker:summary -->"
    base_url: str = "https://gitea.com/api/v1"

    def _client(self) -> httpx.Client:
        return httpx.Client(
            base_url=self.base_url.rstrip("/"),
            timeout=30.0,
            headers={
                "Authorization": f"token {self.token}",
                "Accept": "application/json",
                "User-Agent": _USER_AGENT,
            },
        )

    def _pr_path(self) -> str:
        """Return the ``/repos/{repo}/pulls/{n}`` path prefix."""
        return f"/repos/{self.repo}/pulls/{self.pr_number}"

    def _pull(self, client: httpx.Client) -> dict[str, Any]:
        """Fetch the PR object from ``GET /repos/{repo}/pulls/{n}``."""
        response = client.get(self._pr_path())
        response.raise_for_status()
        return response.json()

    # ----- metadata ------------------------------------------------------

    def fetch_diff(self) -> str:
        """Return the unified diff via ``GET /pulls/{n}.diff``."""
        with self._client() as client:
            response = client.get(f"{self._pr_path()}.diff")
            response.raise_for_status()
            return response.text

    def fetch_head_sha(self) -> str:
        """Return the PR head commit SHA — required by the gate API."""
        with self._client() as client:
            head = self._pull(client).get("head") or {}
        return str(head.get("sha") or "")

    def fetch_base_branch(self) -> str:
        """Return the PR base branch name — used by auto-fix PRs."""
        with self._client() as client:
            base = self._pull(client).get("base") or {}
        return str(base.get("ref") or "")

    def fetch_pr_meta(self) -> tuple[str, str]:
        """Return ``(title, body)`` from the PR object."""
        with self._client() as client:
            pull = self._pull(client)
        return (str(pull.get("title") or ""), str(pull.get("body") or ""))

    # ----- summary comment ----------------------------------------------

    def upsert_summary_comment(self, body: str) -> int:
        """Create-or-update the marker-tagged PR comment. Return its id."""
        if self.comment_marker not in body:
            raise ValueError("body must contain the configured comment marker")

        with self._client() as client:
            existing = self._find_marker_comment(client)
            if existing is not None:
                log.info("Gitea: updating existing comment %d", existing)
                response = client.patch(
                    f"/repos/{self.repo}/issues/comments/{existing}",
                    json={"body": body},
                )
                response.raise_for_status()
                return existing
            log.info("Gitea: creating new comment")
            response = client.post(
                f"/repos/{self.repo}/issues/{self.pr_number}/comments",
                json={"body": body},
            )
            response.raise_for_status()
            return int(response.json()["id"])

    def _find_marker_comment(self, client: httpx.Client) -> int | None:
        """Return the id of the first comment carrying our marker, else None."""
        page = 1
        while True:
            response = client.get(
                f"/repos/{self.repo}/issues/{self.pr_number}/comments",
                params={"limit": _COMMENTS_PER_PAGE, "page": page},
            )
            response.raise_for_status()
            batch = response.json()
            if not batch:
                return None
            for comment in batch:
                if self.comment_marker in (comment.get("body") or ""):
                    return int(comment["id"])
            if len(batch) < _COMMENTS_PER_PAGE:
                return None
            page += 1

    # ----- inline review ------------------------------------------------

    def submit_inline_review(
        self,
        findings: list[InlineFinding],
        *,
        summary_body: str | None,
        event: str,
    ) -> int | None:
        """Post a single PR review carrying one inline comment per finding."""
        if not findings:
            log.info("Gitea: no findings — skipping review submission")
            return None

        comments = [_build_inline_comment(f) for f in findings]
        payload: dict[str, Any] = {
            "event": _EVENT_TO_GITEA.get(event, "COMMENT"),
            "body": summary_body or "prthinker — inline findings",
            "comments": comments,
        }
        with self._client() as client:
            response = client.post(
                f"{self._pr_path()}/reviews",
                json=payload,
            )
            if response.status_code >= 400:
                log.error(
                    "Gitea review submission failed (%d): %s",
                    response.status_code, response.text,
                )
            response.raise_for_status()
            review_id = int(response.json()["id"])
            log.info(
                "Gitea: submitted review %d with %d inline comments",
                review_id, len(comments),
            )
            return review_id

    # ----- dialogue ------------------------------------------------------

    def fetch_author_replies(self) -> list[AuthorReply]:
        """Return author replies posted after the most recent marker comment.

        Like the GitHub adapter, replies are positional — every non-bot
        comment after the latest prthinker summary comment counts as a
        candidate reply.
        """
        with self._client() as client:
            comments = self._collect_all_comments(client)

        marker_idx = self._find_last_marker_index(comments)
        if marker_idx is None:
            return []
        return self._build_replies(comments, marker_idx)

    def _collect_all_comments(self, client: httpx.Client) -> list[dict]:
        """Page through every PR conversation comment, oldest first."""
        comments: list[dict] = []
        page = 1
        while True:
            response = client.get(
                f"/repos/{self.repo}/issues/{self.pr_number}/comments",
                params={"limit": _COMMENTS_PER_PAGE, "page": page},
            )
            response.raise_for_status()
            batch = response.json()
            if not batch:
                break
            comments.extend(batch)
            if len(batch) < _COMMENTS_PER_PAGE:
                break
            page += 1
        return comments

    def _find_last_marker_index(self, comments: list[dict]) -> int | None:
        """Index of the most recent comment carrying our marker, else None."""
        marker_idx: int | None = None
        for i, comment in enumerate(comments):
            if self.comment_marker in (comment.get("body") or ""):
                marker_idx = i  # last wins
        return marker_idx

    @staticmethod
    def _comment_login(comment: dict) -> str:
        """Login of the comment author, or empty string when absent."""
        return (comment.get("user") or {}).get("login") or ""

    def _build_replies(
        self, comments: list[dict], marker_idx: int,
    ) -> list[AuthorReply]:
        """Author replies trailing the marker comment, dropping our own."""
        marker_user = self._comment_login(comments[marker_idx])
        in_reply_to_id = int(comments[marker_idx]["id"])
        replies: list[AuthorReply] = []
        for comment in comments[marker_idx + 1:]:
            user = self._comment_login(comment)
            if user == marker_user:
                continue
            replies.append(AuthorReply(
                author=user,
                body=str(comment.get("body") or "").strip(),
                in_reply_to_id=in_reply_to_id,
                created_at=str(comment.get("created_at") or ""),
            ))
        return replies

    # ----- gate (commit status) -----------------------------------------

    def open_gate(self, head_sha: str, *, name: str = "prthinker") -> dict[str, str]:
        """Open a ``pending`` commit status and return an opaque handle."""
        with self._client() as client:
            response = client.post(
                f"/repos/{self.repo}/statuses/{head_sha}",
                json={"state": "pending", "context": name},
            )
            response.raise_for_status()
        return {"sha": head_sha, "name": name}

    def close_gate(self, handle: dict[str, str], result: CheckResult) -> None:
        """Mark the previously opened commit status as completed."""
        # Gitea states: pending / success / error / failure / warning.
        gitea_state = "success" if result.conclusion == "success" else "failure"
        description = result.title[:_STATUS_DESCRIPTION_MAX]
        with self._client() as client:
            response = client.post(
                f"/repos/{self.repo}/statuses/{handle['sha']}",
                json={
                    "state": gitea_state,
                    "context": handle["name"],
                    "description": description,
                },
            )
            response.raise_for_status()


def _build_inline_comment(finding: InlineFinding) -> dict[str, Any]:
    """Build the JSON payload for one entry in a Gitea review's ``comments``."""
    return {
        "path": finding.path,
        "new_position": finding.line,
        "body": _format_inline_body(finding),
    }


def _format_inline_body(finding: InlineFinding) -> str:
    """Render a finding's Conventional-Comments body (shared across platforms)."""
    return format_inline_body(finding)


__all__ = ["GiteaAdapter"]

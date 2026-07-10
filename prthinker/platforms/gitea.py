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
from typing import Any, Iterator

import httpx

from prthinker.checks import CheckResult
from prthinker.conventional import format_inline_body
from prthinker.dialogue import AuthorReply
from prthinker.github_api import paginate
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

    def __post_init__(self) -> None:
        # Cache the PR object so head SHA / base branch / title+body don't
        # refetch it across calls (mirrors the GitLab adapter's _mr_cache).
        self._pr_cache: dict[str, Any] | None = None

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
        """Fetch (and cache) the PR object from ``GET /repos/{repo}/pulls/{n}``."""
        if self._pr_cache is None:
            response = client.get(self._pr_path())
            response.raise_for_status()
            self._pr_cache = response.json()
        return self._pr_cache

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
        for comment in self._iter_comments(client):
            if self.comment_marker in (comment.get("body") or ""):
                return int(comment["id"])
        return None

    def _iter_comments(self, client: httpx.Client) -> Iterator[dict]:
        """Page through the PR conversation comments, oldest first.

        Gitea's pagination mirrors GitHub's except the page-size
        parameter is named ``limit``; the shared generator covers that.
        """
        return paginate(
            client,
            f"/repos/{self.repo}/issues/{self.pr_number}/comments",
            per_page=_COMMENTS_PER_PAGE,
            size_param="limit",
        )

    # ----- inline review ------------------------------------------------

    def submit_inline_review(
        self,
        findings: list[InlineFinding],
        *,
        summary_body: str | None,
        event: str,
        diff_text: str | None = None,
    ) -> int | None:
        """Post a single PR review carrying one inline comment per finding."""
        del diff_text  # Gitea posts reviews without a diff pre-filter
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
        candidate reply. The marker scan and reply build are the base
        class's shared template method.
        """
        with self._client() as client:
            comments = list(self._iter_comments(client))
        return self._replies_after_marker(comments, self.comment_marker)

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

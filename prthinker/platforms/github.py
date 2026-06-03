"""GitHub :class:`PlatformAdapter` — thin wrapper over the existing helpers.

The legacy ``prthinker.github_api`` and ``prthinker.checks`` modules
keep working unchanged (this adapter delegates to them) so callers that
imported the function-style API are not broken.
"""

from __future__ import annotations

from dataclasses import dataclass

from prthinker.checks import (
    CheckResult,
    complete_check_run,
    create_check_run,
)
from prthinker.config import GitHubConfig
from prthinker.dialogue import AuthorReply
from prthinker.github_api import (
    fetch_pr_base_branch,
    fetch_pr_commit_messages,
    fetch_pr_diff,
    fetch_pr_head_sha,
    set_pr_labels,
    submit_inline_review,
    upsert_pr_body_section,
    upsert_pr_comment,
    upsert_pr_comments,
)
from prthinker.pr_labels import MANAGED_PREFIX
from prthinker.platforms.base import PlatformAdapter
from prthinker.schemas import InlineFinding

_COMMENTS_PER_PAGE = 100


@dataclass
class GitHubAdapter(PlatformAdapter):
    repo: str
    token: str
    pr_number: int
    comment_marker: str = "<!-- prthinker:summary -->"
    base_url: str = "https://api.github.com"

    def _gh(self) -> GitHubConfig:
        return GitHubConfig(
            repo=self.repo,
            pr_number=self.pr_number,
            token=self.token,
            comment_marker=self.comment_marker,
        )

    # ----- metadata ------------------------------------------------------

    def fetch_diff(self) -> str:
        return fetch_pr_diff(self._gh())

    def fetch_head_sha(self) -> str:
        return fetch_pr_head_sha(self._gh())

    def fetch_base_branch(self) -> str:
        return fetch_pr_base_branch(self._gh())

    def fetch_commit_messages(self) -> list[str]:
        return fetch_pr_commit_messages(self._gh())

    def set_labels(self, labels: list[str]) -> None:
        set_pr_labels(self._gh(), labels, managed_prefix=MANAGED_PREFIX)

    def update_body_section(self, section: str) -> None:
        upsert_pr_body_section(self._gh(), section)

    def fetch_pr_meta(self) -> tuple[str, str]:
        """Pull ``(title, body)`` from ``GET /repos/{repo}/pulls/{n}``."""
        import httpx

        with httpx.Client(
            base_url=self.base_url.rstrip("/"),
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "reviewmind/0.1",
            },
        ) as client:
            response = client.get(
                f"/repos/{self.repo}/pulls/{self.pr_number}"
            )
            response.raise_for_status()
            data = response.json()
        title = str(data.get("title") or "")
        body = str(data.get("body") or "")
        return (title, body)

    # ----- comments ------------------------------------------------------

    def upsert_summary_comment(self, body: str) -> int:
        return upsert_pr_comment(self._gh(), body)

    def upsert_summary_comments(self, bodies: list[str]) -> list[int]:
        return upsert_pr_comments(self._gh(), bodies)

    def submit_inline_review(
        self,
        findings: list[InlineFinding],
        *,
        summary_body: str | None,
        event: str,
    ) -> int | None:
        return submit_inline_review(
            self._gh(), findings,
            summary_body=summary_body, event=event,
        )

    # ----- gate ----------------------------------------------------------

    def open_gate(self, head_sha: str, *, name: str = "prthinker") -> int:
        return create_check_run(self._gh(), head_sha, name=name)

    def close_gate(self, handle: int, result: CheckResult) -> None:
        complete_check_run(self._gh(), handle, result)

    # ----- dialogue ------------------------------------------------------

    def fetch_author_replies(self) -> list[AuthorReply]:
        """All issue-comment replies on this PR posted after the most
        recent prthinker summary comment, by users other than the bot.

        Implementation note: GitHub's issue-comments API on a PR
        ``/issues/:n/comments`` returns the PR conversation timeline
        (NOT the per-line review comments). The summary comment we
        upsert lives there, so all replies to it appear in the same
        feed, ordered by ``created_at``.
        """
        import httpx

        with httpx.Client(
            base_url=self.base_url.rstrip("/"),
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "prthinker/0.1",
            },
        ) as client:
            comments = self._paginate_issue_comments(client)

        # Find the latest prthinker comment by marker; everything posted
        # after it is potential author reply.
        marker_idx = self._find_last_marker_index(comments)
        if marker_idx is None:
            return []
        return self._collect_replies_after_marker(comments, marker_idx)

    def _paginate_issue_comments(self, client: object) -> list[dict]:
        """Fetch every issue-comment page for this PR, oldest first."""
        comments: list[dict] = []
        page = 1
        while True:
            response = client.get(
                f"/repos/{self.repo}/issues/{self.pr_number}/comments",
                params={"per_page": _COMMENTS_PER_PAGE, "page": page},
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
        """Index of the most recent prthinker summary comment, if any."""
        marker_idx = None
        for i, comment in enumerate(comments):
            if self.comment_marker in (comment.get("body") or ""):
                marker_idx = i  # last one wins (re-scan continues)
        return marker_idx

    @staticmethod
    def _comment_login(comment: dict) -> str:
        """Login of the comment author, or empty string when absent."""
        return (comment.get("user") or {}).get("login") or ""

    def _collect_replies_after_marker(
        self, comments: list[dict], marker_idx: int,
    ) -> list[AuthorReply]:
        """Build :class:`AuthorReply` objects for non-bot comments after the marker."""
        marker_user = self._comment_login(comments[marker_idx])
        in_reply_to_id = int(comments[marker_idx]["id"])
        replies: list[AuthorReply] = []
        for comment in comments[marker_idx + 1:]:
            user = self._comment_login(comment)
            if user == marker_user:
                continue  # skip our own follow-up comments
            replies.append(AuthorReply(
                author=user,
                body=str(comment.get("body") or "").strip(),
                in_reply_to_id=in_reply_to_id,
                created_at=str(comment.get("created_at") or ""),
            ))
        return replies


__all__ = ["GitHubAdapter"]

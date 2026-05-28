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
    fetch_pr_diff,
    fetch_pr_head_sha,
    submit_inline_review,
    upsert_pr_comment,
)
from prthinker.platforms.base import PlatformAdapter
from prthinker.schemas import InlineFinding


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

        marker = self.comment_marker
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
            comments: list[dict] = []
            page = 1
            while True:
                response = client.get(
                    f"/repos/{self.repo}/issues/{self.pr_number}/comments",
                    params={"per_page": 100, "page": page},
                )
                response.raise_for_status()
                batch = response.json()
                if not batch:
                    break
                comments.extend(batch)
                if len(batch) < 100:
                    break
                page += 1

        # Find the latest prthinker comment by marker; everything posted
        # after it is potential author reply.
        marker_idx = None
        for i, c in enumerate(comments):
            if marker in (c.get("body") or ""):
                marker_idx = i  # last one wins (re-scan continues)
        if marker_idx is None:
            return []

        replies: list[AuthorReply] = []
        marker_user = (comments[marker_idx].get("user") or {}).get("login") or ""
        for c in comments[marker_idx + 1:]:
            user = (c.get("user") or {}).get("login") or ""
            if user == marker_user:
                continue  # skip our own follow-up comments
            replies.append(AuthorReply(
                author=user,
                body=str(c.get("body") or "").strip(),
                in_reply_to_id=int(comments[marker_idx]["id"]),
                created_at=str(c.get("created_at") or ""),
            ))
        return replies


__all__ = ["GitHubAdapter"]

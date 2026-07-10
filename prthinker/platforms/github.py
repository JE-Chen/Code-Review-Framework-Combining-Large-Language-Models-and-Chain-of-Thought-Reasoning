"""GitHub :class:`PlatformAdapter` — thin wrapper over the existing helpers.

The legacy ``prthinker.github_api`` and ``prthinker.checks`` modules
keep working unchanged (this adapter delegates to them) so callers that
imported the function-style API are not broken.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from prthinker.checks import (
    CheckResult,
    complete_check_run,
    create_check_run,
)
from prthinker.ci_signals import (
    FailureSignal,
    fetch_ci_failure_signals,
)
from prthinker.config import GitHubConfig
from prthinker.dialogue import AuthorReply
from prthinker.github_api import (
    client_for,
    fetch_pr_commit_messages,
    fetch_pr_diff,
    fetch_pr_file_paths,
    paginate,
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

    def __post_init__(self) -> None:
        # Cache the PR object so head SHA / base branch / title+body don't
        # refetch it across calls (mirrors the GitLab adapter's _mr_cache).
        self._pr_cache: dict[str, Any] | None = None

    def _gh(self, marker: str | None = None) -> GitHubConfig:
        return GitHubConfig(
            repo=self.repo,
            pr_number=self.pr_number,
            token=self.token,
            comment_marker=marker or self.comment_marker,
            base_url=self.base_url,
        )

    def _pull(self) -> dict[str, Any]:
        """Fetch (and cache) the PR object from ``GET /repos/{repo}/pulls/{n}``."""
        if self._pr_cache is None:
            with client_for(self._gh()) as client:
                response = client.get(
                    f"/repos/{self.repo}/pulls/{self.pr_number}"
                )
                response.raise_for_status()
                self._pr_cache = response.json()
        return self._pr_cache

    # ----- metadata ------------------------------------------------------

    def fetch_diff(self) -> str:
        return fetch_pr_diff(self._gh())

    def fetch_head_sha(self) -> str:
        return str((self._pull().get("head") or {}).get("sha") or "")

    def fetch_base_branch(self) -> str:
        return str((self._pull().get("base") or {}).get("ref") or "")

    def fetch_commit_messages(self) -> list[str]:
        return fetch_pr_commit_messages(self._gh())

    def fetch_changed_paths(self) -> list[str]:
        return fetch_pr_file_paths(self._gh())

    def set_labels(self, labels: list[str]) -> None:
        set_pr_labels(self._gh(), labels, managed_prefix=MANAGED_PREFIX)
        self._pr_cache = None

    def update_body_section(self, section: str) -> None:
        upsert_pr_body_section(self._gh(), section)
        self._pr_cache = None

    def fetch_pr_meta(self) -> tuple[str, str]:
        """Pull ``(title, body)`` from the PR object we already cache."""
        pull = self._pull()
        return (str(pull.get("title") or ""), str(pull.get("body") or ""))

    # ----- comments ------------------------------------------------------

    def upsert_summary_comment(self, body: str) -> int:
        return upsert_pr_comment(self._gh(), body)

    def upsert_summary_comments(self, bodies: list[str]) -> list[int]:
        return upsert_pr_comments(self._gh(), bodies)

    def upsert_marked_comment(self, body: str, *, marker: str) -> int:
        # A distinct marker means a distinct comment: upsert keys off the
        # config's comment_marker, so swap it in for this one call.
        return upsert_pr_comment(self._gh(marker), body)

    def submit_inline_review(
        self,
        findings: list[InlineFinding],
        *,
        summary_body: str | None,
        event: str,
        diff_text: str | None = None,
    ) -> int | None:
        return submit_inline_review(
            self._gh(), findings,
            summary_body=summary_body, event=event, diff_text=diff_text,
        )

    # ----- CI failure signals ---------------------------------------------

    def fetch_ci_failure_signals(
        self,
        head_sha: str,
        *,
        max_jobs: int = 5,
        log_tail_chars: int = 4000,
    ) -> list[FailureSignal]:
        return fetch_ci_failure_signals(
            self.repo, head_sha, self.token,
            max_jobs=max_jobs, log_tail_chars=log_tail_chars,
            base_url=self.base_url,
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
        feed, ordered by ``created_at``. The marker scan and reply build
        are the base class's shared template method.
        """
        with client_for(self._gh()) as client:
            comments = list(paginate(
                client,
                f"/repos/{self.repo}/issues/{self.pr_number}/comments",
                per_page=_COMMENTS_PER_PAGE,
            ))
        return self._replies_after_marker(comments, self.comment_marker)


__all__ = ["GitHubAdapter"]

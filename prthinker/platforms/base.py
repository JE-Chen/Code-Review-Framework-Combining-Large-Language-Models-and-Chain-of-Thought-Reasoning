"""Platform adapter contract — the smallest API the pipeline needs.

Anything that varies between GitHub, GitLab, Bitbucket, etc. — diff
retrieval, inline-comment posting, status-check creation — goes through
the methods on :class:`PlatformAdapter`. Anything truly identical (diff
parsing, prompt building, dismissed filtering) stays in the core
package and depends only on this ABC.

Methods are deliberately small in number; we resisted adding
``fetch_pr_reviews`` / ``list_milestones`` / etc. until the pipeline
actually needs them. Platform-specific extras (e.g. GitHub's Check Run
API vs GitLab's commit-status API) are unified into one ``open_gate``
+ ``close_gate`` pair that returns an opaque handle each platform
interprets in its own way.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

from prthinker.checks import CheckResult
from prthinker.ci_signals import FailureSignal
from prthinker.dialogue import AuthorReply
from prthinker.schemas import InlineFinding

log = logging.getLogger(__name__)


class PlatformKind(str, Enum):
    GITHUB = "github"
    GITLAB = "gitlab"
    GITEA = "gitea"


class PlatformAdapter(ABC):
    """Single PR / MR worth of state — repo, token, pr/mr identifier."""

    # ----- PR / MR metadata ---------------------------------------------

    @abstractmethod
    def fetch_diff(self) -> str:
        """Return the unified diff for this PR / MR."""

    @abstractmethod
    def fetch_head_sha(self) -> str:
        """Return the head commit SHA — needed for the gate API."""

    @abstractmethod
    def fetch_base_branch(self) -> str:
        """Return the base branch name — used by auto-fix PRs."""

    def fetch_pr_meta(self) -> tuple[str, str]:
        """Return ``(title, body)`` for the PR. Default returns empty
        strings so adapters can opt-in to PR-type classification
        without breaking existing implementations.
        """
        return ("", "")

    def fetch_commit_messages(self) -> list[str]:
        """Return the PR's commit messages, oldest first.

        Default returns ``[]`` so adapters without commit access degrade
        to a files-only preliminary overview. Concrete adapters override.
        """
        return []

    def fetch_changed_paths(self) -> list[str]:
        """Return every changed file path on the PR.

        Default returns ``[]`` so adapters that cannot enumerate files
        skip the full-scan coverage check. Concrete adapters override.
        """
        return []

    def set_labels(self, labels: list[str]) -> None:  # pylint: disable=unused-argument  # overridable no-op; subclasses use labels
        """Apply the prthinker-managed labels to the PR.

        Default is a no-op so adapters without label support simply skip
        labelling. Concrete adapters override to reconcile labels.
        """
        log.info("%s does not support PR labels; skipping", type(self).__name__)

    def update_body_section(self, section: str) -> None:  # pylint: disable=unused-argument  # overridable no-op; subclasses use section
        """Insert / replace a prthinker section in the PR description.

        Default is a no-op; adapters that support editing the PR body
        override to upsert a marker-delimited block.
        """
        log.info(
            "%s does not support PR body editing; skipping", type(self).__name__
        )

    # ----- summary comment (one per PR) ---------------------------------

    @abstractmethod
    def upsert_summary_comment(self, body: str) -> int:
        """Create-or-update the marker-tagged PR comment. Return its id.

        The marker comes from the adapter's ``comment_marker`` field; the
        body must already contain it.
        """

    def upsert_marked_comment(self, body: str, *, marker: str) -> int:  # pylint: disable=unused-argument  # no-op default; overrides consume body
        """Create-or-update a secondary PR comment keyed by ``marker``.

        Used for auxiliary comments that live alongside — not inside — the
        review summary comment (e.g. the Copilot-style PR summary, which
        gets its own marker so it can be upserted independently). Default
        logs that the platform has no support and returns ``-1``; adapters
        that can post a marker-tagged comment override this.
        """
        log.info(
            "%s does not support auxiliary marked comments; skipping",
            type(self).__name__,
        )
        return -1

    def upsert_summary_comments(self, bodies: list[str]) -> list[int]:
        """Create / update / reconcile one-or-more summary comment pages.

        A long review is paginated across several comments. The default
        implementation supports a single comment only: it upserts the
        first page and warns that any overflow pages are dropped.
        Adapters that can reconcile multiple comments (e.g. GitHub)
        override this. Returns the comment ids in page order.
        """
        if not bodies:
            return []
        if len(bodies) > 1:
            log.warning(
                "%s posts a single summary comment; %d overflow page(s) "
                "dropped — full review is in the job logs",
                type(self).__name__, len(bodies) - 1,
            )
        return [self.upsert_summary_comment(bodies[0])]

    # ----- inline review (per-line comments) ----------------------------

    @abstractmethod
    def submit_inline_review(
        self,
        findings: list[InlineFinding],
        *,
        summary_body: str | None,
        event: str,
        diff_text: str | None = None,
    ) -> int | None:
        """Post inline comments with optional ``suggestion`` blocks.

        ``event`` is the platform-neutral verdict — one of ``COMMENT``,
        ``APPROVE``, ``REQUEST_CHANGES``. Each adapter maps to its own
        API verb. ``diff_text`` lets a caller that already holds the PR
        diff skip the off-hunk pre-filter's re-download (``None`` keeps
        the fetch-on-demand behaviour). Return the new review /
        discussion id, or ``None`` if the findings list was empty.
        """

    # ----- CI failure signals -------------------------------------------

    def fetch_ci_failure_signals(
        self,
        head_sha: str,  # pylint: disable=unused-argument  # overridable no-op; subclasses use it
        *,
        max_jobs: int = 5,  # pylint: disable=unused-argument
        log_tail_chars: int = 4000,  # pylint: disable=unused-argument
    ) -> list[FailureSignal]:
        """Return failed-job log tails for the head commit.

        Default returns ``[]`` so adapters without a CI API degrade to a
        review without failure context. Concrete adapters override
        (GitHub Actions runs / GitLab pipelines).
        """
        log.info(
            "%s does not support CI failure signals; skipping",
            type(self).__name__,
        )
        return []

    # ----- dialogue (closed-loop multi-turn review) ---------------------

    def fetch_author_replies(self) -> list[AuthorReply]:
        """Return author replies to the most recent prthinker comment.

        Default implementation returns ``[]`` so adapters without
        dialogue support degrade to one-shot reviews. Concrete adapters
        override to fetch from the platform's reply / thread API.
        """
        return []

    # ----- dialogue helpers (shared marker scan / reply build) ----------

    @staticmethod
    def _comment_author(comment: dict) -> str:
        """Author login of a raw comment payload, or empty string.

        Template-method hook: GitHub and Gitea nest the author under
        ``user.login`` (this default); adapters with a different payload
        shape (GitLab notes use ``author.username``) override just this
        extractor and reuse the shared reply scan below.
        """
        return (comment.get("user") or {}).get("login") or ""

    def _skip_reply(self, comment: dict, marker_author: str) -> bool:
        """Whether a trailing comment is not an author reply.

        Default skips the bot's own follow-up comments; adapters add
        platform-specific noise (e.g. GitLab system notes) on top.
        """
        return self._comment_author(comment) == marker_author

    @staticmethod
    def _find_last_marker_index(
        comments: list[dict], marker: str
    ) -> int | None:
        """Index of the most recent comment containing ``marker``, if any."""
        marker_idx: int | None = None
        for i, comment in enumerate(comments):
            if marker in (comment.get("body") or ""):
                marker_idx = i  # last one wins (re-scan continues)
        return marker_idx

    def _replies_after_marker(
        self, comments: list[dict], marker: str
    ) -> list[AuthorReply]:
        """Author replies trailing the last ``marker`` comment (template).

        Shared by every adapter: find the most recent marker comment,
        then collect the non-skipped comments after it as
        :class:`AuthorReply` objects. The per-platform variation lives in
        the ``_comment_author`` / ``_skip_reply`` hooks.
        """
        marker_idx = self._find_last_marker_index(comments, marker)
        if marker_idx is None:
            return []
        marker_author = self._comment_author(comments[marker_idx])
        in_reply_to_id = int(comments[marker_idx]["id"])
        return [
            AuthorReply(
                author=self._comment_author(comment),
                body=str(comment.get("body") or "").strip(),
                in_reply_to_id=in_reply_to_id,
                created_at=str(comment.get("created_at") or ""),
            )
            for comment in comments[marker_idx + 1:]
            if not self._skip_reply(comment, marker_author)
        ]

    # ----- status-check / gate (Check Run on GitHub, commit status on GitLab) ---

    @abstractmethod
    def open_gate(self, head_sha: str, *, name: str = "prthinker") -> Any:
        """Open an in-progress status check and return an opaque handle."""

    @abstractmethod
    def close_gate(self, handle: Any, result: CheckResult) -> None:
        """Mark the previously opened gate as completed with the given result."""


__all__ = ["PlatformAdapter", "PlatformKind"]

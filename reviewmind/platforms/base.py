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

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

from reviewmind.checks import CheckResult
from reviewmind.dialogue import AuthorReply
from reviewmind.schemas import InlineFinding


class PlatformKind(str, Enum):
    GITHUB = "github"
    GITLAB = "gitlab"


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

    # ----- summary comment (one per PR) ---------------------------------

    @abstractmethod
    def upsert_summary_comment(self, body: str) -> int:
        """Create-or-update the marker-tagged PR comment. Return its id.

        The marker comes from the adapter's ``comment_marker`` field; the
        body must already contain it.
        """

    # ----- inline review (per-line comments) ----------------------------

    @abstractmethod
    def submit_inline_review(
        self,
        findings: list[InlineFinding],
        *,
        summary_body: str | None,
        event: str,
    ) -> int | None:
        """Post inline comments with optional ``suggestion`` blocks.

        ``event`` is the platform-neutral verdict — one of ``COMMENT``,
        ``APPROVE``, ``REQUEST_CHANGES``. Each adapter maps to its own
        API verb. Return the new review / discussion id, or ``None`` if
        the findings list was empty.
        """

    # ----- dialogue (closed-loop multi-turn review) ---------------------

    def fetch_author_replies(self) -> list[AuthorReply]:
        """Return author replies to the most recent reviewmind comment.

        Default implementation returns ``[]`` so adapters without
        dialogue support degrade to one-shot reviews. Concrete adapters
        override to fetch from the platform's reply / thread API.
        """
        return []

    # ----- status-check / gate (Check Run on GitHub, commit status on GitLab) ---

    @abstractmethod
    def open_gate(self, head_sha: str, *, name: str = "reviewmind") -> Any:
        """Open an in-progress status check and return an opaque handle."""

    @abstractmethod
    def close_gate(self, handle: Any, result: CheckResult) -> None:
        """Mark the previously opened gate as completed with the given result."""


__all__ = ["PlatformAdapter", "PlatformKind"]

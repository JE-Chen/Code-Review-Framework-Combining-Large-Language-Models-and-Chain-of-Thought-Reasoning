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
from prthinker.github_api import (
    filter_findings_to_diff,
    new_side_lines,
    paginate,
    replace_marked_section,
)
from prthinker.platforms.base import PlatformAdapter
from prthinker.pr_labels import MANAGED_PREFIX
from prthinker.schemas import InlineFinding

log = logging.getLogger(__name__)

_USER_AGENT = "prthinker/0.1"
_COMMENTS_PER_PAGE = 50
_STATUS_DESCRIPTION_MAX = 255
_DEFAULT_LABEL_COLOR = "ededed"
_LABEL_CREATED = 201

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

    def fetch_commit_messages(self) -> list[str]:
        """Return the PR's commit messages, oldest first (paginated)."""
        with self._client() as client:
            return [
                str((c.get("commit") or {}).get("message") or "")
                for c in paginate(
                    client, f"{self._pr_path()}/commits",
                    per_page=_COMMENTS_PER_PAGE, size_param="limit",
                )
            ]

    def fetch_changed_paths(self) -> list[str]:
        """Return every changed file path on the PR (paginated)."""
        with self._client() as client:
            return [
                str(f["filename"])
                for f in paginate(
                    client, f"{self._pr_path()}/files",
                    per_page=_COMMENTS_PER_PAGE, size_param="limit",
                )
                if f.get("filename")
            ]

    # ----- labels / body ---------------------------------------------------

    def set_labels(self, labels: list[str]) -> None:
        """Reconcile the managed-prefix labels on the PR, keeping human ones.

        Gitea's label API is GitHub-shaped and lives on the *issue*
        resource; ``PUT .../issues/{n}/labels`` replaces the whole set, so
        the desired list re-applies the human labels plus the new managed
        ones (stale managed labels drop out).
        """
        issue_path = f"/repos/{self.repo}/issues/{self.pr_number}"
        with self._client() as client:
            response = client.get(f"{issue_path}/labels")
            response.raise_for_status()
            current = [str(lb.get("name") or "") for lb in (response.json() or [])]
            for name in labels:
                self._ensure_label_exists(client, name)
            applied = client.put(
                f"{issue_path}/labels",
                json={"labels": _reconcile_labels(current, labels)},
            )
            applied.raise_for_status()
            self._pr_cache = None
        log.info("Gitea: set PR labels: %s", labels)

    def _ensure_label_exists(self, client: httpx.Client, name: str) -> None:
        """Create the repo label if missing; an existing one is fine."""
        response = client.post(
            f"/repos/{self.repo}/labels",
            json={"name": name, "color": _DEFAULT_LABEL_COLOR},
        )
        if response.status_code != _LABEL_CREATED:
            log.debug(
                "Gitea: label %r create returned %d (already exists or "
                "insufficient rights); continuing",
                name, response.status_code,
            )

    def update_body_section(self, section: str) -> None:
        """Insert / replace the prthinker block in the PR description."""
        with self._client() as client:
            body = str(self._pull(client).get("body") or "")
            new_body = replace_marked_section(body, section)
            if new_body == body:
                return
            response = client.patch(self._pr_path(), json={"body": new_body})
            response.raise_for_status()
            self._pr_cache = None
        log.info("Gitea: updated PR description section")

    # ----- summary comment ----------------------------------------------

    def upsert_summary_comment(self, body: str) -> int:
        """Create-or-update the marker-tagged PR comment. Return its id."""
        return self._upsert_by_marker(body, self.comment_marker)

    def upsert_marked_comment(self, body: str, *, marker: str) -> int:
        """Create-or-update a secondary PR comment keyed by ``marker``."""
        return self._upsert_by_marker(body, marker)

    def _upsert_by_marker(self, body: str, marker: str) -> int:
        """Update the first comment carrying ``marker``, or create one."""
        if marker not in body:
            raise ValueError("body must contain the configured comment marker")

        with self._client() as client:
            existing = self._find_marker_comment(client, marker)
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

    def _find_marker_comment(
        self, client: httpx.Client, marker: str
    ) -> int | None:
        """Return the id of the first comment carrying ``marker``, else None."""
        for comment in self._iter_comments(client):
            if marker in (comment.get("body") or ""):
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
        """Post a PR review carrying one inline comment per finding.

        Findings are pre-filtered against the diff hunks first (a caller
        that already holds the diff passes ``diff_text`` to skip the
        re-download). If the batched review is still rejected, each
        comment is retried in its own review so one bad line skips only
        that comment instead of aborting the whole review.
        """
        if not findings:
            log.info("Gitea: no findings — skipping review submission")
            return None
        items = self._prefilter_findings(findings, diff_text)
        if not items:
            log.info("Gitea: all inline findings dropped — skipping review")
            return None

        payload: dict[str, Any] = {
            "event": _EVENT_TO_GITEA.get(event, "COMMENT"),
            "body": summary_body or "prthinker — inline findings",
            "comments": [_build_inline_comment(f) for f in items],
        }
        with self._client() as client:
            review_id = self._post_review(client, payload)
            if review_id is not None:
                log.info(
                    "Gitea: submitted review %d with %d inline comments",
                    review_id, len(items),
                )
                return review_id
            return self._post_single_comment_reviews(client, items, payload)

    def _prefilter_findings(
        self,
        findings: list[InlineFinding],
        diff_text: str | None = None,
    ) -> list[InlineFinding]:
        """Drop findings off the PR's diff hunks before the review POST.

        Same first-line-of-defence as the GitHub / GitLab adapters: an
        off-hunk line 4xxs Gitea's whole batched review. Fail-open — when
        the diff cannot be fetched or yields no hunk lines, every finding
        is submitted and the per-comment fallback stays the backstop.
        """
        if diff_text is None:
            try:
                diff_text = self.fetch_diff()
            except httpx.HTTPError as exc:
                log.warning(
                    "Gitea: could not fetch PR diff for pre-filtering (%s); "
                    "submitting all findings", exc,
                )
                return findings
        if not new_side_lines(diff_text):
            log.info(
                "Gitea: PR diff yielded no hunk lines; "
                "submitting all findings unfiltered",
            )
            return findings
        return filter_findings_to_diff(findings, diff_text)

    def _post_review(
        self, client: httpx.Client, payload: dict[str, Any]
    ) -> int | None:
        """POST one review payload; return the review id, or None on 4xx/5xx."""
        response = client.post(f"{self._pr_path()}/reviews", json=payload)
        if response.status_code >= 400:
            log.warning(
                "Gitea review submission failed (%d): %s",
                response.status_code, response.text,
            )
            return None
        return int(response.json()["id"])

    def _post_single_comment_reviews(
        self,
        client: httpx.Client,
        items: list[InlineFinding],
        payload: dict[str, Any],
    ) -> int | None:
        """Fallback after a batch rejection: one review per comment.

        A single unresolvable line fails Gitea's whole batched review, so
        each finding is retried in its own single-comment review — a bad
        line then skips only that comment (logged) instead of dropping
        every other finding. The summary body rides on the first review
        that succeeds. Returns that review's id, or None if all failed.
        """
        first_id: int | None = None
        for finding in items:
            single = {
                "event": payload["event"],
                "body": payload["body"] if first_id is None else "",
                "comments": [_build_inline_comment(finding)],
            }
            review_id = self._post_review(client, single)
            if review_id is None:
                log.warning(
                    "Gitea: skipped inline comment %s:%d",
                    finding.path, finding.line,
                )
            elif first_id is None:
                first_id = review_id
        return first_id

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


def _reconcile_labels(current: list[str], labels: list[str]) -> list[str]:
    """Human labels (no managed prefix) survive; managed ones are replaced."""
    human = [n for n in current if not n.startswith(MANAGED_PREFIX)]
    return human + [n for n in labels if n not in human]


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

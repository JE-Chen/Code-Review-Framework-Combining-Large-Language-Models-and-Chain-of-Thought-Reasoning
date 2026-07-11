"""Issue-tracker strategy layer — read, create, comment, open fix PRs / MRs.

The repository-scoped counterpart of the PR-scoped platform adapters:
everything the auto-file / auto-fix features need from an issue tracker
goes through the :class:`IssueTracker` protocol, with one concrete
strategy per platform (:class:`GitHubIssueTracker`,
:class:`GitLabIssueTracker`, :class:`GiteaIssueTracker`) and a single
factory entry point (:func:`create_issue_tracker`) — the same Strategy +
Factory shape as the backends. Adding a platform means one class + one
factory branch.

``open_pull_request`` is the platform-neutral verb: it opens a pull
request on GitHub and a merge request on GitLab (draft rendered as the
``Draft:`` title prefix). All calls are authenticated HTTPS; the GitHub
strategy reuses :func:`prthinker.github_api._client` for the canonical
header/timeout set.

Runner-safe: ``httpx`` + stdlib only.
"""

from __future__ import annotations

import logging
import urllib.parse
from dataclasses import dataclass
from typing import Protocol

import httpx

from prthinker.github_api import _client, paginate

log = logging.getLogger(__name__)

_MAX_PAGE_SIZE = 100
_DEFAULT_LIST_LIMIT = 50
_GITLAB_DEFAULT_URL = "https://gitlab.com/api/v4"
_GITEA_DEFAULT_URL = "https://gitea.com/api/v1"
_GITEA_LABEL_COLOR = "ededed"
_USER_AGENT = "prthinker/0.1"


@dataclass(frozen=True)
class Issue:
    """The slice of a tracker issue the auto-file / auto-fix features use.

    ``number`` is GitHub's issue number or GitLab's per-project ``iid``.
    """

    number: int
    title: str
    body: str
    labels: tuple[str, ...] = ()
    html_url: str = ""


class IssueTracker(Protocol):
    """What a platform must offer to host auto-filed issues and fix PRs."""

    def fetch_issue(self, number: int) -> Issue:
        """Return one issue by number / iid."""

    def list_open_issues(
        self, *, label: str = "", limit: int = _DEFAULT_LIST_LIMIT
    ) -> list[Issue]:
        """Return up to ``limit`` open issues, optionally filtered by label."""

    def create_issue(
        self, *, title: str, body: str, labels: tuple[str, ...] = ()
    ) -> Issue:
        """Open a new issue and return it."""

    def add_issue_comment(self, number: int, body: str) -> int:
        """Post a comment / note on an issue; return its id."""

    def default_branch(self) -> str:
        """Return the repository's default branch name."""

    def open_pull_request(
        self, *, title: str, body: str, head: str, base: str, draft: bool = True
    ) -> tuple[int, str]:
        """Open a PR (GitHub) / MR (GitLab); return ``(number, html_url)``."""


def _validated(repo: str, token: str) -> None:
    """Reject unusable tracker coordinates at construction time."""
    if "/" not in repo:
        raise ValueError(f"tracker repo must be 'owner/name', got {repo!r}")
    if not token:
        raise ValueError("tracker token is required")


@dataclass(frozen=True)
class GitHubIssueTracker:
    """GitHub Issues / Pulls strategy for :class:`IssueTracker`."""

    repo: str
    token: str

    def __post_init__(self) -> None:
        _validated(self.repo, self.token)

    @staticmethod
    def _to_issue(row: dict) -> Issue:
        return Issue(
            number=int(row["number"]),
            title=str(row.get("title") or ""),
            body=str(row.get("body") or ""),
            labels=tuple(str(label.get("name", "")) for label in row.get("labels", [])),
            html_url=str(row.get("html_url") or ""),
        )

    def fetch_issue(self, number: int) -> Issue:
        """Return one issue by number; reject pull requests.

        GitHub's issues endpoint also serves PRs; fixing a PR as if it
        were an issue would be nonsense, so those raise ``ValueError``.
        """
        with _client(self.token) as client:
            response = client.get(f"/repos/{self.repo}/issues/{number}")
            response.raise_for_status()
            row = response.json()
        if "pull_request" in row:
            raise ValueError(f"#{number} in {self.repo} is a pull request, not an issue")
        return self._to_issue(row)

    def list_open_issues(
        self, *, label: str = "", limit: int = _DEFAULT_LIST_LIMIT
    ) -> list[Issue]:
        """One page of open issues (GitHub caps a page at 100), PRs filtered."""
        limit = max(0, limit)
        params: dict[str, str | int] = {
            "state": "open", "per_page": min(max(limit, 1), _MAX_PAGE_SIZE)}
        if label:
            params["labels"] = label
        with _client(self.token) as client:
            response = client.get(f"/repos/{self.repo}/issues", params=params)
            response.raise_for_status()
            rows = response.json()
        issues = [self._to_issue(row) for row in rows if "pull_request" not in row]
        return issues[:limit]

    def create_issue(
        self, *, title: str, body: str, labels: tuple[str, ...] = ()
    ) -> Issue:
        """Open a new issue and return it."""
        payload: dict[str, object] = {"title": title, "body": body}
        if labels:
            payload["labels"] = list(labels)
        with _client(self.token) as client:
            response = client.post(f"/repos/{self.repo}/issues", json=payload)
            response.raise_for_status()
            return self._to_issue(response.json())

    def add_issue_comment(self, number: int, body: str) -> int:
        """Post a comment on an issue; return the new comment id."""
        with _client(self.token) as client:
            response = client.post(
                f"/repos/{self.repo}/issues/{number}/comments", json={"body": body})
            response.raise_for_status()
            return int(response.json()["id"])

    def default_branch(self) -> str:
        """Return the repository's default branch name."""
        with _client(self.token) as client:
            response = client.get(f"/repos/{self.repo}")
            response.raise_for_status()
            return str(response.json()["default_branch"])

    def open_pull_request(
        self, *, title: str, body: str, head: str, base: str, draft: bool = True
    ) -> tuple[int, str]:
        """Open a pull request and return ``(number, html_url)``."""
        payload = {
            "title": title, "body": body, "head": head, "base": base, "draft": draft}
        with _client(self.token) as client:
            response = client.post(f"/repos/{self.repo}/pulls", json=payload)
            response.raise_for_status()
            row = response.json()
            return int(row["number"]), str(row["html_url"])


def _gitlab_client(base_url: str, token: str) -> httpx.Client:
    """An authenticated client against one GitLab API root."""
    return httpx.Client(
        base_url=base_url.rstrip("/"),
        headers={"PRIVATE-TOKEN": token, "User-Agent": _USER_AGENT},
        timeout=30.0,
    )


@dataclass(frozen=True)
class GitLabIssueTracker:
    """GitLab Issues / Merge Requests strategy for :class:`IssueTracker`.

    ``repo`` is the project path (``group/project``) or numeric id; issue
    numbers are GitLab's per-project ``iid``. A draft merge request is
    expressed as the ``Draft:`` title prefix, matching
    :func:`prthinker.auto_fix.open_auto_fix_mr`.
    """

    repo: str
    token: str
    base_url: str = _GITLAB_DEFAULT_URL

    def __post_init__(self) -> None:
        _validated(self.repo, self.token)

    @property
    def _project(self) -> str:
        return urllib.parse.quote(str(self.repo), safe="")

    @staticmethod
    def _to_issue(row: dict) -> Issue:
        return Issue(
            number=int(row["iid"]),
            title=str(row.get("title") or ""),
            body=str(row.get("description") or ""),
            labels=tuple(str(label) for label in row.get("labels", [])),
            html_url=str(row.get("web_url") or ""),
        )

    def fetch_issue(self, number: int) -> Issue:
        """Return one issue by iid (GitLab serves MRs from a separate endpoint)."""
        with _gitlab_client(self.base_url, self.token) as client:
            response = client.get(f"/projects/{self._project}/issues/{number}")
            response.raise_for_status()
            return self._to_issue(response.json())

    def list_open_issues(
        self, *, label: str = "", limit: int = _DEFAULT_LIST_LIMIT
    ) -> list[Issue]:
        """One page of open issues (GitLab caps a page at 100)."""
        limit = max(0, limit)
        params: dict[str, str | int] = {
            "state": "opened", "per_page": min(max(limit, 1), _MAX_PAGE_SIZE)}
        if label:
            params["labels"] = label
        with _gitlab_client(self.base_url, self.token) as client:
            response = client.get(f"/projects/{self._project}/issues", params=params)
            response.raise_for_status()
            return [self._to_issue(row) for row in response.json()][:limit]

    def create_issue(
        self, *, title: str, body: str, labels: tuple[str, ...] = ()
    ) -> Issue:
        """Open a new issue and return it (labels are comma-joined)."""
        payload: dict[str, object] = {"title": title, "description": body}
        if labels:
            payload["labels"] = ",".join(labels)
        with _gitlab_client(self.base_url, self.token) as client:
            response = client.post(f"/projects/{self._project}/issues", json=payload)
            response.raise_for_status()
            return self._to_issue(response.json())

    def add_issue_comment(self, number: int, body: str) -> int:
        """Post a note on an issue; return the new note id."""
        with _gitlab_client(self.base_url, self.token) as client:
            response = client.post(
                f"/projects/{self._project}/issues/{number}/notes",
                json={"body": body})
            response.raise_for_status()
            return int(response.json()["id"])

    def default_branch(self) -> str:
        """Return the project's default branch name."""
        with _gitlab_client(self.base_url, self.token) as client:
            response = client.get(f"/projects/{self._project}")
            response.raise_for_status()
            return str(response.json()["default_branch"])

    def open_pull_request(
        self, *, title: str, body: str, head: str, base: str, draft: bool = True
    ) -> tuple[int, str]:
        """Open a merge request and return ``(iid, web_url)``."""
        payload = {
            "title": f"Draft: {title}" if draft else title,
            "description": body,
            "source_branch": head,
            "target_branch": base,
        }
        with _gitlab_client(self.base_url, self.token) as client:
            response = client.post(
                f"/projects/{self._project}/merge_requests", json=payload)
            response.raise_for_status()
            row = response.json()
            return int(row["iid"]), str(row["web_url"])


def _gitea_client(base_url: str, token: str) -> httpx.Client:
    """An authenticated client against one Gitea API root."""
    return httpx.Client(
        base_url=base_url.rstrip("/"),
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/json",
            "User-Agent": _USER_AGENT,
        },
        timeout=30.0,
    )


@dataclass(frozen=True)
class GiteaIssueTracker:
    """Gitea Issues / Pulls strategy for :class:`IssueTracker`.

    Gitea's issue API is GitHub-shaped with two deviations this class
    absorbs: ``CreateIssueOption.labels`` takes label *ids* rather than
    names, so names are resolved — and created when missing — through
    the repo labels endpoint first (best-effort: a resolution failure
    files the issue unlabelled); and ``POST /pulls`` has no ``draft``
    flag, so a draft is expressed as Gitea's ``WIP:`` title prefix.
    """

    repo: str
    token: str
    base_url: str = _GITEA_DEFAULT_URL

    def __post_init__(self) -> None:
        _validated(self.repo, self.token)

    @staticmethod
    def _to_issue(row: dict) -> Issue:
        return Issue(
            number=int(row["number"]),
            title=str(row.get("title") or ""),
            body=str(row.get("body") or ""),
            labels=tuple(str(label.get("name", "")) for label in row.get("labels") or []),
            html_url=str(row.get("html_url") or ""),
        )

    def fetch_issue(self, number: int) -> Issue:
        """Return one issue by number; reject pull requests.

        Gitea's issues endpoint shares the index space with PRs (a PR
        row carries a ``pull_request`` block); fixing a PR as if it were
        an issue would be nonsense, so those raise ``ValueError``.
        """
        with _gitea_client(self.base_url, self.token) as client:
            response = client.get(f"/repos/{self.repo}/issues/{number}")
            response.raise_for_status()
            row = response.json()
        if row.get("pull_request"):
            raise ValueError(f"#{number} in {self.repo} is a pull request, not an issue")
        return self._to_issue(row)

    def list_open_issues(
        self, *, label: str = "", limit: int = _DEFAULT_LIST_LIMIT
    ) -> list[Issue]:
        """One page of open issues (``type=issues`` keeps PRs out)."""
        limit = max(0, limit)
        params: dict[str, str | int] = {
            "state": "open", "type": "issues",
            "limit": min(max(limit, 1), _MAX_PAGE_SIZE)}
        if label:
            params["labels"] = label
        with _gitea_client(self.base_url, self.token) as client:
            response = client.get(f"/repos/{self.repo}/issues", params=params)
            response.raise_for_status()
            rows = response.json() or []
        # ``type=issues`` should exclude PRs; the row filter is a belt
        # for older Gitea versions that ignore the parameter.
        issues = [self._to_issue(row) for row in rows if not row.get("pull_request")]
        return issues[:limit]

    def create_issue(
        self, *, title: str, body: str, labels: tuple[str, ...] = ()
    ) -> Issue:
        """Open a new issue and return it (label names resolved to ids)."""
        payload: dict[str, object] = {"title": title, "body": body}
        with _gitea_client(self.base_url, self.token) as client:
            if labels:
                label_ids = self._label_ids(client, labels)
                if label_ids:
                    payload["labels"] = label_ids
            response = client.post(f"/repos/{self.repo}/issues", json=payload)
            response.raise_for_status()
            return self._to_issue(response.json())

    def _label_ids(
        self, client: httpx.Client, labels: tuple[str, ...]
    ) -> list[int]:
        """Resolve label names to repo label ids, creating missing ones.

        Best-effort: a failure to list the repo labels files the issue
        unlabelled rather than failing the create.
        """
        try:
            existing = {
                str(row.get("name") or ""): int(row["id"])
                for row in paginate(
                    client, f"/repos/{self.repo}/labels",
                    per_page=_MAX_PAGE_SIZE, size_param="limit",
                )
            }
        except httpx.HTTPError as exc:
            log.warning(
                "Gitea: could not list repo labels (%s); "
                "creating the issue unlabelled", exc)
            return []
        ids: list[int] = []
        for name in labels:
            label_id = existing.get(name) or self._create_label(client, name)
            if label_id is not None:
                ids.append(label_id)
        return ids

    def _create_label(self, client: httpx.Client, name: str) -> int | None:
        """Create one repo label; None (and a log) on failure."""
        response = client.post(
            f"/repos/{self.repo}/labels",
            json={"name": name, "color": _GITEA_LABEL_COLOR})
        if response.status_code >= 400:
            log.warning(
                "Gitea: could not create label %r (%d); skipping it",
                name, response.status_code)
            return None
        return int(response.json()["id"])

    def add_issue_comment(self, number: int, body: str) -> int:
        """Post a comment on an issue; return the new comment id."""
        with _gitea_client(self.base_url, self.token) as client:
            response = client.post(
                f"/repos/{self.repo}/issues/{number}/comments",
                json={"body": body})
            response.raise_for_status()
            return int(response.json()["id"])

    def default_branch(self) -> str:
        """Return the repository's default branch name."""
        with _gitea_client(self.base_url, self.token) as client:
            response = client.get(f"/repos/{self.repo}")
            response.raise_for_status()
            return str(response.json()["default_branch"])

    def open_pull_request(
        self, *, title: str, body: str, head: str, base: str, draft: bool = True
    ) -> tuple[int, str]:
        """Open a pull request and return ``(number, html_url)``.

        Gitea has no ``draft`` field on the create-PR payload; the WIP
        title prefix (Gitea's default draft convention) stands in.
        """
        payload = {
            "title": f"WIP: {title}" if draft else title,
            "body": body, "head": head, "base": base}
        with _gitea_client(self.base_url, self.token) as client:
            response = client.post(f"/repos/{self.repo}/pulls", json=payload)
            response.raise_for_status()
            row = response.json()
            return int(row["number"]), str(row["html_url"])


def create_issue_tracker(
    kind: str, *, repo: str, token: str, base_url: str = ""
) -> IssueTracker:
    """Factory: the issue-tracker strategy for a platform kind.

    ``kind`` accepts the same values as ``PlatformKind`` (which is a str
    enum, so the enum members themselves also work). ``base_url`` applies
    to GitLab and Gitea (self-hosted instances); empty keeps the public
    cloud default of each.
    """
    if kind == "github":
        return GitHubIssueTracker(repo=repo, token=token)
    if kind == "gitlab":
        return GitLabIssueTracker(
            repo=repo, token=token, base_url=base_url or _GITLAB_DEFAULT_URL)
    if kind == "gitea":
        return GiteaIssueTracker(
            repo=repo, token=token, base_url=base_url or _GITEA_DEFAULT_URL)
    raise ValueError(f"no issue-tracker support for platform {kind!r}")


__all__ = [
    "GitHubIssueTracker",
    "GitLabIssueTracker",
    "GiteaIssueTracker",
    "Issue",
    "IssueTracker",
    "create_issue_tracker",
]

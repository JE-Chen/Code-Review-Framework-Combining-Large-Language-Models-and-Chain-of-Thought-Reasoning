"""Tests for the issue-tracker strategies (:mod:`prthinker.issue_tracker`)."""

from __future__ import annotations

import pytest

from prthinker import issue_tracker
from prthinker.issue_tracker import (
    GiteaIssueTracker,
    GitHubIssueTracker,
    GitLabIssueTracker,
    Issue,
    create_issue_tracker,
)

_GH = GitHubIssueTracker(repo="octo/demo", token="tok")  # nosec B106 - test fixture token, not a credential
_GL = GitLabIssueTracker(repo="group/demo", token="tok")  # nosec B106 - test fixture token, not a credential
_GT = GiteaIssueTracker(repo="tea/demo", token="tok")  # nosec B106 - test fixture token, not a credential


class _Resp:
    """Minimal httpx.Response stand-in with a programmable status."""

    def __init__(self, json_data=None, *, status: int = 200) -> None:
        self.status_code = status
        self._json = json_data

    def json(self):
        return self._json

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class _ScriptedClient:
    """Context-managed client replaying one response and recording the call."""

    def __init__(self, response: _Resp) -> None:
        self._response = response
        self.calls: list[tuple[str, str, dict]] = []

    def __enter__(self) -> "_ScriptedClient":
        return self

    def __exit__(self, *exc) -> bool:
        return False

    def get(self, url: str, **kw) -> _Resp:
        self.calls.append(("GET", url, kw))
        return self._response

    def post(self, url: str, **kw) -> _Resp:
        self.calls.append(("POST", url, kw))
        return self._response


def _patch_github(monkeypatch, response: _Resp) -> _ScriptedClient:
    client = _ScriptedClient(response)
    monkeypatch.setattr(issue_tracker, "_client", lambda _token: client)
    return client


def _patch_gitlab(monkeypatch, response: _Resp) -> _ScriptedClient:
    client = _ScriptedClient(response)
    monkeypatch.setattr(
        issue_tracker, "_gitlab_client", lambda _url, _token: client)
    return client


def _gh_row(number: int = 7, **extra) -> dict:
    row = {
        "number": number,
        "title": "boom",
        "body": "it crashes",
        "labels": [{"name": "bug"}],
        "html_url": f"https://github.com/octo/demo/issues/{number}",
    }
    row.update(extra)
    return row


def _gl_row(iid: int = 7, **extra) -> dict:
    row = {
        "iid": iid,
        "title": "boom",
        "description": "it crashes",
        "labels": ["bug"],
        "web_url": f"https://gitlab.com/group/demo/-/issues/{iid}",
    }
    row.update(extra)
    return row


class TestConstruction:
    def test_rejects_repo_without_owner(self):
        with pytest.raises(ValueError, match="owner/name"):
            GitHubIssueTracker(repo="demo", token="tok")  # nosec B106 - test fixture token, not a credential

    def test_rejects_empty_token(self):
        with pytest.raises(ValueError, match="token"):
            GitLabIssueTracker(repo="group/demo", token="")  # nosec B106 - test fixture token, not a credential


class TestFactory:
    def test_github_kind(self):
        tracker = create_issue_tracker("github", repo="o/r", token="t")  # nosec B106 - test fixture token, not a credential
        assert isinstance(tracker, GitHubIssueTracker)

    def test_gitlab_kind_with_default_and_custom_url(self):
        tracker = create_issue_tracker("gitlab", repo="g/p", token="t")  # nosec B106 - test fixture token, not a credential
        assert isinstance(tracker, GitLabIssueTracker)
        assert tracker.base_url == "https://gitlab.com/api/v4"
        hosted = create_issue_tracker(
            "gitlab", repo="g/p", token="t", base_url="https://git.corp/api/v4")  # nosec B106 - test fixture token, not a credential
        assert hosted.base_url == "https://git.corp/api/v4"

    def test_gitea_kind_with_default_and_custom_url(self):
        tracker = create_issue_tracker("gitea", repo="o/r", token="t")  # nosec B106 - test fixture token, not a credential
        assert isinstance(tracker, GiteaIssueTracker)
        assert tracker.base_url == "https://gitea.com/api/v1"
        hosted = create_issue_tracker(
            "gitea", repo="o/r", token="t", base_url="https://tea.corp/api/v1")  # nosec B106 - test fixture token, not a credential
        assert hosted.base_url == "https://tea.corp/api/v1"

    def test_platform_kind_enum_values_work(self):
        from prthinker.platforms import PlatformKind

        tracker = create_issue_tracker(
            PlatformKind.GITLAB, repo="g/p", token="t")  # nosec B106 - test fixture token, not a credential
        assert isinstance(tracker, GitLabIssueTracker)

    def test_unknown_kind_raises(self):
        with pytest.raises(ValueError, match="bitbucket"):
            create_issue_tracker("bitbucket", repo="o/r", token="t")  # nosec B106 - test fixture token, not a credential


class TestGitHubFetchIssue:
    def test_happy_path_maps_fields(self, monkeypatch):
        client = _patch_github(monkeypatch, _Resp(_gh_row()))
        issue = _GH.fetch_issue(7)
        assert issue == Issue(
            7, "boom", "it crashes", ("bug",),
            "https://github.com/octo/demo/issues/7")
        assert client.calls[0][:2] == ("GET", "/repos/octo/demo/issues/7")

    def test_null_body_becomes_empty_string(self, monkeypatch):
        _patch_github(monkeypatch, _Resp(_gh_row(body=None)))
        assert _GH.fetch_issue(7).body == ""

    def test_rejects_pull_requests(self, monkeypatch):
        _patch_github(monkeypatch, _Resp(_gh_row(pull_request={"url": "x"})))
        with pytest.raises(ValueError, match="pull request"):
            _GH.fetch_issue(7)

    def test_http_error_propagates(self, monkeypatch):
        _patch_github(monkeypatch, _Resp(status=404))
        with pytest.raises(RuntimeError, match="404"):
            _GH.fetch_issue(7)


class TestGitHubListOpenIssues:
    def test_filters_out_pull_requests(self, monkeypatch):
        rows = [_gh_row(1), _gh_row(2, pull_request={"url": "x"}), _gh_row(3)]
        _patch_github(monkeypatch, _Resp(rows))
        assert [issue.number for issue in _GH.list_open_issues()] == [1, 3]

    def test_passes_label_filter_and_state(self, monkeypatch):
        client = _patch_github(monkeypatch, _Resp([]))
        _GH.list_open_issues(label="bug", limit=5)
        params = client.calls[0][2]["params"]
        assert params == {"state": "open", "per_page": 5, "labels": "bug"}

    def test_limit_truncates_results(self, monkeypatch):
        _patch_github(monkeypatch, _Resp([_gh_row(n) for n in (1, 2, 3)]))
        assert len(_GH.list_open_issues(limit=2)) == 2

    def test_limit_zero_returns_empty(self, monkeypatch):
        _patch_github(monkeypatch, _Resp([_gh_row(1)]))
        assert _GH.list_open_issues(limit=0) == []

    def test_page_size_is_capped_at_api_maximum(self, monkeypatch):
        client = _patch_github(monkeypatch, _Resp([]))
        _GH.list_open_issues(limit=500)
        assert client.calls[0][2]["params"]["per_page"] == 100


class TestGitHubWrites:
    def test_create_issue_posts_payload_with_labels(self, monkeypatch):
        client = _patch_github(monkeypatch, _Resp(_gh_row()))
        created = _GH.create_issue(title="t", body="b", labels=("prthinker",))
        assert created.number == 7
        method, url, kw = client.calls[0]
        assert (method, url) == ("POST", "/repos/octo/demo/issues")
        assert kw["json"] == {"title": "t", "body": "b", "labels": ["prthinker"]}

    def test_create_issue_omits_labels_key_when_none_given(self, monkeypatch):
        client = _patch_github(monkeypatch, _Resp(_gh_row()))
        _GH.create_issue(title="t", body="b")
        assert "labels" not in client.calls[0][2]["json"]

    def test_add_issue_comment_returns_id(self, monkeypatch):
        client = _patch_github(monkeypatch, _Resp({"id": 42}))
        assert _GH.add_issue_comment(7, "hello") == 42
        method, url, kw = client.calls[0]
        assert (method, url) == ("POST", "/repos/octo/demo/issues/7/comments")
        assert kw["json"] == {"body": "hello"}

    def test_default_branch(self, monkeypatch):
        client = _patch_github(monkeypatch, _Resp({"default_branch": "main"}))
        assert _GH.default_branch() == "main"
        assert client.calls[0][:2] == ("GET", "/repos/octo/demo")

    def test_open_pull_request_returns_number_and_url(self, monkeypatch):
        client = _patch_github(
            monkeypatch, _Resp({"number": 12, "html_url": "https://x/pr/12"}))
        number, url = _GH.open_pull_request(
            title="fix", body="Fixes #7", head="issue-fix/7",
            base="main", draft=True)
        assert (number, url) == (12, "https://x/pr/12")
        assert client.calls[0][2]["json"] == {
            "title": "fix", "body": "Fixes #7", "head": "issue-fix/7",
            "base": "main", "draft": True}


class TestGitLab:
    def test_fetch_issue_maps_iid_and_description(self, monkeypatch):
        client = _patch_gitlab(monkeypatch, _Resp(_gl_row()))
        issue = _GL.fetch_issue(7)
        assert issue == Issue(
            7, "boom", "it crashes", ("bug",),
            "https://gitlab.com/group/demo/-/issues/7")
        assert client.calls[0][:2] == ("GET", "/projects/group%2Fdemo/issues/7")

    def test_fetch_issue_null_description(self, monkeypatch):
        _patch_gitlab(monkeypatch, _Resp(_gl_row(description=None)))
        assert _GL.fetch_issue(7).body == ""

    def test_list_open_issues_uses_opened_state(self, monkeypatch):
        client = _patch_gitlab(monkeypatch, _Resp([_gl_row(1), _gl_row(2)]))
        issues = _GL.list_open_issues(label="bug", limit=1)
        assert [issue.number for issue in issues] == [1]
        params = client.calls[0][2]["params"]
        assert params == {"state": "opened", "per_page": 1, "labels": "bug"}

    def test_create_issue_joins_labels_and_uses_description(self, monkeypatch):
        client = _patch_gitlab(monkeypatch, _Resp(_gl_row()))
        _GL.create_issue(title="t", body="b", labels=("a", "b"))
        method, url, kw = client.calls[0]
        assert (method, url) == ("POST", "/projects/group%2Fdemo/issues")
        assert kw["json"] == {"title": "t", "description": "b", "labels": "a,b"}

    def test_add_issue_comment_posts_a_note(self, monkeypatch):
        client = _patch_gitlab(monkeypatch, _Resp({"id": 99}))
        assert _GL.add_issue_comment(7, "hello") == 99
        assert client.calls[0][:2] == (
            "POST", "/projects/group%2Fdemo/issues/7/notes")

    def test_default_branch(self, monkeypatch):
        _patch_gitlab(monkeypatch, _Resp({"default_branch": "main"}))
        assert _GL.default_branch() == "main"

    def test_open_merge_request_draft_title_prefix(self, monkeypatch):
        client = _patch_gitlab(
            monkeypatch, _Resp({"iid": 12, "web_url": "https://x/mr/12"}))
        number, url = _GL.open_pull_request(
            title="fix", body="Fixes #7", head="issue-fix/7",
            base="main", draft=True)
        assert (number, url) == (12, "https://x/mr/12")
        assert client.calls[0][2]["json"] == {
            "title": "Draft: fix", "description": "Fixes #7",
            "source_branch": "issue-fix/7", "target_branch": "main"}

    def test_open_merge_request_non_draft_keeps_title(self, monkeypatch):
        client = _patch_gitlab(
            monkeypatch, _Resp({"iid": 12, "web_url": "https://x/mr/12"}))
        _GL.open_pull_request(
            title="fix", body="b", head="h", base="main", draft=False)
        assert client.calls[0][2]["json"]["title"] == "fix"

    def test_http_error_propagates(self, monkeypatch):
        _patch_gitlab(monkeypatch, _Resp(status=401))
        with pytest.raises(RuntimeError, match="401"):
            _GL.default_branch()


class _HttpxErrResp(_Resp):
    """Response whose raise_for_status raises a real httpx error.

    The Gitea tracker's label resolution catches ``httpx.HTTPError``
    specifically, so the fail-open tests need the genuine exception
    type instead of this file's RuntimeError stand-in.
    """

    def raise_for_status(self) -> None:
        import httpx

        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                f"HTTP {self.status_code}", request=None, response=None  # type: ignore[arg-type]
            )


class _RoutedClient:
    """Scripted client routing ``(method, url)`` to canned responses.

    Unlike ``_ScriptedClient`` above, several endpoints can be scripted
    at once (the Gitea create-issue flow touches labels + issues).
    Unscripted GETs return an empty list so pagination terminates.
    """

    def __init__(self, routes: dict[tuple[str, str], object]) -> None:
        self._routes = routes
        self.calls: list[tuple[str, str, dict]] = []

    def __enter__(self) -> "_RoutedClient":
        return self

    def __exit__(self, *exc) -> bool:
        return False

    def _respond(self, method: str, url: str, **kw) -> _Resp:
        self.calls.append((method, url, kw))
        hit = self._routes.get((method, url))
        if isinstance(hit, list):
            return hit.pop(0) if hit else _Resp([])
        return hit if hit is not None else _Resp([])

    def get(self, url: str, **kw) -> _Resp:
        return self._respond("GET", url, **kw)

    def post(self, url: str, **kw) -> _Resp:
        return self._respond("POST", url, **kw)


def _patch_gitea(monkeypatch, routes: dict[tuple[str, str], object]) -> _RoutedClient:
    client = _RoutedClient(routes)
    monkeypatch.setattr(
        issue_tracker, "_gitea_client", lambda _url, _token: client)
    return client


def _gt_row(number: int = 7, **extra) -> dict:
    row = {
        "number": number,
        "title": "boom",
        "body": "it crashes",
        "labels": [{"name": "bug"}],
        "html_url": f"https://gitea.com/tea/demo/issues/{number}",
    }
    row.update(extra)
    return row


class TestGiteaReads:
    def test_fetch_issue_maps_fields(self, monkeypatch):
        client = _patch_gitea(
            monkeypatch, {("GET", "/repos/tea/demo/issues/7"): _Resp(_gt_row())})
        issue = _GT.fetch_issue(7)
        assert issue == Issue(
            7, "boom", "it crashes", ("bug",),
            "https://gitea.com/tea/demo/issues/7")
        assert client.calls[0][:2] == ("GET", "/repos/tea/demo/issues/7")

    def test_fetch_issue_null_body_and_labels(self, monkeypatch):
        _patch_gitea(monkeypatch, {
            ("GET", "/repos/tea/demo/issues/7"): _Resp(
                _gt_row(body=None, labels=None)),
        })
        issue = _GT.fetch_issue(7)
        assert issue.body == ""
        assert issue.labels == ()

    def test_fetch_issue_rejects_pull_requests(self, monkeypatch):
        _patch_gitea(monkeypatch, {
            ("GET", "/repos/tea/demo/issues/7"): _Resp(
                _gt_row(pull_request={"merged": False})),
        })
        with pytest.raises(ValueError, match="pull request"):
            _GT.fetch_issue(7)

    def test_list_open_issues_params_and_pr_filter(self, monkeypatch):
        rows = [_gt_row(1), _gt_row(2, pull_request={"merged": True}), _gt_row(3)]
        client = _patch_gitea(
            monkeypatch, {("GET", "/repos/tea/demo/issues"): _Resp(rows)})
        issues = _GT.list_open_issues(label="bug", limit=5)
        assert [issue.number for issue in issues] == [1, 3]
        params = client.calls[0][2]["params"]
        assert params == {
            "state": "open", "type": "issues", "limit": 5, "labels": "bug"}

    def test_list_open_issues_limit_zero_and_page_cap(self, monkeypatch):
        client = _patch_gitea(
            monkeypatch, {("GET", "/repos/tea/demo/issues"): _Resp([_gt_row(1)])})
        assert _GT.list_open_issues(limit=0) == []
        _GT.list_open_issues(limit=500)
        assert client.calls[-1][2]["params"]["limit"] == 100

    def test_default_branch(self, monkeypatch):
        client = _patch_gitea(
            monkeypatch,
            {("GET", "/repos/tea/demo"): _Resp({"default_branch": "main"})})
        assert _GT.default_branch() == "main"
        assert client.calls[0][:2] == ("GET", "/repos/tea/demo")


class TestGiteaCreateIssue:
    def test_labels_resolved_to_existing_ids(self, monkeypatch):
        client = _patch_gitea(monkeypatch, {
            ("GET", "/repos/tea/demo/labels"): _Resp(
                [{"id": 3, "name": "prthinker"}]),
            ("POST", "/repos/tea/demo/issues"): _Resp(_gt_row()),
        })
        created = _GT.create_issue(title="t", body="b", labels=("prthinker",))
        assert created.number == 7
        post = next(c for c in client.calls
                    if c[:2] == ("POST", "/repos/tea/demo/issues"))
        # Gitea's CreateIssueOption takes label ids, not names.
        assert post[2]["json"] == {"title": "t", "body": "b", "labels": [3]}

    def test_missing_label_is_created_first(self, monkeypatch):
        client = _patch_gitea(monkeypatch, {
            ("GET", "/repos/tea/demo/labels"): _Resp([]),
            ("POST", "/repos/tea/demo/labels"): _Resp({"id": 8}, status=201),
            ("POST", "/repos/tea/demo/issues"): _Resp(_gt_row()),
        })
        _GT.create_issue(title="t", body="b", labels=("prthinker",))
        label_post = next(c for c in client.calls
                          if c[:2] == ("POST", "/repos/tea/demo/labels"))
        assert label_post[2]["json"]["name"] == "prthinker"
        issue_post = next(c for c in client.calls
                          if c[:2] == ("POST", "/repos/tea/demo/issues"))
        assert issue_post[2]["json"]["labels"] == [8]

    def test_label_listing_failure_files_unlabelled(self, monkeypatch):
        client = _patch_gitea(monkeypatch, {
            ("GET", "/repos/tea/demo/labels"): _HttpxErrResp(status=500),
            ("POST", "/repos/tea/demo/issues"): _Resp(_gt_row()),
        })
        created = _GT.create_issue(title="t", body="b", labels=("prthinker",))
        assert created.number == 7  # the create still went through
        issue_post = next(c for c in client.calls
                          if c[:2] == ("POST", "/repos/tea/demo/issues"))
        assert "labels" not in issue_post[2]["json"]

    def test_failed_label_create_is_skipped(self, monkeypatch):
        client = _patch_gitea(monkeypatch, {
            ("GET", "/repos/tea/demo/labels"): _Resp(
                [{"id": 3, "name": "known"}]),
            ("POST", "/repos/tea/demo/labels"): _Resp({}, status=403),
            ("POST", "/repos/tea/demo/issues"): _Resp(_gt_row()),
        })
        _GT.create_issue(title="t", body="b", labels=("known", "forbidden"))
        issue_post = next(c for c in client.calls
                          if c[:2] == ("POST", "/repos/tea/demo/issues"))
        assert issue_post[2]["json"]["labels"] == [3]  # only the resolvable one

    def test_no_labels_omits_labels_key(self, monkeypatch):
        client = _patch_gitea(monkeypatch, {
            ("POST", "/repos/tea/demo/issues"): _Resp(_gt_row()),
        })
        _GT.create_issue(title="t", body="b")
        assert client.calls[0][:2] == ("POST", "/repos/tea/demo/issues")
        assert "labels" not in client.calls[0][2]["json"]


class TestGiteaWrites:
    def test_add_issue_comment_returns_id(self, monkeypatch):
        client = _patch_gitea(monkeypatch, {
            ("POST", "/repos/tea/demo/issues/7/comments"): _Resp({"id": 42}),
        })
        assert _GT.add_issue_comment(7, "hello") == 42
        assert client.calls[0][2]["json"] == {"body": "hello"}

    def test_open_pull_request_draft_wip_prefix(self, monkeypatch):
        client = _patch_gitea(monkeypatch, {
            ("POST", "/repos/tea/demo/pulls"): _Resp(
                {"number": 12, "html_url": "https://x/pr/12"}),
        })
        number, url = _GT.open_pull_request(
            title="fix", body="Fixes #7", head="issue-fix/7",
            base="main", draft=True)
        assert (number, url) == (12, "https://x/pr/12")
        assert client.calls[0][2]["json"] == {
            "title": "WIP: fix", "body": "Fixes #7",
            "head": "issue-fix/7", "base": "main"}

    def test_open_pull_request_non_draft_keeps_title(self, monkeypatch):
        client = _patch_gitea(monkeypatch, {
            ("POST", "/repos/tea/demo/pulls"): _Resp(
                {"number": 12, "html_url": "https://x/pr/12"}),
        })
        _GT.open_pull_request(
            title="fix", body="b", head="h", base="main", draft=False)
        assert client.calls[0][2]["json"]["title"] == "fix"

    def test_http_error_propagates(self, monkeypatch):
        _patch_gitea(
            monkeypatch, {("GET", "/repos/tea/demo"): _Resp(status=401)})
        with pytest.raises(RuntimeError, match="401"):
            _GT.default_branch()

    def test_rejects_repo_without_owner(self):
        with pytest.raises(ValueError, match="owner/name"):
            GiteaIssueTracker(repo="demo", token="tok")  # nosec B106 - test fixture token, not a credential

"""Behaviour tests for :class:`GiteaAdapter`.

Every test substitutes a scripted ``httpx.Client`` stand-in (never a live
endpoint) so the diff fetch, comment upsert, inline-review POST, gate
status calls, and dialogue scan are exercised deterministically. Each
test asserts the request URLs, HTTP methods, and JSON payloads the
adapter produces.
"""

from __future__ import annotations

from typing import Any

import httpx
import pytest

from prthinker.checks import CheckResult
from prthinker.dialogue import AuthorReply
from prthinker.platforms.gitea import GiteaAdapter
from prthinker.schemas import InlineFinding

MARKER = "<!-- prthinker:summary -->"


class _Resp:
    """Minimal ``httpx.Response`` stand-in with text + JSON + status."""

    def __init__(
        self,
        *,
        json_data: Any = None,
        text: str = "",
        status_code: int = 200,
    ) -> None:
        self._json = json_data
        self.text = text
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                "error", request=None, response=None  # type: ignore[arg-type]
            )

    def json(self) -> Any:
        return self._json


class _ScriptedClient:
    """Scripted ``httpx.Client`` recording requests and replaying responses.

    ``responses`` maps ``(method, url)`` to either a single ``_Resp`` or a
    list of ``_Resp`` consumed in order (for paginated endpoints). Missing
    keys fall back to an empty-list 200 so unscripted pagination just
    terminates.
    """

    def __init__(
        self,
        responses: dict[tuple[str, str], Any] | None = None,
        **_kwargs: Any,
    ) -> None:
        self._responses = responses or {}
        self.requests: list[dict[str, Any]] = []

    def __enter__(self) -> "_ScriptedClient":
        return self

    def __exit__(self, *_exc: Any) -> None:
        return None

    def _record(self, method: str, url: str, **kwargs: Any) -> _Resp:
        self.requests.append({"method": method, "url": url, **kwargs})
        scripted = self._responses.get((method, url))
        if isinstance(scripted, list):
            return scripted.pop(0) if scripted else _Resp(json_data=[])
        if scripted is not None:
            return scripted
        return _Resp(json_data=[])

    def get(
        self, url: str, params: dict[str, Any] | None = None, **_kw: Any
    ) -> _Resp:
        return self._record("GET", url, params=params)

    def post(
        self, url: str, json: dict[str, Any] | None = None, **_kw: Any
    ) -> _Resp:
        return self._record("POST", url, json=json)

    def patch(
        self, url: str, json: dict[str, Any] | None = None, **_kw: Any
    ) -> _Resp:
        return self._record("PATCH", url, json=json)

    def put(
        self, url: str, json: dict[str, Any] | None = None, **_kw: Any
    ) -> _Resp:
        return self._record("PUT", url, json=json)


def _install(
    monkeypatch: pytest.MonkeyPatch,
    responses: dict[tuple[str, str], Any] | None = None,
) -> list[_ScriptedClient]:
    created: list[_ScriptedClient] = []

    def _factory(**kwargs: Any) -> _ScriptedClient:
        client = _ScriptedClient(responses, **kwargs)
        created.append(client)
        return client

    monkeypatch.setattr(httpx, "Client", _factory)
    return created


def _adapter() -> GiteaAdapter:
    return GiteaAdapter(  # nosec B106 - test fixture token, not a credential
        repo="o/r", token="t", pr_number=7, comment_marker=MARKER,
        base_url="https://gitea.example/api/v1",
    )


# ----- fetch_diff --------------------------------------------------------


def test_fetch_diff_returns_diff_body(monkeypatch: pytest.MonkeyPatch) -> None:
    diff = "diff --git a/x b/x\n+added\n"
    clients = _install(monkeypatch, {
        ("GET", "/repos/o/r/pulls/7.diff"): _Resp(text=diff),
    })
    assert _adapter().fetch_diff() == diff
    assert clients[0].requests[0] == {
        "method": "GET", "url": "/repos/o/r/pulls/7.diff", "params": None,
    }


def test_fetch_diff_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    _install(monkeypatch, {("GET", "/repos/o/r/pulls/7.diff"): _Resp(text="")})
    assert _adapter().fetch_diff() == ""


# ----- fetch_head_sha / fetch_base_branch / meta -------------------------


def test_fetch_head_sha(monkeypatch: pytest.MonkeyPatch) -> None:
    _install(monkeypatch, {
        ("GET", "/repos/o/r/pulls/7"): _Resp(
            json_data={"head": {"sha": "abc123"}, "base": {"ref": "main"}},
        ),
    })
    assert _adapter().fetch_head_sha() == "abc123"


def test_fetch_head_sha_missing_head(monkeypatch: pytest.MonkeyPatch) -> None:
    _install(monkeypatch, {
        ("GET", "/repos/o/r/pulls/7"): _Resp(json_data={}),
    })
    assert _adapter().fetch_head_sha() == ""


def test_fetch_base_branch(monkeypatch: pytest.MonkeyPatch) -> None:
    _install(monkeypatch, {
        ("GET", "/repos/o/r/pulls/7"): _Resp(json_data={"base": {"ref": "dev"}}),
    })
    assert _adapter().fetch_base_branch() == "dev"


def test_fetch_pr_meta(monkeypatch: pytest.MonkeyPatch) -> None:
    _install(monkeypatch, {
        ("GET", "/repos/o/r/pulls/7"): _Resp(
            json_data={"title": "Fix", "body": "why"},
        ),
    })
    assert _adapter().fetch_pr_meta() == ("Fix", "why")


def test_fetch_pr_meta_missing_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    _install(monkeypatch, {("GET", "/repos/o/r/pulls/7"): _Resp(json_data={})})
    assert _adapter().fetch_pr_meta() == ("", "")


# ----- upsert_summary_comment -------------------------------------------


def test_upsert_creates_when_no_marker(monkeypatch: pytest.MonkeyPatch) -> None:
    body = f"{MARKER}\nsummary"
    clients = _install(monkeypatch, {
        ("GET", "/repos/o/r/issues/7/comments"): _Resp(
            json_data=[{"id": 1, "body": "unrelated"}],
        ),
        ("POST", "/repos/o/r/issues/7/comments"): _Resp(json_data={"id": 99}),
    })
    assert _adapter().upsert_summary_comment(body) == 99
    methods = [(r["method"], r["url"]) for r in clients[0].requests]
    assert ("POST", "/repos/o/r/issues/7/comments") in methods
    post = next(r for r in clients[0].requests if r["method"] == "POST")
    assert post["json"] == {"body": body}


def test_upsert_updates_when_marker_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    body = f"{MARKER}\nnew"
    clients = _install(monkeypatch, {
        ("GET", "/repos/o/r/issues/7/comments"): _Resp(
            json_data=[{"id": 42, "body": f"{MARKER}\nold"}],
        ),
    })
    assert _adapter().upsert_summary_comment(body) == 42
    patch = next(r for r in clients[0].requests if r["method"] == "PATCH")
    assert patch["url"] == "/repos/o/r/issues/comments/42"
    assert patch["json"] == {"body": body}


def test_upsert_rejects_body_without_marker(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install(monkeypatch, {})
    with pytest.raises(ValueError, match="comment marker"):
        _adapter().upsert_summary_comment("no marker here")


def test_upsert_paginates_to_find_marker(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    body = f"{MARKER}\nupdate"
    full_page = [{"id": i, "body": "x"} for i in range(50)]
    clients = _install(monkeypatch, {
        ("GET", "/repos/o/r/issues/7/comments"): [
            _Resp(json_data=full_page),
            _Resp(json_data=[{"id": 500, "body": f"{MARKER} found"}]),
        ],
    })
    assert _adapter().upsert_summary_comment(body) == 500
    pages = [
        r["params"]["page"]
        for r in clients[0].requests if r["method"] == "GET"
    ]
    assert pages == [1, 2]


# ----- submit_inline_review ---------------------------------------------


def _finding(**kw: Any) -> InlineFinding:
    base = {"path": "a.py", "line": 3, "severity": "warning", "comment": "x"}
    base.update(kw)
    return InlineFinding(**base)


# ``a.py`` has new-side lines 1-4 inside one hunk — line 3 is postable.
_DIFF = (
    "diff --git a/a.py b/a.py\n"
    "--- a/a.py\n"
    "+++ b/a.py\n"
    "@@ -1,2 +1,4 @@\n"
    " one\n"
    "+two\n"
    "+three\n"
    " four\n"
)


def test_submit_inline_review_posts(monkeypatch: pytest.MonkeyPatch) -> None:
    clients = _install(monkeypatch, {
        ("POST", "/repos/o/r/pulls/7/reviews"): _Resp(json_data={"id": 314}),
    })
    findings = [_finding(comment="bug here", suggestion="fixed")]
    review_id = _adapter().submit_inline_review(
        findings, summary_body="please look", event="REQUEST_CHANGES",
        diff_text=_DIFF,
    )
    assert review_id == 314
    post = clients[0].requests[0]
    assert post["method"] == "POST"
    assert post["url"] == "/repos/o/r/pulls/7/reviews"
    payload = post["json"]
    assert payload["event"] == "REQUEST_CHANGES"
    assert payload["body"] == "please look"
    assert payload["comments"] == [{
        "path": "a.py",
        "new_position": 3,
        "body": "🟡 **suggestion:** bug here\n\n```suggestion\nfixed\n```",
    }]


def test_submit_inline_review_empty_returns_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clients = _install(monkeypatch, {})
    assert _adapter().submit_inline_review(
        [], summary_body=None, event="COMMENT",
    ) is None
    assert clients == []  # no client even constructed


def test_submit_inline_review_default_body_and_event(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clients = _install(monkeypatch, {
        ("POST", "/repos/o/r/pulls/7/reviews"): _Resp(json_data={"id": 1}),
    })
    _adapter().submit_inline_review(
        [_finding()], summary_body=None, event="WEIRD", diff_text=_DIFF,
    )
    payload = clients[0].requests[0]["json"]
    assert payload["event"] == "COMMENT"  # unknown event maps to COMMENT
    assert payload["body"] == "prthinker — inline findings"


def test_submit_inline_review_prefilters_off_diff(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clients = _install(monkeypatch, {
        ("POST", "/repos/o/r/pulls/7/reviews"): _Resp(json_data={"id": 2}),
    })
    _adapter().submit_inline_review(
        [_finding(line=3), _finding(line=99)],
        summary_body=None, event="COMMENT", diff_text=_DIFF,
    )
    comments = clients[0].requests[0]["json"]["comments"]
    assert [c["new_position"] for c in comments] == [3]  # 99 dropped


def test_submit_inline_review_all_off_diff_skips_post(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clients = _install(monkeypatch, {})
    assert _adapter().submit_inline_review(
        [_finding(line=99)], summary_body=None, event="COMMENT",
        diff_text=_DIFF,
    ) is None
    assert clients == []  # filtered to nothing before any POST


def test_submit_inline_review_fetches_diff_when_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clients = _install(monkeypatch, {
        ("GET", "/repos/o/r/pulls/7.diff"): _Resp(text=_DIFF),
        ("POST", "/repos/o/r/pulls/7/reviews"): _Resp(json_data={"id": 3}),
    })
    review_id = _adapter().submit_inline_review(
        [_finding(line=3), _finding(line=99)],
        summary_body=None, event="COMMENT",
    )
    assert review_id == 3
    # First client fetched the diff; second posted the filtered review.
    assert clients[0].requests[0]["url"] == "/repos/o/r/pulls/7.diff"
    comments = clients[1].requests[0]["json"]["comments"]
    assert [c["new_position"] for c in comments] == [3]


def test_submit_inline_review_fail_open_on_diff_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clients = _install(monkeypatch, {
        ("GET", "/repos/o/r/pulls/7.diff"): _Resp(text="", status_code=500),
        ("POST", "/repos/o/r/pulls/7/reviews"): _Resp(json_data={"id": 4}),
    })
    review_id = _adapter().submit_inline_review(
        [_finding(line=99)], summary_body=None, event="COMMENT",
    )
    assert review_id == 4  # unfiltered submission when the diff fetch fails
    assert len(clients[1].requests[0]["json"]["comments"]) == 1


def test_submit_inline_review_fail_open_on_hunkless_diff(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clients = _install(monkeypatch, {
        ("GET", "/repos/o/r/pulls/7.diff"): _Resp(text=""),
        ("POST", "/repos/o/r/pulls/7/reviews"): _Resp(json_data={"id": 5}),
    })
    review_id = _adapter().submit_inline_review(
        [_finding(line=99)], summary_body=None, event="COMMENT",
    )
    assert review_id == 5  # a hunkless diff must not drop every finding
    assert len(clients[1].requests[0]["json"]["comments"]) == 1


def test_submit_inline_review_falls_back_per_comment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Batch 422s; the fallback posts one review per comment: the first
    # succeeds (carrying the summary body), the second is skipped.
    clients = _install(monkeypatch, {
        ("POST", "/repos/o/r/pulls/7/reviews"): [
            _Resp(json_data={}, text="boom", status_code=422),
            _Resp(json_data={"id": 77}),
            _Resp(json_data={}, text="bad line", status_code=422),
        ],
    })
    review_id = _adapter().submit_inline_review(
        [_finding(line=2), _finding(line=3)],
        summary_body="summary", event="COMMENT", diff_text=_DIFF,
    )
    assert review_id == 77
    posts = clients[0].requests
    assert len(posts) == 3
    assert len(posts[0]["json"]["comments"]) == 2   # batch attempt
    assert posts[1]["json"]["body"] == "summary"    # first single carries body
    assert [c["new_position"] for c in posts[1]["json"]["comments"]] == [2]
    assert posts[2]["json"]["body"] == ""           # follow-ups stay quiet
    assert [c["new_position"] for c in posts[2]["json"]["comments"]] == [3]


def test_submit_inline_review_returns_none_when_all_fail(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clients = _install(monkeypatch, {
        ("POST", "/repos/o/r/pulls/7/reviews"): _Resp(
            json_data={}, text="boom", status_code=422,
        ),
    })
    # No raise: a 4xx on every attempt degrades to "no inline review".
    assert _adapter().submit_inline_review(
        [_finding()], summary_body=None, event="COMMENT", diff_text=_DIFF,
    ) is None
    assert len(clients[0].requests) == 2  # batch + one per-comment retry


# ----- open_gate / close_gate -------------------------------------------


def test_open_gate_hits_statuses(monkeypatch: pytest.MonkeyPatch) -> None:
    clients = _install(monkeypatch, {
        ("POST", "/repos/o/r/statuses/sha9"): _Resp(json_data={}),
    })
    handle = _adapter().open_gate("sha9")
    assert handle == {"sha": "sha9", "name": "prthinker"}
    req = clients[0].requests[0]
    assert req["method"] == "POST"
    assert req["url"] == "/repos/o/r/statuses/sha9"
    assert req["json"] == {"state": "pending", "context": "prthinker"}


def test_close_gate_success(monkeypatch: pytest.MonkeyPatch) -> None:
    clients = _install(monkeypatch, {
        ("POST", "/repos/o/r/statuses/sha9"): _Resp(json_data={}),
    })
    result = CheckResult(
        conclusion="success", title="No findings", summary="ok",
        error_count=0, warning_count=0, info_count=0,
    )
    _adapter().close_gate({"sha": "sha9", "name": "gate"}, result)
    req = clients[0].requests[0]
    assert req["json"] == {
        "state": "success", "context": "gate", "description": "No findings",
    }


def test_close_gate_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    clients = _install(monkeypatch, {
        ("POST", "/repos/o/r/statuses/sha9"): _Resp(json_data={}),
    })
    result = CheckResult(
        conclusion="failure", title="1 error", summary="bad",
        error_count=1, warning_count=0, info_count=0,
    )
    _adapter().close_gate({"sha": "sha9", "name": "prthinker"}, result)
    assert clients[0].requests[0]["json"]["state"] == "failure"


def test_close_gate_truncates_long_description(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clients = _install(monkeypatch, {
        ("POST", "/repos/o/r/statuses/sha9"): _Resp(json_data={}),
    })
    result = CheckResult(
        conclusion="failure", title="z" * 300, summary="s",
        error_count=1, warning_count=0, info_count=0,
    )
    _adapter().close_gate({"sha": "sha9", "name": "prthinker"}, result)
    assert len(clients[0].requests[0]["json"]["description"]) == 255


# ----- fetch_author_replies (dialogue) ----------------------------------


def test_replies_empty_when_no_marker(monkeypatch: pytest.MonkeyPatch) -> None:
    _install(monkeypatch, {
        ("GET", "/repos/o/r/issues/7/comments"): _Resp(
            json_data=[{"id": 1, "body": "hi", "user": {"login": "alice"}}],
        ),
    })
    assert _adapter().fetch_author_replies() == []


def test_replies_collected_after_marker(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install(monkeypatch, {
        ("GET", "/repos/o/r/issues/7/comments"): _Resp(json_data=[
            {"id": 1, "body": f"{MARKER} s", "user": {"login": "bot"},
             "created_at": "t0"},
            {"id": 2, "body": "wontfix", "user": {"login": "alice"},
             "created_at": "t1"},
            {"id": 3, "body": "bot followup", "user": {"login": "bot"}},
        ]),
    })
    replies = _adapter().fetch_author_replies()
    assert replies == [
        AuthorReply(author="alice", body="wontfix",
                    in_reply_to_id=1, created_at="t1"),
    ]


# ----- PR-object cache -----------------------------------------------------


def test_pr_object_fetched_once_across_meta_calls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clients = _install(monkeypatch, {
        ("GET", "/repos/o/r/pulls/7"): _Resp(json_data={
            "head": {"sha": "abc123"},
            "base": {"ref": "main"},
            "title": "Fix",
            "body": "why",
        }),
    })
    adapter = _adapter()
    assert adapter.fetch_head_sha() == "abc123"
    assert adapter.fetch_base_branch() == "main"
    assert adapter.fetch_pr_meta() == ("Fix", "why")
    total_gets = sum(
        1 for c in clients for r in c.requests if r["method"] == "GET"
    )
    assert total_gets == 1  # PR object cached after the first fetch


# ----- fetch_commit_messages / fetch_changed_paths -------------------------


def test_fetch_commit_messages_paginates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    page1 = [{"commit": {"message": f"feat: c{i}"}} for i in range(50)]
    page2 = [{"commit": {"message": "fix: last"}}, {"sha": "no-commit-key"}]
    clients = _install(monkeypatch, {
        ("GET", "/repos/o/r/pulls/7/commits"): [
            _Resp(json_data=page1), _Resp(json_data=page2),
        ],
    })
    msgs = _adapter().fetch_commit_messages()
    assert len(msgs) == 52
    assert msgs[0] == "feat: c0"
    assert msgs[50] == "fix: last"
    assert msgs[51] == ""  # missing commit key degrades to empty message
    params = [r["params"] for r in clients[0].requests]
    assert params[0] == {"limit": 50, "page": 1}
    assert params[1] == {"limit": 50, "page": 2}


def test_fetch_commit_messages_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    _install(monkeypatch, {
        ("GET", "/repos/o/r/pulls/7/commits"): _Resp(json_data=[]),
    })
    assert _adapter().fetch_commit_messages() == []


def test_fetch_changed_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    _install(monkeypatch, {
        ("GET", "/repos/o/r/pulls/7/files"): _Resp(json_data=[
            {"filename": "a.py"}, {"filename": "b.md"}, {"status": "weird"},
        ]),
    })
    # Entries without a filename are skipped rather than crashing.
    assert _adapter().fetch_changed_paths() == ["a.py", "b.md"]


def test_fetch_changed_paths_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    _install(monkeypatch, {
        ("GET", "/repos/o/r/pulls/7/files"): _Resp(json_data=[]),
    })
    assert _adapter().fetch_changed_paths() == []


# ----- set_labels ----------------------------------------------------------


def test_set_labels_reconciles_keeping_human_labels(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clients = _install(monkeypatch, {
        ("GET", "/repos/o/r/issues/7/labels"): _Resp(json_data=[
            {"name": "needs-qa"}, {"name": "prthinker/size-xl"},
        ]),
        ("POST", "/repos/o/r/labels"): _Resp(json_data={}, status_code=201),
        ("PUT", "/repos/o/r/issues/7/labels"): _Resp(json_data=[]),
    })
    _adapter().set_labels(["prthinker/size-s", "prthinker/clean"])
    put = next(r for r in clients[0].requests if r["method"] == "PUT")
    applied = put["json"]["labels"]
    assert "needs-qa" in applied                # human label preserved
    assert "prthinker/size-s" in applied        # new managed labels
    assert "prthinker/clean" in applied
    assert "prthinker/size-xl" not in applied   # stale managed label dropped


def test_set_labels_tolerates_existing_label_conflict(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clients = _install(monkeypatch, {
        ("GET", "/repos/o/r/issues/7/labels"): _Resp(json_data=[]),
        ("POST", "/repos/o/r/labels"): _Resp(json_data={}, status_code=409),
        ("PUT", "/repos/o/r/issues/7/labels"): _Resp(json_data=[]),
    })
    _adapter().set_labels(["prthinker/clean"])  # 409 create must not raise
    assert any(r["method"] == "PUT" for r in clients[0].requests)


def test_set_labels_invalidates_pr_cache(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clients = _install(monkeypatch, {
        ("GET", "/repos/o/r/pulls/7"): _Resp(json_data={"head": {"sha": "s1"}}),
        ("GET", "/repos/o/r/issues/7/labels"): _Resp(json_data=[]),
        ("POST", "/repos/o/r/labels"): _Resp(json_data={}, status_code=201),
        ("PUT", "/repos/o/r/issues/7/labels"): _Resp(json_data=[]),
    })
    adapter = _adapter()
    adapter.fetch_head_sha()
    adapter.set_labels(["prthinker/clean"])
    adapter.fetch_head_sha()
    pr_gets = [
        r for c in clients for r in c.requests
        if r["method"] == "GET" and r["url"] == "/repos/o/r/pulls/7"
    ]
    assert len(pr_gets) == 2  # cache invalidated by the label write


# ----- update_body_section -------------------------------------------------


def test_update_body_section_patches_pr_body(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clients = _install(monkeypatch, {
        ("GET", "/repos/o/r/pulls/7"): _Resp(json_data={"body": "desc"}),
        ("PATCH", "/repos/o/r/pulls/7"): _Resp(json_data={}),
    })
    _adapter().update_body_section("DIGEST")
    patch = next(r for r in clients[0].requests if r["method"] == "PATCH")
    assert patch["url"] == "/repos/o/r/pulls/7"
    assert "DIGEST" in patch["json"]["body"]
    assert patch["json"]["body"].startswith("desc")


def test_update_body_section_skips_when_unchanged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from prthinker.github_api import replace_marked_section

    existing = replace_marked_section("desc", "DIGEST")
    clients = _install(monkeypatch, {
        ("GET", "/repos/o/r/pulls/7"): _Resp(json_data={"body": existing}),
    })
    _adapter().update_body_section("DIGEST")
    assert all(r["method"] != "PATCH" for c in clients for r in c.requests)


def test_update_body_section_invalidates_pr_cache(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clients = _install(monkeypatch, {
        ("GET", "/repos/o/r/pulls/7"): _Resp(json_data={"body": "d"}),
        ("PATCH", "/repos/o/r/pulls/7"): _Resp(json_data={}),
    })
    adapter = _adapter()
    adapter.fetch_pr_meta()
    adapter.update_body_section("DIGEST")
    adapter.fetch_pr_meta()
    pr_gets = [
        r for c in clients for r in c.requests
        if r["method"] == "GET" and r["url"] == "/repos/o/r/pulls/7"
    ]
    # First meta fetch fills the cache (the body edit reuses it); the
    # write invalidates it, so the second meta call refetches.
    assert len(pr_gets) == 2


# ----- upsert_marked_comment ------------------------------------------------


def test_upsert_marked_comment_creates(monkeypatch: pytest.MonkeyPatch) -> None:
    marker = "<!-- prthinker:aux -->"
    clients = _install(monkeypatch, {
        ("GET", "/repos/o/r/issues/7/comments"): _Resp(
            json_data=[{"id": 1, "body": f"{MARKER} summary"}],
        ),
        ("POST", "/repos/o/r/issues/7/comments"): _Resp(json_data={"id": 55}),
    })
    body = f"{marker}\naux content"
    assert _adapter().upsert_marked_comment(body, marker=marker) == 55
    post = next(r for r in clients[0].requests if r["method"] == "POST")
    assert post["json"] == {"body": body}


def test_upsert_marked_comment_updates_by_its_own_marker(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    marker = "<!-- prthinker:aux -->"
    clients = _install(monkeypatch, {
        ("GET", "/repos/o/r/issues/7/comments"): _Resp(json_data=[
            {"id": 1, "body": f"{MARKER} summary"},   # summary must not match
            {"id": 9, "body": f"{marker} old aux"},
        ]),
    })
    body = f"{marker}\nnew aux"
    assert _adapter().upsert_marked_comment(body, marker=marker) == 9
    patch = next(r for r in clients[0].requests if r["method"] == "PATCH")
    assert patch["url"] == "/repos/o/r/issues/comments/9"


def test_upsert_marked_comment_rejects_missing_marker(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install(monkeypatch, {})
    with pytest.raises(ValueError, match="marker"):
        _adapter().upsert_marked_comment("nope", marker="<!-- aux -->")

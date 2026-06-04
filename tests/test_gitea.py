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


def test_submit_inline_review_posts(monkeypatch: pytest.MonkeyPatch) -> None:
    clients = _install(monkeypatch, {
        ("POST", "/repos/o/r/pulls/7/reviews"): _Resp(json_data={"id": 314}),
    })
    findings = [_finding(comment="bug here", suggestion="fixed")]
    review_id = _adapter().submit_inline_review(
        findings, summary_body="please look", event="REQUEST_CHANGES",
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
        "body": "🟡 **warning** — bug here\n\n```suggestion\nfixed\n```",
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
        [_finding()], summary_body=None, event="WEIRD",
    )
    payload = clients[0].requests[0]["json"]
    assert payload["event"] == "COMMENT"  # unknown event maps to COMMENT
    assert payload["body"] == "prthinker — inline findings"


def test_submit_inline_review_raises_on_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install(monkeypatch, {
        ("POST", "/repos/o/r/pulls/7/reviews"): _Resp(
            json_data={}, text="boom", status_code=422,
        ),
    })
    with pytest.raises(httpx.HTTPStatusError):
        _adapter().submit_inline_review(
            [_finding()], summary_body=None, event="COMMENT",
        )


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

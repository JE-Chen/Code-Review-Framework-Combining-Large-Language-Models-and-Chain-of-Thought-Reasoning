"""GitHub Enterprise ``base_url`` threading — every API call, full URL.

A custom API root (e.g. ``https://ghe.example/api/v3``) configured on the
:class:`GitHubAdapter` must reach EVERY GitHub call the adapter makes —
diff fetch, comment upsert (incl. multi-page reconcile), inline review
(incl. pre-filter and stale cleanup), labels, body edit, commit messages,
changed paths, check-run gate, and CI signals. Each test substitutes a
scripted ``httpx.Client`` stand-in that records the FULL request URL
(base_url + path) so a half-threaded default silently pointing at
``api.github.com`` fails loudly here.
"""

from __future__ import annotations

from typing import Any

import httpx
import pytest

from prthinker.checks import CheckResult
from prthinker.config import GitHubConfig
from prthinker.github_api import client_for
from prthinker.platforms.github import GitHubAdapter
from prthinker.schemas import InlineFinding

_GHE = "https://ghe.example/api/v3"
_PUBLIC = "https://api.github.com"
MARKER = "<!-- prthinker:summary -->"

# ``a.py`` adds new-side lines 1-2 — line 1 is postable inline.
_DIFF = (
    "diff --git a/a.py b/a.py\n"
    "--- a/a.py\n"
    "+++ b/a.py\n"
    "@@ -0,0 +1,2 @@\n"
    "+first\n"
    "+second\n"
)


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
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self) -> Any:
        return self._json


class _ScriptedClient:
    """Scripted client recording FULL request URLs (base_url + path).

    ``responses`` maps ``(method, path)`` to a ``_Resp`` or a FIFO list of
    them; unscripted requests fall back to an empty-list 200 so pagination
    terminates. The ``base_url`` constructor kwarg — exactly what the
    production ``_client`` passes to ``httpx.Client`` — is captured so the
    recorded URLs prove which host each call would really hit.
    """

    def __init__(
        self,
        responses: dict[tuple[str, str], Any],
        recorder: list[dict[str, Any]],
        **kwargs: Any,
    ) -> None:
        self.base_url = str(kwargs.get("base_url") or "")
        self._responses = responses
        self._recorder = recorder

    def __enter__(self) -> "_ScriptedClient":
        return self

    def __exit__(self, *_exc: Any) -> None:
        return None

    def _record(self, method: str, path: str, **kw: Any) -> _Resp:
        self._recorder.append(
            {"method": method, "url": f"{self.base_url}{path}", **kw}
        )
        scripted = self._responses.get((method, path))
        if isinstance(scripted, list):
            return scripted.pop(0) if scripted else _Resp(json_data=[])
        if scripted is not None:
            return scripted
        return _Resp(json_data=[])

    def get(self, path: str, **kw: Any) -> _Resp:
        return self._record("GET", path, params=kw.get("params"))

    def post(self, path: str, **kw: Any) -> _Resp:
        return self._record("POST", path, json=kw.get("json"))

    def patch(self, path: str, **kw: Any) -> _Resp:
        return self._record("PATCH", path, json=kw.get("json"))

    def put(self, path: str, **kw: Any) -> _Resp:
        return self._record("PUT", path, json=kw.get("json"))

    def delete(self, path: str, **kw: Any) -> _Resp:
        return self._record("DELETE", path, json=kw.get("json"))


def _install(
    monkeypatch: pytest.MonkeyPatch,
    responses: dict[tuple[str, str], Any] | None = None,
) -> tuple[list[dict[str, Any]], list[_ScriptedClient]]:
    recorder: list[dict[str, Any]] = []
    created: list[_ScriptedClient] = []

    def _factory(**kwargs: Any) -> _ScriptedClient:
        client = _ScriptedClient(responses or {}, recorder, **kwargs)
        created.append(client)
        return client

    monkeypatch.setattr(httpx, "Client", _factory)
    return recorder, created


def _adapter() -> GitHubAdapter:
    return GitHubAdapter(  # nosec B106 - test fixture token, not a credential
        repo="o/r", token="t", pr_number=7, comment_marker=MARKER,
        base_url=_GHE,
    )


def _assert_all_on_ghe(recorder: list[dict[str, Any]]) -> None:
    assert recorder, "expected at least one request"
    for request in recorder:
        assert request["url"].startswith(f"{_GHE}/"), request["url"]
        assert _PUBLIC not in request["url"], request["url"]


# ----- fetch_diff ----------------------------------------------------------


def test_fetch_diff_full_url_hits_custom_host(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recorder, _ = _install(monkeypatch, {
        ("GET", "/repos/o/r/pulls/7"): _Resp(text=_DIFF),
    })
    assert _adapter().fetch_diff() == _DIFF
    assert recorder[0]["url"] == f"{_GHE}/repos/o/r/pulls/7"
    _assert_all_on_ghe(recorder)


# ----- summary comment upsert (incl. multi-page reconcile) ------------------


def test_upsert_summary_comment_full_urls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recorder, _ = _install(monkeypatch, {
        ("GET", "/repos/o/r/issues/7/comments"): _Resp(json_data=[]),
        ("POST", "/repos/o/r/issues/7/comments"): _Resp(json_data={"id": 5}),
    })
    assert _adapter().upsert_summary_comment(f"{MARKER}\nbody") == 5
    urls = [r["url"] for r in recorder]
    assert f"{_GHE}/repos/o/r/issues/7/comments" in urls
    _assert_all_on_ghe(recorder)


def test_upsert_summary_comments_reconcile_full_urls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    existing = [{"id": i, "body": MARKER} for i in (10, 11, 12)]
    recorder, _ = _install(monkeypatch, {
        ("GET", "/repos/o/r/issues/7/comments"): _Resp(json_data=existing),
        ("PATCH", "/repos/o/r/issues/comments/10"): _Resp(json_data={}),
        ("PATCH", "/repos/o/r/issues/comments/11"): _Resp(json_data={}),
        ("DELETE", "/repos/o/r/issues/comments/12"): _Resp(status_code=204),
    })
    ids = _adapter().upsert_summary_comments([f"{MARKER}\nP1", f"{MARKER}\nP2"])
    assert ids == [10, 11]
    urls = [r["url"] for r in recorder]
    assert f"{_GHE}/repos/o/r/issues/comments/10" in urls
    assert f"{_GHE}/repos/o/r/issues/comments/12" in urls
    _assert_all_on_ghe(recorder)


def test_upsert_marked_comment_full_urls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    marker = "<!-- prthinker:aux -->"
    recorder, _ = _install(monkeypatch, {
        ("GET", "/repos/o/r/issues/7/comments"): _Resp(json_data=[]),
        ("POST", "/repos/o/r/issues/7/comments"): _Resp(json_data={"id": 8}),
    })
    assert _adapter().upsert_marked_comment(f"{marker}\naux", marker=marker) == 8
    _assert_all_on_ghe(recorder)


# ----- inline review (pre-filter + post + stale cleanup) --------------------


def test_submit_inline_review_full_urls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recorder, _ = _install(monkeypatch, {
        # Pre-filter diff download must hit the custom host too.
        ("GET", "/repos/o/r/pulls/7"): _Resp(text=_DIFF),
        ("POST", "/repos/o/r/pulls/7/reviews"): _Resp(json_data={"id": 9}),
        # Stale-cleanup review scan pages to empty (default empty resp).
    })
    finding = InlineFinding(path="a.py", line=1, comment="c")
    review_id = _adapter().submit_inline_review(
        [finding], summary_body="s", event="COMMENT",
    )
    assert review_id == 9
    urls = [r["url"] for r in recorder]
    assert urls[0] == f"{_GHE}/repos/o/r/pulls/7"            # pre-filter diff
    assert f"{_GHE}/repos/o/r/pulls/7/reviews" in urls       # post + cleanup
    _assert_all_on_ghe(recorder)


def test_inline_review_stale_cleanup_deletes_on_custom_host(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from prthinker.github_api import _INLINE_REVIEW_MARKER

    reviews = [{"id": 888, "body": _INLINE_REVIEW_MARKER},
               {"id": 999, "body": _INLINE_REVIEW_MARKER}]
    comments = [{"id": 5, "pull_request_review_id": 888}]
    recorder, _ = _install(monkeypatch, {
        ("POST", "/repos/o/r/pulls/7/reviews"): _Resp(json_data={"id": 999}),
        ("GET", "/repos/o/r/pulls/7/reviews"): _Resp(json_data=reviews),
        ("GET", "/repos/o/r/pulls/7/comments"): _Resp(json_data=comments),
        ("DELETE", "/repos/o/r/pulls/comments/5"): _Resp(status_code=204),
    })
    finding = InlineFinding(path="a.py", line=1, comment="c")
    _adapter().submit_inline_review(
        [finding], summary_body=None, event="COMMENT", diff_text=_DIFF,
    )
    urls = [r["url"] for r in recorder]
    assert f"{_GHE}/repos/o/r/pulls/comments/5" in urls
    _assert_all_on_ghe(recorder)


# ----- labels / body edit / commits / changed paths -------------------------


def test_set_labels_full_urls(monkeypatch: pytest.MonkeyPatch) -> None:
    recorder, _ = _install(monkeypatch, {
        ("GET", "/repos/o/r/issues/7"): _Resp(json_data={"labels": []}),
        ("POST", "/repos/o/r/labels"): _Resp(json_data={}, status_code=201),
        ("PUT", "/repos/o/r/issues/7/labels"): _Resp(json_data=[]),
    })
    _adapter().set_labels(["prthinker/clean"])
    urls = [r["url"] for r in recorder]
    assert f"{_GHE}/repos/o/r/issues/7/labels" in urls
    assert f"{_GHE}/repos/o/r/labels" in urls
    _assert_all_on_ghe(recorder)


def test_body_edit_commits_and_paths_full_urls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recorder, _ = _install(monkeypatch, {
        ("GET", "/repos/o/r/pulls/7"): _Resp(json_data={"body": "d"}),
        ("PATCH", "/repos/o/r/pulls/7"): _Resp(json_data={}),
    })
    adapter = _adapter()
    assert adapter.fetch_commit_messages() == []
    assert adapter.fetch_changed_paths() == []
    adapter.update_body_section("DIGEST")
    urls = [r["url"] for r in recorder]
    assert f"{_GHE}/repos/o/r/pulls/7/commits" in urls
    assert f"{_GHE}/repos/o/r/pulls/7/files" in urls
    assert urls.count(f"{_GHE}/repos/o/r/pulls/7") >= 2  # GET + PATCH body
    _assert_all_on_ghe(recorder)


# ----- check-run gate --------------------------------------------------------


def test_gate_check_runs_full_urls(monkeypatch: pytest.MonkeyPatch) -> None:
    recorder, _ = _install(monkeypatch, {
        ("GET", "/repos/o/r/commits/sha1/check-runs"): _Resp(
            json_data={"check_runs": []},
        ),
        ("POST", "/repos/o/r/check-runs"): _Resp(json_data={"id": 3}),
        ("PATCH", "/repos/o/r/check-runs/3"): _Resp(json_data={}),
    })
    adapter = _adapter()
    handle = adapter.open_gate("sha1")
    assert handle == 3
    result = CheckResult(
        conclusion="success", title="No findings", summary="ok",
        error_count=0, warning_count=0, info_count=0,
    )
    adapter.close_gate(handle, result)
    urls = [r["url"] for r in recorder]
    assert f"{_GHE}/repos/o/r/commits/sha1/check-runs" in urls  # supersede scan
    assert f"{_GHE}/repos/o/r/check-runs" in urls               # open
    assert f"{_GHE}/repos/o/r/check-runs/3" in urls             # close
    _assert_all_on_ghe(recorder)


# ----- CI failure signals ----------------------------------------------------


def test_ci_signals_full_urls(monkeypatch: pytest.MonkeyPatch) -> None:
    recorder, _ = _install(monkeypatch, {
        ("GET", "/repos/o/r/actions/runs"): _Resp(
            json_data={"workflow_runs": []},
        ),
    })
    assert _adapter().fetch_ci_failure_signals("sha1") == []
    assert recorder[0]["url"] == f"{_GHE}/repos/o/r/actions/runs"
    _assert_all_on_ghe(recorder)


# ----- GitHubConfig.base_url semantics ----------------------------------------


def test_config_normalises_trailing_slash() -> None:
    cfg = GitHubConfig(  # nosec B106 - test fixture token, not a credential
        repo="o/r", pr_number=7, token="t", base_url=f"{_GHE}/",
    )
    assert cfg.base_url == _GHE


def test_config_default_base_url_keeps_public_cloud(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, created = _install(monkeypatch, {})
    cfg = GitHubConfig(repo="o/r", pr_number=7, token="t")  # nosec B106 - test fixture token, not a credential
    assert cfg.base_url == ""  # backward compatible default
    with client_for(cfg) as client:
        assert client.base_url == _PUBLIC
    assert len(created) == 1


def test_config_custom_base_url_reaches_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, created = _install(monkeypatch, {})
    cfg = GitHubConfig(  # nosec B106 - test fixture token, not a credential
        repo="o/r", pr_number=7, token="t", base_url=_GHE,
    )
    with client_for(cfg) as client:
        assert client.base_url == _GHE
    assert len(created) == 1

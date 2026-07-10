"""Behaviour tests for harvest._harvest_one_pr and its helpers.

These pin the observable behaviour of dismissed-comment harvesting using a
scripted httpx.Client stand-in (no live GitHub) and a capturing store.
"""

from __future__ import annotations

from typing import Any

from prthinker.harvest import HarvestStats, _harvest_one_pr


class _CapturingStore:
    """Minimal DismissedExamplesStore stand-in that records appends."""

    def __init__(self) -> None:
        self.appended: list[Any] = []

    def append(self, example: Any) -> None:
        self.appended.append(example)


class _FakeResponse:
    """Scripted httpx.Response stand-in."""

    def __init__(self, payload: Any, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise AssertionError(f"unexpected status {self.status_code}")

    def json(self) -> Any:
        return self._payload


class _ScriptedClient:
    """Routes GET calls by URL substring to canned payloads."""

    def __init__(
        self,
        *,
        comments: list[dict],
        reactions_by_id: dict[int, Any] | None = None,
    ) -> None:
        self._comments = comments
        self._reactions_by_id = reactions_by_id or {}

    def get(self, url: str, params: dict | None = None) -> _FakeResponse:
        if url.endswith("/comments") and "/pulls/" in url:
            page = (params or {}).get("page", 1)
            return _FakeResponse(self._comments if page == 1 else [])
        if "/pulls/comments/" in url and url.endswith("/reactions"):
            comment_id = int(url.split("/pulls/comments/")[1].split("/")[0])
            payload = self._reactions_by_id.get(comment_id, [])
            return _FakeResponse(payload)
        raise AssertionError(f"unexpected GET {url}")


def _run(client: _ScriptedClient) -> tuple[_CapturingStore, HarvestStats]:
    store = _CapturingStore()
    stats = HarvestStats()
    _harvest_one_pr(client, "owner/name", 7, store, stats)  # type: ignore[arg-type]
    return store, stats


def test_thumbs_down_comment_is_harvested() -> None:
    client = _ScriptedClient(
        comments=[
            {
                "id": 1,
                "path": "src/a.py",
                "body": "  this is wrong  ",
                "diff_hunk": "@@ hunk @@",
            }
        ],
        reactions_by_id={1: [{"content": "-1"}]},
    )
    store, stats = _run(client)

    assert stats.comments_scanned == 1
    assert stats.dismissed_found == 1
    assert len(store.appended) == 1
    example = store.appended[0]
    assert example.path == "src/a.py"
    assert example.comment == "this is wrong"
    assert example.reason == "thumbs-down reaction"
    assert example.diff_snippet == "@@ hunk @@"


def test_reply_keyword_marks_parent_dismissed() -> None:
    client = _ScriptedClient(
        comments=[
            {"id": 10, "path": "b.py", "body": "nit"},
            {"id": 11, "in_reply_to_id": 10, "body": "false positive, ignore"},
        ],
    )
    store, stats = _run(client)

    # Both comments scanned, but the reply is not a candidate parent.
    assert stats.comments_scanned == 2
    assert stats.dismissed_found == 1
    assert store.appended[0].reason.startswith("reply matched:")


def test_non_dismissed_comment_is_skipped() -> None:
    client = _ScriptedClient(
        comments=[{"id": 20, "path": "c.py", "body": "looks good"}],
        reactions_by_id={20: []},
    )
    store, stats = _run(client)

    assert stats.comments_scanned == 1
    assert stats.dismissed_found == 0
    assert store.appended == []


def test_empty_body_dismissed_comment_is_dropped() -> None:
    client = _ScriptedClient(
        comments=[{"id": 30, "path": "d.py", "body": "   "}],
        reactions_by_id={30: [{"content": "-1"}]},
    )
    store, stats = _run(client)

    assert stats.comments_scanned == 1
    assert stats.dismissed_found == 0
    assert store.appended == []


def test_missing_path_and_hunk_default_to_empty() -> None:
    client = _ScriptedClient(
        comments=[{"id": 40, "body": "bad"}],
        reactions_by_id={40: [{"content": "-1"}]},
    )
    store, stats = _run(client)

    assert stats.dismissed_found == 1
    assert store.appended[0].path == ""
    assert store.appended[0].diff_snippet == ""


def test_no_comments_harvests_nothing() -> None:
    store, stats = _run(_ScriptedClient(comments=[]))
    assert stats.comments_scanned == 0
    assert stats.dismissed_found == 0
    assert store.appended == []


# --------------------------------------------------------------------------
# reactions rollup — the list payload's counts avoid the per-comment call
# --------------------------------------------------------------------------

class _RecordingClient(_ScriptedClient):
    """Scripted client that records hits on the per-comment reactions endpoint."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.reaction_urls: list[str] = []

    def get(self, url: str, params: dict | None = None) -> _FakeResponse:
        if "/pulls/comments/" in url and url.endswith("/reactions"):
            self.reaction_urls.append(url)
        return super().get(url, params)


def test_reactions_rollup_positive_skips_endpoint() -> None:
    client = _RecordingClient(
        comments=[{
            "id": 1,
            "path": "a.py",
            "body": "wrong",
            "reactions": {"-1": 2, "+1": 0},
        }],
    )
    store, stats = _run(client)
    assert stats.dismissed_found == 1
    assert store.appended[0].reason == "thumbs-down reaction"
    assert client.reaction_urls == []  # rollup answered without a request


def test_reactions_rollup_zero_skips_endpoint_and_not_dismissed() -> None:
    client = _RecordingClient(
        comments=[{
            "id": 2,
            "path": "a.py",
            "body": "fine",
            "reactions": {"-1": 0},
        }],
    )
    store, stats = _run(client)
    assert stats.dismissed_found == 0
    assert store.appended == []
    assert client.reaction_urls == []


def test_reactions_rollup_missing_key_falls_back_to_endpoint() -> None:
    client = _RecordingClient(
        comments=[{
            "id": 3,
            "path": "a.py",
            "body": "wrong",
            "reactions": {"+1": 1},  # no "-1" key -> endpoint consulted
        }],
        reactions_by_id={3: [{"content": "-1"}]},
    )
    _store, stats = _run(client)
    assert stats.dismissed_found == 1
    assert len(client.reaction_urls) == 1


def test_reactions_absent_falls_back_to_endpoint() -> None:
    client = _RecordingClient(
        comments=[{"id": 4, "path": "a.py", "body": "wrong"}],
        reactions_by_id={4: [{"content": "-1"}]},
    )
    store, stats = _run(client)
    assert stats.dismissed_found == 1
    assert len(client.reaction_urls) == 1

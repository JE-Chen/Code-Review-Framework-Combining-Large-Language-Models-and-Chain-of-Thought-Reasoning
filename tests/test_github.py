"""Behaviour tests for :class:`GitHubAdapter.fetch_author_replies`.

The adapter performs network I/O via a lazily-imported ``httpx.Client``.
These tests substitute a scripted client stand-in (never a live endpoint)
so the pagination loop, marker scan, and reply-filtering logic are
exercised deterministically.
"""

from __future__ import annotations

from typing import Any

import httpx
import pytest

from prthinker.dialogue import AuthorReply
from prthinker.platforms.github import GitHubAdapter

MARKER = "<!-- prthinker:summary -->"


class _ScriptedResponse:
    """Minimal ``httpx.Response`` stand-in carrying a fixed JSON payload."""

    def __init__(self, payload: list[dict[str, Any]]) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> list[dict[str, Any]]:
        return self._payload


class _ScriptedClient:
    """Scripted ``httpx.Client`` returning queued comment pages in order."""

    def __init__(self, pages: list[list[dict[str, Any]]], **_kwargs: Any) -> None:
        self._pages = pages
        self.requests: list[dict[str, Any]] = []

    def __enter__(self) -> "_ScriptedClient":
        return self

    def __exit__(self, *_exc: Any) -> None:
        return None

    def get(self, url: str, params: dict[str, Any] | None = None) -> _ScriptedResponse:
        self.requests.append({"url": url, "params": params})
        page = (params or {}).get("page", 1)
        idx = page - 1
        payload = self._pages[idx] if idx < len(self._pages) else []
        return _ScriptedResponse(payload)


def _install_client(
    monkeypatch: pytest.MonkeyPatch,
    pages: list[list[dict[str, Any]]],
) -> list[_ScriptedClient]:
    created: list[_ScriptedClient] = []

    def _factory(**kwargs: Any) -> _ScriptedClient:
        client = _ScriptedClient(pages, **kwargs)
        created.append(client)
        return client

    monkeypatch.setattr(httpx, "Client", _factory)
    return created


def _adapter() -> GitHubAdapter:
    return GitHubAdapter(repo="o/r", token="t", pr_number=7, comment_marker=MARKER)  # nosec B106 - test fixture token, not a credential


def test_no_marker_returns_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_client(monkeypatch, [[{"body": "hello", "user": {"login": "alice"}}]])
    assert _adapter().fetch_author_replies() == []


def test_empty_feed_returns_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_client(monkeypatch, [[]])
    assert _adapter().fetch_author_replies() == []


def test_replies_after_marker_are_collected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pages = [[
        {"id": 1, "body": f"{MARKER} summary", "user": {"login": "bot"},
         "created_at": "t0"},
        {"id": 2, "body": "wontfix because X", "user": {"login": "alice"},
         "created_at": "t1"},
        {"id": 3, "body": "more thoughts", "user": {"login": "bob"},
         "created_at": "t2"},
    ]]
    _install_client(monkeypatch, pages)
    replies = _adapter().fetch_author_replies()
    assert replies == [
        AuthorReply(author="alice", body="wontfix because X",
                    in_reply_to_id=1, created_at="t1"),
        AuthorReply(author="bob", body="more thoughts",
                    in_reply_to_id=1, created_at="t2"),
    ]


def test_bot_followups_are_skipped(monkeypatch: pytest.MonkeyPatch) -> None:
    pages = [[
        {"id": 1, "body": f"{MARKER} summary", "user": {"login": "bot"}},
        {"id": 2, "body": "bot follow-up", "user": {"login": "bot"}},
        {"id": 3, "body": "author reply", "user": {"login": "alice"}},
    ]]
    _install_client(monkeypatch, pages)
    replies = _adapter().fetch_author_replies()
    assert [r.author for r in replies] == ["alice"]


def test_last_marker_wins(monkeypatch: pytest.MonkeyPatch) -> None:
    pages = [[
        {"id": 1, "body": f"{MARKER} first", "user": {"login": "bot"}},
        {"id": 2, "body": "early reply", "user": {"login": "alice"}},
        {"id": 3, "body": f"{MARKER} second", "user": {"login": "bot"}},
        {"id": 4, "body": "late reply", "user": {"login": "alice"}},
    ]]
    _install_client(monkeypatch, pages)
    replies = _adapter().fetch_author_replies()
    assert [r.body for r in replies] == ["late reply"]
    assert replies[0].in_reply_to_id == 3


def test_missing_user_and_body_default_to_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pages = [[
        {"id": 1, "body": f"{MARKER} summary", "user": {"login": "bot"}},
        {"id": 2},  # no user, no body, no created_at
    ]]
    _install_client(monkeypatch, pages)
    replies = _adapter().fetch_author_replies()
    assert replies == [
        AuthorReply(author="", body="", in_reply_to_id=1, created_at=""),
    ]


def test_pagination_walks_full_pages(monkeypatch: pytest.MonkeyPatch) -> None:
    first = [{"id": 0, "body": f"{MARKER} s", "user": {"login": "bot"}}]
    first += [
        {"id": i, "body": "x", "user": {"login": "bot"}}
        for i in range(1, 100)
    ]  # exactly 100 -> triggers next page fetch
    second = [{"id": 200, "body": "reply", "user": {"login": "alice"}}]
    clients = _install_client(monkeypatch, [first, second])
    replies = _adapter().fetch_author_replies()
    assert [r.author for r in replies] == ["alice"]
    # Two pages requested (page 1 had 100 -> page 2 fetched).
    pages_requested = [r["params"]["page"] for r in clients[0].requests]
    assert pages_requested == [1, 2]


def test_short_page_stops_pagination(monkeypatch: pytest.MonkeyPatch) -> None:
    pages = [[
        {"id": 1, "body": f"{MARKER} s", "user": {"login": "bot"}},
        {"id": 2, "body": "reply", "user": {"login": "alice"}},
    ]]
    clients = _install_client(monkeypatch, pages)
    _adapter().fetch_author_replies()
    assert len(clients[0].requests) == 1

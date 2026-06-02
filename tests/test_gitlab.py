"""Tests for GitLabAdapter.fetch_author_replies and its helpers.

Network is not hit: a scripted httpx-Client stand-in replays paginated
``notes`` batches so the positional reply-extraction convention is pinned.
"""

from __future__ import annotations

from typing import Any

import httpx

from prthinker.dialogue import AuthorReply
from prthinker.platforms.gitlab import GitLabAdapter

_MARKER = "<!-- prthinker:summary -->"


def _note(
    note_id: int,
    *,
    body: str = "",
    username: str = "alice",
    system: bool = False,
    created_at: str = "2024-01-01T00:00:00Z",
) -> dict[str, Any]:
    return {
        "id": note_id,
        "body": body,
        "author": {"username": username},
        "system": system,
        "created_at": created_at,
    }


class _ScriptedNotesClient:
    """Replays scripted ``notes`` GET batches keyed by the ``page`` param."""

    def __init__(self, pages: list[list[dict]]) -> None:
        self._pages = pages

    def __enter__(self) -> _ScriptedNotesClient:
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def get(self, path: str, params: dict | None = None) -> httpx.Response:
        del path
        page = (params or {}).get("page", 1)
        idx = page - 1
        batch = self._pages[idx] if idx < len(self._pages) else []
        return httpx.Response(
            200,
            request=httpx.Request("GET", "http://test/notes"),
            json=batch,
        )


def _adapter_with_pages(pages: list[list[dict]]) -> GitLabAdapter:
    adapter = GitLabAdapter(project="g/p", token="t", mr_iid=7)
    adapter._client = lambda: _ScriptedNotesClient(pages)  # type: ignore[method-assign]  # noqa: SLF001
    return adapter


# ----- _find_last_marker_idx ------------------------------------------------

def test_find_last_marker_idx_returns_last_match() -> None:
    notes = [
        _note(1, body="hi"),
        _note(2, body=f"first {_MARKER}"),
        _note(3, body="reply"),
        _note(4, body=f"second {_MARKER}"),
    ]
    assert GitLabAdapter._find_last_marker_idx(notes, _MARKER) == 3  # noqa: SLF001


def test_find_last_marker_idx_none_when_absent() -> None:
    notes = [_note(1, body="hi"), _note(2, body="bye")]
    assert GitLabAdapter._find_last_marker_idx(notes, _MARKER) is None  # noqa: SLF001


def test_find_last_marker_idx_empty_list() -> None:
    assert GitLabAdapter._find_last_marker_idx([], _MARKER) is None  # noqa: SLF001


# ----- _build_replies -------------------------------------------------------

def test_build_replies_excludes_marker_author_and_system() -> None:
    notes = [
        _note(10, body=f"{_MARKER}", username="bot"),
        _note(11, body="please fix", username="alice"),
        _note(12, body="bot follow-up", username="bot"),
        _note(13, body="system event", username="alice", system=True),
        _note(14, body="  trailing  ", username="bob"),
    ]
    replies = GitLabAdapter._build_replies(notes, 0)  # noqa: SLF001
    assert replies == [
        AuthorReply(
            author="alice",
            body="please fix",
            in_reply_to_id=10,
            created_at="2024-01-01T00:00:00Z",
        ),
        AuthorReply(
            author="bob",
            body="trailing",
            in_reply_to_id=10,
            created_at="2024-01-01T00:00:00Z",
        ),
    ]


def test_build_replies_empty_after_marker() -> None:
    notes = [_note(1, body=f"{_MARKER}", username="bot")]
    assert GitLabAdapter._build_replies(notes, 0) == []  # noqa: SLF001


# ----- fetch_author_replies (end-to-end through scripted client) ------------

def test_fetch_author_replies_no_marker_returns_empty() -> None:
    adapter = _adapter_with_pages([[_note(1, body="hi"), _note(2, body="bye")]])
    assert adapter.fetch_author_replies() == []


def test_fetch_author_replies_happy_path() -> None:
    pages = [[
        _note(1, body="unrelated", username="carol"),
        _note(2, body=f"{_MARKER}", username="bot"),
        _note(3, body="I disagree", username="dave"),
        _note(4, body="bot noise", username="bot"),
    ]]
    adapter = _adapter_with_pages(pages)
    replies = adapter.fetch_author_replies()
    assert replies == [
        AuthorReply(
            author="dave",
            body="I disagree",
            in_reply_to_id=2,
            created_at="2024-01-01T00:00:00Z",
        ),
    ]


def test_fetch_author_replies_paginates() -> None:
    page1 = [_note(i, body="x", username="carol") for i in range(100)]
    page1[50] = _note(50, body=f"{_MARKER}", username="bot")
    page2 = [_note(200, body="late reply", username="erin")]
    adapter = _adapter_with_pages([page1, page2])
    replies = adapter.fetch_author_replies()
    authors = [r.author for r in replies]
    assert "erin" in authors
    assert all(a != "bot" for a in authors)
    assert all(r.in_reply_to_id == 50 for r in replies)


def test_fetch_author_replies_empty_notes() -> None:
    adapter = _adapter_with_pages([[]])
    assert adapter.fetch_author_replies() == []

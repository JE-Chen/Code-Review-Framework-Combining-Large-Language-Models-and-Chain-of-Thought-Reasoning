"""Behaviour tests for the Gitea dismissed / accepted harvesters.

Mirrors ``tests/test_gitlab_harvest.py``: a scripted httpx.Client
stand-in replays PR / review / reaction payloads (no live Gitea) and a
capturing store records appends.
"""

from __future__ import annotations

from typing import Any

import httpx
import pytest

from prthinker import gitea_harvest
from prthinker.harvest import HarvestStats
from prthinker.gitea_harvest import (
    _harvest_accepted_one_pr,
    _harvest_one_pr,
    _threads_by_position,
    harvest,
    harvest_accepted,
)


class _CapturingStore:
    """Minimal corpora-store stand-in that records appends."""

    def __init__(self) -> None:
        self.appended: list[Any] = []

    def append(self, example: Any) -> None:
        self.appended.append(example)


def _comment(
    comment_id: int,
    *,
    body: str = "finding text",
    path: str = "src/a.py",
    position: int = 3,
    diff_hunk: str = "@@ -1 +1 @@",
) -> dict[str, Any]:
    return {
        "id": comment_id,
        "body": body,
        "path": path,
        "position": position,
        "diff_hunk": diff_hunk,
    }


class _ScriptedClient:
    """Routes GETs by path shape to canned paginated payloads."""

    def __init__(
        self,
        *,
        prs: list[dict] | None = None,
        reviews: list[dict] | None = None,
        comments_by_review: dict[int, list[dict]] | None = None,
        reactions_by_comment: dict[int, list[dict]] | None = None,
        commits: list[dict] | None = None,
        reaction_status: int = 200,
        reviews_status_by_pr: dict[int, int] | None = None,
    ) -> None:
        self._prs = prs or []
        self._reviews = reviews or []
        self._comments_by_review = comments_by_review or {}
        self._reactions_by_comment = reactions_by_comment or {}
        self._commits = commits or []
        self._reaction_status = reaction_status
        self._reviews_status_by_pr = reviews_status_by_pr or {}

    def __enter__(self) -> "_ScriptedClient":
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    @staticmethod
    def _response(payload: Any, status: int = 200) -> httpx.Response:
        return httpx.Response(
            status, request=httpx.Request("GET", "http://test"), json=payload
        )

    def get(self, path: str, params: dict | None = None) -> httpx.Response:
        page = (params or {}).get("page", 1)
        if "/issues/comments/" in path and path.endswith("/reactions"):
            comment_id = int(path.split("/comments/")[1].split("/")[0])
            payload = self._reactions_by_comment.get(comment_id, [])
            return self._response(payload, self._reaction_status)
        if "/reviews/" in path and path.endswith("/comments"):
            review_id = int(path.split("/reviews/")[1].split("/")[0])
            return self._response(self._comments_by_review.get(review_id, []))
        if path.endswith("/reviews"):
            pr = int(path.split("/pulls/")[1].split("/")[0])
            status = self._reviews_status_by_pr.get(pr, 200)
            return self._response(
                self._reviews if page == 1 else [], status,
            )
        if path.endswith("/commits"):
            return self._response(self._commits if page == 1 else [])
        if path.endswith("/pulls"):
            return self._response(self._prs if page == 1 else [])
        raise AssertionError(f"unexpected GET {path}")


def _run_dismissed(client: _ScriptedClient) -> tuple[_CapturingStore, HarvestStats]:
    store = _CapturingStore()
    stats = HarvestStats()
    _harvest_one_pr(client, "o/r", 7, store, stats)  # type: ignore[arg-type]
    return store, stats


# ----- dismissed: signals ----------------------------------------------------


def test_thumbs_down_comment_is_harvested() -> None:
    client = _ScriptedClient(
        reviews=[{"id": 1}],
        comments_by_review={1: [_comment(10, body="  this is wrong  ")]},
        reactions_by_comment={10: [{"content": "-1"}]},
    )
    store, stats = _run_dismissed(client)

    assert stats.comments_scanned == 1
    assert stats.dismissed_found == 1
    example = store.appended[0]
    assert example.path == "src/a.py"
    assert example.comment == "this is wrong"
    assert example.reason == "thumbs-down reaction"
    assert example.diff_snippet == "@@ -1 +1 @@"


def test_reply_keyword_marks_thread_parent_dismissed() -> None:
    # Same (path, position) → one thread: 10 is the parent, 11 a reply.
    client = _ScriptedClient(
        reviews=[{"id": 1}, {"id": 2}],
        comments_by_review={
            1: [_comment(10, body="nit")],
            2: [_comment(11, body="false positive, ignore")],
        },
    )
    store, stats = _run_dismissed(client)

    assert stats.comments_scanned == 1
    assert stats.dismissed_found == 1
    assert store.appended[0].comment == "nit"
    assert store.appended[0].reason.startswith("reply matched:")


def test_other_reaction_is_not_a_dismissal() -> None:
    client = _ScriptedClient(
        reviews=[{"id": 1}],
        comments_by_review={1: [_comment(10)]},
        reactions_by_comment={10: [{"content": "+1"}]},
    )
    store, stats = _run_dismissed(client)

    assert stats.dismissed_found == 0
    assert store.appended == []


def test_reaction_endpoint_404_means_no_thumbs_down() -> None:
    client = _ScriptedClient(
        reviews=[{"id": 1}],
        comments_by_review={1: [_comment(10)]},
        reaction_status=404,
    )
    store, stats = _run_dismissed(client)

    assert stats.dismissed_found == 0
    assert store.appended == []


def test_empty_body_dismissed_comment_is_dropped() -> None:
    client = _ScriptedClient(
        reviews=[{"id": 1}],
        comments_by_review={1: [_comment(10, body="   ")]},
        reactions_by_comment={10: [{"content": "-1"}]},
    )
    store, stats = _run_dismissed(client)

    assert stats.dismissed_found == 0
    assert store.appended == []


def test_distinct_positions_are_distinct_threads() -> None:
    # A comment on another line is NOT a reply to the first one.
    client = _ScriptedClient(
        reviews=[{"id": 1}],
        comments_by_review={1: [
            _comment(10, body="finding A", position=3),
            _comment(11, body="wontfix", position=9),
        ]},
    )
    store, stats = _run_dismissed(client)

    assert stats.comments_scanned == 2
    assert stats.dismissed_found == 0  # keyword sits on its own thread
    assert store.appended == []


def test_threads_order_replies_by_id() -> None:
    threads = _threads_by_position([
        _comment(12, position=3),
        _comment(10, position=3),
        _comment(11, position=3),
    ])
    assert [c["id"] for c in threads[0]] == [10, 11, 12]


# ----- bulk harvest ----------------------------------------------------------


def _patch_client(monkeypatch, client: _ScriptedClient) -> None:
    monkeypatch.setattr(
        gitea_harvest, "_client", lambda token, base_url: client
    )


def test_harvest_bulk_caps_max_prs(monkeypatch) -> None:
    client = _ScriptedClient(
        prs=[{"number": 1}, {"number": 2}, {"number": 3}],
        reviews=[],
    )
    _patch_client(monkeypatch, client)
    stats = harvest("o/r", "tok", store=_CapturingStore(), max_prs=2)  # type: ignore[arg-type]

    assert stats.prs_scanned == 2


def test_harvest_bulk_continues_after_one_pr_fails(monkeypatch) -> None:
    client = _ScriptedClient(
        prs=[{"number": 1}, {"number": 2}],
        reviews=[{"id": 5}],
        comments_by_review={5: [_comment(50, body="bad line")]},
        reactions_by_comment={50: [{"content": "-1"}]},
        reviews_status_by_pr={1: 500},
    )
    _patch_client(monkeypatch, client)
    store = _CapturingStore()
    stats = harvest("o/r", "tok", store=store)  # type: ignore[arg-type]

    assert stats.prs_scanned == 2
    # PR #1 500ed and was skipped; PR #2 still harvested.
    assert stats.dismissed_found == 1
    assert store.appended[0].comment == "bad line"


def test_harvest_single_pr_targets_that_number(monkeypatch) -> None:
    client = _ScriptedClient(
        reviews=[{"id": 5}],
        comments_by_review={5: [_comment(50, body="only this")]},
        reactions_by_comment={50: [{"content": "-1"}]},
    )
    _patch_client(monkeypatch, client)
    stats = harvest("o/r", "tok", store=_CapturingStore(), pr_number=42)  # type: ignore[arg-type]

    assert stats.prs_scanned == 1
    assert stats.dismissed_found == 1


def test_harvest_rejects_bad_repo() -> None:
    with pytest.raises(ValueError, match="owner/name"):
        harvest("demo", "tok", store=_CapturingStore())  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="owner/name"):
        harvest_accepted("demo", "tok", store=_CapturingStore())  # type: ignore[arg-type]


# ----- accepted --------------------------------------------------------------


_SUGGESTION_BODY = (
    "use a constant here\n\n```suggestion\nMAX_RETRIES = 3\n```"
)


def _run_accepted(client: _ScriptedClient) -> tuple[_CapturingStore, HarvestStats]:
    store = _CapturingStore()
    stats = HarvestStats()
    _harvest_accepted_one_pr(client, "o/r", 7, store, stats)  # type: ignore[arg-type]
    return store, stats


def test_accepted_requires_apply_commit() -> None:
    client = _ScriptedClient(
        commits=[{"commit": {"message": "fix: normal commit"}}],
        reviews=[{"id": 1}],
        comments_by_review={1: [_comment(10, body=_SUGGESTION_BODY)]},
    )
    store, stats = _run_accepted(client)

    assert stats.accepted_found == 0
    assert store.appended == []


def test_accepted_harvests_suggestion_blocks() -> None:
    client = _ScriptedClient(
        commits=[{"commit": {"message": "Apply suggestions from code review"}}],
        reviews=[{"id": 1}],
        comments_by_review={1: [
            _comment(10, body=_SUGGESTION_BODY),
            _comment(11, body="no suggestion block here"),
        ]},
    )
    store, stats = _run_accepted(client)

    assert stats.accepted_found == 1
    example = store.appended[0]
    assert example.path == "src/a.py"
    assert example.comment == "use a constant here"
    assert example.suggestion == "MAX_RETRIES = 3"
    assert example.pr_number == 7


def test_accepted_suggestion_only_comment_gets_placeholder() -> None:
    client = _ScriptedClient(
        commits=[{"commit": {"message": "Apply suggestions from code review"}}],
        reviews=[{"id": 1}],
        comments_by_review={1: [_comment(10, body="```suggestion\nx = 1\n```")]},
    )
    store, _ = _run_accepted(client)

    assert store.appended[0].comment == "(suggestion only)"


def test_accepted_bulk_flow_end_to_end(monkeypatch) -> None:
    client = _ScriptedClient(
        prs=[{"number": 3}],
        commits=[{"commit": {"message": "Apply suggestions from code review"}}],
        reviews=[{"id": 1}],
        comments_by_review={1: [_comment(10, body=_SUGGESTION_BODY)]},
    )
    _patch_client(monkeypatch, client)
    store = _CapturingStore()
    stats = harvest_accepted("o/r", "tok", store=store)  # type: ignore[arg-type]

    assert stats.prs_scanned == 1
    assert stats.accepted_found == 1
    assert store.appended[0].pr_number == 3


def test_accepted_bulk_continues_after_one_pr_fails(monkeypatch) -> None:
    client = _ScriptedClient(
        prs=[{"number": 1}, {"number": 2}],
        commits=[{"commit": {"message": "Apply suggestions from code review"}}],
        reviews=[{"id": 1}],
        comments_by_review={1: [_comment(10, body=_SUGGESTION_BODY)]},
        reviews_status_by_pr={1: 500},
    )
    _patch_client(monkeypatch, client)
    stats = harvest_accepted("o/r", "tok", store=_CapturingStore())  # type: ignore[arg-type]

    assert stats.prs_scanned == 2
    assert stats.accepted_found == 1

"""Behaviour tests for the GitLab dismissed / accepted harvesters.

Mirrors ``tests/test_harvest.py``: a scripted httpx.Client stand-in
replays MR / discussion / award-emoji payloads (no live GitLab) and a
capturing store records appends.
"""

from __future__ import annotations

from typing import Any

import httpx

from prthinker import gitlab_harvest
from prthinker.harvest import HarvestStats
from prthinker.gitlab_harvest import (
    _harvest_accepted_one_mr,
    _harvest_one_mr,
    harvest,
    harvest_accepted,
)


class _CapturingStore:
    """Minimal corpora-store stand-in that records appends."""

    def __init__(self) -> None:
        self.appended: list[Any] = []

    def append(self, example: Any) -> None:
        self.appended.append(example)


def _diff_note(
    note_id: int,
    *,
    body: str = "finding text",
    path: str = "src/a.py",
    note_type: str | None = "DiffNote",
    system: bool = False,
) -> dict[str, Any]:
    return {
        "id": note_id,
        "type": note_type,
        "body": body,
        "system": system,
        "position": {"new_path": path},
    }


class _ScriptedClient:
    """Routes GETs by path suffix to canned paginated payloads."""

    def __init__(
        self,
        *,
        mrs: list[dict] | None = None,
        discussions: list[dict] | None = None,
        awards_by_note: dict[int, list[dict]] | None = None,
        commits: list[dict] | None = None,
        award_status: int = 200,
        discussions_status_by_iid: dict[int, int] | None = None,
    ) -> None:
        self._mrs = mrs or []
        self._discussions = discussions or []
        self._awards_by_note = awards_by_note or {}
        self._commits = commits or []
        self._award_status = award_status
        self._discussions_status_by_iid = discussions_status_by_iid or {}

    def __enter__(self) -> _ScriptedClient:
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
        if path.endswith("/award_emoji"):
            note_id = int(path.split("/notes/")[1].split("/")[0])
            payload = self._awards_by_note.get(note_id, [])
            return self._response(payload, self._award_status)
        if path.endswith("/discussions"):
            iid = int(path.split("/merge_requests/")[1].split("/")[0])
            status = self._discussions_status_by_iid.get(iid, 200)
            return self._response(
                self._discussions if page == 1 else [], status,
            )
        if path.endswith("/commits"):
            return self._response(self._commits if page == 1 else [])
        if path.endswith("/merge_requests"):
            return self._response(self._mrs if page == 1 else [])
        raise AssertionError(f"unexpected GET {path}")


def _run_dismissed(client: _ScriptedClient) -> tuple[_CapturingStore, HarvestStats]:
    store = _CapturingStore()
    stats = HarvestStats()
    _harvest_one_mr(client, "g%2Fp", 7, store, stats)  # type: ignore[arg-type]
    return store, stats


# ----- dismissed: signals ----------------------------------------------------


def test_thumbs_down_note_is_harvested() -> None:
    client = _ScriptedClient(
        discussions=[{"notes": [_diff_note(1, body="  this is wrong  ")]}],
        awards_by_note={1: [{"name": "thumbsdown"}]},
    )
    store, stats = _run_dismissed(client)

    assert stats.comments_scanned == 1
    assert stats.dismissed_found == 1
    example = store.appended[0]
    assert example.path == "src/a.py"
    assert example.comment == "this is wrong"
    assert example.reason == "thumbs-down award"


def test_reply_keyword_marks_parent_dismissed() -> None:
    client = _ScriptedClient(
        discussions=[{
            "notes": [
                _diff_note(10, body="nit"),
                {"id": 11, "body": "false positive, ignore", "system": False},
            ],
        }],
    )
    store, stats = _run_dismissed(client)

    assert stats.dismissed_found == 1
    assert store.appended[0].reason.startswith("reply matched:")


def test_other_award_emoji_is_not_a_dismissal() -> None:
    client = _ScriptedClient(
        discussions=[{"notes": [_diff_note(1)]}],
        awards_by_note={1: [{"name": "thumbsup"}]},
    )
    store, stats = _run_dismissed(client)

    assert stats.dismissed_found == 0
    assert store.appended == []


def test_award_endpoint_404_means_no_thumbs_down() -> None:
    client = _ScriptedClient(
        discussions=[{"notes": [_diff_note(1)]}],
        award_status=404,
    )
    store, stats = _run_dismissed(client)

    assert stats.dismissed_found == 0
    assert store.appended == []


def test_empty_body_dismissed_note_is_dropped() -> None:
    client = _ScriptedClient(
        discussions=[{"notes": [_diff_note(1, body="   ")]}],
        awards_by_note={1: [{"name": "thumbsdown"}]},
    )
    store, stats = _run_dismissed(client)

    assert stats.dismissed_found == 0
    assert store.appended == []


# ----- dismissed: candidate filtering ----------------------------------------


def test_non_diff_notes_are_not_candidates() -> None:
    client = _ScriptedClient(
        discussions=[
            {"notes": [_diff_note(1, note_type=None, body="top-level note")]},
            {"notes": []},
        ],
    )
    store, stats = _run_dismissed(client)

    assert stats.comments_scanned == 0
    assert store.appended == []


def test_system_notes_are_skipped_before_candidate_check() -> None:
    client = _ScriptedClient(
        discussions=[{
            "notes": [
                _diff_note(1, system=True),
                _diff_note(2, body="real finding"),
            ],
        }],
        awards_by_note={2: [{"name": "thumbsdown"}]},
    )
    store, stats = _run_dismissed(client)

    assert stats.comments_scanned == 1
    assert stats.dismissed_found == 1
    assert store.appended[0].comment == "real finding"


# ----- bulk harvest ------------------------------------------------------------


def _patch_client(monkeypatch, client: _ScriptedClient) -> None:
    monkeypatch.setattr(
        gitlab_harvest, "_client", lambda token, base_url: client
    )


def test_harvest_bulk_skips_open_mrs_and_caps_max(monkeypatch) -> None:
    client = _ScriptedClient(
        mrs=[
            {"iid": 1, "state": "opened"},
            {"iid": 2, "state": "merged"},
            {"iid": 3, "state": "closed"},
            {"iid": 4, "state": "merged"},
        ],
        discussions=[],
    )
    _patch_client(monkeypatch, client)
    stats = harvest("g/p", "tok", store=_CapturingStore(), max_mrs=2)  # type: ignore[arg-type]

    assert stats.prs_scanned == 2


def test_harvest_bulk_continues_after_one_mr_fails(monkeypatch) -> None:
    client = _ScriptedClient(
        mrs=[
            {"iid": 1, "state": "merged"},
            {"iid": 2, "state": "merged"},
        ],
        discussions=[{"notes": [_diff_note(5, body="bad line")]}],
        awards_by_note={5: [{"name": "thumbsdown"}]},
        discussions_status_by_iid={1: 500},
    )
    _patch_client(monkeypatch, client)
    store = _CapturingStore()
    stats = harvest("g/p", "tok", store=store)  # type: ignore[arg-type]

    assert stats.prs_scanned == 2
    # MR !1 500ed and was skipped; MR !2 still harvested.
    assert stats.dismissed_found == 1
    assert store.appended[0].comment == "bad line"


def test_harvest_single_mr_targets_that_iid(monkeypatch) -> None:
    client = _ScriptedClient(
        discussions=[{"notes": [_diff_note(9, body="only this")]}],
        awards_by_note={9: [{"name": "thumbsdown"}]},
    )
    _patch_client(monkeypatch, client)
    stats = harvest("g/p", "tok", store=_CapturingStore(), mr_iid=42)  # type: ignore[arg-type]

    assert stats.prs_scanned == 1
    assert stats.dismissed_found == 1


# ----- accepted -----------------------------------------------------------------


_SUGGESTION_BODY = (
    "use a constant here\n\n```suggestion\nMAX_RETRIES = 3\n```"
)


def _run_accepted(client: _ScriptedClient) -> tuple[_CapturingStore, HarvestStats]:
    store = _CapturingStore()
    stats = HarvestStats()
    _harvest_accepted_one_mr(client, "g%2Fp", 7, store, stats)  # type: ignore[arg-type]
    return store, stats


def test_accepted_requires_apply_commit() -> None:
    client = _ScriptedClient(
        commits=[{"message": "fix: normal commit"}],
        discussions=[{"notes": [_diff_note(1, body=_SUGGESTION_BODY)]}],
    )
    store, stats = _run_accepted(client)

    assert stats.accepted_found == 0
    assert store.appended == []


def test_accepted_harvests_suggestion_blocks_on_gitlab_apply_message() -> None:
    client = _ScriptedClient(
        commits=[{"message": "Apply 2 suggestion(s) to 1 file(s)"}],
        discussions=[{
            "notes": [
                _diff_note(1, body=_SUGGESTION_BODY),
                _diff_note(2, body="no suggestion block here"),
            ],
        }],
    )
    store, stats = _run_accepted(client)

    assert stats.accepted_found == 1
    example = store.appended[0]
    assert example.path == "src/a.py"
    assert example.comment == "use a constant here"
    assert example.suggestion == "MAX_RETRIES = 3"
    assert example.pr_number == 7


def test_accepted_matches_github_style_apply_message() -> None:
    client = _ScriptedClient(
        commits=[{"message": "Apply suggestions from code review"}],
        discussions=[{"notes": [_diff_note(1, body=_SUGGESTION_BODY)]}],
    )
    _, stats = _run_accepted(client)

    assert stats.accepted_found == 1


def test_accepted_suggestion_only_comment_gets_placeholder() -> None:
    client = _ScriptedClient(
        commits=[{"message": "Apply 1 suggestion(s) to 1 file(s)"}],
        discussions=[{
            "notes": [_diff_note(1, body="```suggestion\nx = 1\n```")],
        }],
    )
    store, _ = _run_accepted(client)

    assert store.appended[0].comment == "(suggestion only)"


def test_accepted_bulk_flow_end_to_end(monkeypatch) -> None:
    client = _ScriptedClient(
        mrs=[{"iid": 3, "state": "merged"}],
        commits=[{"message": "Apply 1 suggestion(s) to 1 file(s)"}],
        discussions=[{"notes": [_diff_note(1, body=_SUGGESTION_BODY)]}],
    )
    _patch_client(monkeypatch, client)
    store = _CapturingStore()
    stats = harvest_accepted("g/p", "tok", store=store)  # type: ignore[arg-type]

    assert stats.prs_scanned == 1
    assert stats.accepted_found == 1
    assert store.appended[0].pr_number == 3

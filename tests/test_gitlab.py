"""Tests for GitLabAdapter.fetch_author_replies and its helpers.

Network is not hit: a scripted httpx-Client stand-in replays paginated
``notes`` batches so the positional reply-extraction convention is pinned.
"""

from __future__ import annotations

from typing import Any

import httpx

from prthinker.checks import CheckResult
from prthinker.dialogue import AuthorReply
from prthinker.platforms.gitlab import GitLabAdapter
from prthinker.schemas import InlineFinding

_MARKER = "<!-- prthinker:summary -->"
_INLINE_MARKER = "<!-- prthinker:inline -->"


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
    adapter = GitLabAdapter(project="g/p", token="t", mr_iid=7)  # nosec B106 - test fixture token, not a credential
    adapter._client = lambda: _ScriptedNotesClient(pages)  # type: ignore[method-assign]  # noqa: SLF001
    return adapter


# ----- _find_last_marker_index (shared base template hook) -------------------

def test_find_last_marker_index_returns_last_match() -> None:
    notes = [
        _note(1, body="hi"),
        _note(2, body=f"first {_MARKER}"),
        _note(3, body="reply"),
        _note(4, body=f"second {_MARKER}"),
    ]
    assert GitLabAdapter._find_last_marker_index(notes, _MARKER) == 3  # noqa: SLF001


def test_find_last_marker_index_none_when_absent() -> None:
    notes = [_note(1, body="hi"), _note(2, body="bye")]
    assert GitLabAdapter._find_last_marker_index(notes, _MARKER) is None  # noqa: SLF001


def test_find_last_marker_index_empty_list() -> None:
    assert GitLabAdapter._find_last_marker_index([], _MARKER) is None  # noqa: SLF001


# ----- _replies_after_marker (shared base template method) --------------------

def _bare_adapter() -> GitLabAdapter:
    return GitLabAdapter(project="g/p", token="t", mr_iid=7)  # nosec B106 - test fixture token, not a credential


def test_replies_after_marker_excludes_marker_author_and_system() -> None:
    notes = [
        _note(10, body=f"{_MARKER}", username="bot"),
        _note(11, body="please fix", username="alice"),
        _note(12, body="bot follow-up", username="bot"),
        _note(13, body="system event", username="alice", system=True),
        _note(14, body="  trailing  ", username="bob"),
    ]
    replies = _bare_adapter()._replies_after_marker(notes, _MARKER)  # noqa: SLF001
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


def test_replies_after_marker_empty_after_marker() -> None:
    notes = [_note(1, body=f"{_MARKER}", username="bot")]
    assert _bare_adapter()._replies_after_marker(notes, _MARKER) == []  # noqa: SLF001


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


# ----- submit_inline_review -------------------------------------------------

_DIFF_REFS = {
    "base_sha": "b" * 40,
    "start_sha": "s" * 40,
    "head_sha": "h" * 40,
}


class _ScriptedReviewClient:
    """Replays the MR GET then records every discussion / note POST."""

    def __init__(
        self,
        *,
        diff_refs: dict | None,
        post_statuses: list[int] | None = None,
    ) -> None:
        self._diff_refs = diff_refs
        self._post_statuses = list(post_statuses or [])
        self.posts: list[tuple[str, dict]] = []
        self._next_id = 100

    def __enter__(self) -> _ScriptedReviewClient:
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def get(self, path: str, params: dict | None = None) -> httpx.Response:
        del params
        if path.endswith("/notes"):
            # No prior notes: the stale-cleanup scan finds nothing.
            return httpx.Response(
                200,
                request=httpx.Request("GET", "http://test/notes"),
                json=[],
            )
        body: dict[str, Any] = {}
        if self._diff_refs is not None:
            body["diff_refs"] = self._diff_refs
        return httpx.Response(
            200,
            request=httpx.Request("GET", "http://test/mr"),
            json=body,
        )

    def post(self, path: str, json: dict | None = None) -> httpx.Response:
        self.posts.append((path, json or {}))
        status = self._post_statuses.pop(0) if self._post_statuses else 201
        self._next_id += 1
        return httpx.Response(
            status,
            request=httpx.Request("POST", "http://test" + path),
            json={"id": self._next_id},
        )


def _review_adapter(client: _ScriptedReviewClient) -> GitLabAdapter:
    adapter = GitLabAdapter(project="g/p", token="t", mr_iid=7)  # nosec B106 - test fixture token, not a credential
    adapter._client = lambda: client  # type: ignore[method-assign]  # noqa: SLF001
    return adapter


def _finding(path: str = "a.py", line: int = 3) -> InlineFinding:
    return InlineFinding(
        path=path, line=line, severity="error", comment="fix this"
    )


def test_submit_inline_review_no_findings_returns_none() -> None:
    adapter = GitLabAdapter(project="g/p", token="t", mr_iid=7)  # nosec B106 - test fixture token, not a credential
    assert adapter.submit_inline_review(
        [], summary_body=None, event="COMMENT"
    ) is None


def test_submit_inline_review_missing_shas_raises() -> None:
    client = _ScriptedReviewClient(diff_refs={"base_sha": "b" * 40})
    adapter = _review_adapter(client)
    try:
        adapter.submit_inline_review(
            [_finding()], summary_body=None, event="COMMENT"
        )
    except RuntimeError as err:
        assert "diff_refs missing required SHAs" in str(err)
    else:
        raise AssertionError("expected RuntimeError")


def test_submit_inline_review_happy_path_returns_first_id() -> None:
    client = _ScriptedReviewClient(diff_refs=dict(_DIFF_REFS))
    adapter = _review_adapter(client)
    result = adapter.submit_inline_review(
        [_finding("a.py", 3), _finding("b.py", 4)],
        summary_body=None,
        event="APPROVE",
    )
    assert result == 101
    discussions = [p for p in client.posts if p[0].endswith("/discussions")]
    assert len(discussions) == 2
    first_payload = discussions[0][1]
    assert first_payload["position"]["new_path"] == "a.py"
    assert first_payload["position"]["new_line"] == 3
    assert first_payload["position"]["base_sha"] == "b" * 40
    assert first_payload["body"].startswith("**Verdict: APPROVE** — ")


def test_submit_inline_review_skips_failed_posts() -> None:
    client = _ScriptedReviewClient(
        diff_refs=dict(_DIFF_REFS), post_statuses=[422, 201]
    )
    adapter = _review_adapter(client)
    result = adapter.submit_inline_review(
        [_finding("a.py", 3), _finding("b.py", 4)],
        summary_body=None,
        event="COMMENT",
    )
    # First POST failed (422) so first_id comes from the second POST.
    assert result == 102


def test_submit_inline_review_posts_summary_note() -> None:
    client = _ScriptedReviewClient(diff_refs=dict(_DIFF_REFS))
    adapter = _review_adapter(client)
    adapter.submit_inline_review(
        [_finding()], summary_body="overall summary", event="COMMENT"
    )
    notes = [
        p for p in client.posts
        if p[0].endswith("/notes")
        and p[1].get("body", "").startswith("overall summary")
    ]
    assert len(notes) == 1
    # The note carries the hidden inline marker so the next run can
    # identify and clean it up.
    assert _INLINE_MARKER in notes[0][1]["body"]


# ----- full-feature parity: scripted routing client --------------------------

_HUNK_DIFF = (
    "diff --git a/a.py b/a.py\n"
    "--- a/a.py\n"
    "+++ b/a.py\n"
    "@@ -1,2 +1,3 @@\n"
    " kept\n"
    "+added\n"
    " tail\n"
)


class _ScriptedFullClient:
    """Routes GETs by path suffix; records every mutating call."""

    def __init__(
        self,
        *,
        mr: dict | None = None,
        notes: list[dict] | None = None,
        commits: list[dict] | None = None,
        diffs: list[dict] | None = None,
        raw_diff: str = "",
        raw_diff_status: int = 200,
        notes_status: int = 200,
    ) -> None:
        self._mr = mr or {"diff_refs": dict(_DIFF_REFS)}
        self._notes = notes or []
        self._commits = commits or []
        self._diffs = diffs or []
        self._raw_diff = raw_diff
        self._raw_diff_status = raw_diff_status
        self._notes_status = notes_status
        self.posts: list[tuple[str, dict]] = []
        self.puts: list[tuple[str, dict]] = []
        self.deletes: list[str] = []
        self._next_id = 500

    def __enter__(self) -> _ScriptedFullClient:
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    @staticmethod
    def _json_response(payload: object, status: int = 200) -> httpx.Response:
        return httpx.Response(
            status, request=httpx.Request("GET", "http://test"), json=payload
        )

    def get(self, path: str, params: dict | None = None) -> httpx.Response:
        page = (params or {}).get("page", 1)
        if path.endswith("/raw_diffs"):
            return httpx.Response(
                self._raw_diff_status,
                request=httpx.Request("GET", "http://test/raw_diffs"),
                text=self._raw_diff,
            )
        if path.endswith("/notes"):
            return self._json_response(
                self._notes if page == 1 else [], self._notes_status,
            )
        for suffix, items in (
            ("/commits", self._commits),
            ("/diffs", self._diffs),
        ):
            if path.endswith(suffix):
                return self._json_response(items if page == 1 else [])
        return self._json_response(self._mr)

    def post(
        self, path: str, json: dict | None = None, params: dict | None = None
    ) -> httpx.Response:
        self.posts.append((path, json or params or {}))
        self._next_id += 1
        return httpx.Response(
            201,
            request=httpx.Request("POST", "http://test" + path),
            json={"id": self._next_id},
        )

    def put(self, path: str, json: dict | None = None) -> httpx.Response:
        self.puts.append((path, json or {}))
        return self._json_response({"id": 1})

    def delete(self, path: str) -> httpx.Response:
        self.deletes.append(path)
        return httpx.Response(
            204, request=httpx.Request("DELETE", "http://test" + path)
        )


def _full_adapter(client: _ScriptedFullClient) -> GitLabAdapter:
    adapter = GitLabAdapter(project="g/p", token="t", mr_iid=7)  # nosec B106 - test fixture token, not a credential
    adapter._client = lambda: client  # type: ignore[method-assign]  # noqa: SLF001
    return adapter


# ----- fetch_commit_messages / fetch_changed_paths ----------------------------


def test_fetch_commit_messages_oldest_first_with_title_fallback() -> None:
    client = _ScriptedFullClient(commits=[
        {"message": "newest"},
        {"title": "middle-title"},
        {"message": "oldest"},
    ])
    adapter = _full_adapter(client)
    assert adapter.fetch_commit_messages() == [
        "oldest", "middle-title", "newest",
    ]


def test_fetch_commit_messages_empty() -> None:
    assert _full_adapter(_ScriptedFullClient()).fetch_commit_messages() == []


def test_fetch_changed_paths_prefers_new_path() -> None:
    client = _ScriptedFullClient(diffs=[
        {"new_path": "a.py", "old_path": "a_old.py"},
        {"new_path": None, "old_path": "deleted.py"},
        {"new_path": "", "old_path": ""},
    ])
    assert _full_adapter(client).fetch_changed_paths() == [
        "a.py", "deleted.py",
    ]


# ----- set_labels / update_body_section ---------------------------------------


def test_set_labels_keeps_human_labels_and_replaces_managed() -> None:
    client = _ScriptedFullClient(
        mr={"labels": ["prthinker/size-l", "human-tag"]}
    )
    adapter = _full_adapter(client)
    adapter.set_labels(["prthinker/size-s", "prthinker/clean"])
    put_path, payload = client.puts[0]
    assert put_path.endswith("/merge_requests/7")
    assert payload["labels"] == "human-tag,prthinker/size-s,prthinker/clean"
    label_posts = [p for p in client.posts if p[0].endswith("/labels")]
    assert [p[1]["name"] for p in label_posts] == [
        "prthinker/size-s", "prthinker/clean",
    ]


def test_update_body_section_appends_marked_block() -> None:
    client = _ScriptedFullClient(mr={"description": "original text"})
    adapter = _full_adapter(client)
    adapter.update_body_section("verdict here")
    _, payload = client.puts[0]
    assert "original text" in payload["description"]
    assert "verdict here" in payload["description"]
    assert "<!-- prthinker:body:start -->" in payload["description"]


def test_update_body_section_noop_when_unchanged() -> None:
    body = (
        "original\n\n<!-- prthinker:body:start -->\nsame\n"
        "<!-- prthinker:body:end -->\n"
    )
    client = _ScriptedFullClient(mr={"description": body})
    adapter = _full_adapter(client)
    adapter.update_body_section("same")
    assert client.puts == []


# ----- upsert_marked_comment / upsert_summary_comments -------------------------


def test_upsert_marked_comment_creates_when_absent() -> None:
    client = _ScriptedFullClient(notes=[_note(1, body="unrelated")])
    adapter = _full_adapter(client)
    new_id = adapter.upsert_marked_comment("body <!-- m -->", marker="<!-- m -->")
    assert new_id == 501
    assert client.posts[0][1]["body"] == "body <!-- m -->"


def test_upsert_marked_comment_updates_existing() -> None:
    client = _ScriptedFullClient(notes=[_note(42, body="old <!-- m -->")])
    adapter = _full_adapter(client)
    assert adapter.upsert_marked_comment("new <!-- m -->", marker="<!-- m -->") == 42
    assert client.puts[0][0].endswith("/notes/42")


def test_upsert_summary_comments_updates_creates_and_deletes() -> None:
    client = _ScriptedFullClient(notes=[
        _note(10, body=f"page1 {_MARKER}"),
        _note(11, body=f"page2 {_MARKER}"),
        _note(12, body=f"page3 {_MARKER}"),
    ])
    adapter = _full_adapter(client)
    ids = adapter.upsert_summary_comments(
        [f"new1 {_MARKER}", f"new2 {_MARKER}"]
    )
    assert ids == [10, 11]
    assert [p.rsplit("/", 1)[1] for p, _ in client.puts] == ["10", "11"]
    assert client.deletes[0].endswith("/notes/12")


def test_upsert_summary_comments_creates_overflow_pages() -> None:
    client = _ScriptedFullClient(notes=[_note(10, body=f"page1 {_MARKER}")])
    adapter = _full_adapter(client)
    ids = adapter.upsert_summary_comments(
        [f"new1 {_MARKER}", f"new2 {_MARKER}"]
    )
    assert ids == [10, 501]
    assert client.deletes == []


def test_upsert_summary_comments_empty_is_noop() -> None:
    client = _ScriptedFullClient()
    assert _full_adapter(client).upsert_summary_comments([]) == []
    assert client.posts == [] and client.puts == []


# ----- inline-review diff pre-filter -------------------------------------------


def test_submit_inline_review_prefilters_off_hunk_findings() -> None:
    client = _ScriptedFullClient(raw_diff=_HUNK_DIFF)
    adapter = _full_adapter(client)
    adapter.submit_inline_review(
        [_finding("a.py", 2), _finding("a.py", 99), _finding("zzz.py", 1)],
        summary_body=None,
        event="COMMENT",
    )
    discussions = [p for p in client.posts if p[0].endswith("/discussions")]
    assert len(discussions) == 1
    assert discussions[0][1]["position"]["new_line"] == 2


def test_submit_inline_review_fail_open_when_diff_fetch_fails() -> None:
    client = _ScriptedFullClient(raw_diff="", raw_diff_status=500)
    adapter = _full_adapter(client)
    adapter.submit_inline_review(
        [_finding("a.py", 99)], summary_body=None, event="COMMENT"
    )
    discussions = [p for p in client.posts if p[0].endswith("/discussions")]
    assert len(discussions) == 1


def test_submit_inline_review_uses_provided_diff_text() -> None:
    # raw_diffs would 500, but the caller-supplied diff is used instead:
    # off-hunk findings are still filtered (no fail-open, no re-download).
    client = _ScriptedFullClient(raw_diff="", raw_diff_status=500)
    adapter = _full_adapter(client)
    adapter.submit_inline_review(
        [_finding("a.py", 2), _finding("a.py", 99)],
        summary_body=None,
        event="COMMENT",
        diff_text=_HUNK_DIFF,
    )
    discussions = [p for p in client.posts if p[0].endswith("/discussions")]
    assert len(discussions) == 1
    assert discussions[0][1]["position"]["new_line"] == 2


def test_submit_inline_review_fail_open_when_diff_has_no_hunks() -> None:
    client = _ScriptedFullClient(raw_diff="not a diff at all")
    adapter = _full_adapter(client)
    adapter.submit_inline_review(
        [_finding("a.py", 99)], summary_body=None, event="COMMENT"
    )
    discussions = [p for p in client.posts if p[0].endswith("/discussions")]
    assert len(discussions) == 1


# ----- approvals mirror ---------------------------------------------------------


def test_submit_inline_review_approve_hits_approvals_endpoint() -> None:
    client = _ScriptedFullClient(raw_diff=_HUNK_DIFF)
    adapter = _full_adapter(client)
    adapter.submit_inline_review(
        [_finding("a.py", 2)], summary_body=None, event="APPROVE"
    )
    assert any(p[0].endswith("/merge_requests/7/approve") for p in client.posts)


def test_submit_inline_review_request_changes_unapproves() -> None:
    client = _ScriptedFullClient(raw_diff=_HUNK_DIFF)
    adapter = _full_adapter(client)
    adapter.submit_inline_review(
        [_finding("a.py", 2)], summary_body=None, event="REQUEST_CHANGES"
    )
    assert any(
        p[0].endswith("/merge_requests/7/unapprove") for p in client.posts
    )


def test_submit_inline_review_comment_leaves_approvals_alone() -> None:
    client = _ScriptedFullClient(raw_diff=_HUNK_DIFF)
    adapter = _full_adapter(client)
    adapter.submit_inline_review(
        [_finding("a.py", 2)], summary_body=None, event="COMMENT"
    )
    assert not any("approve" in p[0] for p in client.posts)


# ----- CI failure signals delegation --------------------------------------------


def test_fetch_ci_failure_signals_delegates(monkeypatch) -> None:
    from prthinker.platforms import gitlab as gitlab_mod

    seen = {}

    def _fake(project, head_sha, token, *, base_url, max_jobs, log_tail_chars):
        seen.update(
            project=project, head_sha=head_sha, token=token,
            base_url=base_url, max_jobs=max_jobs,
            log_tail_chars=log_tail_chars,
        )
        return []

    monkeypatch.setattr(
        gitlab_mod, "fetch_gitlab_ci_failure_signals", _fake
    )
    adapter = GitLabAdapter(project="g/p", token="t", mr_iid=7)  # nosec B106 - test fixture token, not a credential
    assert adapter.fetch_ci_failure_signals(
        "sha1", max_jobs=2, log_tail_chars=99
    ) == []
    assert seen == {
        "project": "g/p", "head_sha": "sha1", "token": "t",
        "base_url": "https://gitlab.com/api/v4",
        "max_jobs": 2, "log_tail_chars": 99,
    }


# ----- stale inline-note cleanup -------------------------------------------------


def test_submit_inline_review_deletes_prior_marked_notes() -> None:
    client = _ScriptedFullClient(
        raw_diff=_HUNK_DIFF,
        notes=[
            _note(70, body=f"old finding {_INLINE_MARKER}"),
            _note(71, body="human comment, must stay"),
            _note(72, body=f"old summary {_INLINE_MARKER}"),
        ],
    )
    adapter = _full_adapter(client)
    adapter.submit_inline_review(
        [_finding("a.py", 2)], summary_body="fresh summary", event="COMMENT"
    )
    deleted = sorted(int(p.rsplit("/", 1)[1]) for p in client.deletes)
    assert deleted == [70, 72]


def test_submit_inline_review_new_discussions_carry_marker() -> None:
    client = _ScriptedFullClient(raw_diff=_HUNK_DIFF)
    adapter = _full_adapter(client)
    adapter.submit_inline_review(
        [_finding("a.py", 2)], summary_body="tie-together", event="COMMENT"
    )
    discussions = [p for p in client.posts if p[0].endswith("/discussions")]
    assert _INLINE_MARKER in discussions[0][1]["body"]
    notes = [p for p in client.posts if p[0].endswith("/notes")]
    assert any(_INLINE_MARKER in p[1].get("body", "") for p in notes)


def test_submit_inline_review_no_prior_notes_deletes_nothing() -> None:
    client = _ScriptedFullClient(raw_diff=_HUNK_DIFF)
    adapter = _full_adapter(client)
    adapter.submit_inline_review(
        [_finding("a.py", 2)], summary_body=None, event="COMMENT"
    )
    assert client.deletes == []


def test_submit_inline_review_survives_notes_list_failure() -> None:
    client = _ScriptedFullClient(raw_diff=_HUNK_DIFF, notes_status=500)
    adapter = _full_adapter(client)
    adapter.submit_inline_review(
        [_finding("a.py", 2)], summary_body=None, event="COMMENT"
    )
    # The stale scan failed, so nothing was deleted — but the new
    # discussion still posted.
    discussions = [p for p in client.posts if p[0].endswith("/discussions")]
    assert len(discussions) == 1
    assert client.deletes == []


# ----- gate (commit statuses) ----------------------------------------------------


def _check_result(
    conclusion: str = "success",
    title: str = "all good",
    annotations: list[dict] | None = None,
) -> CheckResult:
    return CheckResult(
        conclusion=conclusion,  # type: ignore[arg-type]
        title=title,
        summary="s",
        error_count=0,
        warning_count=0,
        info_count=0,
        annotations=annotations or [],
    )


def test_open_gate_posts_pending_status() -> None:
    client = _ScriptedFullClient()
    adapter = _full_adapter(client)
    handle = adapter.open_gate("deadbeef", name="prthinker")
    assert handle == {"sha": "deadbeef", "name": "prthinker"}
    path, payload = client.posts[0]
    assert path.endswith("/statuses/deadbeef")
    assert payload == {"state": "pending", "name": "prthinker"}


def test_close_gate_maps_success() -> None:
    client = _ScriptedFullClient()
    adapter = _full_adapter(client)
    adapter.close_gate(
        {"sha": "deadbeef", "name": "prthinker"}, _check_result("success")
    )
    _, payload = client.posts[0]
    assert payload["state"] == "success"
    assert payload["description"] == "all good"


def test_close_gate_maps_failure_conclusions_to_failed() -> None:
    for conclusion in ("failure", "neutral"):
        client = _ScriptedFullClient()
        adapter = _full_adapter(client)
        adapter.close_gate(
            {"sha": "d" * 8, "name": "prthinker"}, _check_result(conclusion)
        )
        assert client.posts[0][1]["state"] == "failed"


def test_close_gate_truncates_description_to_255() -> None:
    client = _ScriptedFullClient()
    adapter = _full_adapter(client)
    adapter.close_gate(
        {"sha": "d" * 8, "name": "prthinker"},
        _check_result("failure", title="x" * 300),
    )
    assert client.posts[0][1]["description"] == "x" * 255


def test_close_gate_logs_omitted_annotations(caplog) -> None:
    client = _ScriptedFullClient()
    adapter = _full_adapter(client)
    with caplog.at_level("INFO", logger="prthinker.platforms.gitlab"):
        adapter.close_gate(
            {"sha": "d" * 8, "name": "prthinker"},
            _check_result("failure", annotations=[{"path": "a.py"}]),
        )
    assert "annotation(s) not attached" in caplog.text
    # The status itself still posts.
    assert client.posts[0][1]["state"] == "failed"


# ----- fetch_diff fallback --------------------------------------------------------


def test_fetch_diff_happy_path_uses_raw_diffs() -> None:
    client = _ScriptedFullClient(raw_diff=_HUNK_DIFF)
    assert _full_adapter(client).fetch_diff() == _HUNK_DIFF


def test_fetch_diff_falls_back_to_diffs_endpoint() -> None:
    client = _ScriptedFullClient(
        raw_diff_status=500,
        diffs=[{
            "old_path": "a.py",
            "new_path": "a.py",
            "diff": "@@ -1,2 +1,3 @@\n kept\n+added\n tail\n",
        }],
    )
    text = _full_adapter(client).fetch_diff()
    assert "diff --git a/a.py b/a.py" in text
    assert "--- a/a.py" in text
    assert "+++ b/a.py" in text
    assert "+added" in text


def test_fetch_diff_fallback_marks_new_and_deleted_files() -> None:
    client = _ScriptedFullClient(
        raw_diff_status=500,
        diffs=[
            {
                "old_path": "new.py",
                "new_path": "new.py",
                "new_file": True,
                "diff": "@@ -0,0 +1 @@\n+hello\n",
            },
            {
                "old_path": "gone.py",
                "new_path": "gone.py",
                "deleted_file": True,
                "diff": "@@ -1 +0,0 @@\n-bye\n",
            },
            {
                "old_path": "img.png",
                "new_path": "img.png",
                "diff": "",
            },
        ],
    )
    text = _full_adapter(client).fetch_diff()
    assert "--- /dev/null\n+++ b/new.py" in text
    assert "--- a/gone.py\n+++ /dev/null" in text
    assert "Binary files a/img.png and b/img.png differ" in text

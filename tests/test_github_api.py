"""Behaviour tests for the diff-hunk helpers in :mod:`prthinker.github_api`.

These cover the pure functions that decide whether an inline finding can
be posted (its line falls inside a diff hunk) without touching the
network: ``_new_side_lines``, ``_finding_diff_miss``,
``_filter_findings_to_diff``, and the public ``count_findings_on_diff``.
"""

from __future__ import annotations

import pytest

from prthinker import github_api
from prthinker.config import GitHubConfig
from prthinker.schemas import InlineFinding


class _Resp:
    """Minimal httpx.Response stand-in with a programmable status."""

    def __init__(self, *, status: int = 200, json_data=None, text=None) -> None:
        self.status_code = status
        self._json = json_data
        if text is not None:
            self.text = text
        else:
            self.text = "" if json_data is None else str(json_data)

    def json(self):
        return self._json

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class _ScriptedClient:
    """Records requests and replays per-method FIFO queues of _Resp."""

    def __init__(self, queues: dict[str, list[_Resp]]) -> None:
        self.requests: list[tuple[str, str]] = []
        self._queues = {k: list(v) for k, v in queues.items()}

    def __enter__(self) -> "_ScriptedClient":
        return self

    def __exit__(self, *exc) -> bool:
        return False

    def _handle(self, method: str, url: str) -> _Resp:
        self.requests.append((method, url))
        queue = self._queues.get(method, [])
        if not queue:
            raise AssertionError(f"no scripted {method} response for {url}")
        return queue.pop(0)

    def get(self, url: str, **_kw) -> _Resp:
        return self._handle("GET", url)

    def post(self, url: str, **_kw) -> _Resp:
        return self._handle("POST", url)

    def patch(self, url: str, **_kw) -> _Resp:
        return self._handle("PATCH", url)

    def delete(self, url: str, **_kw) -> _Resp:
        return self._handle("DELETE", url)


_CFG = GitHubConfig(repo="o/r", pr_number=7, token="t")  # nosec B106 - test fixture token, not a credential
_M = _CFG.comment_marker


def _methods(client: _ScriptedClient) -> list[str]:
    return [m for m, _ in client.requests]

# A two-file unified diff. ``a.py`` adds lines 1-2; ``b.py`` adds line 5.
_DIFF = (
    "diff --git a/a.py b/a.py\n"
    "--- a/a.py\n"
    "+++ b/a.py\n"
    "@@ -0,0 +1,2 @@\n"
    "+first\n"
    "+second\n"
    "diff --git a/b.py b/b.py\n"
    "--- a/b.py\n"
    "+++ b/b.py\n"
    "@@ -4,0 +5,1 @@\n"
    "+fifth\n"
)


def _finding(**kw) -> InlineFinding:
    base = {"path": "a.py", "line": 1, "comment": "do thing"}
    base.update(kw)
    return InlineFinding(**base)


# --------------------------------------------------------------------------
# _new_side_lines
# --------------------------------------------------------------------------

def test_new_side_lines_maps_each_file_to_hunk_lines():
    mapping = github_api._new_side_lines(_DIFF)
    assert mapping == {"a.py": {1, 2}, "b.py": {5}}


def test_new_side_lines_empty_diff():
    assert github_api._new_side_lines("") == {}


# --------------------------------------------------------------------------
# _finding_diff_miss
# --------------------------------------------------------------------------

def test_finding_diff_miss_on_hunk_returns_none():
    valid = github_api._new_side_lines(_DIFF)
    assert github_api._finding_diff_miss(_finding(line=2), valid) is None


def test_finding_diff_miss_line_off_hunk():
    valid = github_api._new_side_lines(_DIFF)
    reason = github_api._finding_diff_miss(_finding(line=99), valid)
    assert reason is not None
    assert "line not on a diff hunk" in reason


def test_finding_diff_miss_unknown_file():
    valid = github_api._new_side_lines(_DIFF)
    reason = github_api._finding_diff_miss(_finding(path="z.py", line=1), valid)
    assert reason is not None


def test_finding_diff_miss_multiline_start_off_hunk():
    valid = github_api._new_side_lines(_DIFF)
    # line 2 is on a hunk but start_line 99 is not -> rejected.
    finding = _finding(line=2, start_line=99)
    reason = github_api._finding_diff_miss(finding, valid)
    assert reason is not None
    assert "start_line not on a diff hunk" in reason


def test_finding_diff_miss_multiline_both_on_hunk():
    valid = github_api._new_side_lines(_DIFF)
    finding = _finding(line=2, start_line=1)
    assert github_api._finding_diff_miss(finding, valid) is None


# --------------------------------------------------------------------------
# _filter_findings_to_diff
# --------------------------------------------------------------------------

def test_filter_findings_to_diff_keeps_only_on_hunk():
    findings = [
        _finding(line=1),
        _finding(line=99),
        _finding(path="b.py", line=5),
    ]
    kept = github_api._filter_findings_to_diff(findings, _DIFF)
    assert [(f.path, f.line) for f in kept] == [("a.py", 1), ("b.py", 5)]


def test_filter_findings_to_diff_empty_input():
    assert github_api._filter_findings_to_diff([], _DIFF) == []


# --------------------------------------------------------------------------
# count_findings_on_diff
# --------------------------------------------------------------------------

def test_count_findings_on_diff_matches_filter():
    findings = [
        _finding(line=1),
        _finding(line=2),
        _finding(line=99),
        _finding(path="b.py", line=5),
        _finding(path="b.py", line=6),
    ]
    assert github_api.count_findings_on_diff(findings, _DIFF) == 3


def test_count_findings_on_diff_empty_findings():
    assert github_api.count_findings_on_diff([], _DIFF) == 0


def test_count_findings_on_diff_empty_diff():
    assert github_api.count_findings_on_diff([_finding()], "") == 0


def test_count_findings_on_diff_all_outside():
    findings = [_finding(line=50), _finding(line=51)]
    assert github_api.count_findings_on_diff(findings, _DIFF) == 0


# --------------------------------------------------------------------------
# upsert_pr_comments — multi-comment reconcile
# --------------------------------------------------------------------------

def _existing(*ids: int) -> _Resp:
    return _Resp(json_data=[{"id": i, "body": _M} for i in ids])


def test_upsert_comments_patches_and_deletes_orphans(monkeypatch):
    # 3 existing comments, 2 new pages → patch 2, delete the leftover.
    client = _ScriptedClient({
        "GET": [_existing(10, 11, 12)],
        "PATCH": [_Resp(), _Resp()],
        "DELETE": [_Resp(status=204)],
    })
    monkeypatch.setattr(github_api, "_client", lambda _t: client)
    ids = github_api.upsert_pr_comments(_CFG, [f"{_M}\nP1", f"{_M}\nP2"])
    assert ids == [10, 11]
    assert _methods(client) == ["GET", "PATCH", "PATCH", "DELETE"]
    assert ("DELETE", "/repos/o/r/issues/comments/12") in client.requests


def test_upsert_comments_creates_extra_pages(monkeypatch):
    # 1 existing, 3 pages → patch 1, create 2 (no deletes).
    client = _ScriptedClient({
        "GET": [_existing(10)],
        "PATCH": [_Resp()],
        "POST": [_Resp(json_data={"id": 20}), _Resp(json_data={"id": 21})],
    })
    monkeypatch.setattr(github_api, "_client", lambda _t: client)
    ids = github_api.upsert_pr_comments(
        _CFG, [f"{_M}\nP1", f"{_M}\nP2", f"{_M}\nP3"]
    )
    assert ids == [10, 20, 21]
    assert "DELETE" not in _methods(client)


def test_upsert_comment_singular_creates_when_none(monkeypatch):
    client = _ScriptedClient({
        "GET": [_Resp(json_data=[])],
        "POST": [_Resp(json_data={"id": 99})],
    })
    monkeypatch.setattr(github_api, "_client", lambda _t: client)
    assert github_api.upsert_pr_comment(_CFG, f"{_M}\nbody") == 99


def test_upsert_comments_rejects_body_without_marker():
    with pytest.raises(ValueError, match="marker"):
        github_api.upsert_pr_comments(_CFG, ["no marker here"])


def test_upsert_comments_empty_list_returns_empty():
    assert github_api.upsert_pr_comments(_CFG, []) == []


# --------------------------------------------------------------------------
# submit_inline_review — post BEFORE dismiss; 422 leaves prior intact
# --------------------------------------------------------------------------

def _reviews(*ids: int) -> _Resp:
    return _Resp(json_data=[{"id": i, "body": github_api._INLINE_REVIEW_MARKER}
                            for i in ids])


def test_inline_review_posts_then_dismisses_excluding_new(monkeypatch):
    monkeypatch.setattr(github_api, "fetch_pr_diff", lambda _c: _DIFF)
    # Prior review 888 has a comment (id 5); the new review 999 has one
    # (id 7) — exclude must keep 7 and only delete 5.
    pr_comments = _Resp(json_data=[
        {"id": 5, "pull_request_review_id": 888},
        {"id": 7, "pull_request_review_id": 999},
    ])
    client = _ScriptedClient({
        "POST": [_Resp(json_data={"id": 999})],
        "GET": [_reviews(999, 888), pr_comments],
        "DELETE": [_Resp(status=204)],
    })
    monkeypatch.setattr(github_api, "_client", lambda _t: client)
    review_id = github_api.submit_inline_review(_CFG, [_finding(line=1)])
    assert review_id == 999
    methods = _methods(client)
    # The new review is posted before any deletion runs.
    assert methods.index("POST") < methods.index("DELETE")
    # Only the prior review's comment (5) is deleted; the new one (7) stays.
    assert ("DELETE", "/repos/o/r/pulls/comments/5") in client.requests
    assert ("DELETE", "/repos/o/r/pulls/comments/7") not in client.requests


def test_inline_review_422_leaves_prior_comments_intact(monkeypatch):
    monkeypatch.setattr(github_api, "fetch_pr_diff", lambda _c: _DIFF)
    client = _ScriptedClient({"POST": [_Resp(status=422)]})
    monkeypatch.setattr(github_api, "_client", lambda _t: client)
    with pytest.raises(RuntimeError, match="422"):
        github_api.submit_inline_review(_CFG, [_finding(line=1)])
    # The failed post never reached the dismissal step — nothing deleted.
    assert "DELETE" not in _methods(client)


def test_inline_review_skips_when_all_off_diff(monkeypatch):
    monkeypatch.setattr(github_api, "fetch_pr_diff", lambda _c: _DIFF)
    client = _ScriptedClient({})
    monkeypatch.setattr(github_api, "_client", lambda _t: client)
    # line 999 is off every hunk → filtered out → no POST at all.
    assert github_api.submit_inline_review(_CFG, [_finding(line=999)]) is None
    assert client.requests == []


# --------------------------------------------------------------------------
# fetch_pr_diff — 406 (too large) falls back to the files API
# --------------------------------------------------------------------------

def test_fetch_pr_diff_returns_text_on_200(monkeypatch):
    client = _ScriptedClient({"GET": [_Resp(text="diff --git a/x b/x\n")]})
    monkeypatch.setattr(github_api, "_client", lambda _t: client)
    assert github_api.fetch_pr_diff(_CFG) == "diff --git a/x b/x\n"


def test_fetch_pr_diff_406_reconstructs_from_files(monkeypatch):
    files = [
        {"filename": "a.py", "status": "modified",
         "patch": "@@ -1,1 +1,2 @@\n line\n+added"},
        {"filename": "new.py", "status": "added", "patch": "@@ -0,0 +1,1 @@\n+hi"},
        {"filename": "img.png", "status": "added"},  # binary: no patch
    ]
    client = _ScriptedClient({"GET": [_Resp(status=406), _Resp(json_data=files)]})
    monkeypatch.setattr(github_api, "_client", lambda _t: client)
    diff = github_api.fetch_pr_diff(_CFG)
    # Reconstructed diff is parseable by the inline diff-hunk filter.
    valid = github_api._new_side_lines(diff)
    assert valid["a.py"] == {1, 2}
    assert valid["new.py"] == {1}
    assert "diff --git a/img.png b/img.png" in diff
    assert "Binary files" in diff


def test_file_patch_to_diff_added():
    out = github_api._file_patch_to_diff(
        {"filename": "n.py", "status": "added", "patch": "@@ -0,0 +1,1 @@\n+x"}
    )
    assert "diff --git a/n.py b/n.py" in out
    assert "--- /dev/null" in out
    assert "+++ b/n.py" in out


def test_file_patch_to_diff_removed():
    out = github_api._file_patch_to_diff(
        {"filename": "d.py", "status": "removed", "patch": "@@ -1,1 +0,0 @@\n-x"}
    )
    assert "--- a/d.py" in out
    assert "+++ /dev/null" in out


def test_file_patch_to_diff_renamed_uses_previous():
    out = github_api._file_patch_to_diff({
        "filename": "new.py", "previous_filename": "old.py",
        "status": "renamed", "patch": "@@ -1,1 +1,1 @@\n-a\n+b",
    })
    assert "diff --git a/old.py b/new.py" in out
    assert "--- a/old.py" in out
    assert "+++ b/new.py" in out


def test_file_patch_to_diff_binary_no_patch():
    out = github_api._file_patch_to_diff({"filename": "b.bin", "status": "added"})
    assert "diff --git a/b.bin b/b.bin" in out
    assert "Binary files a/b.bin and b/b.bin differ" in out
    assert "@@" not in out


def test_reconstruct_diff_paginates(monkeypatch):
    page1 = [{"filename": f"f{i}.py", "status": "added",
              "patch": "@@ -0,0 +1,1 @@\n+x"} for i in range(100)]
    page2 = [{"filename": "last.py", "status": "added",
              "patch": "@@ -0,0 +1,1 @@\n+y"}]
    client = _ScriptedClient({
        "GET": [_Resp(status=406), _Resp(json_data=page1), _Resp(json_data=page2)],
    })
    monkeypatch.setattr(github_api, "_client", lambda _t: client)
    diff = github_api.fetch_pr_diff(_CFG)
    assert "f0.py" in diff and "f99.py" in diff and "last.py" in diff

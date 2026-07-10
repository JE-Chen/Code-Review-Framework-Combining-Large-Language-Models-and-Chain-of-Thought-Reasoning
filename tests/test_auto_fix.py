"""Auto-fix pure transforms — suggestion application + conflict detection.

The git / GitHub side effects in ``prthinker.auto_fix.open_auto_fix_pr``
are not exercised here (they need a real git repo + GitHub credentials);
the pure functions are what the test suite locks in.
"""

from __future__ import annotations

import httpx

from prthinker.auto_fix import apply_suggestions_to_text, detect_conflicts
from prthinker.schemas import InlineFinding


def _f(
    *, line: int, severity: str = "warning",
    suggestion: str | None = "REPLACED",
    start_line: int | None = None,
    original: str | None = None,
) -> InlineFinding:
    return InlineFinding(
        path="x.py", line=line, severity=severity,
        comment="c", suggestion=suggestion,
        start_line=start_line, original=original,
    )


# ----- single-line replacement ------------------------------------------

def test_single_line_warning_is_applied() -> None:
    text = "a\nb\nc\n"
    findings = [_f(line=2, suggestion="B")]
    new_text, report = apply_suggestions_to_text(text, findings)
    assert new_text == "a\nB\nc\n"
    assert len(report.applied) == 1
    assert report.skipped == []


def test_error_severity_is_NOT_auto_applied() -> None:
    text = "a\nb\nc\n"
    findings = [_f(line=2, severity="error", suggestion="B")]
    new_text, report = apply_suggestions_to_text(text, findings)
    assert new_text == text
    assert report.applied == []


def test_finding_without_suggestion_is_skipped() -> None:
    text = "a\nb\nc\n"
    findings = [_f(line=2, suggestion=None)]
    new_text, report = apply_suggestions_to_text(text, findings)
    assert new_text == text
    assert report.applied == []


# ----- multi-line replacement -------------------------------------------

def test_multiline_replacement_keeps_other_lines() -> None:
    text = "a\nb\nc\nd\ne\n"
    findings = [_f(line=4, start_line=2, suggestion="X\nY\nZ")]
    new_text, report = apply_suggestions_to_text(text, findings)
    # Lines 2..4 (b, c, d) replaced with X, Y, Z.
    assert new_text == "a\nX\nY\nZ\ne\n"
    assert len(report.applied) == 1


# ----- conflict detection -----------------------------------------------

def test_overlapping_edits_keep_first_drop_second() -> None:
    text = "a\nb\nc\nd\ne\n"
    findings = [
        _f(line=3, start_line=2, suggestion="X\nY"),
        _f(line=4, start_line=3, suggestion="Q\nR"),  # overlaps line 3
    ]
    new_text, report = apply_suggestions_to_text(text, findings)
    # First wins; second is skipped.
    assert new_text == "a\nX\nY\nd\ne\n"
    assert len(report.applied) == 1
    assert len(report.skipped) == 1


def test_non_overlapping_edits_both_apply() -> None:
    text = "a\nb\nc\nd\ne\n"
    findings = [
        _f(line=2, suggestion="B"),
        _f(line=4, suggestion="D"),
    ]
    new_text, report = apply_suggestions_to_text(text, findings)
    assert new_text == "a\nB\nc\nD\ne\n"
    assert len(report.applied) == 2
    assert report.skipped == []


def test_bottom_up_application_keeps_line_numbers_stable() -> None:
    # Replace lines 5 and 2 with multi-line content. If we applied
    # top-down the second edit's indices would shift; bottom-up keeps
    # them honest.
    text = "1\n2\n3\n4\n5\n6\n"
    findings = [
        _f(line=2, suggestion="A\nB"),
        _f(line=5, suggestion="C\nD"),
    ]
    new_text, report = apply_suggestions_to_text(text, findings)
    assert new_text == "1\nA\nB\n3\n4\nC\nD\n6\n"
    assert len(report.applied) == 2


# ----- pure ConflictReport behaviour ------------------------------------

def test_detect_conflicts_first_come_priority() -> None:
    from prthinker.auto_fix import _Edit  # noqa: SLF001

    edits = [
        _Edit(start=10, end=12, replacement="x", finding_index=0),
        _Edit(start=11, end=11, replacement="y", finding_index=1),
        _Edit(start=20, end=22, replacement="z", finding_index=2),
    ]
    report = detect_conflicts(edits)
    assert [e.finding_index for e in report.applied] == [0, 2]
    assert [s.finding_index for s, _ in report.skipped] == [1]


def test_detect_conflicts_no_edges_no_overlap() -> None:
    from prthinker.auto_fix import _Edit  # noqa: SLF001

    # Touching but not overlapping: edit1 ends at 10, edit2 starts at 11.
    edits = [
        _Edit(start=1, end=10, replacement="a", finding_index=0),
        _Edit(start=11, end=20, replacement="b", finding_index=1),
    ]
    report = detect_conflicts(edits)
    assert len(report.applied) == 2
    assert report.skipped == []


# ----- GitLab draft-MR opener --------------------------------------------

def test_draft_body_renders_platform_ref() -> None:
    from prthinker.auto_fix import _draft_pr_body  # noqa: SLF001

    body = _draft_pr_body("!7", 2, 1, ["a.py"])
    assert "blocks from !7." in body
    assert "**2** suggestion(s) applied" in body
    assert "- `a.py`" in body


def test_gitlab_mr_target_default_base_url() -> None:
    from prthinker.auto_fix import GitLabMRTarget

    target = GitLabMRTarget(project="g/p", token="t", mr_iid=7)  # nosec B106 - test fixture token, not a credential
    assert target.base_url == "https://gitlab.com/api/v4"


class _ScriptedMRClient:
    """Stands in for httpx.Client; records the create-MR POST."""

    instances: list["_ScriptedMRClient"] = []

    def __init__(self, **kwargs: object) -> None:
        self.kwargs = kwargs
        self.posts: list[tuple[str, dict]] = []
        _ScriptedMRClient.instances.append(self)

    def __enter__(self) -> "_ScriptedMRClient":
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def post(self, path: str, json: dict | None = None):
        self.posts.append((path, json or {}))
        return httpx.Response(
            201,
            request=httpx.Request("POST", "http://test" + path),
            json={"iid": 55, "web_url": "https://gl.example/mr/55"},
        )


def test_open_draft_mr_payload_and_result(monkeypatch) -> None:
    from prthinker import auto_fix
    from prthinker.auto_fix import GitLabMRTarget, _open_draft_mr  # noqa: SLF001

    _ScriptedMRClient.instances.clear()
    monkeypatch.setattr(auto_fix.httpx, "Client", _ScriptedMRClient)

    target = GitLabMRTarget(project="g/p", token="t", mr_iid=7)  # nosec B106 - test fixture token, not a credential
    mr_iid, mr_url = _open_draft_mr(
        target=target,
        base_branch="main",
        head_branch="auto-fix/prthinker-mr-7",
        total_applied=1,
        total_skipped=0,
        files_changed=["a.py"],
    )
    assert (mr_iid, mr_url) == (55, "https://gl.example/mr/55")
    client = _ScriptedMRClient.instances[0]
    path, payload = client.posts[0]
    assert path == "/projects/g%2Fp/merge_requests"
    assert payload["source_branch"] == "auto-fix/prthinker-mr-7"
    assert payload["target_branch"] == "main"
    assert payload["title"].startswith("Draft: ")
    assert "!7" in payload["description"]
    assert client.kwargs["headers"]["PRIVATE-TOKEN"] == "t"


# ----- Gitea draft-PR opener ----------------------------------------------

def test_gitea_pr_target_default_base_url() -> None:
    from prthinker.auto_fix import GiteaPRTarget

    target = GiteaPRTarget(repo="o/r", token="t", pr_number=7)  # nosec B106 - test fixture token, not a credential
    assert target.base_url == "https://gitea.com/api/v1"


class _ScriptedGiteaPRClient:
    """Stands in for httpx.Client; records the create-PR POST."""

    instances: list["_ScriptedGiteaPRClient"] = []

    def __init__(self, **kwargs: object) -> None:
        self.kwargs = kwargs
        self.posts: list[tuple[str, dict]] = []
        _ScriptedGiteaPRClient.instances.append(self)

    def __enter__(self) -> "_ScriptedGiteaPRClient":
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def post(self, path: str, json: dict | None = None):
        self.posts.append((path, json or {}))
        return httpx.Response(
            201,
            request=httpx.Request("POST", "http://test" + path),
            json={"number": 66, "html_url": "https://tea.example/o/r/pulls/66"},
        )


def test_open_draft_gitea_pr_payload_and_result(monkeypatch) -> None:
    from prthinker import auto_fix
    from prthinker.auto_fix import GiteaPRTarget, _open_draft_gitea_pr  # noqa: SLF001

    _ScriptedGiteaPRClient.instances.clear()
    monkeypatch.setattr(auto_fix.httpx, "Client", _ScriptedGiteaPRClient)

    target = GiteaPRTarget(repo="o/r", token="t", pr_number=7)  # nosec B106 - test fixture token, not a credential
    number, url = _open_draft_gitea_pr(
        target=target,
        base_branch="main",
        head_branch="auto-fix/prthinker-pr-7",
        total_applied=1,
        total_skipped=0,
        files_changed=["a.py"],
    )
    assert (number, url) == (66, "https://tea.example/o/r/pulls/66")
    client = _ScriptedGiteaPRClient.instances[0]
    path, payload = client.posts[0]
    assert path == "/repos/o/r/pulls"
    assert payload["head"] == "auto-fix/prthinker-pr-7"
    assert payload["base"] == "main"
    # Gitea has no draft flag; the WIP title prefix stands in.
    assert payload["title"].startswith("WIP: ")
    assert "#7" in payload["body"]
    assert client.kwargs["headers"]["Authorization"] == "token t"


def test_open_auto_fix_gitea_pr_none_when_nothing_applies(tmp_path) -> None:
    # The target file is absent, so no edit lands and the flow stops
    # before any git or network side effect.
    from prthinker.auto_fix import GiteaPRTarget, open_auto_fix_gitea_pr

    target = GiteaPRTarget(repo="o/r", token="t", pr_number=7)  # nosec B106 - test fixture token, not a credential
    result = open_auto_fix_gitea_pr(
        target, {"missing.py": [_f(line=1)]}, "main", tmp_path
    )
    assert result is None

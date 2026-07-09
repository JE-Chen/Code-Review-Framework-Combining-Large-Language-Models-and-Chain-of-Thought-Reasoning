"""Tests for the review-pr auto-file-issues hook (:mod:`prthinker.cli_review_issues`)."""

from __future__ import annotations

import argparse

import httpx

from prthinker import issue_autofile
from prthinker.cli_review_issues import _issue_labels, _maybe_file_issues
from prthinker.issue_tracker import GitHubIssueTracker, GitLabIssueTracker
from prthinker.pipeline import ReviewResult
from prthinker.platforms import PlatformKind
from prthinker.schemas import InlineFinding

_DIFF = (
    "diff --git a/a.py b/a.py\n"
    "--- a/a.py\n"
    "+++ b/a.py\n"
    "@@ -1,1 +1,1 @@\n"
    "-old\n"
    "+new\n"
)


class _Adapter:
    """Platform-adapter stand-in exposing an optional base_url."""

    def __init__(self, base_url: str = "") -> None:
        if base_url:
            self.base_url = base_url


def _args(**overrides) -> argparse.Namespace:
    base = {
        "auto_file_issues": "off-diff", "issue_labels": "prthinker",
        "dry_run": False, "repo": "octo/demo", "github_token": "tok",
    }
    base.update(overrides)
    return argparse.Namespace(**base)


def _result(findings) -> ReviewResult:
    return ReviewResult(code_diff=_DIFF, rag_docs=[], inline_findings=findings)


def _on_diff() -> InlineFinding:
    return InlineFinding(path="a.py", line=1, severity="warning", comment="on diff")


def _off_diff() -> InlineFinding:
    return InlineFinding(path="b.py", line=9, severity="warning", comment="off diff")


def _capture_filing(monkeypatch):
    calls: list[dict] = []

    def fake_file(tracker, findings, *, labels):
        calls.append({"tracker": tracker, "findings": findings, "labels": labels})
        return []

    monkeypatch.setattr(issue_autofile, "file_findings_as_issues", fake_file)
    return calls


def test_labels_parse_and_strip():
    assert _issue_labels(_args(issue_labels=" a, b ,")) == ("a", "b")
    assert _issue_labels(_args(issue_labels="")) == ()


def test_mode_none_files_nothing(monkeypatch):
    calls = _capture_filing(monkeypatch)
    _maybe_file_issues(
        _args(auto_file_issues="none"), _result([_off_diff()]),
        PlatformKind.GITHUB, _Adapter())
    assert calls == []


def test_dry_run_files_nothing(monkeypatch):
    calls = _capture_filing(monkeypatch)
    _maybe_file_issues(
        _args(dry_run=True), _result([_off_diff()]),
        PlatformKind.GITHUB, _Adapter())
    assert calls == []


def test_gitea_platform_skips(monkeypatch):
    calls = _capture_filing(monkeypatch)
    _maybe_file_issues(
        _args(), _result([_off_diff()]), PlatformKind.GITEA, _Adapter())
    assert calls == []


def test_off_diff_mode_selects_only_off_diff_findings(monkeypatch):
    calls = _capture_filing(monkeypatch)
    _maybe_file_issues(
        _args(), _result([_on_diff(), _off_diff()]),
        PlatformKind.GITHUB, _Adapter())
    assert len(calls) == 1
    assert [finding.path for finding in calls[0]["findings"]] == ["b.py"]
    tracker = calls[0]["tracker"]
    assert isinstance(tracker, GitHubIssueTracker)
    assert tracker.repo == "octo/demo"
    assert calls[0]["labels"] == ("prthinker",)


def test_gitlab_platform_builds_gitlab_tracker(monkeypatch):
    calls = _capture_filing(monkeypatch)
    _maybe_file_issues(
        _args(repo="group/proj"), _result([_off_diff()]),
        PlatformKind.GITLAB, _Adapter("https://git.corp/api/v4"))
    tracker = calls[0]["tracker"]
    assert isinstance(tracker, GitLabIssueTracker)
    assert tracker.repo == "group/proj"
    assert tracker.base_url == "https://git.corp/api/v4"


def test_gitlab_without_adapter_url_uses_default(monkeypatch):
    calls = _capture_filing(monkeypatch)
    _maybe_file_issues(
        _args(repo="group/proj"), _result([_off_diff()]),
        PlatformKind.GITLAB, _Adapter())
    assert calls[0]["tracker"].base_url == "https://gitlab.com/api/v4"


def test_all_mode_selects_every_finding(monkeypatch):
    calls = _capture_filing(monkeypatch)
    _maybe_file_issues(
        _args(auto_file_issues="all"), _result([_on_diff(), _off_diff()]),
        PlatformKind.GITHUB, _Adapter())
    assert [finding.path for finding in calls[0]["findings"]] == ["a.py", "b.py"]


def test_no_selected_findings_files_nothing(monkeypatch):
    calls = _capture_filing(monkeypatch)
    _maybe_file_issues(
        _args(), _result([_on_diff()]), PlatformKind.GITHUB, _Adapter())
    assert calls == []


def test_api_failure_is_swallowed(monkeypatch):
    def boom(*_a, **_kw):
        raise httpx.HTTPError("api down")

    monkeypatch.setattr(issue_autofile, "file_findings_as_issues", boom)
    # Must not raise — the review already succeeded.
    _maybe_file_issues(
        _args(), _result([_off_diff()]), PlatformKind.GITHUB, _Adapter())

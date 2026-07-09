"""Tests for the ``issue-autofix`` CLI command wiring."""

from __future__ import annotations

import argparse
import json

import prthinker.issue_autofix_cli as cli
from prthinker.cli_parser import _build_parser
from prthinker.issue_autofix import IssueAutoFixResult
from prthinker.issue_tracker import GitLabIssueTracker, Issue


class _ScriptedBackend:
    def __init__(self, response: str) -> None:
        self._response = response

    def generate(self, prompt: str, max_new_tokens: int) -> str:
        return self._response


class _FakeTracker:
    """IssueTracker stand-in serving canned issues."""

    def __init__(self, issues=()) -> None:
        self._issues = list(issues)
        self.fetched: list[int] = []
        self.listed: list[tuple[str, int]] = []

    def fetch_issue(self, number):
        self.fetched.append(number)
        return next(issue for issue in self._issues if issue.number == number)

    def list_open_issues(self, *, label="", limit=50):
        self.listed.append((label, limit))
        return list(self._issues)[:limit]


def _patch_backend(monkeypatch, response: str) -> None:
    monkeypatch.setattr(cli, "_build_config", lambda args: object())
    monkeypatch.setattr(cli, "create_backend", lambda config: _ScriptedBackend(response))


def _patch_tracker(monkeypatch, issues=()) -> _FakeTracker:
    tracker = _FakeTracker(issues)
    monkeypatch.setattr(cli, "create_issue_tracker", lambda *_a, **_kw: tracker)
    return tracker


def _args(**overrides) -> argparse.Namespace:
    base = {
        "repo": "octo/demo", "platform": "github", "github_token": "tok",
        "gitlab_url": "", "issue_number": 5, "issue_label": None, "limit": 3,
        "workdir": None, "retriever": "lexical", "top_k": 5, "max_retries": 0,
        "open_pr": False, "no_draft": False, "base_branch": "",
        "branch_prefix": "issue-fix", "test_cmd": None, "test_timeout": 600.0,
        "output": None,
    }
    base.update(overrides)
    return argparse.Namespace(**base)


def test_parser_registers_issue_autofix_with_backend_args():
    parser = _build_parser()
    args = parser.parse_args([
        "issue-autofix", "--repo", "octo/demo", "--workdir", ".",
        "--issue-number", "5", "--github-token", "tok",
    ])
    assert args.command == "issue-autofix"
    assert args.platform == "github"  # default
    assert args.retriever == "graph-rerank"  # default
    assert args.open_pr is False  # dry-run by default
    assert hasattr(args, "backend")  # inherited common backend args


def test_parser_accepts_gitlab_platform():
    parser = _build_parser()
    args = parser.parse_args([
        "issue-autofix", "--repo", "group/proj", "--workdir", ".",
        "--issue-number", "5", "--platform", "gitlab",
        "--gitlab-url", "https://git.corp/api/v4",
    ])
    assert (args.platform, args.gitlab_url) == (
        "gitlab", "https://git.corp/api/v4")


def test_gitlab_platform_builds_gitlab_tracker(monkeypatch, tmp_path):
    _patch_backend(monkeypatch, "[]")
    built = {}

    def spy(kind, **kw):
        built["kind"], built["kw"] = kind, kw
        return _FakeTracker([Issue(5, "t", "b")])

    monkeypatch.setattr(cli, "create_issue_tracker", spy)
    cli.command(_args(platform="gitlab", repo="group/proj",
                      gitlab_url="https://git.corp/api/v4", workdir=tmp_path))
    assert built["kind"] == "gitlab"
    assert built["kw"] == {"repo": "group/proj", "token": "tok",
                           "base_url": "https://git.corp/api/v4"}


def test_real_factory_wires_gitlab_tracker():
    # The CLI passes --gitlab-url through to the strategy unchanged.
    tracker = cli.create_issue_tracker(
        "gitlab", repo="g/p", token="t", base_url="https://git.corp/api/v4")
    assert isinstance(tracker, GitLabIssueTracker)
    assert tracker.base_url == "https://git.corp/api/v4"


class TestArgValidation:
    def test_missing_token_exits_2(self, capsys):
        assert cli.command(_args(github_token="")) == 2
        assert "github-token" in capsys.readouterr().err

    def test_needs_exactly_one_selector(self, capsys):
        assert cli.command(_args(issue_number=None, issue_label=None)) == 2
        assert cli.command(_args(issue_number=5, issue_label="bug")) == 2
        assert "exactly one" in capsys.readouterr().err

    def test_issue_number_zero_counts_as_selected(self, monkeypatch, tmp_path):
        # Regression: 0 is falsy but is a deliberate selector value.
        _patch_backend(monkeypatch, "[]")
        tracker = _patch_tracker(monkeypatch, [Issue(0, "t", "b")])
        cli.command(_args(issue_number=0, workdir=tmp_path))
        assert tracker.fetched == [0]


class TestDryRun:
    def test_emits_proposal_and_patch_without_mutation(
            self, tmp_path, monkeypatch, capsys):
        (tmp_path / "a.py").write_text("def f():\n    return WRONG\n", encoding="utf-8")
        _patch_backend(monkeypatch, json.dumps(
            [{"file": "a.py", "original": "return WRONG",
              "replacement": "return RIGHT"}]))
        _patch_tracker(monkeypatch, [Issue(5, "bad return", "fix it")])
        rc = cli.command(_args(workdir=tmp_path))
        assert rc == 0
        payload = json.loads(capsys.readouterr().out)
        assert payload[0]["issue_number"] == 5
        assert payload[0]["valid"] is True
        assert "+    return RIGHT" in payload[0]["patch"]
        # Dry run must not mutate the work-tree.
        assert "WRONG" in (tmp_path / "a.py").read_text(encoding="utf-8")

    def test_invalid_proposal_exits_1(self, tmp_path, monkeypatch, capsys):
        (tmp_path / "a.py").write_text("x = 1\n", encoding="utf-8")
        _patch_backend(monkeypatch, "not json at all")
        _patch_tracker(monkeypatch, [Issue(5, "bad", "fix")])
        assert cli.command(_args(workdir=tmp_path)) == 1
        assert json.loads(capsys.readouterr().out)[0]["valid"] is False

    def test_label_mode_lists_open_issues(self, tmp_path, monkeypatch, capsys):
        (tmp_path / "a.py").write_text("x = 1\n", encoding="utf-8")
        _patch_backend(monkeypatch, "[]")
        tracker = _patch_tracker(monkeypatch, [Issue(9, "t", "b")])
        cli.command(_args(issue_number=None, issue_label="bug",
                          workdir=tmp_path))
        payload = json.loads(capsys.readouterr().out)
        assert payload[0]["issue_number"] == 9
        assert tracker.listed == [("bug", 3)]

    def test_writes_output_file(self, tmp_path, monkeypatch):
        (tmp_path / "a.py").write_text("x = 1\n", encoding="utf-8")
        _patch_backend(monkeypatch, "[]")
        _patch_tracker(monkeypatch, [Issue(5, "t", "b")])
        out = tmp_path / "out" / "results.json"
        cli.command(_args(workdir=tmp_path, output=out))
        assert json.loads(out.read_text(encoding="utf-8"))[0]["issue_number"] == 5


class TestFullRun:
    def test_single_issue_calls_auto_fix_with_options(self, tmp_path, monkeypatch, capsys):
        _patch_backend(monkeypatch, "[]")
        tracker = _patch_tracker(monkeypatch, [Issue(5, "t", "b")])
        captured = {}

        def fake_auto_fix(proposer, got_tracker, issue, workdir, *, options):
            captured["tracker"] = got_tracker
            captured["options"] = options
            captured["issue"] = issue
            return IssueAutoFixResult(issue.number, True, branch="issue-fix/5",
                                      pr_number=12, pr_url="https://x/pr/12")

        monkeypatch.setattr(cli, "auto_fix_issue", fake_auto_fix)
        rc = cli.command(_args(
            workdir=tmp_path, open_pr=True, no_draft=True,
            base_branch="develop", test_cmd="pytest -x"))
        assert rc == 0
        assert captured["tracker"] is tracker
        assert captured["issue"].number == 5
        assert captured["options"].draft is False
        assert captured["options"].base_branch == "develop"
        assert captured["options"].test_cmd == ("pytest", "-x")
        payload = json.loads(capsys.readouterr().out)
        assert payload[0]["pr_number"] == 12

    def test_label_mode_uses_batch_loop_and_reports_failures(
            self, tmp_path, monkeypatch, capsys):
        _patch_backend(monkeypatch, "[]")
        _patch_tracker(monkeypatch)
        monkeypatch.setattr(
            cli, "fix_open_issues",
            lambda *_a, **_kw: [IssueAutoFixResult(1, True),
                                IssueAutoFixResult(2, False, "test command failed")])
        rc = cli.command(_args(
            issue_number=None, issue_label="bug", workdir=tmp_path, open_pr=True))
        assert rc == 1  # one failure -> non-zero
        payload = json.loads(capsys.readouterr().out)
        assert [row["valid"] for row in payload] == [True, False]

"""Tests for the end-to-end issue auto-fix loop (:mod:`prthinker.issue_autofix`)."""

from __future__ import annotations

import subprocess

import httpx

from prthinker.execution_sandbox import ExecutionResult
from prthinker.issue_autofix import (
    IssueFixOptions,
    auto_fix_issue,
    fix_open_issues,
)
from prthinker.issue_fix import FixEdit, IssueFixProposal
from prthinker.issue_tracker import Issue

_ISSUE = Issue(5, "f returns wrong value", "should return RIGHT")


class _FakeTracker:
    """IssueTracker stand-in recording PR opens and issue comments."""

    def __init__(self, *, open_issues=(), branch="main",
                 comment_error=None, forbid_default_branch=False) -> None:
        self._open_issues = list(open_issues)
        self._branch = branch
        self._comment_error = comment_error
        self._forbid_default_branch = forbid_default_branch
        self.pr_calls: list[dict] = []
        self.comments: list[tuple[int, str]] = []

    def list_open_issues(self, *, label="", limit=50):
        del label, limit
        return list(self._open_issues)

    def default_branch(self):
        if self._forbid_default_branch:
            raise AssertionError("default_branch should not be called")
        return self._branch

    def open_pull_request(self, **kw):
        self.pr_calls.append(kw)
        return 12, "https://x/pr/12"

    def add_issue_comment(self, number, body):
        if self._comment_error is not None:
            raise self._comment_error
        self.comments.append((number, body))
        return 1


class _FakeProposer:
    def __init__(self, proposal: IssueFixProposal) -> None:
        self._proposal = proposal
        self.calls: list[str] = []

    def propose(self, issue: str, workdir) -> IssueFixProposal:
        self.calls.append(issue)
        return self._proposal


class _GitRecorder:
    def __init__(self, branch: str = "main") -> None:
        self.calls: list[tuple[str, ...]] = []
        self._branch = branch
        self.fail_on: str | None = None

    def __call__(self, workdir, *args: str) -> str:
        self.calls.append(args)
        if self.fail_on and args[0] == self.fail_on:
            raise subprocess.CalledProcessError(1, ["git", *args])
        if args == ("rev-parse", "--abbrev-ref", "HEAD"):
            return self._branch
        return ""


class _FakeExecutor:
    def __init__(self, exit_code: int = 0) -> None:
        self.commands: list[tuple[str, ...]] = []
        self._exit_code = exit_code

    def run(self, command, workdir, timeout) -> ExecutionResult:
        self.commands.append(tuple(command))
        return ExecutionResult(exit_code=self._exit_code)


def _valid_proposal() -> IssueFixProposal:
    return IssueFixProposal(
        localized_files=("a.py",),
        edits=(FixEdit("a.py", "return WRONG", "return RIGHT"),),
        valid=True,
    )


def _write_target_file(tmp_path) -> None:
    (tmp_path / "a.py").write_text("def f():\n    return WRONG\n", encoding="utf-8")


class TestAutoFixIssue:
    def test_invalid_proposal_stops_before_git(self, tmp_path):
        tracker = _FakeTracker()
        git = _GitRecorder()
        proposer = _FakeProposer(IssueFixProposal(reason="no files localised"))
        result = auto_fix_issue(proposer, tracker, _ISSUE, tmp_path, git=git)
        assert result.valid is False
        assert result.reason == "no files localised"
        assert git.calls == [] and tracker.pr_calls == []

    def test_proposer_sees_title_and_body(self, tmp_path):
        proposer = _FakeProposer(IssueFixProposal(reason="x"))
        auto_fix_issue(proposer, _FakeTracker(), _ISSUE, tmp_path, git=_GitRecorder())
        assert proposer.calls == ["f returns wrong value\n\nshould return RIGHT"]

    def test_happy_path_applies_commits_and_opens_pr(self, tmp_path):
        tracker = _FakeTracker()
        _write_target_file(tmp_path)
        git = _GitRecorder()
        result = auto_fix_issue(
            _FakeProposer(_valid_proposal()), tracker, _ISSUE, tmp_path, git=git)
        assert result.valid is True
        assert result.files_changed == ("a.py",)
        assert result.branch == "issue-fix/5"
        assert (result.pr_number, result.pr_url) == (12, "https://x/pr/12")
        assert "return RIGHT" in (tmp_path / "a.py").read_text(encoding="utf-8")
        assert ("checkout", "-B", "issue-fix/5") in git.calls
        assert ("push", "--force-with-lease", "origin", "issue-fix/5") in git.calls
        commit = next(c for c in git.calls if c[0] == "commit")
        assert commit[2] == "fix: resolve issue #5"
        assert tracker.pr_calls[0]["head"] == "issue-fix/5"
        assert tracker.pr_calls[0]["base"] == "main"
        assert tracker.pr_calls[0]["draft"] is True
        assert "Fixes #5" in tracker.pr_calls[0]["body"]
        assert tracker.comments == [
            (5, "An automated fix was proposed in https://x/pr/12.")]

    def test_edits_changing_no_files_stop_cleanly(self, tmp_path):
        tracker = _FakeTracker()
        (tmp_path / "a.py").write_text("already RIGHT\n", encoding="utf-8")
        result = auto_fix_issue(
            _FakeProposer(_valid_proposal()), tracker, _ISSUE, tmp_path,
            git=_GitRecorder())
        assert result.valid is False
        assert result.reason == "edits changed no files"
        assert tracker.pr_calls == []

    def test_failing_test_gate_blocks_the_pr(self, tmp_path):
        tracker = _FakeTracker()
        _write_target_file(tmp_path)
        options = IssueFixOptions(test_cmd=("pytest", "-x"))
        result = auto_fix_issue(
            _FakeProposer(_valid_proposal()), tracker, _ISSUE, tmp_path,
            options=options, executor=_FakeExecutor(exit_code=1),
            git=_GitRecorder())
        assert result.valid is False
        assert result.test_passed is False
        assert result.reason == "test command failed"
        assert tracker.pr_calls == []

    def test_passing_test_gate_reaches_the_pr(self, tmp_path):
        tracker = _FakeTracker()
        _write_target_file(tmp_path)
        executor = _FakeExecutor(exit_code=0)
        result = auto_fix_issue(
            _FakeProposer(_valid_proposal()), tracker, _ISSUE, tmp_path,
            options=IssueFixOptions(test_cmd=("pytest", "-x")),
            executor=executor, git=_GitRecorder())
        assert result.valid is True and result.test_passed is True
        assert executor.commands == [("pytest", "-x")]
        assert len(tracker.pr_calls) == 1

    def test_explicit_base_branch_skips_default_lookup(self, tmp_path):
        tracker = _FakeTracker(forbid_default_branch=True)
        _write_target_file(tmp_path)
        options = IssueFixOptions(base_branch="develop", draft=False)
        auto_fix_issue(
            _FakeProposer(_valid_proposal()), tracker, _ISSUE, tmp_path,
            options=options, git=_GitRecorder())
        assert tracker.pr_calls[0]["base"] == "develop"
        assert tracker.pr_calls[0]["draft"] is False

    def test_issue_comment_failure_never_fails_the_fix(self, tmp_path):
        tracker = _FakeTracker(comment_error=httpx.HTTPError("comment down"))
        _write_target_file(tmp_path)
        result = auto_fix_issue(
            _FakeProposer(_valid_proposal()), tracker, _ISSUE, tmp_path,
            git=_GitRecorder())
        assert result.valid is True


class TestFixOpenIssues:
    def test_restores_starting_ref_between_issues(self, tmp_path):
        tracker = _FakeTracker(
            open_issues=[Issue(1, "t1", "b1"), Issue(2, "t2", "b2")])
        git = _GitRecorder(branch="work")
        results = fix_open_issues(
            _FakeProposer(IssueFixProposal(reason="nope")), tracker, tmp_path,
            git=git)
        assert [r.valid for r in results] == [False, False]
        assert git.calls.count(("checkout", "--force", "work")) == 2

    def test_detached_head_falls_back_to_sha(self, tmp_path):
        def git(workdir, *args):
            if args == ("rev-parse", "--abbrev-ref", "HEAD"):
                return "HEAD"
            assert args == ("rev-parse", "HEAD")
            return "abc123"

        assert fix_open_issues(
            _FakeProposer(IssueFixProposal()), _FakeTracker(), tmp_path,
            git=git) == []

    def test_one_git_failure_does_not_stop_the_batch(self, tmp_path):
        tracker = _FakeTracker(
            open_issues=[Issue(1, "t1", "b1"), Issue(2, "t2", "b2")])
        _write_target_file(tmp_path)
        git = _GitRecorder()
        git.fail_on = "push"
        results = fix_open_issues(
            _FakeProposer(_valid_proposal()), tracker, tmp_path, git=git)
        assert len(results) == 2
        assert all(r.valid is False for r in results)
        # First issue dies on the push; the fake git cannot restore the
        # work-tree, so the second sees the already-applied edit and stops
        # on the no-files-changed guard instead of crashing the batch.
        assert "git" in results[0].reason
        assert results[1].reason == "edits changed no files"

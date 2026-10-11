"""Real worktree integration verifies isolation, retries and persistent dedup."""

from pathlib import Path

import pytest

from prthinker.execution_sandbox import ExecutionResult
from prthinker.issue_fix import FixEdit, IssueFixProposal
from prthinker.issue_tracker import Issue
from prthinker.repair_loop import (
    RepairJournal,
    RepairLimits,
    RepairLoop,
    run_git,
    validate_proposal,
)


def repository(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    run_git(repo, "init")
    run_git(repo, "config", "user.email", "test@example.invalid")
    run_git(repo, "config", "user.name", "Test")
    (repo / "mod.py").write_text("VALUE = 1\n")
    run_git(repo, "add", "mod.py")
    run_git(repo, "commit", "-m", "initial")
    return repo


class Proposer:
    def __init__(self):
        self.workdirs = []
        self.prompts = []

    def propose(self, text, workdir):
        self.workdirs.append(workdir)
        self.prompts.append(text)
        return IssueFixProposal(("mod.py",), (FixEdit("mod.py", "VALUE = 1", "VALUE = 2"),), True)


class Executor:
    def __init__(self, codes):
        self.codes = iter(codes)

    def run(self, command, workdir, timeout):
        assert command and timeout > 0
        assert (workdir / "mod.py").read_text() == "VALUE = 2\n"
        return ExecutionResult(next(self.codes), stderr="failed test")


def test_isolation_retry_and_dedup(tmp_path):
    repo = repository(tmp_path)
    proposer = Proposer()
    loop = RepairLoop(proposer, Executor([1, 0]), lambda _patch, _wd: True,
                      RepairJournal(tmp_path / "audit.sqlite"))
    issue = Issue(1, "wrong value", "use 2")
    result = loop.run(issue, repo, ("test",))
    assert result.status == "verified" and result.attempts == 2
    assert Path(result.patch_path).is_file()
    assert "+VALUE = 2" in Path(result.patch_path).read_text()
    assert (repo / "mod.py").read_text() == "VALUE = 1\n"
    assert run_git(repo, "status", "--porcelain") == ""
    assert all(not path.exists() for path in proposer.workdirs)
    assert "failed test" in proposer.prompts[1]
    assert loop.run(issue, repo, ("test",)).status == "deduplicated"


def test_post_review_rejection_and_test_requirement(tmp_path):
    repo = repository(tmp_path)
    loop = RepairLoop(Proposer(), Executor([0]), lambda _patch, _wd: False,
                      RepairJournal(tmp_path / "audit.sqlite"), limits=RepairLimits(attempts=1))
    with pytest.raises(ValueError, match="verification"):
        loop.run(Issue(2, "bug", ""), repo, ())
    assert loop.run(Issue(2, "bug", ""), repo, ("test",)).status == "exhausted"
    assert (repo / "mod.py").read_text() == "VALUE = 1\n"


@pytest.mark.parametrize("path", ["../escape.py", "C:\\escape.py", ".git/config", "/etc/passwd"])
def test_unsafe_paths_are_rejected(tmp_path, path):
    proposal = IssueFixProposal((), (FixEdit(path, "", "x"),), True)
    assert validate_proposal(proposal, tmp_path, RepairLimits()) == "unsafe edit path"


def test_composed_invalid_python_is_rejected(tmp_path):
    (tmp_path / "mod.py").write_text("x = 1")
    proposal = IssueFixProposal((), (FixEdit("mod.py", "x = 1", "def :"),), True)
    assert "invalid syntax" in validate_proposal(proposal, tmp_path, RepairLimits())

"""Auto-fix tracker issues end-to-end — fetch, propose, verify, open a PR.

Closes the loop that :mod:`prthinker.issue_fix` opens: where the proposer
turns issue text into validated edits, this module drives the whole
repair — apply the edits to a work-tree, optionally gate on a test
command, commit them to a fresh branch, push, open a pull request (GitHub)
or merge request (GitLab) that ``Fixes #N``, and leave a link back on the
issue. Platform specifics live entirely in the injected
:class:`~prthinker.issue_tracker.IssueTracker` strategy.

Layering matches :mod:`prthinker.auto_fix`: the git and tracker side
effects are isolated behind an injectable ``git`` runner and the tracker
strategy, so tests drive the full flow with fakes and never touch a
network or a real repository.

The work-tree is mutated (edits applied, branches created). Point it at a
dedicated scratch clone, not a working checkout; batch mode restores the
starting ref between issues but does not undo untracked files.

Runner-safe: ``httpx`` (via issue_tracker) + stdlib.
"""

from __future__ import annotations

import logging
import subprocess  # nosec B404 — git via arg lists, shell=False
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Protocol

import httpx

from prthinker.execution_sandbox import Executor, LocalExecutor
from prthinker.issue_fix import IssueFixProposal, apply_to_workdir, validate_fix
from prthinker.issue_tracker import Issue, IssueTracker

log = logging.getLogger(__name__)

_DEFAULT_TEST_TIMEOUT = 600.0
_DEFAULT_BATCH_LIMIT = 3
_TITLE_CAP = 60
_REASON_CAP = 300

GitRunner = Callable[..., str]


class _Proposer(Protocol):
    """The proposer surface this module needs (IssueFixProposer fits)."""

    def propose(self, issue: str, workdir: Path) -> IssueFixProposal:
        """Return validated fix edits for ``issue`` against the work-tree."""


def _run_git(workdir: Path, *args: str) -> str:
    """Run one git command in ``workdir`` with an arg list; raise on failure."""
    proc = subprocess.run(  # nosec B603 B607 — fixed git exe, arg list, no shell
        ["git", *args], cwd=str(workdir), capture_output=True,
        text=True, check=True, encoding="utf-8",
    )
    return proc.stdout.strip()


@dataclass(frozen=True)
class IssueFixOptions:
    """Knobs for one auto-fix run — branching, PR shape, and the test gate."""

    branch_prefix: str = "issue-fix"
    base_branch: str = ""  # empty -> the repository's default branch
    draft: bool = True
    test_cmd: tuple[str, ...] = ()
    test_timeout: float = _DEFAULT_TEST_TIMEOUT
    comment_on_issue: bool = True


@dataclass(frozen=True)
class IssueAutoFixResult:
    """What one issue's auto-fix attempt produced (or why it stopped)."""

    issue_number: int
    valid: bool
    reason: str = ""
    files_changed: tuple[str, ...] = ()
    branch: str = ""
    pr_number: int | None = None
    pr_url: str = ""
    test_passed: bool | None = None


def _test_gate(
    proposal: IssueFixProposal, workdir: Path, options: IssueFixOptions,
    executor: Executor,
) -> bool:
    """Run the optional test command against the applied fix.

    ``validate_fix`` re-applies the edits first; on an already-applied
    work-tree every ``original`` snippet is gone, so the re-apply is a
    no-op and only the command run matters.
    """
    validation = validate_fix(
        proposal, workdir, options.test_cmd, executor,
        timeout=options.test_timeout,
    )
    return validation.passed


def _publish_fix(
    tracker: IssueTracker, issue: Issue, workdir: Path,
    changed: tuple[str, ...], options: IssueFixOptions, git: GitRunner,
) -> tuple[str, int, str]:
    """Commit the applied fix to a branch, push, and open the fix PR / MR."""
    branch = f"{options.branch_prefix}/{issue.number}"
    git(workdir, "checkout", "-B", branch)
    git(workdir, "add", *changed)
    git(workdir, "commit", "-m", f"fix: resolve issue #{issue.number}")
    git(workdir, "push", "--force-with-lease", "origin", branch)
    base = options.base_branch or tracker.default_branch()
    pr_number, pr_url = tracker.open_pull_request(
        title=f"fix: {issue.title[:_TITLE_CAP]} (#{issue.number})",
        body=_pr_body(issue, changed, options),
        head=branch, base=base, draft=options.draft,
    )
    return branch, pr_number, pr_url


def _pr_body(issue: Issue, changed: tuple[str, ...], options: IssueFixOptions) -> str:
    """Markdown body for the fix PR — closes the issue, lists the changes."""
    lines = [
        f"Fixes #{issue.number}.",
        "",
        "Automatically proposed fix for the linked issue.",
        "",
        f"### Files changed ({len(changed)})",
        "",
        *[f"- `{path}`" for path in changed],
    ]
    if options.test_cmd:
        lines += ["", f"Validated by running: `{' '.join(options.test_cmd)}`"]
    lines += ["", "Review the diff before merging."]
    return "\n".join(lines)


def _comment_best_effort(tracker: IssueTracker, issue: Issue, pr_url: str) -> None:
    """Link the fix PR / MR from the issue; a failure never fails the fix."""
    try:
        tracker.add_issue_comment(
            issue.number, f"An automated fix was proposed in {pr_url}.")
    except httpx.HTTPError as exc:
        log.warning("Could not comment on issue #%d: %s", issue.number, exc)


def auto_fix_issue(
    proposer: _Proposer,
    tracker: IssueTracker,
    issue: Issue,
    workdir: Path,
    *,
    options: IssueFixOptions = IssueFixOptions(),
    executor: Executor | None = None,
    git: GitRunner = _run_git,
) -> IssueAutoFixResult:
    """Propose, verify, and publish a fix for one issue; report the outcome.

    Stops (without touching git or the API) when the proposal is invalid,
    changes no files, or fails the test gate — every stop is an explicit
    ``reason`` on the result, never an exception.
    """
    workdir = Path(workdir)
    issue_text = f"{issue.title}\n\n{issue.body}".strip()
    proposal = proposer.propose(issue_text, workdir)
    if not proposal.valid:
        return IssueAutoFixResult(issue.number, False, proposal.reason)
    changed = tuple(apply_to_workdir(proposal, workdir))
    if not changed:
        return IssueAutoFixResult(issue.number, False, "edits changed no files")
    test_passed: bool | None = None
    if options.test_cmd:
        test_passed = _test_gate(proposal, workdir, options, executor or LocalExecutor())
        if not test_passed:
            return IssueAutoFixResult(
                issue.number, False, "test command failed", changed,
                test_passed=False)
    branch, pr_number, pr_url = _publish_fix(
        tracker, issue, workdir, changed, options, git)
    if options.comment_on_issue:
        _comment_best_effort(tracker, issue, pr_url)
    return IssueAutoFixResult(
        issue.number, True, "", changed, branch, pr_number, pr_url, test_passed)


def _starting_ref(workdir: Path, git: GitRunner) -> str:
    """The branch (or detached SHA) to restore between batch issues."""
    ref = git(workdir, "rev-parse", "--abbrev-ref", "HEAD")
    if ref == "HEAD":
        ref = git(workdir, "rev-parse", "HEAD")
    return ref


def fix_open_issues(
    proposer: _Proposer,
    tracker: IssueTracker,
    workdir: Path,
    *,
    label: str = "",
    limit: int = _DEFAULT_BATCH_LIMIT,
    options: IssueFixOptions = IssueFixOptions(),
    executor: Executor | None = None,
    git: GitRunner = _run_git,
) -> list[IssueAutoFixResult]:
    """Auto-fix up to ``limit`` open issues (optionally by label), best-effort.

    Each issue starts from the same git ref: the work-tree is force-checked
    back to the starting branch between issues so one fix never leaks into
    the next. A git or API failure on one issue records a failed result and
    the batch continues.
    """
    workdir = Path(workdir)
    start = _starting_ref(workdir, git)
    results: list[IssueAutoFixResult] = []
    for issue in tracker.list_open_issues(label=label, limit=limit):
        try:
            results.append(auto_fix_issue(
                proposer, tracker, issue, workdir,
                options=options, executor=executor, git=git))
        except (subprocess.CalledProcessError, httpx.HTTPError, OSError) as exc:
            log.warning("Auto-fix for issue #%d failed: %s", issue.number, exc)
            results.append(IssueAutoFixResult(
                issue.number, False, str(exc)[:_REASON_CAP]))
        finally:
            git(workdir, "checkout", "--force", start)
    return results


__all__ = [
    "IssueAutoFixResult",
    "IssueFixOptions",
    "auto_fix_issue",
    "fix_open_issues",
]

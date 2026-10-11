"""CLI command: fetch tracker issues, propose fixes, optionally open PRs.

Wires :mod:`prthinker.issue_autofix` into the ``issue-autofix`` subcommand,
against GitHub or GitLab (``--platform``). Without ``--open-pr`` it is a
dry run: it fetches the issue(s), proposes and validates edits, and prints
them as JSON without touching git or the tracker. With ``--open-pr`` it
runs the full loop — apply, optional test gate, branch, push, pull /
merge request, issue comment.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import shlex
import sys
from pathlib import Path

from prthinker.backends import create_backend
from prthinker.cli_review import _build_config
from prthinker.config import env_str
from prthinker.issue_autofix import IssueFixOptions, auto_fix_issue, fix_open_issues
from prthinker.issue_fix import IssueFixProposer, build_patch
from prthinker.issue_fix_cli import _make_retriever
from prthinker.issue_tracker import IssueTracker, create_issue_tracker
from prthinker.repair_loop import RepairJournal, RepairLimits, RepairLoop
from prthinker.repair_review import BudgetBackend, post_fix_reviewer
from prthinker.verify_cli import _build_executor

_DEFAULT_TOP_K = 10
_DEFAULT_BATCH_LIMIT = 3
_DEFAULT_TEST_TIMEOUT = 600.0


def add_parser(sub, common: argparse.ArgumentParser) -> None:
    """Register the ``issue-autofix`` subcommand on the shared parser."""
    parser = sub.add_parser(
        "issue-autofix", parents=[common],
        help="Fetch tracker issues, propose validated fixes, open fix PRs",
    )
    parser.add_argument("--repo", required=True,
                        help="owner/name repository (GitLab: project path or id)")
    parser.add_argument(
        "--platform", choices=["github", "gitlab"], default="github")
    parser.add_argument(
        "--github-token",
        default=env_str("GITHUB_TOKEN") or env_str("GITLAB_TOKEN"),
        help="Tracker API token. Reads GITHUB_TOKEN for GitHub, "
        "GITLAB_TOKEN for GitLab.",
    )
    parser.add_argument(
        "--gitlab-url", default="",
        help="GitLab API root for self-hosted instances "
        "(default https://gitlab.com/api/v4)",
    )
    parser.add_argument("--issue-number", type=int, help="fix one issue by number")
    parser.add_argument("--issue-label", help="fix open issues carrying this label")
    parser.add_argument("--limit", type=int, default=_DEFAULT_BATCH_LIMIT,
                        help="max issues to fix in --issue-label mode")
    parser.add_argument("--workdir", type=Path, required=True,
                        help="scratch clone of the repository (will be mutated)")
    parser.add_argument(
        "--retriever", choices=["graph-rerank", "graph", "rerank", "lexical"],
        default="graph-rerank", help="localisation strategy (default graph-rerank)",
    )
    parser.add_argument("--top-k", type=int, default=_DEFAULT_TOP_K)
    parser.add_argument("--max-retries", type=int, default=1)
    parser.add_argument(
        "--open-pr", action="store_true",
        help="apply, commit, push, and open the fix PR; off = dry-run JSON only",
    )
    parser.add_argument("--no-draft", action="store_true",
                        help="open the fix PR ready-for-review instead of draft")
    parser.add_argument("--base-branch", default="",
                        help="PR base branch (default: the repo's default branch)")
    parser.add_argument("--branch-prefix", default="issue-fix")
    parser.add_argument("--test-cmd",
                        help="gate the PR on this command passing in the workdir")
    parser.add_argument("--test-timeout", type=float, default=_DEFAULT_TEST_TIMEOUT)
    parser.add_argument("--output", type=Path, help="write the results JSON here")
    parser.add_argument("--autonomous", action="store_true", help="Isolated bounded repair with tests and post-fix review")
    parser.add_argument("--repair-audit", type=Path, default=Path(".prthinker/repairs.sqlite"))
    parser.add_argument("--total-timeout", type=float, default=1800)
    parser.add_argument("--max-patch-bytes", type=int, default=100000)
    parser.add_argument("--sandbox", choices=("docker", "none"), default="docker")
    parser.add_argument("--sandbox-image", default="")
    parser.add_argument("--allow-unsandboxed", action="store_true")
    parser.add_argument("--allow-unpinned-image", action="store_true")


def _validate_args(args: argparse.Namespace) -> str:
    """Return an error message for unusable argument combinations, else ''."""
    if not args.github_token:
        return "issue-autofix needs --github-token (or GITHUB_TOKEN)"
    picked_number = args.issue_number is not None
    if picked_number == bool(args.issue_label):
        return "issue-autofix needs exactly one of --issue-number / --issue-label"
    if getattr(args, "autonomous", False) and (not args.test_cmd or args.no_draft):
        return "autonomous repair requires --test-cmd and draft PRs"
    return ""


def _options_from(args: argparse.Namespace) -> IssueFixOptions:
    """Map CLI arguments onto :class:`IssueFixOptions`."""
    test_cmd = tuple(shlex.split(args.test_cmd)) if args.test_cmd else ()
    return IssueFixOptions(
        branch_prefix=args.branch_prefix,
        base_branch=args.base_branch,
        draft=not args.no_draft,
        test_cmd=test_cmd,
        test_timeout=args.test_timeout,
    )


def _issues_for(args: argparse.Namespace, tracker: IssueTracker) -> list:
    """Resolve the issue set named by --issue-number / --issue-label."""
    if args.issue_number is not None:
        return [tracker.fetch_issue(args.issue_number)]
    return tracker.list_open_issues(label=args.issue_label, limit=args.limit)


def _dry_run(proposer: IssueFixProposer, issues: list,
             workdir: Path) -> list[dict]:
    """Propose per issue without mutating anything; return result payloads."""
    payloads = []
    for issue in issues:
        proposal = proposer.propose(f"{issue.title}\n\n{issue.body}".strip(), workdir)
        payloads.append({
            "issue_number": issue.number,
            "valid": proposal.valid,
            "reason": proposal.reason,
            "edits": [dataclasses.asdict(edit) for edit in proposal.edits],
            "patch": build_patch(proposal, workdir),
        })
    return payloads


def _full_run(proposer: IssueFixProposer, args: argparse.Namespace,
              tracker: IssueTracker) -> list[dict]:
    """Run the apply/branch/PR loop; return result payloads."""
    options = _options_from(args)
    if args.issue_number is not None:
        issue = tracker.fetch_issue(args.issue_number)
        results = [auto_fix_issue(
            proposer, tracker, issue, args.workdir, options=options)]
    else:
        results = fix_open_issues(
            proposer, tracker, args.workdir,
            label=args.issue_label, limit=args.limit, options=options)
    return [dataclasses.asdict(result) for result in results]


def _emit(payloads: list[dict], output: Path | None) -> None:
    """Serialise the results to JSON, to ``output`` or stdout."""
    text = json.dumps(payloads, indent=2, ensure_ascii=False) + "\n"
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


def command(args: argparse.Namespace) -> int:
    """Run issue-autofix; exit 0 only when every attempted issue succeeded."""
    error = _validate_args(args)
    if error:
        sys.stderr.write(error + "\n")
        return 2
    tracker = create_issue_tracker(
        args.platform, repo=args.repo, token=args.github_token,
        base_url=args.gitlab_url)
    backend = create_backend(_build_config(args))
    proposer = IssueFixProposer(
        _make_retriever(args, backend), backend, max_retries=args.max_retries)
    try:
        if getattr(args, "autonomous", False):
            bounded = BudgetBackend(backend, args.total_timeout, 3 * (args.max_retries + 1) * args.limit)
            proposer = IssueFixProposer(_make_retriever(args, bounded), bounded,
                                        max_new_tokens=args.max_new_tokens, max_retries=0)
            loop = RepairLoop(proposer, _build_executor(args),
                              post_fix_reviewer(bounded, args.max_new_tokens),
                              RepairJournal(args.repair_audit),
                              limits=RepairLimits(attempts=args.max_retries + 1,
                                                  total_seconds=args.total_timeout,
                                                  test_seconds=args.test_timeout,
                                                  max_patch_bytes=args.max_patch_bytes))
            results = [loop.run(issue, args.workdir, tuple(shlex.split(args.test_cmd)),
                                tracker=tracker if args.open_pr else None,
                                base=args.base_branch or "HEAD")
                       for issue in _issues_for(args, tracker)]
            payloads = [dataclasses.asdict(result) | {"valid": result.valid} for result in results]
        elif args.open_pr:
            payloads = _full_run(proposer, args, tracker)
        else:
            payloads = _dry_run(proposer, _issues_for(args, tracker), args.workdir)
    finally:
        close = getattr(backend, "close", None)
        if close:
            close()
    _emit(payloads, args.output)
    return 0 if payloads and all(row["valid"] for row in payloads) else 1

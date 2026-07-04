"""CLI command: propose fixes for an issue against a repository work-tree.

Wires :class:`prthinker.issue_fix.IssueFixProposer` into the ``issue-fix``
subcommand — localise the relevant files, propose validated find/replace
edits, and print them as JSON. Read-only: it never writes to the work-tree.
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
from prthinker.execution_sandbox import LocalExecutor
from prthinker.issue_fix import (
    IssueFixProposer,
    apply_to_workdir,
    build_patch,
    validate_fix,
)
from prthinker.repo_retrieval import (
    GraphExpandedRetriever,
    RerankingRepoRetriever,
    create_repo_retriever,
)

_DEFAULT_TOP_K = 10
_SIMPLE_KINDS = ("lexical", "graph")


def add_parser(sub, common: argparse.ArgumentParser) -> None:
    """Register the ``issue-fix`` subcommand on the shared parser."""
    parser = sub.add_parser(
        "issue-fix", parents=[common],
        help="Localise and propose validated edits that resolve an issue",
    )
    parser.add_argument("issue", nargs="?", help="issue text, or '-' for stdin")
    parser.add_argument("--issue-file", type=Path, help="read the issue from a file")
    parser.add_argument("--workdir", type=Path, required=True, help="repository work-tree")
    parser.add_argument(
        "--retriever", choices=["graph-rerank", "graph", "rerank", "lexical"],
        default="graph-rerank", help="localisation strategy (default graph-rerank)",
    )
    parser.add_argument("--top-k", type=int, default=_DEFAULT_TOP_K)
    parser.add_argument("--max-retries", type=int, default=1)
    parser.add_argument("--output", type=Path, help="write the proposal JSON here")
    parser.add_argument("--patch", type=Path, help="write a unified diff of the edits here")
    parser.add_argument(
        "--apply", action="store_true",
        help="write the edits to the work-tree (mutates files); off by default",
    )
    parser.add_argument(
        "--test-cmd",
        help="apply the fix and run this command as a Pass@1 check (mutates work-tree)",
    )
    parser.add_argument("--test-timeout", type=float, default=600.0)


def _read_issue(args: argparse.Namespace) -> str:
    """Resolve the issue text from --issue-file, the argument, or stdin."""
    if args.issue_file:
        return args.issue_file.read_text(encoding="utf-8")
    if args.issue in (None, "-"):
        return sys.stdin.read()
    return args.issue


def _make_retriever(args: argparse.Namespace, backend):
    """Build the localisation retriever named by ``--retriever``."""
    if args.retriever in _SIMPLE_KINDS:
        return create_repo_retriever(args.retriever, top_k=args.top_k)
    if args.retriever == "rerank":
        return create_repo_retriever("rerank", backend=backend)
    base = GraphExpandedRetriever(create_repo_retriever("lexical", top_k=args.top_k))
    return RerankingRepoRetriever(base, backend)


def _emit(proposal, output: Path | None) -> None:
    """Serialise the proposal to JSON, to ``output`` or stdout."""
    payload = {
        "valid": proposal.valid,
        "reason": proposal.reason,
        "localized_files": list(proposal.localized_files),
        "edits": [dataclasses.asdict(edit) for edit in proposal.edits],
    }
    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


def command(args: argparse.Namespace) -> int:
    """Run the issue-fix proposer and emit its validated edits."""
    issue = _read_issue(args)
    if not issue.strip():
        args_error = "issue-fix needs an issue (argument, --issue-file, or stdin)"
        sys.stderr.write(args_error + "\n")
        return 2
    backend = create_backend(_build_config(args))
    retriever = _make_retriever(args, backend)
    proposer = IssueFixProposer(retriever, backend, max_retries=args.max_retries)
    proposal = proposer.propose(issue, args.workdir)
    _emit(proposal, args.output)
    _emit_side_effects(proposal, args)
    if args.test_cmd:
        return 0 if _run_validation(proposal, args) else 1
    return 0 if proposal.valid else 1


def _emit_side_effects(proposal, args: argparse.Namespace) -> None:
    """Write the patch and/or apply the edits when requested and valid."""
    if args.patch:
        args.patch.parent.mkdir(parents=True, exist_ok=True)
        args.patch.write_text(build_patch(proposal, args.workdir), encoding="utf-8")
    if args.apply and proposal.valid:
        changed = apply_to_workdir(proposal, args.workdir)
        sys.stderr.write(f"applied edits to {len(changed)} file(s): {', '.join(changed)}\n")


def _run_validation(proposal, args: argparse.Namespace) -> bool:
    """Apply the fix and run the test command; report the Pass@1 result."""
    validation = validate_fix(
        proposal, args.workdir, tuple(shlex.split(args.test_cmd)),
        LocalExecutor(), timeout=args.test_timeout,
    )
    status = "PASSED" if validation.passed else "FAILED"
    sys.stderr.write(f"test command {status} (exit={validation.exit_code})\n")
    return validation.passed

"""Auto-fix draft PR — apply ``suggestion`` blocks to a working copy and
open a draft PR pointed at the original PR's head.

Triggered from ``review-pr`` when the number of surviving
``suggestion``-bearing findings reaches ``--auto-fix-threshold``. Only
``warning``-severity suggestions are auto-applied; ``error``-severity
findings stay as inline comments for human judgement (the principle in
the original pitch).

Two layers:

1. :func:`apply_suggestions_to_text` and :func:`detect_conflicts` are
   **pure data transforms** — they take a file's text and a list of
   ``InlineFinding`` and return modified text + a conflict report. These
   are unit-testable without touching disk or git.

2. :func:`open_auto_fix_pr` is the glue: it walks the per-file results,
   applies the pure transform, drives ``git`` via :mod:`subprocess`, and
   POSTs to the GitHub create-PR endpoint. Network + filesystem effects
   live here.
"""

from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import httpx

from prthinker.config import GitHubConfig
from prthinker.schemas import InlineFinding

log = logging.getLogger(__name__)

_API_ROOT = "https://api.github.com"
_USER_AGENT = "prthinker/0.1"

# Severities that get auto-applied. ``error`` stays inline so a human
# decides; ``info`` already had its ``suggestion`` stripped by the
# sanitizer (see prthinker.findings).
_AUTO_APPLY_SEVERITIES = {"warning"}


@dataclass(frozen=True)
class _Edit:
    """One contiguous line-range replacement.

    Lines are 1-based, inclusive at both ends. ``replacement`` already
    contains the trailing newline if needed.
    """

    start: int
    end: int
    replacement: str
    finding_index: int  # for reporting which finding produced the edit


@dataclass(frozen=True)
class ConflictReport:
    """Result of conflict detection over a single file's edits."""

    applied: list[_Edit]
    skipped: list[tuple[_Edit, _Edit]]  # (skipped_edit, blocking_edit)


def _to_edit(finding: InlineFinding, index: int) -> _Edit | None:
    if finding.suggestion is None:
        return None
    if finding.severity not in _AUTO_APPLY_SEVERITIES:
        return None
    start = finding.start_line or finding.line
    end = finding.line
    if start > end:
        return None
    return _Edit(
        start=start, end=end,
        replacement=finding.suggestion,
        finding_index=index,
    )


def detect_conflicts(edits: Iterable[_Edit]) -> ConflictReport:
    """Sort edits by start line; drop any whose range overlaps a kept edit.

    First-come wins — earlier indices keep priority. Two ``info`` /
    out-of-scope edits returning the same line range will leave only the
    first applied.
    """
    ordered = sorted(edits, key=lambda e: (e.start, e.end, e.finding_index))
    applied: list[_Edit] = []
    skipped: list[tuple[_Edit, _Edit]] = []
    for edit in ordered:
        conflict = next(
            (kept for kept in applied
             if not (edit.end < kept.start or edit.start > kept.end)),
            None,
        )
        if conflict is not None:
            skipped.append((edit, conflict))
            continue
        applied.append(edit)
    return ConflictReport(applied=applied, skipped=skipped)


def _normalize_replacement(repl: str, lines: list[str], i0: int, i1: int) -> str:
    """Append a trailing newline when the last replaced line had one."""
    if repl.endswith("\n") or not i0 < i1 <= len(lines):
        return repl
    # If the original last line had a newline, the replacement should too —
    # diffs rarely include trailing-newline-less final lines, but be defensive.
    if lines[i1 - 1].endswith("\n"):
        return repl + "\n"
    return repl


def apply_suggestions_to_text(
    text: str,
    findings: list[InlineFinding],
) -> tuple[str, ConflictReport]:
    """Return (new_text, report). Lines outside any edit are left untouched."""
    edits = [e for e in (_to_edit(f, i) for i, f in enumerate(findings))
             if e is not None]
    report = detect_conflicts(edits)
    if not report.applied:
        return text, report

    # Apply from the bottom up so earlier line numbers stay stable.
    lines = text.splitlines(keepends=True)
    for edit in sorted(report.applied, key=lambda e: e.start, reverse=True):
        # Convert 1-based inclusive range to 0-based slice [start-1, end).
        i0 = max(0, edit.start - 1)
        i1 = min(len(lines), edit.end)
        lines[i0:i1] = [_normalize_replacement(edit.replacement, lines, i0, i1)]
    return "".join(lines), report


# ---------------------------------------------------------------------------
# git + GitHub side effects (kept separate from the pure transforms above).
# ---------------------------------------------------------------------------


def _git(*args: str) -> str:
    """Run a git command, return stdout, raise on non-zero."""
    proc = subprocess.run(
        ["git", *args],
        capture_output=True, text=True, check=True, encoding="utf-8",
    )
    return proc.stdout.strip()


@dataclass
class AutoFixResult:
    branch: str
    pr_number: int | None
    pr_url: str | None
    files_changed: list[str]
    total_findings_applied: int
    total_findings_skipped: int


def _apply_fixes_to_disk(
    findings_by_file: dict[str, list[InlineFinding]], repo_root: Path
) -> tuple[list[str], int, int]:
    """Apply each file's suggestions on disk; return (changed, applied, skipped)."""
    files_changed: list[str] = []
    total_applied = 0
    total_skipped = 0
    for path_str, findings in findings_by_file.items():
        target = repo_root / path_str
        if not target.exists():
            log.warning("Auto-fix: target file does not exist on disk: %s", target)
            continue
        original = target.read_text(encoding="utf-8")
        new_text, report = apply_suggestions_to_text(original, findings)
        if not report.applied:
            continue
        target.write_text(new_text, encoding="utf-8")
        files_changed.append(path_str)
        total_applied += len(report.applied)
        total_skipped += len(report.skipped)
        log.info(
            "Auto-fix %s: applied %d, skipped %d",
            path_str, len(report.applied), len(report.skipped),
        )
    return files_changed, total_applied, total_skipped


def _commit_and_push_fixes(branch: str, files_changed: list[str], base_pr_number: int) -> None:
    """Stage the changed files on a fresh branch, commit, and force-push."""
    _git("checkout", "-B", branch)
    for path_str in files_changed:
        _git("add", path_str)
    _git("commit", "-m", f"Apply prthinker suggestions for #{base_pr_number}")
    _git("push", "--force-with-lease", "origin", branch)


def open_auto_fix_pr(
    config: GitHubConfig,
    findings_by_file: dict[str, list[InlineFinding]],
    base_pr_number: int,
    base_branch: str,
    repo_root: Path,
) -> AutoFixResult | None:
    """Walk per-file findings, apply suggestions, commit, push, open draft PR.

    Returns ``None`` when there is nothing to apply (no surviving
    warning-severity suggestion across all files).
    """
    files_changed, total_applied, total_skipped = _apply_fixes_to_disk(
        findings_by_file, repo_root
    )
    if not files_changed:
        return None

    branch = f"auto-fix/prthinker-pr-{base_pr_number}"
    _commit_and_push_fixes(branch, files_changed, base_pr_number)

    pr_url: str | None = None
    pr_number: int | None = None
    try:
        pr_number, pr_url = _open_draft_pr(
            config=config,
            base_branch=base_branch,
            head_branch=branch,
            base_pr_number=base_pr_number,
            total_applied=total_applied,
            total_skipped=total_skipped,
            files_changed=files_changed,
        )
    except httpx.HTTPStatusError as exc:
        log.error("Auto-fix PR creation failed: %d %s",
                  exc.response.status_code, exc.response.text)

    return AutoFixResult(
        branch=branch,
        pr_number=pr_number,
        pr_url=pr_url,
        files_changed=files_changed,
        total_findings_applied=total_applied,
        total_findings_skipped=total_skipped,
    )


def _draft_pr_body(
    base_pr_number: int, total_applied: int, total_skipped: int, files_changed: list[str]
) -> str:
    """Render the Markdown body for the auto-fix draft PR."""
    body_lines = [
        f"Mechanically applies prthinker's `suggestion` blocks from #{base_pr_number}.",
        "",
        f"- **{total_applied}** suggestion(s) applied",
    ]
    if total_skipped:
        body_lines.append(
            f"- **{total_skipped}** suggestion(s) skipped due to overlap "
            f"(see the inline comments on the original PR)"
        )
    body_lines += [
        "",
        f"### Files changed ({len(files_changed)})",
        "",
        *[f"- `{p}`" for p in files_changed],
        "",
        "Review the diff, then merge this branch into the original PR if "
        "the changes look right.",
    ]
    return "\n".join(body_lines)


def _open_draft_pr(
    *,
    config: GitHubConfig,
    base_branch: str,
    head_branch: str,
    base_pr_number: int,
    total_applied: int,
    total_skipped: int,
    files_changed: list[str],
) -> tuple[int, str]:
    payload = {
        "title": f"Apply prthinker suggestions from #{base_pr_number}",
        "head": head_branch,
        "base": base_branch,
        "body": _draft_pr_body(base_pr_number, total_applied, total_skipped, files_changed),
        "draft": True,
    }
    with httpx.Client(
        base_url=_API_ROOT,
        timeout=30.0,
        headers={
            "Authorization": f"Bearer {config.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": _USER_AGENT,
        },
    ) as client:
        response = client.post(
            f"/repos/{config.repo}/pulls",
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        return int(data["number"]), str(data["html_url"])


__all__ = [
    "AutoFixResult",
    "ConflictReport",
    "apply_suggestions_to_text",
    "detect_conflicts",
    "open_auto_fix_pr",
]

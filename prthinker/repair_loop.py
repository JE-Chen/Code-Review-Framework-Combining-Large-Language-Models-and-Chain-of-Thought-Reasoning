"""Bounded issue repair in disposable worktrees with persistent deduplication."""

from __future__ import annotations

import ast
import hashlib
import json
import sqlite3
import subprocess
import tempfile
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass, replace
from pathlib import Path, PurePosixPath, PureWindowsPath

from prthinker.issue_fix import apply_file_edits, apply_to_workdir, build_patch
from prthinker.redaction import redact


@dataclass(frozen=True)
class RepairLimits:
    attempts: int = 2
    total_seconds: float = 1800
    test_seconds: float = 600
    max_patch_bytes: int = 100_000
    max_files: int = 10

    def __post_init__(self):
        if not 1 <= self.attempts <= 10:
            raise ValueError("repair attempts must be between 1 and 10")
        if min(self.total_seconds, self.test_seconds, self.max_patch_bytes, self.max_files) <= 0:
            raise ValueError("repair resource limits must be positive")


@dataclass(frozen=True)
class RepairResult:
    issue_number: int
    status: str
    fingerprint: str
    attempts: int = 0
    reason: str = ""
    branch: str = ""
    pr_number: int | None = None
    pr_url: str = ""
    patch_path: str = ""
    patch_sha256: str = ""

    @property
    def valid(self):
        return (self.status in ("verified", "draft_pr")
                or self.status == "deduplicated" and bool(self.patch_sha256 or self.pr_number))


class RepairJournal:
    """Atomically reserve fingerprints and keep content-safe event history."""

    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        with sqlite3.connect(path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS repairs (
                    fingerprint TEXT PRIMARY KEY, result TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY, fingerprint TEXT NOT NULL,
                    timestamp REAL NOT NULL, state TEXT NOT NULL, detail TEXT NOT NULL);
            """)

    def claim(self, fingerprint: str) -> bool:
        with sqlite3.connect(self.path) as conn:
            row = conn.execute("INSERT OR IGNORE INTO repairs VALUES (?, ?)",
                               (fingerprint, '{"status":"running"}'))
            return row.rowcount == 1

    def event(self, fingerprint: str, state: str, detail: str = ""):
        with sqlite3.connect(self.path) as conn:
            conn.execute("INSERT INTO events (fingerprint,timestamp,state,detail) VALUES (?,?,?,?)",
                         (fingerprint, time.time(), state, redact(detail)[0]))

    def previous(self, fingerprint: str):
        with sqlite3.connect(self.path) as conn:
            row = conn.execute("SELECT result FROM repairs WHERE fingerprint=?", (fingerprint,)).fetchone()
        payload = json.loads(row[0]) if row else {}
        return RepairResult(**payload) if "issue_number" in payload else None

    def finish(self, result: RepairResult):
        with sqlite3.connect(self.path) as conn:
            conn.execute("UPDATE repairs SET result=? WHERE fingerprint=?",
                         (json.dumps(asdict(result)), result.fingerprint))
        self.event(result.fingerprint, result.status, result.reason)


def run_git(workdir: Path, *args: str) -> str:
    """Git operations are bounded and always use argument lists."""
    return subprocess.run(["git", *args], cwd=workdir, check=True, capture_output=True,
                          text=True, encoding="utf-8", timeout=60).stdout.strip()


def validate_proposal(proposal, workdir: Path, limits: RepairLimits) -> str:
    """Validate composed edits and reject paths outside the owned worktree."""
    if not proposal.valid or not proposal.edits:
        return proposal.reason or "no valid edits"
    files = set(proposal.edited_files)
    if len(files) > limits.max_files:
        return "file limit exceeded"
    for rel in files:
        path = Path(rel)
        if PurePosixPath(rel).is_absolute() or PureWindowsPath(rel).root or PureWindowsPath(rel).drive:
            return "unsafe edit path"
        if ".." in path.parts or ".git" in path.parts:
            return "unsafe edit path"
        target = workdir / path
        if target.is_symlink() or not target.resolve().is_relative_to(workdir.resolve()):
            return "edit escapes worktree"
        if not target.is_file():
            return "edit target does not exist"
        text = target.read_text(encoding="utf-8")
        edits = [edit for edit in proposal.edits if edit.file == rel]
        for edit in edits:
            if edit.original and edit.original not in text:
                return "original snippet does not match"
            text = apply_file_edits(text, [edit])
        if path.suffix == ".py":
            try:
                ast.parse(text)
            except SyntaxError:
                return "patch produces invalid syntax"
    if len(build_patch(proposal, workdir).encode()) > limits.max_patch_bytes:
        return "patch byte limit exceeded"
    return ""


class RepairLoop:
    """Inject proposal, verification, review and tracker strategies for testing."""

    def __init__(self, proposer, executor, post_review: Callable, journal: RepairJournal,
                 *, limits=None, git=run_git):
        self.proposer = proposer
        self.executor = executor
        self.post_review = post_review
        self.journal = journal
        self.limits = limits or RepairLimits()
        self.git = git

    def run(self, issue, repository: Path, command: tuple[str, ...], *, tracker=None, base="HEAD") -> RepairResult:
        if not command:
            raise ValueError("autonomous repair requires a verification command")
        revision = self.git(repository, "rev-parse", "--verify", base)
        identity = f"{repository.resolve()}\n{revision}\n{issue.number}\n{issue.title}\n{issue.body}"
        fingerprint = hashlib.sha256(identity.encode()).hexdigest()
        if not self.journal.claim(fingerprint):
            previous = self.journal.previous(fingerprint)
            if previous and previous.valid:
                return replace(previous, status="deduplicated", reason="previous verified repair retained")
            return RepairResult(issue.number, "deduplicated", fingerprint)
        started = time.monotonic()
        result = RepairResult(issue.number, "failed", fingerprint)
        try:
            result = self._isolated(issue, repository, revision, command, fingerprint, started, tracker)
            return result
        except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as exc:
            result = RepairResult(issue.number, "failed", fingerprint, reason=redact(str(exc))[0])
            return result
        finally:
            self.journal.finish(result)

    def _isolated(self, issue, repository, revision, command, fingerprint, started, tracker):
        with tempfile.TemporaryDirectory(prefix="prthinker-repair-") as temporary:
            workdir = Path(temporary) / "worktree"
            self.git(repository, "worktree", "add", "--detach", str(workdir), revision)
            try:
                return self._attempts(issue, workdir, revision, command, fingerprint, started, tracker)
            finally:
                self.git(repository, "worktree", "remove", "--force", str(workdir))

    def _attempts(self, issue, workdir, revision, command, fingerprint, started, tracker):
        feedback = ""
        for attempt in range(1, self.limits.attempts + 1):
            remaining = self.limits.total_seconds - (time.monotonic() - started)
            if remaining <= 0:
                return RepairResult(issue.number, "timed_out", fingerprint, attempt - 1)
            self.journal.event(fingerprint, "localize_plan_patch", f"attempt={attempt}")
            text = redact(f"{issue.title}\n\n{issue.body}\n\nPrevious verification: {feedback}")[0]
            proposal = self.proposer.propose(text, workdir)
            feedback = validate_proposal(proposal, workdir, self.limits)
            if not feedback:
                result, feedback = self._verify(issue, proposal, workdir, command, fingerprint, started, attempt)
                if result:
                    return self._publish(result, issue, workdir, tracker)
            self.journal.event(fingerprint, "retry", feedback)
            self.git(workdir, "reset", "--hard", revision)
            self.git(workdir, "clean", "-fd")
        return RepairResult(issue.number, "exhausted", fingerprint, self.limits.attempts,
                            redact(feedback)[0])

    def _verify(self, issue, proposal, workdir, command, fingerprint, started, attempt):
        changed = apply_to_workdir(proposal, workdir)
        if not changed:
            return None, "patch changed no files"
        remaining = self.limits.total_seconds - (time.monotonic() - started)
        if remaining <= 0:
            return None, "time budget exceeded"
        self.journal.event(fingerprint, "tests", f"files={len(changed)}")
        check = self.executor.run(command, workdir, min(self.limits.test_seconds, remaining))
        if check.unsupported or check.timed_out or check.exit_code != 0:
            return None, redact(check.stderr or check.stdout or "verification failed")[0][-4000:]
        if time.monotonic() - started >= self.limits.total_seconds:
            return None, "time budget exceeded"
        patch = self.git(workdir, "diff", "--")
        self.journal.event(fingerprint, "post_fix_review", hashlib.sha256(patch.encode()).hexdigest())
        review_input = redact(f"Issue: {issue.title}\n{issue.body}\n\nProposed diff:\n{patch}")[0]
        if not self.post_review(review_input, workdir):
            return None, "post-fix review rejected patch"
        if time.monotonic() - started >= self.limits.total_seconds:
            return None, "time budget exceeded"
        archive = self.journal.path.parent / "patches"
        archive.mkdir(parents=True, exist_ok=True)
        patch_path = archive / (fingerprint + ".patch")
        patch_path.write_text(redact(patch)[0] + "\n", encoding="utf-8")
        digest = hashlib.sha256(patch_path.read_bytes()).hexdigest()
        return RepairResult(issue.number, "verified", fingerprint, attempt,
                            patch_path=str(patch_path.resolve()), patch_sha256=digest), ""

    def _publish(self, result, issue, workdir, tracker):
        if tracker is None:
            return result
        branch = f"issue-fix/{issue.number}-{result.fingerprint[:12]}"
        self.git(workdir, "checkout", "-b", branch)
        self.git(workdir, "add", "-u")
        self.git(workdir, "commit", "-m", f"fix: resolve issue #{issue.number}")
        self.git(workdir, "push", "origin", branch)
        number, url = tracker.open_pull_request(
            title=redact(f"fix: {issue.title[:60]} (#{issue.number})")[0],
            body=f"Fixes #{issue.number}.\n\nVerification and post-fix review passed.\nHuman approval is required before merge.",
            head=branch, base=tracker.default_branch(), draft=True)
        return RepairResult(issue.number, "draft_pr", result.fingerprint, result.attempts,
                            branch=branch, pr_number=number, pr_url=url,
                            patch_path=result.patch_path, patch_sha256=result.patch_sha256)

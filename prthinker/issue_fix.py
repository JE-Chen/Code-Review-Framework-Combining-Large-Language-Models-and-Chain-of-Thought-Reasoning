"""Propose fixes for an issue — localise, edit, validate, self-correct.

Absorbs the strengths of SWE-agent's agent-computer loop in a framework-
idiomatic, leakage-free form: given an issue and a repository work-tree,
:class:`IssueFixProposer` localises the relevant files with the injected
:class:`~prthinker.repo_retrieval.RepoContextRetriever`, asks the backend for
concrete find/replace edits, then *validates* each edit the way SWE-agent's
linter-gated editor does — the edit must apply and (for Python) leave the file
syntactically valid — and *requeries* once on failure (its self-correcting
requery loop). Only the issue and the repository are read; no gold/patch.

Runner-safe: stdlib (``ast`` / ``json`` / ``re`` / ``pathlib``) + the injected
backend and retriever.
"""

from __future__ import annotations

import ast
import difflib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from prthinker.execution_sandbox import Executor
from prthinker.repo_retrieval import (
    RepoContext,
    RepoContextRetriever,
    enclosing_blocks,
)

_DEFAULT_MAX_NEW_TOKENS = 2048
_DEFAULT_MAX_RETRIES = 1
_CONTEXT_FILE_CHARS = 4000
_VALIDATION_OUTPUT_CAP = 4000
_DEFAULT_TEST_TIMEOUT = 600.0
_JSON_ARRAY_RE = re.compile(r"\[.*\]", re.DOTALL)


class _Backend(Protocol):
    """Minimal backend surface the proposer needs (any InferenceBackend fits)."""

    def generate(self, prompt: str, max_new_tokens: int) -> str:
        """Return the model's completion for ``prompt``."""


@dataclass(frozen=True)
class FixEdit:
    """A single find/replace edit proposed for one file."""

    file: str
    original: str
    replacement: str


@dataclass(frozen=True)
class IssueFixProposal:
    """The localised files and validated edits proposed for an issue."""

    localized_files: tuple[str, ...] = ()
    edits: tuple[FixEdit, ...] = ()
    valid: bool = False
    reason: str = ""


def _extract_edits(raw: str) -> list[FixEdit]:
    """Parse the model's JSON edit array into FixEdit records (lenient)."""
    match = _JSON_ARRAY_RE.search(raw)
    if not match:
        return []
    try:
        rows = json.loads(match.group(0))
    except json.JSONDecodeError:
        return []
    edits = []
    for row in rows:
        if isinstance(row, dict) and row.get("file") and "replacement" in row:
            edits.append(FixEdit(row["file"], row.get("original", ""), row["replacement"]))
    return edits


def _apply_edit(text: str, edit: FixEdit) -> str | None:
    """Apply a find/replace edit to file text, or None if it does not apply."""
    if edit.original == "":
        return text + ("\n" if not text.endswith("\n") else "") + edit.replacement
    if edit.original not in text:
        return None
    return text.replace(edit.original, edit.replacement, 1)


def _syntax_ok(path: str, new_text: str) -> bool:
    """True if the edited text is syntactically valid (Python only; else True)."""
    if not path.endswith(".py"):
        return True
    try:
        ast.parse(new_text)
    except SyntaxError:
        return False
    return True


def _edits_by_file(edits: tuple[FixEdit, ...]) -> dict[str, list[FixEdit]]:
    """Group edits by their target file, preserving order."""
    grouped: dict[str, list[FixEdit]] = {}
    for edit in edits:
        grouped.setdefault(edit.file, []).append(edit)
    return grouped


def apply_file_edits(text: str, edits: list[FixEdit]) -> str:
    """Apply every edit for one file in order, skipping any that no longer apply."""
    for edit in edits:
        applied = _apply_edit(text, edit)
        if applied is not None:
            text = applied
    return text


def build_patch(proposal: "IssueFixProposal", workdir: Path) -> str:
    """Build a unified diff (SWE-agent-style model_patch) from the edits."""
    workdir = Path(workdir)
    chunks: list[str] = []
    for rel, edits in _edits_by_file(proposal.edits).items():
        try:
            original = (workdir / rel).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        updated = apply_file_edits(original, edits)
        if updated == original:
            continue
        chunks.append("".join(difflib.unified_diff(
            original.splitlines(keepends=True), updated.splitlines(keepends=True),
            fromfile=f"a/{rel}", tofile=f"b/{rel}",
        )))
    return "".join(chunks)


def apply_to_workdir(proposal: "IssueFixProposal", workdir: Path) -> list[str]:
    """Write the proposal's edits to disk; return the changed file paths."""
    workdir = Path(workdir)
    changed: list[str] = []
    for rel, edits in _edits_by_file(proposal.edits).items():
        path = workdir / rel
        try:
            original = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        updated = apply_file_edits(original, edits)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed.append(rel)
    return changed


def _edit_line_range(text: str, edit: FixEdit) -> tuple[int, int] | None:
    """1-based line range that ``edit.original`` occupies in ``text``."""
    if not edit.original:
        return None
    index = text.find(edit.original)
    if index < 0:
        return None
    start = text.count("\n", 0, index) + 1
    return start, start + edit.original.count("\n")


def _expand_to_blocks(
    lines: list[str], edit_ranges: list[tuple[int, int]]
) -> tuple[list[tuple[int, int]], list[str]]:
    """Expand each edited line range to its enclosing def/class block.

    A change inside a function contributes that whole function's span and the
    names of every block enclosing it (method + class), matching the block
    granularity of the gold context; a module-level change keeps its own range
    and contributes no symbol.
    """
    blocks = enclosing_blocks(lines)
    spans: list[tuple[int, int]] = []
    symbols: list[str] = []
    for start, end in edit_ranges:
        covering = [b for b in blocks if b[0] <= start <= b[1]]
        if not covering:
            spans.append((start, end))
            continue
        innermost = min(covering, key=lambda b: b[1] - b[0])
        spans.append((innermost[0], innermost[1]))
        symbols.extend(name for _, _, name in covering)
    return spans, symbols


def patch_context(proposal: "IssueFixProposal", workdir: Path) -> RepoContext:
    """Derive files / block spans / symbols from the edits (patch localisation).

    The proposed fix pins exactly which lines change and which functions
    enclose them. Each change is expanded to its enclosing function block so
    line/symbol predictions match the gold context's block granularity while
    staying grounded in the real edit — far more precise than keyword windows.
    """
    workdir = Path(workdir)
    spans: dict[str, list[tuple[int, int]]] = {}
    symbols: dict[str, list[str]] = {}
    for rel, edits in _edits_by_file(proposal.edits).items():
        try:
            text = (workdir / rel).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        ranges = [r for r in (_edit_line_range(text, e) for e in edits) if r]
        spans[rel], symbols[rel] = _expand_to_blocks(text.splitlines(), ranges)
    return RepoContext(tuple(spans), spans, symbols)


@dataclass(frozen=True)
class FixValidation:
    """Outcome of executing a test/reproduction command against an applied fix."""

    passed: bool
    exit_code: int | None = None
    output: str = ""


def validate_fix(
    proposal: "IssueFixProposal",
    workdir: Path,
    command: tuple[str, ...],
    executor: Executor,
    *,
    timeout: float = _DEFAULT_TEST_TIMEOUT,
) -> FixValidation:
    """Apply the edits and run a test command — the execution (Pass@1) check.

    This is the execution half of issue resolution, distinct from the
    syntax/apply validation done while proposing: it applies the validated
    edits to the work-tree and runs ``command`` through the injected sandbox
    executor, reporting whether it passed (exit code 0). Mutates the work-tree
    — run it on a scratch checkout.
    """
    if not proposal.valid:
        return FixValidation(False, output="proposal was not valid")
    apply_to_workdir(proposal, workdir)
    result = executor.run(tuple(command), Path(workdir), timeout)
    output = (result.stdout + result.stderr)[-_VALIDATION_OUTPUT_CAP:]
    if result.timed_out:
        return FixValidation(False, None, output or "test command timed out")
    return FixValidation(result.exit_code == 0, result.exit_code, output)


class IssueFixProposer:
    """Localise -> propose edits -> validate -> self-correct, for an issue."""

    def __init__(
        self,
        retriever: RepoContextRetriever,
        backend: _Backend,
        *,
        max_new_tokens: int = _DEFAULT_MAX_NEW_TOKENS,
        max_retries: int = _DEFAULT_MAX_RETRIES,
    ) -> None:
        self._retriever = retriever
        self._backend = backend
        self._max_new_tokens = max_new_tokens
        self._max_retries = max(0, max_retries)

    def propose(self, issue: str, workdir: Path) -> IssueFixProposal:
        """Return validated fix edits for ``issue`` against the work-tree."""
        workdir = Path(workdir)
        context = self._retriever.retrieve(issue, workdir)
        files = context.files
        if not files:
            return IssueFixProposal(reason="no files localised")
        prompt = self._build_prompt(issue, files, workdir)
        return self._propose_with_retries(prompt, files, workdir)

    def _propose_with_retries(
        self, prompt: str, files: tuple[str, ...], workdir: Path
    ) -> IssueFixProposal:
        """Run the propose/validate/requery loop, returning the best proposal."""
        edits: tuple[FixEdit, ...] = ()
        reason = "no edits proposed"
        for _ in range(self._max_retries + 1):
            raw = self._backend.generate(prompt, self._max_new_tokens)
            edits = tuple(_extract_edits(raw))
            valid, reason = self._validate(edits, workdir)
            if valid:
                return IssueFixProposal(files, edits, True)
            prompt = f"{prompt}\n\nYour previous edits were invalid: {reason}\nFix them."
        return IssueFixProposal(files, edits, False, reason)

    def _validate(self, edits: tuple[FixEdit, ...], workdir: Path) -> tuple[bool, str]:
        """Every edit must apply and leave valid syntax (SWE-agent linter gate)."""
        if not edits:
            return False, "no edits proposed"
        for edit in edits:
            path = workdir / edit.file
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                return False, f"{edit.file}: file not found"
            new_text = _apply_edit(text, edit)
            if new_text is None:
                return False, f"{edit.file}: original snippet not found"
            if not _syntax_ok(edit.file, new_text):
                return False, f"{edit.file}: edit produces invalid syntax"
        return True, ""

    def _build_prompt(self, issue: str, files: tuple[str, ...], workdir: Path) -> str:
        """Assemble the issue + localised file contents into a fix prompt."""
        blocks = [self._file_block(rel, workdir) for rel in files]
        return (
            "Propose the minimal code edits that resolve the issue below. "
            "Return ONLY a JSON array; each element is "
            '{"file": <path>, "original": <exact snippet to replace>, '
            '"replacement": <new snippet>}. The "original" must be copied '
            "verbatim from the file so it can be located.\n\n"
            f"Issue:\n{issue}\n\nRelevant files:\n" + "\n".join(blocks)
        )

    @staticmethod
    def _file_block(rel: str, workdir: Path) -> str:
        """A capped view of one localised file for the fix prompt."""
        try:
            text = (workdir / rel).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return f"# {rel}\n(unreadable)\n"
        return f"# {rel}\n{text[:_CONTEXT_FILE_CHARS]}\n"

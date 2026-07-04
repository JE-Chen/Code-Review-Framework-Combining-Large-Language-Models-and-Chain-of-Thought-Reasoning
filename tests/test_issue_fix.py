"""Tests for the issue -> fix proposer (localise, edit, validate, self-correct)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from prthinker.execution_sandbox import ExecutionResult, LocalExecutor
from prthinker.issue_fix import (
    FixEdit,
    IssueFixProposal,
    IssueFixProposer,
    _apply_edit,
    _extract_edits,
    _syntax_ok,
    apply_to_workdir,
    build_patch,
    validate_fix,
)
from prthinker.repo_retrieval import RepoContext, RepoContextRetriever


class _FakeExecutor:
    def __init__(self, exit_code, timed_out=False) -> None:
        self._exit = exit_code
        self._timed_out = timed_out

    def run(self, command, workdir, timeout):
        code = None if self._timed_out else self._exit
        return ExecutionResult(code, "out", "err", timed_out=self._timed_out)


def _valid_proposal() -> IssueFixProposal:
    return IssueFixProposal(("a.py",), (FixEdit("a.py", "x = 1", "x = 2"),), True)


class _FixedRetriever(RepoContextRetriever):
    """Localises to a fixed file list."""

    def __init__(self, files: tuple[str, ...]) -> None:
        self._files = files

    def retrieve(self, query: str, workdir: Path) -> RepoContext:
        return RepoContext(files=self._files)


class _ScriptedBackend:
    """Returns a scripted sequence of completions, recording prompts."""

    def __init__(self, responses: list[str]) -> None:
        self._responses = responses
        self.prompts: list[str] = []

    def generate(self, prompt: str, max_new_tokens: int) -> str:
        self.prompts.append(prompt)
        return self._responses.pop(0) if self._responses else "[]"


def _edits_json(edits: list[dict]) -> str:
    return json.dumps(edits)


# --------------------------------------------------------------------------
# pure helpers
# --------------------------------------------------------------------------

def test_extract_edits_parses_and_filters():
    raw = 'noise ' + _edits_json([
        {"file": "a.py", "original": "x", "replacement": "y"},
        {"file": "b.py"},  # missing replacement -> dropped
        {"replacement": "z"},  # missing file -> dropped
    ]) + ' trailing'
    edits = _extract_edits(raw)
    assert edits == [FixEdit("a.py", "x", "y")]


def test_extract_edits_bad_json_returns_empty():
    assert _extract_edits("not json at all") == []
    assert _extract_edits("[ broken") == []


def test_apply_edit_replace_append_and_missing():
    assert _apply_edit("a\nx\nb", FixEdit("f", "x", "Y")) == "a\nY\nb"
    assert _apply_edit("a\n", FixEdit("f", "", "tail")) == "a\ntail"
    assert _apply_edit("abc", FixEdit("f", "zzz", "Y")) is None


def test_syntax_ok_python_and_other():
    assert _syntax_ok("m.py", "def f():\n    return 1\n") is True
    assert _syntax_ok("m.py", "def f(:\n") is False
    assert _syntax_ok("readme.txt", "def f(:\n") is True  # non-python not checked


# --------------------------------------------------------------------------
# proposer
# --------------------------------------------------------------------------

def test_propose_happy_path(tmp_path):
    (tmp_path / "a.py").write_text("def f():\n    return WRONG\n", encoding="utf-8")
    backend = _ScriptedBackend([_edits_json([
        {"file": "a.py", "original": "return WRONG", "replacement": "return RIGHT"}
    ])])
    proposer = IssueFixProposer(_FixedRetriever(("a.py",)), backend)
    proposal = proposer.propose("f returns the wrong value", tmp_path)
    assert proposal.valid
    assert proposal.edits[0].replacement == "return RIGHT"
    assert proposal.localized_files == ("a.py",)


def test_propose_self_corrects_on_invalid_then_valid(tmp_path):
    (tmp_path / "a.py").write_text("def f():\n    return 1\n", encoding="utf-8")
    backend = _ScriptedBackend([
        _edits_json([{"file": "a.py", "original": "NOT THERE", "replacement": "x"}]),
        _edits_json([{"file": "a.py", "original": "return 1", "replacement": "return 2"}]),
    ])
    proposer = IssueFixProposer(_FixedRetriever(("a.py",)), backend, max_retries=1)
    proposal = proposer.propose("fix it", tmp_path)
    assert proposal.valid
    assert len(backend.prompts) == 2  # requeried once
    assert "previous edits were invalid" in backend.prompts[1]


def test_propose_rejects_syntax_breaking_edit(tmp_path):
    (tmp_path / "a.py").write_text("def f():\n    return 1\n", encoding="utf-8")
    backend = _ScriptedBackend([
        _edits_json([{"file": "a.py", "original": "return 1", "replacement": "return ("}]),
    ])
    proposer = IssueFixProposer(_FixedRetriever(("a.py",)), backend, max_retries=0)
    proposal = proposer.propose("fix", tmp_path)
    assert not proposal.valid
    assert "invalid syntax" in proposal.reason


def test_propose_no_files_localised(tmp_path):
    proposer = IssueFixProposer(_FixedRetriever(()), _ScriptedBackend([]))
    proposal = proposer.propose("anything", tmp_path)
    assert not proposal.valid
    assert proposal.edits == ()
    assert "no files" in proposal.reason


def test_build_patch_produces_unified_diff(tmp_path):
    (tmp_path / "a.py").write_text("def f():\n    return 1\n", encoding="utf-8")
    proposal = IssueFixProposal(
        localized_files=("a.py",),
        edits=(FixEdit("a.py", "return 1", "return 2"),),
        valid=True,
    )
    patch = build_patch(proposal, tmp_path)
    assert "--- a/a.py" in patch and "+++ b/a.py" in patch
    assert "-    return 1" in patch and "+    return 2" in patch


def test_apply_to_workdir_writes_changed_files(tmp_path):
    (tmp_path / "a.py").write_text("x = 1\n", encoding="utf-8")
    proposal = IssueFixProposal(
        localized_files=("a.py",),
        edits=(FixEdit("a.py", "x = 1", "x = 2"),),
        valid=True,
    )
    changed = apply_to_workdir(proposal, tmp_path)
    assert changed == ["a.py"]
    assert (tmp_path / "a.py").read_text(encoding="utf-8") == "x = 2\n"


def test_validate_fix_passes_and_applies(tmp_path):
    (tmp_path / "a.py").write_text("x = 1\n", encoding="utf-8")
    v = validate_fix(_valid_proposal(), tmp_path, ("noop",), _FakeExecutor(0))
    assert v.passed and v.exit_code == 0
    assert (tmp_path / "a.py").read_text(encoding="utf-8") == "x = 2\n"  # applied


def test_validate_fix_fails_on_nonzero_exit(tmp_path):
    (tmp_path / "a.py").write_text("x = 1\n", encoding="utf-8")
    v = validate_fix(_valid_proposal(), tmp_path, ("noop",), _FakeExecutor(1))
    assert not v.passed and v.exit_code == 1


def test_validate_fix_reports_timeout(tmp_path):
    (tmp_path / "a.py").write_text("x = 1\n", encoding="utf-8")
    v = validate_fix(_valid_proposal(), tmp_path, ("noop",), _FakeExecutor(0, timed_out=True))
    assert not v.passed


def test_validate_fix_skips_invalid_proposal(tmp_path):
    proposal = IssueFixProposal(("a.py",), (), valid=False)
    v = validate_fix(proposal, tmp_path, ("noop",), _FakeExecutor(0))
    assert not v.passed
    assert "not valid" in v.output


def test_validate_fix_with_real_local_executor(tmp_path):
    (tmp_path / "a.py").write_text("x = 1\n", encoding="utf-8")
    ok = validate_fix(
        _valid_proposal(), tmp_path,
        (sys.executable, "-c", "raise SystemExit(0)"), LocalExecutor(),
    )
    fail = validate_fix(
        _valid_proposal(), tmp_path,
        (sys.executable, "-c", "raise SystemExit(1)"), LocalExecutor(),
    )
    assert ok.passed and not fail.passed


def test_propose_missing_file_is_invalid(tmp_path):
    backend = _ScriptedBackend([
        _edits_json([{"file": "ghost.py", "original": "x", "replacement": "y"}]),
    ])
    proposer = IssueFixProposer(_FixedRetriever(("ghost.py",)), backend, max_retries=0)
    proposal = proposer.propose("fix", tmp_path)
    assert not proposal.valid
    assert "not found" in proposal.reason

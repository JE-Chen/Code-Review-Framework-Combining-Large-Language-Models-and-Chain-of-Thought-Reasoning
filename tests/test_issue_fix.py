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
    _distinct,
    _edit_line_range,
    _extract_edits,
    _span_window,
    _syntax_ok,
    apply_to_workdir,
    build_patch,
    patch_context,
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


class _SpannedRetriever(RepoContextRetriever):
    """Localises to fixed files with predicted line spans."""

    def __init__(
        self, files: tuple[str, ...], spans: dict[str, list[tuple[int, int]]]
    ) -> None:
        self._files = files
        self._spans = spans

    def retrieve(self, query: str, workdir: Path) -> RepoContext:
        return RepoContext(files=self._files, spans=self._spans)


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


def test_edit_line_range_locates_original():
    text = "a\nb\nc\nd\n"
    assert _edit_line_range(text, FixEdit("f", "c", "x")) == (3, 3)
    assert _edit_line_range(text, FixEdit("f", "b\nc", "x")) == (2, 3)  # multi-line
    assert _edit_line_range(text, FixEdit("f", "", "x")) is None        # append
    assert _edit_line_range(text, FixEdit("f", "zzz", "x")) is None     # not found


def test_patch_context_derives_lines_and_enclosing_symbols(tmp_path):
    (tmp_path / "m.py").write_text(
        "class A:\n    def foo(self):\n        return WRONG\n    def bar(self):\n        return 1\n",
        encoding="utf-8",
    )
    proposal = IssueFixProposal(
        ("m.py",), (FixEdit("m.py", "return WRONG", "return RIGHT"),), True
    )
    ctx = patch_context(proposal, tmp_path)
    assert ctx.files == ("m.py",)
    # the change at line 3 expands to its enclosing function block foo (2-3)
    assert ctx.spans["m.py"] == [(2, 3)]
    assert set(ctx.symbols["m.py"]) == {"A", "foo"}  # enclosing class + function


def test_patch_context_skips_unreadable_file(tmp_path):
    proposal = IssueFixProposal(
        ("ghost.py",), (FixEdit("ghost.py", "x", "y"),), True
    )
    ctx = patch_context(proposal, tmp_path)
    assert ctx.files == ()  # nothing derivable from a missing file


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


# --------------------------------------------------------------------------
# self-consistent localised files (edited files are part of the proposal)
# --------------------------------------------------------------------------

def test_distinct_preserves_first_seen_order():
    assert _distinct(["a", "b", "a", "c", "b"]) == ("a", "b", "c")
    assert _distinct([]) == ()


def test_edited_files_property_dedupes_in_order():
    proposal = IssueFixProposal(edits=(
        FixEdit("b.py", "x", "y"), FixEdit("a.py", "p", "q"),
        FixEdit("b.py", "m", "n"),  # duplicate file
    ))
    assert proposal.edited_files == ("b.py", "a.py")
    assert IssueFixProposal().edited_files == ()


def test_localized_files_include_files_the_model_edited(tmp_path):
    # The retriever surfaces a.py, but the model edits b.py (append mode). The
    # proposal must still declare b.py localised — you cannot edit a file you
    # did not localise. This is the file-metric consistency guarantee.
    (tmp_path / "a.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "b.py").write_text("y = 1\n", encoding="utf-8")
    backend = _ScriptedBackend([_edits_json([
        {"file": "b.py", "original": "", "replacement": "z = 2"}
    ])])
    proposer = IssueFixProposer(_FixedRetriever(("a.py",)), backend, max_retries=0)
    proposal = proposer.propose("touch b", tmp_path)
    assert proposal.valid
    assert proposal.localized_files == ("a.py", "b.py")


def test_localized_files_union_holds_on_invalid_proposal(tmp_path):
    (tmp_path / "a.py").write_text("x = 1\n", encoding="utf-8")
    backend = _ScriptedBackend([_edits_json([
        {"file": "c.py", "original": "NOPE", "replacement": "z"}  # will not apply
    ])])
    proposer = IssueFixProposer(_FixedRetriever(("a.py",)), backend, max_retries=0)
    proposal = proposer.propose("bad", tmp_path)
    assert not proposal.valid
    assert proposal.localized_files == ("a.py", "c.py")  # both still declared


# --------------------------------------------------------------------------
# span-centred file windows in the fix prompt
# --------------------------------------------------------------------------

def _big_file(marker_line: int, total: int = 200) -> str:
    # comment filler keeps the whole module syntactically valid so an edit to
    # the one real statement passes the proposer's syntax gate.
    lines = [f"# filler line number {i:04d} padding padding padding" for i in range(total)]
    lines[marker_line] = "TARGET_SNIPPET = 12345  # the line to edit"
    return "\n".join(lines) + "\n"


def test_span_window_covers_span_and_is_a_verbatim_substring():
    text = _big_file(150)
    window = _span_window(text, [(151, 151)])  # 1-based line of the marker
    assert "TARGET_SNIPPET" in window
    assert window in text          # exact substring -> a copied edit still applies
    assert len(window) <= 4000     # capped


def test_span_window_preserves_crlf_line_endings():
    text = "a = 1\r\nb = 2\r\nTARGET\r\nc = 3\r\n"
    window = _span_window(text, [(3, 3)])
    assert "TARGET" in window
    assert window in text  # CRLF kept, so the excerpt is a real substring


def test_span_window_clamps_margin_at_file_bounds():
    text = "one\ntwo\nthree\n"
    assert _span_window(text, [(1, 3)]) in text  # no negative / overflow slice


def test_file_block_small_file_shown_whole_ignoring_spans(tmp_path):
    (tmp_path / "s.py").write_text("x = 1\n", encoding="utf-8")
    block = IssueFixProposer._file_block("s.py", tmp_path, [(1, 1)])
    assert block == "# s.py\nx = 1\n\n"


def test_file_block_large_file_windows_around_spans(tmp_path):
    (tmp_path / "big.py").write_text(_big_file(150), encoding="utf-8")
    windowed = IssueFixProposer._file_block("big.py", tmp_path, [(151, 151)])
    head = IssueFixProposer._file_block("big.py", tmp_path, None)
    assert "excerpt around the relevant lines" in windowed
    assert "TARGET_SNIPPET" in windowed          # relevant region survives
    assert "TARGET_SNIPPET" not in head          # head truncation would miss it


def test_build_prompt_shows_span_excerpt_for_large_file(tmp_path):
    (tmp_path / "big.py").write_text(_big_file(150), encoding="utf-8")
    backend = _ScriptedBackend([_edits_json([
        {"file": "big.py", "original": "TARGET_SNIPPET = 12345",
         "replacement": "TARGET_SNIPPET = 999"}
    ])])
    retriever = _SpannedRetriever(("big.py",), {"big.py": [(151, 151)]})
    proposer = IssueFixProposer(retriever, backend, max_retries=0)
    proposal = proposer.propose("fix the target", tmp_path)
    assert proposal.valid                         # editable region was in view
    assert "TARGET_SNIPPET" in backend.prompts[0]


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

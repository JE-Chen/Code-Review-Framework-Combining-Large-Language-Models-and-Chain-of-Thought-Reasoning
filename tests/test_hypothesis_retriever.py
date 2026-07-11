"""Tests for the hypothesis-verification localiser (prthinker.hypothesis_retriever)."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from prthinker.hypothesis_retriever import (
    Hypothesis,
    HypothesisRetriever,
    create_hypothesis_retriever,
    find_symbol_span,
    parse_hypothesis_round,
    verify_hypothesis,
)
from prthinker.repo_retrieval import (
    LexicalRepoRetriever,
    RepoContext,
    RepoContextRetriever,
)
from tests.conftest import FakeBackend
from tests.test_repo_retrieval import _make_repo


def _round(hypotheses: list, done: bool) -> str:
    """One scripted hypothesis-round JSON payload."""
    return json.dumps({"hypotheses": hypotheses, "done": done})


_APP = (
    "def handler(request):\n"
    "    value = request.token\n"
    "    return value\n"
)


# --------------------------------------------------------------------------
# pure helpers: round parsing
# --------------------------------------------------------------------------

def test_parse_round_accepts_fenced_json():
    raw = "```json\n" + _round([{"path": "a.py"}], True) + "\n```"
    hypotheses, done = parse_hypothesis_round(raw, 5)
    assert [hyp.path for hyp in hypotheses] == ["a.py"]
    assert done


def test_parse_round_clamps_to_max_hypotheses():
    raw = _round([{"path": f"f{i}.py"} for i in range(10)], False)
    hypotheses, done = parse_hypothesis_round(raw, 3)
    assert len(hypotheses) == 3
    assert not done


def test_parse_round_rejects_malformed_payloads():
    assert parse_hypothesis_round("no json here", 5) is None
    assert parse_hypothesis_round('{"hypotheses": "nope"}', 5) is None
    assert parse_hypothesis_round("[1, 2]", 5) is None
    assert parse_hypothesis_round("{not valid json}", 5) is None


def test_parse_round_drops_bad_items_and_coerces_fields():
    raw = _round(
        [
            {"path": "a.py", "confidence": "not-a-number", "line": "x"},
            {"path": ""},        # empty path dropped
            "just a string",     # non-dict dropped
            {"symbol": "f"},     # missing path dropped
        ],
        False,
    )
    hypotheses, _ = parse_hypothesis_round(raw, 5)
    assert len(hypotheses) == 1
    assert hypotheses[0].confidence == 0.0
    assert hypotheses[0].line is None


# --------------------------------------------------------------------------
# pure helpers: symbol span verification
# --------------------------------------------------------------------------

def test_find_symbol_span_python_ast_def_and_class():
    text = "import os\n\nclass Widget:\n    def render(self):\n        return os.name\n"
    assert find_symbol_span(text, "Widget", is_python=True) == (3, 5)
    assert find_symbol_span(text, "render", is_python=True) == (4, 5)
    assert find_symbol_span(text, "missing", is_python=True) is None


def test_find_symbol_span_regex_fallback_for_other_languages():
    text = "function handler(x) {\n  return x;\n}\n"
    assert find_symbol_span(text, "handler", is_python=False) == (1, 1)
    assert find_symbol_span(text, "missing", is_python=False) is None


def test_find_symbol_span_broken_python_falls_back_to_regex():
    text = "def broken(:\n    pass\n"  # unparseable — AST raises SyntaxError
    assert find_symbol_span(text, "broken", is_python=True) == (1, 1)


# --------------------------------------------------------------------------
# pure helpers: static hypothesis verification
# --------------------------------------------------------------------------

def test_verify_hypothesis_reports_span_for_real_symbol(tmp_path):
    repo = _make_repo(tmp_path, {"app.py": _APP})
    verdict = verify_hypothesis(repo, Hypothesis(path="app.py", symbol="handler"))
    assert verdict.confirmed
    assert verdict.span == (1, 3)
    assert "lines 1-3" in verdict.feedback


def test_verify_hypothesis_refutes_missing_path_and_symbol(tmp_path):
    repo = _make_repo(tmp_path, {"app.py": _APP})
    ghost = verify_hypothesis(repo, Hypothesis(path="ghost.py"))
    assert not ghost.confirmed
    assert "path does not exist" in ghost.feedback
    wrong = verify_hypothesis(repo, Hypothesis(path="app.py", symbol="no_such"))
    assert not wrong.confirmed
    assert "not found" in wrong.feedback


def test_verify_hypothesis_rejects_traversal_and_absolute_paths(tmp_path):
    repo = _make_repo(tmp_path, {"app.py": _APP})
    for bad in ("../app.py", "/etc/passwd", "..\\app.py", ""):
        verdict = verify_hypothesis(repo, Hypothesis(path=bad))
        assert not verdict.confirmed
        assert "path does not exist" in verdict.feedback


# --------------------------------------------------------------------------
# retriever: round loop behaviour
# --------------------------------------------------------------------------

def test_happy_path_confirms_and_stops_on_done(tmp_path):
    repo = _make_repo(tmp_path, {"app.py": _APP})
    backend = FakeBackend([
        _round(
            [{"path": "app.py", "symbol": "handler", "line": 2,
              "reason": "touches token", "confidence": 0.9}],
            True,
        ),
    ])
    result = HypothesisRetriever(backend, LexicalRepoRetriever()).retrieve(
        "token bug in handler", repo)
    assert result.files[0] == "app.py"
    assert result.symbols["app.py"] == ["handler"]
    assert result.spans["app.py"] == [(1, 3)]     # verified span, not base guess
    assert len(backend.calls) == 1                # done=true stops the loop


def test_refutation_feedback_reaches_round_two_and_corrects(tmp_path):
    repo = _make_repo(tmp_path, {"app.py": _APP})
    backend = FakeBackend([
        _round([{"path": "ghost.py", "confidence": 0.5},
                {"path": "app.py", "symbol": "no_such_symbol"}], False),
        _round([{"path": "app.py", "symbol": "handler"}], True),
    ])
    result = HypothesisRetriever(backend, LexicalRepoRetriever()).retrieve(
        "token bug", repo)
    round_two_prompt = backend.calls[1][0]
    assert "REFUTED ghost.py: path does not exist" in round_two_prompt
    assert "symbol 'no_such_symbol' not found" in round_two_prompt
    assert result.files[0] == "app.py"
    assert result.symbols["app.py"] == ["handler"]


def test_max_rounds_caps_iteration(tmp_path):
    repo = _make_repo(tmp_path, {"app.py": _APP})
    backend = FakeBackend([
        _round([{"path": f"ghost{i}.py"}], False) for i in range(5)
    ])
    result = HypothesisRetriever(
        backend, LexicalRepoRetriever(), max_rounds=2).retrieve("token", repo)
    assert len(backend.calls) == 2
    assert result.files == ("app.py",)  # nothing confirmed — base order kept


def test_malformed_round_degrades_to_base(tmp_path, caplog):
    repo = _make_repo(tmp_path, {"app.py": _APP})
    expected = LexicalRepoRetriever().retrieve("token", repo)
    backend = FakeBackend(["definitely not json"])
    with caplog.at_level(logging.WARNING):
        result = HypothesisRetriever(backend, LexicalRepoRetriever()).retrieve(
            "token", repo)
    assert result.files == expected.files
    assert result.spans == expected.spans
    assert result.symbols == expected.symbols
    assert len(backend.calls) == 1  # empty round adds nothing — loop stops
    assert any("malformed" in record.message for record in caplog.records)


def test_dedupe_across_rounds_confirms_once_then_stops(tmp_path):
    repo = _make_repo(tmp_path, {"app.py": _APP})
    backend = FakeBackend([
        _round([{"path": "app.py", "symbol": "handler"}], False),
        _round([{"path": "app.py", "symbol": "handler"}], False),
        _round([{"path": "app.py", "symbol": "handler"}], False),
    ])
    result = HypothesisRetriever(backend, LexicalRepoRetriever()).retrieve(
        "token", repo)
    assert result.symbols["app.py"] == ["handler"]  # confirmed exactly once
    assert result.spans["app.py"] == [(1, 3)]
    assert len(backend.calls) == 2  # repeat-only round adds nothing — stop


class _EmptyBase(RepoContextRetriever):
    """Base retriever stub that never finds anything."""

    def retrieve(self, query: str, workdir: Path) -> RepoContext:
        del query, workdir
        return RepoContext()


def test_empty_base_retrieval_still_localises(tmp_path):
    repo = _make_repo(tmp_path, {"app.py": _APP})
    backend = FakeBackend([
        _round([{"path": "app.py", "symbol": "handler"}], True),
    ])
    result = HypothesisRetriever(backend, _EmptyBase()).retrieve("token", repo)
    assert result.files == ("app.py",)
    assert result.spans["app.py"] == [(1, 3)]
    assert "(no candidates retrieved)" in backend.calls[0][0]


def test_confirmed_file_feeds_import_neighbours_forward(tmp_path):
    repo = _make_repo(tmp_path, {
        "core.py": "def compute(x):\n    return x\n",
        "caller.py": "import core\n\n\ndef run():\n    return core.compute(1)\n",
    })
    backend = FakeBackend([
        _round([{"path": "core.py", "symbol": "compute"}], False),
        _round([], False),
    ])
    HypothesisRetriever(backend, LexicalRepoRetriever()).retrieve("compute", repo)
    round_two_prompt = backend.calls[1][0]
    assert (
        "EVIDENCE core.py: import-graph callers/dependents: caller.py"
        in round_two_prompt
    )


def test_path_only_hypothesis_confirms_and_ranks_first(tmp_path):
    repo = _make_repo(tmp_path, {
        "a.py": "def one():\n    return 1\n",
        "b.py": "def two():\n    return token\n",
    })
    backend = FakeBackend([_round([{"path": "a.py"}], True)])
    result = HypothesisRetriever(backend, LexicalRepoRetriever()).retrieve(
        "token", repo)
    assert result.files[0] == "a.py"          # confirmed outranks base order
    assert set(result.files) == {"a.py", "b.py"}


def test_create_hypothesis_retriever_factory():
    retriever = create_hypothesis_retriever(
        FakeBackend(), LexicalRepoRetriever(), max_rounds=1, max_hypotheses=2)
    assert isinstance(retriever, HypothesisRetriever)


# --------------------------------------------------------------------------
# prompt mirror parity
# --------------------------------------------------------------------------

def test_prompt_mirror_is_byte_identical():
    root = Path(__file__).resolve().parents[1]
    canonical = root / "codes" / "run" / "CoT_Prompts" / "localization_hypothesis.py"
    bundled = root / "prthinker" / "prompts" / "localization_hypothesis.py"
    assert canonical.is_file()
    assert bundled.is_file()
    assert canonical.read_bytes() == bundled.read_bytes()

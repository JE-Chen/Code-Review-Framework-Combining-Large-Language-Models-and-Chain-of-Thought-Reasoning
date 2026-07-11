"""Tests for prthinker.execution_retriever — evidence-fused retrieval."""

from __future__ import annotations

from pathlib import Path

import pytest

from prthinker import execution_retriever
from prthinker.execution_retriever import (
    ExecutionGroundedRetriever,
    ExecutionSignalsConfig,
    create_execution_retriever,
)
from prthinker.fault_localization import CoverageMatrix, FusionWeights
from prthinker.repo_retrieval import RepoContext, RepoContextRetriever


class StubRetriever(RepoContextRetriever):
    """Base-retriever stand-in returning a fixed context, recording queries."""

    def __init__(self, context: RepoContext) -> None:
        self.context = context
        self.queries: list[str] = []

    def retrieve(self, query: str, workdir: Path) -> RepoContext:
        self.queries.append(query)
        return self.context


def _base_context() -> RepoContext:
    return RepoContext(
        files=("a.py", "b.py"),
        spans={"a.py": [(1, 3)], "b.py": []},
        symbols={"a.py": ["alpha"], "b.py": []},
    )


def _traceback_for(workdir: Path, rel: str, line: int, symbol: str) -> str:
    return (
        "Traceback (most recent call last):\n"
        f'  File "{workdir / rel}", line {line}, in {symbol}\n'
        "ValueError: boom\n"
    )


class TestDegradation:
    def test_no_signals_returns_base_context_unchanged(self, tmp_path):
        base = StubRetriever(_base_context())
        retriever = ExecutionGroundedRetriever(base)
        result = retriever.retrieve("plain refactor request, no failures", tmp_path)
        assert result is base.context
        assert base.queries == ["plain refactor request, no failures"]

    def test_matrix_without_failures_degrades_to_base(self, tmp_path):
        matrix = CoverageMatrix(
            coverage={"t": {("a.py", 1)}}, outcomes={"t": True}
        )
        retriever = ExecutionGroundedRetriever(
            StubRetriever(_base_context()),
            config=ExecutionSignalsConfig(matrix=matrix),
        )
        result = retriever.retrieve("no traceback here", tmp_path)
        assert result == _base_context()


class TestTraceOnlyPath:
    def test_trace_file_reranked_first_with_hint_and_symbol(self, tmp_path):
        base = StubRetriever(_base_context())
        retriever = ExecutionGroundedRetriever(base)
        query = "tests crash\n" + _traceback_for(tmp_path, "b.py", 5, "boom")
        result = retriever.retrieve(query, tmp_path)
        assert result.files == ("b.py", "a.py")
        assert result.spans["b.py"] == [(5, 5)]
        assert result.symbols["b.py"] == ["boom"]
        # Base spans/symbols survive; the covered a.py line adds no hint.
        assert result.spans["a.py"] == [(1, 3)]
        assert result.symbols["a.py"] == ["alpha"]

    def test_trace_file_outside_base_admitted_when_on_disk(self, tmp_path):
        (tmp_path / "extra.py").write_text("def f():\n    pass\n", encoding="utf-8")
        retriever = ExecutionGroundedRetriever(StubRetriever(_base_context()))
        query = _traceback_for(tmp_path, "extra.py", 2, "f")
        result = retriever.retrieve(query, tmp_path)
        assert result.files[0] == "extra.py"
        assert result.spans["extra.py"] == [(2, 2)]
        assert result.symbols["extra.py"] == ["f"]

    def test_nonexistent_and_unsafe_trace_paths_excluded(self, tmp_path):
        retriever = ExecutionGroundedRetriever(StubRetriever(_base_context()))
        query = (
            '  File "/elsewhere/ghost.py", line 3, in g\n'
            '  File "../escape.py", line 4, in h\n'
        )
        result = retriever.retrieve(query, tmp_path)
        assert "ghost.py" not in " ".join(result.files)
        assert all(".." not in rel for rel in result.files)
        assert set(result.files) == {"a.py", "b.py"}


class TestFullFusionPath:
    def _matrix(self) -> CoverageMatrix:
        return CoverageMatrix(
            coverage={
                "t_fail": {("m.py", 1), ("m.py", 2), ("a.py", 1)},
                "t_pass": {("m.py", 1), ("a.py", 1)},
            },
            outcomes={"t_fail": False, "t_pass": True},
        )

    def _base(self) -> StubRetriever:
        return StubRetriever(RepoContext(
            files=("a.py", "m.py"),
            spans={"a.py": [], "m.py": []},
            symbols={"a.py": [], "m.py": []},
        ))

    def test_sbfl_reranks_files_and_adds_line_hints(self, tmp_path):
        retriever = ExecutionGroundedRetriever(
            self._base(), config=ExecutionSignalsConfig(matrix=self._matrix())
        )
        result = retriever.retrieve("plain query, evidence from matrix", tmp_path)
        # m.py:2 is the only line covered solely by the failing test.
        assert result.files == ("m.py", "a.py")
        assert (2, 2) in result.spans["m.py"]
        assert (1, 1) in result.spans["m.py"]
        assert result.spans["a.py"] == [(1, 1)]

    def test_max_line_hints_caps_the_fused_lines(self, tmp_path):
        retriever = ExecutionGroundedRetriever(
            self._base(),
            config=ExecutionSignalsConfig(matrix=self._matrix(), max_line_hints=1),
        )
        result = retriever.retrieve("query", tmp_path)
        assert result.spans["m.py"] == [(2, 2)]
        assert result.spans["a.py"] == []

    def test_tarantula_formula_accepted(self, tmp_path):
        retriever = ExecutionGroundedRetriever(
            self._base(),
            config=ExecutionSignalsConfig(matrix=self._matrix(), formula="tarantula"),
        )
        result = retriever.retrieve("query", tmp_path)
        assert result.files[0] == "m.py"

    def test_trace_and_sbfl_fuse_together(self, tmp_path):
        base = self._base()
        retriever = ExecutionGroundedRetriever(
            base, config=ExecutionSignalsConfig(matrix=self._matrix())
        )
        query = "boom\n" + _traceback_for(tmp_path, "m.py", 2, "broken")
        result = retriever.retrieve(query, tmp_path)
        assert result.files == ("m.py", "a.py")
        assert (2, 2) in result.spans["m.py"]
        assert "broken" in result.symbols["m.py"]


class TestCoverageCollectionWiring:
    def test_collection_runs_once_per_workdir(self, tmp_path, monkeypatch):
        calls: list[list[str]] = []

        def fake_collect(_workdir, test_cmd, test_ids, timeout):
            del test_cmd, timeout
            calls.append(list(test_ids))
            return CoverageMatrix(
                coverage={"t::fail": {("a.py", 2)}},
                outcomes={"t::fail": False},
            )

        monkeypatch.setattr(execution_retriever, "collect_coverage", fake_collect)
        retriever = ExecutionGroundedRetriever(
            StubRetriever(_base_context()),
            config=ExecutionSignalsConfig(
                failing_tests=("t::fail",), passing_tests=("t::ok",)
            ),
        )
        first = retriever.retrieve("query", tmp_path)
        second = retriever.retrieve("query again", tmp_path)
        assert calls == [["t::fail", "t::ok"]]  # memoized per workdir
        assert (2, 2) in first.spans["a.py"] or (1, 3) in first.spans["a.py"]
        assert first.files == second.files

    def test_no_failing_tests_configured_skips_collection(self, tmp_path, monkeypatch):
        def explode(*_args, **_kwargs):
            raise AssertionError("collect_coverage must not run")

        monkeypatch.setattr(execution_retriever, "collect_coverage", explode)
        retriever = ExecutionGroundedRetriever(StubRetriever(_base_context()))
        result = retriever.retrieve("nothing here", tmp_path)
        assert result == _base_context()


class TestFactory:
    def test_knob_sequences_coerced_to_tuples(self):
        retriever = create_execution_retriever(
            StubRetriever(_base_context()),
            failing_tests=["t::a"],
            passing_tests=["t::b"],
            test_cmd=["pytest", "-q"],
            weights=(1.0, 2.0, 0.25),
        )
        config = retriever._config
        assert config.failing_tests == ("t::a",)
        assert config.passing_tests == ("t::b",)
        assert config.test_cmd == ("pytest", "-q")
        assert config.weights == FusionWeights(sbfl=1.0, trace=2.0, retrieval=0.25)

    def test_none_sequence_knobs_fall_back_to_defaults(self):
        retriever = create_execution_retriever(
            StubRetriever(_base_context()), test_cmd=None, failing_tests=None
        )
        assert retriever._config.test_cmd == ExecutionSignalsConfig().test_cmd
        assert retriever._config.failing_tests == ()

    def test_unknown_formula_raises_at_construction(self):
        with pytest.raises(ValueError, match="unknown SBFL formula"):
            create_execution_retriever(
                StubRetriever(_base_context()), formula="dstar"
            )

    def test_unknown_knob_raises_type_error(self):
        with pytest.raises(TypeError):
            create_execution_retriever(
                StubRetriever(_base_context()), bogus_knob=1
            )

"""Tests for prthinker.fault_localization — SBFL math and rank fusion."""

from __future__ import annotations

import pytest

from prthinker.fault_localization import (
    OCHIAI,
    TARANTULA,
    CoverageMatrix,
    FusionWeights,
    fuse_signals,
    sbfl_scores,
    top_suspicious,
)
from prthinker.stack_trace import TraceFrame

_RRF_BASE = 61.0  # offset 60 + rank 1 for the top-ranked item


def _three_test_matrix() -> CoverageMatrix:
    """Hand-checkable fixture: one failing, two passing tests.

    line 1 covered by all three, line 2 only by the failing test (the
    fault), line 3 only by one passing test.
    """
    return CoverageMatrix(
        coverage={
            "t_fail": {("m.py", 1), ("m.py", 2)},
            "t_pass_a": {("m.py", 1), ("m.py", 3)},
            "t_pass_b": {("m.py", 1)},
        },
        outcomes={"t_fail": False, "t_pass_a": True, "t_pass_b": True},
    )


class TestCoverageMatrix:
    def test_outcome_partitions(self):
        matrix = _three_test_matrix()
        assert matrix.failed_tests == ("t_fail",)
        assert matrix.passed_tests == ("t_pass_a", "t_pass_b")

    def test_empty_matrix(self):
        matrix = CoverageMatrix()
        assert matrix.failed_tests == ()
        assert matrix.passed_tests == ()


class TestSbflScores:
    def test_ochiai_known_answers(self):
        scores = sbfl_scores(_three_test_matrix(), formula=OCHIAI)
        # line 2: 1 / sqrt(1 * (1 + 0)) = 1.0
        assert scores[("m.py", 2)] == pytest.approx(1.0)
        # line 1: 1 / sqrt(1 * (1 + 2)) = 0.5774
        assert scores[("m.py", 1)] == pytest.approx(0.57735, abs=1e-4)
        # line 3: 0 failed cover it
        assert scores[("m.py", 3)] == pytest.approx(0.0)

    def test_tarantula_known_answers(self):
        scores = sbfl_scores(_three_test_matrix(), formula=TARANTULA)
        # line 2: fr=1, pr=0 -> 1.0
        assert scores[("m.py", 2)] == pytest.approx(1.0)
        # line 1: fr=1, pr=1 -> 0.5
        assert scores[("m.py", 1)] == pytest.approx(0.5)
        # line 3: fr=0 -> 0.0
        assert scores[("m.py", 3)] == pytest.approx(0.0)

    def test_no_failed_tests_scores_zero(self):
        matrix = CoverageMatrix(
            coverage={"t": {("m.py", 1)}}, outcomes={"t": True}
        )
        for formula in (OCHIAI, TARANTULA):
            assert sbfl_scores(matrix, formula) == {("m.py", 1): 0.0}

    def test_no_passed_tests_zero_division_guarded(self):
        matrix = CoverageMatrix(
            coverage={"t1": {("m.py", 1)}, "t2": {("m.py", 1)}},
            outcomes={"t1": False, "t2": False},
        )
        # ochiai: 2 / sqrt(2 * 2) = 1.0; tarantula: fr=1, pr guarded -> 1.0
        assert sbfl_scores(matrix, OCHIAI)[("m.py", 1)] == pytest.approx(1.0)
        assert sbfl_scores(matrix, TARANTULA)[("m.py", 1)] == pytest.approx(1.0)

    def test_empty_matrix_yields_empty_scores(self):
        assert sbfl_scores(CoverageMatrix()) == {}

    def test_unknown_formula_raises(self):
        with pytest.raises(ValueError, match="unknown SBFL formula"):
            sbfl_scores(_three_test_matrix(), formula="dstar")


class TestTopSuspicious:
    def test_orders_and_truncates(self):
        scores = {("a.py", 1): 0.2, ("a.py", 2): 0.9, ("b.py", 3): 0.5}
        assert top_suspicious(scores, 2) == [
            ("a.py", 2, 0.9), ("b.py", 3, 0.5),
        ]

    def test_k_larger_than_scores(self):
        scores = {("a.py", 1): 0.2}
        assert top_suspicious(scores, 10) == [("a.py", 1, 0.2)]

    def test_k_zero_or_negative_yields_empty(self):
        scores = {("a.py", 1): 0.2}
        assert top_suspicious(scores, 0) == []
        assert top_suspicious(scores, -3) == []

    def test_ties_break_by_path_then_line(self):
        scores = {("b.py", 1): 0.5, ("a.py", 9): 0.5, ("a.py", 2): 0.5}
        assert top_suspicious(scores, 3) == [
            ("a.py", 2, 0.5), ("a.py", 9, 0.5), ("b.py", 1, 0.5),
        ]


class TestFuseSignals:
    def test_multi_signal_lines_outrank_single_signal(self):
        fused = fuse_signals(
            sbfl={("a.py", 1): 1.0},
            trace_frames=[("b.py", 2)],
            retrieval_lines=[("a.py", 1), ("c.py", 3)],
        )
        order = [(path, line) for path, line, _ in fused]
        assert order == [("a.py", 1), ("b.py", 2), ("c.py", 3)]
        # a.py:1 gets sbfl (1.0) + retrieval (0.5) at rank 1 of each signal.
        assert fused[0][2] == pytest.approx(1.5 / _RRF_BASE)
        assert fused[1][2] == pytest.approx(1.0 / _RRF_BASE)
        assert fused[2][2] == pytest.approx(0.5 / (_RRF_BASE + 1))

    def test_accepts_trace_frame_objects(self):
        fused = fuse_signals(
            sbfl={},
            trace_frames=[TraceFrame(path="x.py", line=7, symbol="f", rank=0)],
            retrieval_lines=[],
        )
        assert fused == [("x.py", 7, pytest.approx(1.0 / _RRF_BASE))]

    def test_duplicates_within_one_signal_count_once(self):
        fused = fuse_signals(
            sbfl={},
            trace_frames=[("x.py", 7), ("x.py", 7), ("y.py", 1)],
            retrieval_lines=[],
        )
        assert fused[0] == ("x.py", 7, pytest.approx(1.0 / _RRF_BASE))
        assert fused[1] == ("y.py", 1, pytest.approx(1.0 / (_RRF_BASE + 1)))

    def test_all_signals_empty_yields_empty(self):
        assert fuse_signals({}, [], []) == []

    def test_zero_weights_tie_broken_deterministically(self):
        fused = fuse_signals(
            sbfl={("b.py", 1): 1.0},
            trace_frames=[("a.py", 2)],
            retrieval_lines=[],
            weights=FusionWeights(sbfl=0.0, trace=0.0, retrieval=0.0),
        )
        assert [(path, line) for path, line, _ in fused] == [("a.py", 2), ("b.py", 1)]
        assert all(score == 0.0 for _, _, score in fused)

    def test_custom_weights_shift_the_order(self):
        fused = fuse_signals(
            sbfl={("s.py", 1): 1.0},
            trace_frames=[("t.py", 2)],
            retrieval_lines=[("r.py", 3)],
            weights=FusionWeights(sbfl=0.1, trace=0.2, retrieval=9.0),
        )
        assert [(path, line) for path, line, _ in fused] == [
            ("r.py", 3), ("t.py", 2), ("s.py", 1),
        ]

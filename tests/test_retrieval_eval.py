"""Tests for retrieval evaluation metrics (base + tolerant localization)."""

from __future__ import annotations

from dataclasses import asdict

from prthinker.retrieval_eval import RetrievalMetrics, evaluate


def test_evaluate_base_metrics_unchanged():
    # The pre-existing four metrics keep their exact values and conventions.
    metrics = evaluate(["a", "b"], ["a"], ["a"], [True, False])
    assert metrics.recall == 1.0
    assert metrics.precision == 0.5
    assert metrics.utilization == 0.5
    assert metrics.citation_correctness == 0.5


def test_evaluate_empty_input_conventions_unchanged():
    metrics = evaluate([], [], [], [])
    assert metrics == RetrievalMetrics(1.0, 1.0, 1.0, 1.0)
    # Empty retrieval against non-empty expected -> zero precision.
    assert evaluate([], ["a"], [], []).precision == 0.0


def test_evaluate_without_span_data_leaves_optional_fields_none():
    metrics = evaluate(["a"], ["a"], ["a"], [True])
    assert metrics.line_hit_at_k is None
    assert metrics.window_recall is None
    assert metrics.block_f1 is None


def test_evaluate_with_span_data_fills_tolerant_metrics():
    metrics = evaluate(
        ["a"], ["a"], ["a"], [True],
        pred_spans={"a.py": [(5, 5)]},
        gold_spans=[{"file": "a.py", "start_line": 7, "end_line": 7}],
    )
    assert metrics.line_hit_at_k == 0.0  # line 5 is not gold line 7
    assert metrics.window_recall == 1.0  # |5 - 7| <= 3
    assert metrics.block_f1 == 1.0      # no sources -> both in bucket (1, 20)


def test_evaluate_with_sources_scores_blocks(tmp_path):
    source = "def alpha():\n    return 1\n\n\ndef beta():\n    return 2\n"
    (tmp_path / "mod.py").write_text(source, encoding="utf-8")
    metrics = evaluate(
        ["mod.py"], ["mod.py"], [], [],
        pred_spans={"mod.py": [(6, 6)]},  # inside beta
        gold_spans=[{"file": "mod.py", "start_line": 2, "end_line": 2}],  # alpha
        sources={"mod.py": (tmp_path / "mod.py").read_text(encoding="utf-8")},
    )
    assert metrics.block_f1 == 0.0


def test_evaluate_empty_gold_spans_yield_none_metrics():
    # Documented convention: empty gold line set -> metric undefined -> None.
    metrics = evaluate(["a"], ["a"], [], [], pred_spans={"a.py": [(1, 1)]}, gold_spans=[])
    assert metrics.line_hit_at_k is None
    assert metrics.window_recall is None
    assert metrics.block_f1 is None


def test_evaluate_none_pred_spans_treated_as_empty_prediction():
    metrics = evaluate(
        [], ["a"], [], [],
        gold_spans=[{"file": "a.py", "start_line": 1, "end_line": 1}],
    )
    assert metrics.line_hit_at_k == 0.0
    assert metrics.window_recall == 0.0
    assert metrics.block_f1 == 0.0


def test_metrics_round_trip_via_asdict():
    metrics = evaluate(
        ["a"], ["a"], ["a"], [True],
        pred_spans={"a.py": [(1, 1)]},
        gold_spans=[{"file": "a.py", "start_line": 1, "end_line": 1}],
    )
    assert RetrievalMetrics(**asdict(metrics)) == metrics

"""Tests for the repository-context retrieval scorer."""

from __future__ import annotations

from prthinker.retrieval_scoring import (
    DimensionScore,
    RetrievalCaseScore,
    _span_bounds,
    aggregate_retrieval,
    gold_files,
    gold_lines,
    gold_symbols,
    predicted_lines,
    score_retrieval_case,
    score_symbols,
)

_GOLD = [
    {"file": "a.py", "start_line": 1, "end_line": 3},
    {"file": "b.py", "start_line": 10, "end_line": 10},
]


def test_dimension_f1():
    score = DimensionScore(coverage=0.5, precision=0.5, intersection=1, gold_size=2, pred_size=2)
    assert score.f1 == 0.5
    empty = DimensionScore(0.0, 0.0, 0, 0, 0)
    assert empty.f1 == 0.0


def test_span_bounds_accepts_tuple_and_mapping():
    assert _span_bounds((3, 7)) == (3, 7)
    assert _span_bounds([3, 7]) == (3, 7)
    assert _span_bounds({"start": 3, "end": 7}) == (3, 7)
    assert _span_bounds({"start_line": 3, "end_line": 7}) == (3, 7)
    assert _span_bounds({"start": 3}) is None
    assert _span_bounds("nope") is None


def test_gold_files_and_lines():
    assert gold_files(_GOLD) == {"a.py", "b.py"}
    assert gold_lines(_GOLD) == {("a.py", 1), ("a.py", 2), ("a.py", 3), ("b.py", 10)}


def test_predicted_lines_from_tuple_and_dict_spans():
    tuples = predicted_lines({"a.py": [(1, 2)]})
    dicts = predicted_lines({"a.py": [{"start": 1, "end": 2}]})
    assert tuples == dicts == {("a.py", 1), ("a.py", 2)}


def test_score_case_file_and_line_overlap():
    score = score_retrieval_case(
        pred_files=["a.py", "z.py"],
        pred_spans={"a.py": [(2, 2)]},
        gold_spans=_GOLD,
    )
    # files: gold {a,b}, pred {a,z} -> intersection 1
    assert score.file.intersection == 1
    assert score.file.gold_size == 2 and score.file.pred_size == 2
    assert score.file.coverage == 0.5 and score.file.precision == 0.5
    # lines: gold has a.py:2, pred has a.py:2 -> intersection 1
    assert score.line.intersection == 1


def test_score_case_no_overlap():
    score = score_retrieval_case(["x.py"], {}, _GOLD)
    assert score.file.intersection == 0
    assert score.file.coverage == 0.0
    assert score.line.pred_size == 0
    assert score.line.precision == 0.0  # empty prediction -> 0 precision


def test_aggregate_is_micro_averaged():
    # Case 1: 1/2 gold files hit, 1 pred. Case 2: 2/2 gold files hit, 4 pred.
    c1 = RetrievalCaseScore(
        file=DimensionScore(0.5, 1.0, 1, 2, 1), line=DimensionScore(0, 0, 0, 5, 0)
    )
    c2 = RetrievalCaseScore(
        file=DimensionScore(1.0, 0.5, 2, 2, 4), line=DimensionScore(0, 0, 0, 5, 0)
    )
    agg = aggregate_retrieval([c1, c2])
    assert agg["cases"] == 2
    # micro coverage = (1+2)/(2+2) = 0.75 ; micro precision = (1+2)/(1+4) = 0.6
    assert agg["file"]["coverage"] == 0.75
    assert agg["file"]["precision"] == 0.6


def test_aggregate_empty_cases():
    agg = aggregate_retrieval([])
    assert agg["cases"] == 0
    assert agg["file"]["coverage"] == 0.0 and agg["file"]["f1"] == 0.0


def test_gold_symbols_extracts_def_and_class_names():
    spans = [
        {"file": "a.py", "content": "class Widget:\n    def render(self):\n        pass\n"},
        {"file": "b.py", "content": "def helper():\n    return 1\n"},
    ]
    assert gold_symbols(spans) == {"Widget", "render", "helper"}


def test_score_symbols_overlap():
    gold = [{"file": "a.py", "content": "def f():\n    pass\nclass C:\n    pass\n"}]
    pred = {"a.py": ["f", "other"]}  # 1 of 2 gold symbols, 1 wrong
    score = score_symbols(pred, gold)
    assert score.intersection == 1
    assert score.gold_size == 2 and score.pred_size == 2
    assert score.coverage == 0.5 and score.precision == 0.5


def test_score_symbols_empty_prediction():
    gold = [{"file": "a.py", "content": "def f():\n    pass\n"}]
    score = score_symbols({}, gold)
    assert score.intersection == 0 and score.precision == 0.0

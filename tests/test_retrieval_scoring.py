"""Tests for the repository-context retrieval scorer."""

from __future__ import annotations

from pathlib import Path

import pytest

from prthinker.retrieval_scoring import (
    DimensionScore,
    RetrievalCaseScore,
    _ordered_predicted_lines,
    _span_bounds,
    aggregate_retrieval,
    block_f1,
    gold_files,
    gold_lines,
    gold_symbols,
    line_hit_at_k,
    predicted_lines,
    score_retrieval_case,
    score_retrieval_case_extended,
    score_symbols,
    window_recall,
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


def test_gold_symbols_ast_ignores_def_in_strings_and_comments():
    # A real AST parse must not count "def"/"class" tokens inside a docstring or
    # comment — the regex fallback would over-count these as symbols.
    spans = [{"file": "a.py", "content":
              'def real():\n    "def fake(): pass"\n    # class Ghost:\n    return 1\n'}]
    assert gold_symbols(spans) == {"real"}


def test_gold_symbols_ast_handles_indented_method_snippet():
    from prthinker.retrieval_scoring import _ast_symbols

    # An indented method body (not a valid module as-is) parses after dedent.
    assert _ast_symbols("    def method(self):\n        return 1\n") == {"method"}


def test_gold_symbols_regex_fallback_on_unparseable_snippet():
    from prthinker.retrieval_scoring import _ast_symbols

    snippet = "def broken(:\n    class C:\n"  # syntactically invalid
    assert _ast_symbols(snippet) is None                       # AST gives up
    assert gold_symbols([{"content": snippet}]) == {"broken", "C"}  # regex fallback


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


# --- tolerant localization metrics ----------------------------------------


def test_ordered_predicted_lines_order_and_dedup():
    # Insertion order across files, span order within a file, ascending lines
    # within a span; repeats keep only the first occurrence.
    spans = {"b.py": [(3, 4), (4, 5)], "a.py": [(1, 1)]}
    assert _ordered_predicted_lines(spans) == [
        ("b.py", 3), ("b.py", 4), ("b.py", 5), ("a.py", 1)
    ]


def test_line_hit_at_k_hit_and_miss():
    gold = [{"file": "a.py", "start_line": 5, "end_line": 5}]
    assert line_hit_at_k({"a.py": [(5, 5)]}, gold) == 1.0
    assert line_hit_at_k({"a.py": [(6, 6)]}, gold) == 0.0
    # Same line number in the wrong file is a miss.
    assert line_hit_at_k({"b.py": [(5, 5)]}, gold) == 0.0


def test_line_hit_at_k_boundary_exactly_k():
    # Gold line 10 is the 10th predicted line -> inside the default k=10 cut.
    gold = [{"file": "a.py", "start_line": 10, "end_line": 10}]
    assert line_hit_at_k({"a.py": [(1, 10)]}, gold) == 1.0
    # Gold line 11 is the 11th predicted line -> just outside k=10.
    gold_11 = [{"file": "a.py", "start_line": 11, "end_line": 11}]
    assert line_hit_at_k({"a.py": [(1, 11)]}, gold_11) == 0.0
    # Explicit k: 3rd line hits at k=3, misses at k=2.
    gold_3 = [{"file": "a.py", "start_line": 3, "end_line": 3}]
    assert line_hit_at_k({"a.py": [(1, 5)]}, gold_3, k=3) == 1.0
    assert line_hit_at_k({"a.py": [(1, 5)]}, gold_3, k=2) == 0.0


def test_line_hit_at_k_empty_gold_returns_none():
    # Convention: no gold lines -> metric undefined -> None (case excluded).
    assert line_hit_at_k({"a.py": [(1, 2)]}, []) is None


def test_line_hit_at_k_empty_prediction_scores_zero():
    gold = [{"file": "a.py", "start_line": 1, "end_line": 1}]
    assert line_hit_at_k({}, gold) == 0.0


def test_line_hit_at_k_rejects_invalid_k():
    gold = [{"file": "a.py", "start_line": 1, "end_line": 1}]
    with pytest.raises(ValueError):
        line_hit_at_k({}, gold, k=0)


def test_window_recall_edges_at_exactly_window():
    gold = [{"file": "a.py", "start_line": 10, "end_line": 10}]
    # Exactly ±window (default 3) counts; ±(window+1) does not.
    assert window_recall({"a.py": [(13, 13)]}, gold) == 1.0
    assert window_recall({"a.py": [(7, 7)]}, gold) == 1.0
    assert window_recall({"a.py": [(14, 14)]}, gold) == 0.0
    assert window_recall({"a.py": [(6, 6)]}, gold) == 0.0
    # A nearby line in a different file does not count.
    assert window_recall({"b.py": [(10, 10)]}, gold) == 0.0


def test_window_recall_zero_window_is_exact_match():
    gold = [{"file": "a.py", "start_line": 10, "end_line": 10}]
    assert window_recall({"a.py": [(10, 10)]}, gold, window=0) == 1.0
    assert window_recall({"a.py": [(11, 11)]}, gold, window=0) == 0.0


def test_window_recall_is_gold_line_fraction():
    # Gold lines 1 and 100; only line 1 has a prediction within ±3.
    gold = [
        {"file": "a.py", "start_line": 1, "end_line": 1},
        {"file": "a.py", "start_line": 100, "end_line": 100},
    ]
    assert window_recall({"a.py": [(2, 2)]}, gold) == 0.5


def test_window_recall_empty_gold_and_empty_prediction():
    # Convention: no gold lines -> None (excluded); empty prediction -> 0.0.
    assert window_recall({"a.py": [(1, 1)]}, []) is None
    gold = [{"file": "a.py", "start_line": 1, "end_line": 1}]
    assert window_recall({}, gold) == 0.0


def test_window_recall_rejects_negative_window():
    gold = [{"file": "a.py", "start_line": 1, "end_line": 1}]
    with pytest.raises(ValueError):
        window_recall({}, gold, window=-1)


_PY_SOURCE = (
    "def alpha():\n"
    "    a = 1\n"
    "    return a\n"
    "\n"
    "\n"
    "def beta():\n"
    "    b = 2\n"
    "    return b\n"
)


def _py_sources(tmp_path: Path) -> dict[str, str]:
    """Write a real Python module to tmp_path and load it as a sources map."""
    module = tmp_path / "mod.py"
    module.write_text(_PY_SOURCE, encoding="utf-8")
    return {"mod.py": module.read_text(encoding="utf-8")}


def test_block_f1_maps_python_lines_to_enclosing_blocks(tmp_path: Path):
    sources = _py_sources(tmp_path)
    gold = [{"file": "mod.py", "start_line": 2, "end_line": 3}]  # inside alpha
    # Prediction inside the same function block -> full credit.
    assert block_f1({"mod.py": [(3, 3)]}, gold, sources) == 1.0
    # Prediction inside the other function block -> no overlap.
    assert block_f1({"mod.py": [(7, 7)]}, gold, sources) == 0.0


def test_block_f1_partial_overlap_hand_computed(tmp_path: Path):
    sources = _py_sources(tmp_path)
    gold = [{"file": "mod.py", "start_line": 2, "end_line": 3}]
    # Pred lines 2..7: alpha block (1,3), blank lines 4-5 -> bucket (1,20),
    # beta block (6,8). Gold blocks {alpha}. F1 = 2*1 / (1+3) = 0.5.
    assert block_f1({"mod.py": [(2, 7)]}, gold, sources) == 0.5


def test_block_f1_bucket_fallback_for_non_python():
    # .js never uses the def/class parser: lines 20 and 21 straddle the
    # 20-line bucket boundary -> gold occupies buckets (1,20) and (21,40).
    gold = [{"file": "app.js", "start_line": 20, "end_line": 21}]
    score = block_f1({"app.js": [(20, 20)]}, gold, {"app.js": "var x = 1;\n"})
    assert score == pytest.approx(2 / 3)


def test_block_f1_bucket_fallback_when_source_missing():
    # No sources entry for the path -> bucket granularity even for .py.
    gold = [{"file": "mod.py", "start_line": 2, "end_line": 3}]
    assert block_f1({"mod.py": [(19, 19)]}, gold, None) == 1.0  # same (1,20) bucket
    assert block_f1({"mod.py": [(21, 21)]}, gold, None) == 0.0  # next bucket


def test_block_f1_python_line_outside_blocks_uses_bucket(tmp_path: Path):
    source = "import os\n\n\ndef alpha():\n    return os\n"
    module = tmp_path / "mod.py"
    module.write_text(source, encoding="utf-8")
    sources = {"mod.py": module.read_text(encoding="utf-8")}
    # Line 1 sits above any def/class block -> bucket (1,20) on both sides.
    gold = [{"file": "mod.py", "start_line": 1, "end_line": 1}]
    assert block_f1({"mod.py": [(2, 2)]}, gold, sources) == 1.0


def test_block_f1_empty_gold_and_empty_prediction(tmp_path: Path):
    sources = _py_sources(tmp_path)
    # Convention: no gold lines -> None (excluded); empty prediction -> 0.0.
    assert block_f1({"mod.py": [(1, 1)]}, [], sources) is None
    gold = [{"file": "mod.py", "start_line": 2, "end_line": 2}]
    assert block_f1({}, gold, sources) == 0.0


def test_score_retrieval_case_extended_fills_new_fields(tmp_path: Path):
    sources = _py_sources(tmp_path)
    gold = [{"file": "mod.py", "start_line": 2, "end_line": 3}]
    score = score_retrieval_case_extended(
        ["mod.py"], {"mod.py": [(3, 3)]}, gold, sources=sources
    )
    # Base file/line dimensions match the plain scorer exactly.
    base = score_retrieval_case(["mod.py"], {"mod.py": [(3, 3)]}, gold)
    assert score.file == base.file and score.line == base.line
    assert score.line_hit_at_k == 1.0
    assert score.window_recall == 1.0
    assert score.block_f1 == 1.0


def test_aggregate_retrieval_omits_tolerant_keys_without_extras():
    # Cases built the pre-existing way keep the pre-existing output shape.
    case = score_retrieval_case(["a.py"], {"a.py": [(1, 1)]}, _GOLD)
    agg = aggregate_retrieval([case])
    assert set(agg) == {"cases", "file", "line"}


def test_aggregate_retrieval_means_tolerant_metrics_and_excludes_none():
    hit = RetrievalCaseScore(
        file=DimensionScore(1, 1, 1, 1, 1), line=DimensionScore(1, 1, 1, 1, 1),
        line_hit_at_k=1.0, window_recall=1.0, block_f1=1.0,
    )
    miss = RetrievalCaseScore(
        file=DimensionScore(0, 0, 0, 1, 1), line=DimensionScore(0, 0, 0, 1, 1),
        line_hit_at_k=0.0, window_recall=0.5, block_f1=0.0,
    )
    undefined = RetrievalCaseScore(  # e.g. empty gold -> excluded from means
        file=DimensionScore(0, 0, 0, 0, 0), line=DimensionScore(0, 0, 0, 0, 0),
    )
    agg = aggregate_retrieval([hit, miss, undefined])
    assert agg["line_hit_at_k"] == 0.5
    assert agg["window_recall"] == 0.75
    assert agg["block_f1"] == 0.5

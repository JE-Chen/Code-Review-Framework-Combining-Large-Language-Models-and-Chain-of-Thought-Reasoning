import json
from pathlib import Path
from prthinker.cli import main


def test_retrieval_eval_cli(tmp_path: Path, capsys):
    source = tmp_path / "rows.jsonl"
    source.write_text(
        json.dumps(
            {
                "retrieved": ["a", "b"],
                "expected": ["a"],
                "used": ["a"],
                "cited_correct": [True],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    assert main(["retrieval-eval", str(source)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert (
        result["aggregate"]["recall"] == 1 and result["aggregate"]["precision"] == 0.5
    )


def test_retrieval_eval_cli_legacy_rows_keep_exact_output_shape(tmp_path: Path, capsys):
    # Rows without span data must not grow new keys anywhere in the output —
    # the pre-existing JSON stays byte-compatible.
    source = tmp_path / "rows.jsonl"
    source.write_text(
        json.dumps({"retrieved": ["a"], "expected": ["a"], "used": [], "cited_correct": []})
        + "\n",
        encoding="utf-8",
    )
    assert main(["retrieval-eval", str(source)]) == 0
    result = json.loads(capsys.readouterr().out)
    base_keys = ["recall", "precision", "utilization", "citation_correctness"]
    assert list(result["aggregate"].keys()) == base_keys
    assert list(result["rows"][0].keys()) == base_keys


def test_retrieval_eval_cli_span_rows_add_tolerant_metrics(tmp_path: Path, capsys):
    source = tmp_path / "rows.jsonl"
    row = {
        "retrieved": ["a"],
        "expected": ["a"],
        "used": ["a"],
        "cited_correct": [True],
        "pred_spans": {"a.py": [[5, 5]]},
        "gold_spans": [{"file": "a.py", "start_line": 7, "end_line": 7}],
    }
    source.write_text(json.dumps(row) + "\n", encoding="utf-8")
    assert main(["retrieval-eval", str(source)]) == 0
    result = json.loads(capsys.readouterr().out)
    # Hand-computed: hit@10 misses (5 != 7), ±3 window covers |5-7|,
    # bucket fallback puts both lines in block (1, 20).
    assert result["aggregate"]["line_hit_at_k"] == 0.0
    assert result["aggregate"]["window_recall"] == 1.0
    assert result["aggregate"]["block_f1"] == 1.0
    assert result["rows"][0]["window_recall"] == 1.0


def test_retrieval_eval_cli_mixed_rows_average_only_scored_rows(tmp_path: Path, capsys):
    span_row = {
        "retrieved": [],
        "expected": [],
        "used": [],
        "cited_correct": [],
        "pred_spans": {"a.py": [[1, 1]]},
        "gold_spans": [{"file": "a.py", "start_line": 1, "end_line": 1}],
    }
    legacy_row = {"retrieved": ["a"], "expected": ["a"], "used": [], "cited_correct": []}
    source = tmp_path / "rows.jsonl"
    source.write_text(
        json.dumps(span_row) + "\n" + json.dumps(legacy_row) + "\n", encoding="utf-8"
    )
    assert main(["retrieval-eval", str(source)]) == 0
    result = json.loads(capsys.readouterr().out)
    # The legacy row is excluded from the tolerant means, not counted as 0.
    assert result["aggregate"]["line_hit_at_k"] == 1.0
    assert "line_hit_at_k" not in result["rows"][1]

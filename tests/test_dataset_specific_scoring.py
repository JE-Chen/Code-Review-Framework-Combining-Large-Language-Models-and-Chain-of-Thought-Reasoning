import json
from pathlib import Path
from prthinker.benchmark_scoring import score_files


def _write(path: Path, rows):
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def test_choice_and_retrieval_evaluators(tmp_path: Path):
    cases = tmp_path / "choice-cases.jsonl"
    out = tmp_path / "choice-out.jsonl"
    _write(
        cases,
        [
            {
                "case_id": "q",
                "prompt": "p",
                "metadata": {"dataset": "codereviewqa", "answer": "B"},
            }
        ],
    )
    _write(out, [{"case_id": "q", "raw_output": "B"}])
    assert score_files(cases, out)[0].f1 == 1
    cases = tmp_path / "ctx-cases.jsonl"
    out = tmp_path / "ctx-out.jsonl"
    _write(
        cases,
        [
            {
                "case_id": "c",
                "prompt": "p",
                "metadata": {"dataset": "contextbench", "gold_context": ["a", "b"]},
            }
        ],
    )
    _write(out, [{"case_id": "c", "raw_output": json.dumps({"retrieved": ["a", "x"]})}])
    score = score_files(cases, out)[0]
    assert (score.tp, score.fp, score.fn) == (1, 1, 1)

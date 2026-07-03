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

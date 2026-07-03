import json
from pathlib import Path
from prthinker.cli import main
from tests.conftest import FakeBackend


def test_benchmark_score_and_compare(tmp_path: Path, capsys):
    cases = tmp_path / "cases.jsonl"
    base = tmp_path / "base.jsonl"
    better = tmp_path / "better.jsonl"
    cases.write_text(
        json.dumps(
            {
                "case_id": "x",
                "prompt": "p",
                "metadata": {
                    "ground_truth": [
                        {"path": "a.py", "line": 2, "comment": "missing validation"}
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    base.write_text(
        json.dumps({"case_id": "x", "raw_output": "[]"}) + "\n", encoding="utf-8"
    )
    better.write_text(
        json.dumps(
            {
                "case_id": "x",
                "raw_output": json.dumps(
                    [{"path": "a.py", "line": 2, "comment": "missing validation"}]
                ),
            }
        )
        + "\n",
        encoding="utf-8",
    )
    assert (
        main(
            ["benchmark", "score", str(cases), str(better), "--bootstrap-samples", "10"]
        )
        == 0
    )
    assert json.loads(capsys.readouterr().out)["aggregate"]["f1"] == 1
    assert (
        main(
            [
                "benchmark",
                "compare",
                str(cases),
                str(base),
                str(better),
                "--bootstrap-samples",
                "10",
            ]
        )
        == 0
    )
    assert json.loads(capsys.readouterr().out)["wins"] == 1


def test_benchmark_run_writes_bundle(tmp_path: Path, capsys, monkeypatch):
    cases = tmp_path / "cases.jsonl"
    cases.write_text('{"case_id":"x","prompt":"review"}\n', encoding="utf-8")
    backend = FakeBackend(['[{"path":"a.py","line":1,"comment":"bug"}]'])
    monkeypatch.setattr("prthinker.backends.create_backend", lambda _config: backend)
    monkeypatch.setattr(
        "prthinker.cli_review._build_config",
        lambda _args: type("Config", (), {"max_new_tokens": 32})(),
    )
    assert main(["benchmark", "run", str(cases), str(tmp_path / "run")]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["cases"] == 1
    assert (tmp_path / "run" / "manifest.json").exists()

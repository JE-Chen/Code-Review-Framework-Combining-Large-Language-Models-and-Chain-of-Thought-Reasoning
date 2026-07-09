from __future__ import annotations

import json
from pathlib import Path

from prthinker.cli import main
from prthinker.retrieval_report_cli import render_markdown, summarize


def test_retrieval_report_summarizes_trajectory(tmp_path: Path, capsys) -> None:
    source = tmp_path / "trace.jsonl"
    rows = [
        {
            "run_id": "r",
            "event": "retrieve",
            "timestamp": 1,
            "path": "a.py",
            "metadata": {"retrieved": ["d1", "d2"]},
        },
        {
            "run_id": "r",
            "event": "retrieval_use",
            "timestamp": 2,
            "path": "a.py",
            "metadata": {"used": ["d1"], "cited_indices": [1]},
        },
    ]
    source.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")

    assert main(["retrieval-report", str(source)]) == 0
    out = capsys.readouterr().out

    assert "# Retrieval report" in out
    assert "`a.py`: 2 retrieved" in out


def test_retrieval_report_json_summary() -> None:
    summary = summarize(
        [
            {"event": "retrieve", "metadata": {"retrieved": ["a", "b"]}},
            {"event": "retrieval_use", "metadata": {"used": ["a"]}},
        ]
    )

    assert summary["retrieved_total"] == 2
    assert summary["used_total"] == 1
    assert "Utilization: 0.50" in render_markdown(summary)

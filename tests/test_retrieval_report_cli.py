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


def test_retrieval_report_without_metrics_keeps_summary_shape() -> None:
    # No tolerant-metric metadata -> no new key, no new markdown section.
    summary = summarize([{"event": "retrieve", "metadata": {"retrieved": ["a"]}}])
    assert "retrieval_metrics" not in summary
    assert "Retrieval quality" not in render_markdown(summary)


def test_retrieval_report_renders_tolerant_metrics_when_present() -> None:
    summary = summarize(
        [
            {
                "event": "retrieval_eval",
                "metadata": {"line_hit_at_k": 1.0, "window_recall": 0.5, "block_f1": 0.25},
            },
            {"event": "retrieval_eval", "metadata": {"line_hit_at_k": 0.0}},
            # Non-numeric / boolean values are ignored, never averaged.
            {"event": "retrieval_eval", "metadata": {"line_hit_at_k": True, "block_f1": "x"}},
        ]
    )
    assert summary["retrieval_metrics"] == {
        "line_hit_at_k": 0.5,
        "window_recall": 0.5,
        "block_f1": 0.25,
    }
    report = render_markdown(summary)
    assert "## Retrieval quality" in report
    assert "- Line hit@k: 0.50" in report
    assert "- Window recall: 0.50" in report
    assert "- Block F1: 0.25" in report


def test_retrieval_report_cli_json_includes_metrics(tmp_path: Path, capsys) -> None:
    source = tmp_path / "trace.jsonl"
    rows = [
        {"event": "retrieve", "metadata": {"retrieved": ["d1"]}},
        {"event": "retrieval_eval", "metadata": {"window_recall": 0.75}},
    ]
    source.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")

    assert main(["retrieval-report", str(source), "--format", "json"]) == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["retrieval_metrics"] == {"window_recall": 0.75}

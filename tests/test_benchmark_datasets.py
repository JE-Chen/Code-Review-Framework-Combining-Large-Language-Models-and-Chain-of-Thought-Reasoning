"""Tests for offline public benchmark adapters."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from prthinker.benchmark_datasets import canonicalize, convert_dataset


def test_canonicalize_preserves_ground_truth_outside_prompt() -> None:
    result = canonicalize(
        {
            "instance_id": "42",
            "repo": "org/repo",
            "pr_title": "Fix parser",
            "issue_text": "Parser crashes",
            "patch": "diff --git a/a.py b/a.py\n+x = 1",
            "human_comments": [{"line": 1, "body": "missing validation"}],
        },
        index=1,
        dataset="swe-prbench",
    )
    assert result["case_id"] == "swe-prbench:42"
    assert "missing validation" not in result["prompt"]
    assert result["metadata"]["ground_truth"][0]["line"] == 1


def test_convert_jsonl(tmp_path: Path) -> None:
    source = tmp_path / "source.jsonl"
    target = tmp_path / "canonical.jsonl"
    source.write_text(
        json.dumps({"id": 1, "diff": "diff --git a/a b/a\n+x"}) + "\n",
        encoding="utf-8",
    )
    assert convert_dataset(source, target, dataset="codefuse-cr-bench") == 1
    assert json.loads(target.read_text(encoding="utf-8"))["case_id"] == (
        "codefuse-cr-bench:1"
    )


def test_missing_diff_is_rejected() -> None:
    with pytest.raises(ValueError, match="no diff"):
        canonicalize({"id": "x"}, index=1, dataset="swe-prbench")


def test_contextbench_accepts_query_without_diff() -> None:
    row = canonicalize(
        {"id": "r", "query": "find parser", "gold_context": ["src/parser.py"]},
        index=1,
        dataset="contextbench",
    )
    assert row["metadata"]["gold_context"] == ["src/parser.py"]
    assert "retrieved" in row["prompt"]


def test_contextbench_preserves_base_commit_and_repo_url() -> None:
    row = canonicalize(
        {
            "id": "r",
            "query": "find parser",
            "gold_context": ["src/parser.py"],
            "base_commit": "abc123",
            "repo_url": "https://github.com/org/repo",
        },
        index=1,
        dataset="contextbench",
    )
    assert row["metadata"]["base_commit"] == "abc123"
    assert row["metadata"]["repo_url"] == "https://github.com/org/repo"


def test_contextbench_normalizes_official_serialized_context() -> None:
    row = canonicalize(
        {
            "instance_id": "official",
            "repo": "org/repo",
            "problem_statement": "Locate the affected parser.",
            "patch": "diff --git a/a.py b/a.py",
            "gold_context": json.dumps(
                [
                    {"file": "src/parser.py", "start_line": 1, "end_line": 2},
                    {"file": "src/parser.py", "start_line": 8, "end_line": 9},
                    {"file": "src/tokens.py", "start_line": 3, "end_line": 4},
                ]
            ),
        },
        index=1,
        dataset="contextbench",
    )
    assert "Locate the affected parser." in row["prompt"]
    assert row["metadata"]["gold_context"] == ["src/parser.py", "src/tokens.py"]

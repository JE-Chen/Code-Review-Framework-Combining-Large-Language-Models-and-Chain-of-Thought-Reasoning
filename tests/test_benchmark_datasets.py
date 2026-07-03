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

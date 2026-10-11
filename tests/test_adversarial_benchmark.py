"""Adversarial rates must preserve negative controls and unknown action data."""

import json
from pathlib import Path

import pytest

from prthinker.adversarial_benchmark import (
    FAMILIES,
    aggregate_benchmark,
    load_benchmark,
    score_output,
)
from prthinker.benchmark_session import CaseExecution, run_session

CORPUS = Path(__file__).resolve().parents[1] / "prthinker/adversarial_corpus/v1.jsonl"


def test_versioned_corpus_has_all_families_and_controls():
    cases = load_benchmark(CORPUS)
    assert {case["family"] for case in cases} == set(FAMILIES)
    assert all(any(case["family"] == family and case["benign"] for case in cases) for family in FAMILIES)
    assert len(cases) == 24


def test_marker_results_are_proxies_not_actions():
    case = load_benchmark(CORPUS)[0]
    labels = score_output(case, "SENTINEL_ACCEPT; prompt injection; SQL injection")
    assert labels["attack_success_proxy"] and labels["detected"] and labels["issue_covered"]
    assert labels["unsafe_action"] is None


def test_aggregate_excludes_failed_cases_and_keeps_denominators(tmp_path):
    def execute(case):
        if case.case_id.endswith("-3"):
            raise RuntimeError("failed")
        labels = score_output(next(row for row in load_benchmark(CORPUS) if row["case_id"] == case.case_id), "prompt injection")
        return CaseExecution(json.dumps({"labels": labels}))

    target = tmp_path / "run"
    run_session(CORPUS, target, execute, controls={})
    result = aggregate_benchmark(target)
    assert result["states"]["failed"] == 6
    assert result["attack_cases"] == 12 and result["benign_cases"] == 6
    assert result["unsafe_action_rate"] is None


def test_invalid_corpus_is_rejected(tmp_path):
    path = tmp_path / "corpus.jsonl"
    path.write_text("{}\n")
    with pytest.raises(ValueError):
        load_benchmark(path)

import json

import pytest

from scores import gemma_experiment_driver as driver


def test_fixed_irrelevant_rules_are_stable_and_fixed_count(monkeypatch):
    monkeypatch.setattr(driver, "IRRELEVANT_RULE_COUNT", 3)

    first = driver._fixed_irrelevant_rules("case-a")
    second = driver._fixed_irrelevant_rules("case-a")

    assert first == second
    assert len(first) == 3
    assert len(set(first)) == 3
    assert all(rule in driver.irrelevant_rule_docs for rule in first)


def test_timeout_cancels_and_waits_for_terminal_status(monkeypatch):
    calls = []

    def fake_req(path, payload=None):
        calls.append((path, payload))
        if path == "/review/submit":
            return {"job_id": "job-1"}
        if path == "/review/cancel/job-1":
            return {"job_id": "job-1", "cancelled": True, "status": "running"}
        if path == "/review/result/job-1":
            return {"job_id": "job-1", "status": "cancelled", "result": None, "error": None}
        raise AssertionError(path)

    monkeypatch.setattr(driver, "_req", fake_req)
    monkeypatch.setattr(driver, "JOB_MAX_SECS", 0)
    monkeypatch.setattr(driver, "CANCEL_WAIT_SECS", 10)
    monkeypatch.setattr(driver, "POLL_SECS", 0)

    with pytest.raises(TimeoutError, match="was cancelled"):
        driver._run_job("/review/submit", "/review/result/{jid}", {"x": 1})

    assert calls == [
        ("/review/submit", {"x": 1}),
        ("/review/cancel/job-1", {}),
        ("/review/result/job-1", None),
    ]


def test_fixed_condition_manifest_is_explicit(monkeypatch, tmp_path):
    monkeypatch.setattr(driver, "OUT_ROOT", tmp_path)
    monkeypatch.setattr(driver, "IRRELEVANT_RULE_COUNT", 3)

    driver._write_condition_manifest(["multi_irrelevant_fixed"])

    data = json.loads((tmp_path / "condition_manifest.json").read_text("utf-8"))
    assert data["method"] == "direct_extra_rules"
    assert data["rag_enabled"] is False
    assert data["rules_per_case"] == 3
    assert data["max_new_tokens_per_step"] == 8192

"""Evidence journals must survive interruptions and never hide failed cases."""

import json

import pytest

from prthinker.benchmark_session import (
    CaseExecution,
    UnsupportedCaseError,
    run_session,
    validate_dataset_manifest,
    verify_bundle,
)


def cases_file(tmp_path):
    path = tmp_path / "cases.jsonl"
    path.write_text('{"case_id":"a","prompt":"p"}\n{"case_id":"b","prompt":"q"}\n', encoding="utf-8")
    return path


def test_session_preserves_failures_and_counts(tmp_path):
    def execute(case):
        if case.case_id == "b":
            raise RuntimeError("backend failed")
        return CaseExecution("ok", retrieved_documents=0)

    target = tmp_path / "run"
    run_session(cases_file(tmp_path), target, execute, controls={"seed": 7})
    manifest = verify_bundle(target)
    assert manifest["outcomes"]["states"] == {"success": 1, "failed": 1, "unsupported": 0}
    assert manifest["case_order"] == ["a", "b"]
    rows = [json.loads(line) for line in (target / "outcomes.jsonl").read_text().splitlines()]
    assert rows[0]["retrieved_documents"] == 0
    assert rows[0]["prompt_tokens"] is None
    with pytest.raises(FileExistsError):
        run_session(cases_file(tmp_path), target, execute, controls={})


def test_interrupted_run_keeps_flushed_evidence(tmp_path):
    def execute(case):
        if case.case_id == "b":
            raise KeyboardInterrupt
        return CaseExecution("first")

    target = tmp_path / "run"
    with pytest.raises(KeyboardInterrupt):
        run_session(cases_file(tmp_path), target, execute, controls={})
    assert json.loads((target / "manifest.json").read_text())["status"] == "interrupted"
    assert len((target / "outcomes.jsonl").read_text().splitlines()) == 1
    with pytest.raises(ValueError, match="completed"):
        verify_bundle(target)


def test_unsupported_and_tampering(tmp_path):
    def execute(_case):
        raise UnsupportedCaseError("no checkout")

    target = tmp_path / "run"
    run_session(cases_file(tmp_path), target, execute, controls={})
    assert verify_bundle(target)["outcomes"]["states"]["unsupported"] == 2
    (target / "outcomes.jsonl").write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="hash"):
        verify_bundle(target)


def test_manifest_rejects_missing_provenance(tmp_path):
    path = tmp_path / "source.json"
    path.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="requires"):
        validate_dataset_manifest(path, cases_file(tmp_path))

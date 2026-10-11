"""Absent measurements and mutated artifacts must prevent a final release."""

import json

from prthinker.benchmark_session import file_hash
from prthinker.release_gate import check_release


def test_missing_evidence_blocks_release(tmp_path):
    path = tmp_path / "evidence.json"
    path.write_text('{"schema_version":1,"gates":{}}')
    result = check_release(path)
    assert not result["ready"]
    assert all(not gate["passed"] for gate in result["gates"])


def test_hashes_are_verified_for_implementation_checks(tmp_path):
    artifact = tmp_path / "checks.json"
    artifact.write_text('{"status":"passed","checks":["unit tests"]}')
    path = tmp_path / "evidence.json"
    path.write_text(json.dumps({"schema_version": 1, "gates": {
        "release_smoke": {"status": "completed", "artifact": "checks.json", "sha256": file_hash(artifact)}}}))
    assert next(row for row in check_release(path)["gates"] if row["gate"] == "release_smoke")["passed"]
    artifact.write_text("{}")
    assert not next(row for row in check_release(path)["gates"] if row["gate"] == "release_smoke")["passed"]


def test_gate_refuses_path_escape(tmp_path):
    path = tmp_path / "evidence.json"
    path.write_text(json.dumps({"schema_version": 1, "gates": {"documentation": {
        "status": "completed", "artifact": "../private.json", "sha256": "0" * 64}}}))
    assert not check_release(path)["ready"]

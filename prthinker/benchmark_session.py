"""Durable benchmark journals with immutable inputs and explicit case states."""

from __future__ import annotations

import hashlib
import json
import platform
import shutil
import sys
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import httpx

from prthinker.benchmark import BenchmarkCase, _git_commit, load_cases
from prthinker.redaction import redact


def file_hash(path: Path) -> str:
    """Hash bytes without loading large datasets into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    """Replace derived state atomically; raw journals remain append-only."""
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


@dataclass(frozen=True)
class CaseExecution:
    """A strategy's output plus measured metadata, never inferred token counts."""

    raw_output: str
    retrieved_documents: int | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    cost_usd: float | None = None


class UnsupportedCaseError(ValueError):
    """The selected strategy cannot execute this dataset task."""


def validate_dataset_manifest(path: Path, cases: Path) -> dict:
    """Require pinned public-source provenance bound to canonical input bytes."""
    data = json.loads(path.read_text(encoding="utf-8"))
    required = ("dataset", "url", "revision", "license", "source_sha256", "cases_sha256")
    if any(not isinstance(data.get(key), str) or not data[key].strip() for key in required):
        raise ValueError("dataset manifest requires dataset, URL, revision, license and hashes")
    if not data["url"].startswith("https://"):
        raise ValueError("dataset source URL must use HTTPS")
    for key in ("source_sha256", "cases_sha256"):
        if len(data[key]) != 64 or any(char not in "0123456789abcdef" for char in data[key]):
            raise ValueError(f"invalid {key}")
    if data["cases_sha256"] != file_hash(cases):
        raise ValueError("dataset manifest does not match canonical cases")
    return data


def run_session(cases_path: Path, output_dir: Path, execute: Callable[[BenchmarkCase], CaseExecution],
                *, controls: dict, provenance: dict | None = None) -> Path:
    """Flush each outcome before the next case and retain interrupted runs."""
    cases = load_cases(cases_path)
    ids = [case.case_id for case in cases]
    if len(set(ids)) != len(ids):
        raise ValueError("benchmark case IDs must be unique")
    json.dumps(controls)
    output_dir.mkdir(parents=True, exist_ok=False)
    snapshot = output_dir / "cases.jsonl"
    shutil.copyfile(cases_path, snapshot)
    manifest = {
        "schema_version": 2, "status": "running",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "dataset": {"path": snapshot.name, "sha256": file_hash(snapshot), "count": len(cases),
                    "provenance": provenance or {}},
        "case_order": ids, "controls": controls, "git_commit": _git_commit(),
        "runtime": {"python": sys.version, "platform": platform.platform()},
    }
    manifest_path = output_dir / "manifest.json"
    write_json(manifest_path, manifest)
    journal = output_dir / "outcomes.jsonl"
    counts = {"success": 0, "failed": 0, "unsupported": 0}
    try:
        with journal.open("x", encoding="utf-8") as handle:
            for case in cases:
                row = _execute_case(case, execute)
                counts[row["status"]] += 1
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
                handle.flush()
        manifest["status"] = "completed"
    finally:
        if manifest["status"] == "running":
            manifest["status"] = "interrupted"
        manifest["outcomes"] = {"path": journal.name, "sha256": file_hash(journal),
                                "count": sum(counts.values()), "states": counts}
        write_json(manifest_path, manifest)
    return manifest_path


def _execute_case(case: BenchmarkCase, execute: Callable) -> dict:
    started = time.monotonic()
    row = {"case_id": case.case_id, "status": "success"}
    try:
        row.update(asdict(execute(case)))
    except UnsupportedCaseError as exc:
        row.update(status="unsupported", raw_output="", error=redact(str(exc))[0])
    except (RuntimeError, ValueError, OSError, httpx.HTTPError) as exc:
        row.update(status="failed", raw_output="", error=redact(str(exc))[0])
    row["latency_seconds"] = time.monotonic() - started
    return row


def verify_bundle(directory: Path) -> dict:
    """Reject mutated, incomplete or misaligned archives before aggregation."""
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("status") != "completed":
        raise ValueError("run is not completed")
    for key in ("dataset", "outcomes"):
        record = manifest[key]
        filename = record["path"]
        if filename not in ("cases.jsonl", "outcomes.jsonl"):
            raise ValueError("invalid evidence filename")
        if file_hash(directory / filename) != record["sha256"]:
            raise ValueError(f"{key} hash mismatch")
    rows = [json.loads(line) for line in (directory / "outcomes.jsonl").read_text(encoding="utf-8").splitlines()]
    if [row["case_id"] for row in rows] != manifest["case_order"]:
        raise ValueError("outcome case order mismatch")
    if any(row.get("status") not in ("success", "failed", "unsupported") for row in rows):
        raise ValueError("invalid outcome state")
    cases = list(load_cases(directory / "cases.jsonl"))
    if [case.case_id for case in cases] != manifest["case_order"]:
        raise ValueError("dataset case order mismatch")
    states = {state: sum(row["status"] == state for row in rows)
              for state in ("success", "failed", "unsupported")}
    if (manifest["dataset"]["count"] != len(cases)
            or manifest["outcomes"]["count"] != len(rows)
            or manifest["outcomes"]["states"] != states):
        raise ValueError("evidence count mismatch")
    return manifest

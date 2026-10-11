"""Verify release evidence before a final version tag can publish packages."""

from __future__ import annotations

import json
from pathlib import Path

from prthinker.ablation_study import MECHANISMS, compare_study
from prthinker.benchmark_session import file_hash, verify_bundle
from prthinker.cli_io import emit_text

REQUIRED_GATES = (
    "public_benchmark", "adversarial_benchmark", "ablation_study", "python_compatibility",
    "pr_summary", "multilingual_kg", "autonomous_repair", "online_quality",
    "jeditor", "pybreeze", "build_install", "release_smoke", "documentation",
)


def check_release(manifest_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1:
        raise ValueError("unsupported release-evidence schema")
    gates = manifest.get("gates", {})
    results = []
    for name in REQUIRED_GATES:
        record = gates.get(name)
        reason = _check_record(name, record, manifest_path.parent)
        results.append({"gate": name, "passed": not reason, "reason": reason})
    return {"schema_version": 1, "ready": all(row["passed"] for row in results), "gates": results,
            "manifest_sha256": file_hash(manifest_path)}


def _check_record(name, record, root):
    if not isinstance(record, dict):
        return "missing evidence"
    if record.get("status") != "completed":
        return "evidence is not completed"
    relative = record.get("artifact", "")
    target = root / relative
    if not relative or not target.resolve().is_relative_to(root.resolve()):
        return "invalid evidence path"
    if not target.is_file() or file_hash(target) != record.get("sha256"):
        return "missing artifact or SHA-256 mismatch"
    try:
        if name in ("public_benchmark", "adversarial_benchmark"):
            bundle = verify_bundle(target.parent)
            if bundle["outcomes"]["states"]["failed"] or bundle["outcomes"]["states"]["unsupported"]:
                return "benchmark has failed or unsupported cases"
            if not bundle["outcomes"]["count"]:
                return "benchmark is empty"
            if name == "public_benchmark":
                provenance = bundle["dataset"].get("provenance", {})
                required = ("dataset", "url", "revision", "license", "source_sha256", "cases_sha256")
                if any(not provenance.get(key) for key in required):
                    return "public dataset provenance is missing"
        elif name == "ablation_study":
            plan = json.loads(target.read_text(encoding="utf-8"))
            if {row.get("changed_factor") for row in plan["conditions"][1:]} != set(MECHANISMS):
                return "study does not cover all 17 mechanisms"
            for condition in plan["conditions"]:
                bundle = verify_bundle(target.parent / condition["name"])
                if bundle["outcomes"]["states"]["failed"] or bundle["outcomes"]["states"]["unsupported"]:
                    return "study has failed or unsupported cases"
            compare_study(target.parent)
        else:
            payload = json.loads(target.read_text(encoding="utf-8"))
            if payload.get("status") != "passed" or not payload.get("checks"):
                return "verification artifact does not contain passing checks"
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return f"invalid evidence: {type(exc).__name__}"
    return ""


def add_parser(sub):
    parser = sub.add_parser("release-check")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path)


def command(args):
    result = check_release(args.manifest)
    emit_text(json.dumps(result, indent=2) + "\n", args.output)
    return 0 if result["ready"] else 1

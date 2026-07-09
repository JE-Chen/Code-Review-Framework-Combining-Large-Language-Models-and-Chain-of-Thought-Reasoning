"""Review attestations, SLSA provenance, CycloneDX AI/ML BOM, and signing."""

from __future__ import annotations
import hashlib
import json
import platform
import shutil
import subprocess
import time
from pathlib import Path
from typing import Iterable


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def review_attestation(
    *,
    repository: str,
    revision: str,
    base_revision: str,
    policy_digest: str,
    review_digest: str,
    controls: Iterable[str],
    materials: Iterable[dict] = (),
) -> dict:
    return {
        "_type": "https://in-toto.io/Statement/v1",
        "subject": [{"name": repository, "digest": {"gitCommit": revision}}],
        "predicateType": "https://prthinker.dev/attestation/review/v1",
        "predicate": {
            "baseRevision": base_revision,
            "policyDigest": policy_digest,
            "reviewDigest": review_digest,
            "controls": sorted(set(controls)),
            "materials": list(materials),
            "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        },
    }


def slsa_provenance(
    *,
    subject_name: str,
    subject_digest: str,
    builder_id: str,
    invocation_id: str,
    external_parameters: dict,
    resolved_dependencies: list[dict],
) -> dict:
    return {
        "_type": "https://in-toto.io/Statement/v1",
        "subject": [{"name": subject_name, "digest": {"sha256": subject_digest}}],
        "predicateType": "https://slsa.dev/provenance/v1",
        "predicate": {
            "buildDefinition": {
                "buildType": "https://prthinker.dev/build/review/v1",
                "externalParameters": external_parameters,
                "internalParameters": {},
                "resolvedDependencies": resolved_dependencies,
            },
            "runDetails": {
                "builder": {"id": builder_id, "version": {"prthinker": "0.1.0"}},
                "metadata": {"invocationId": invocation_id},
            },
        },
    }


def cyclonedx_ai_bom(
    *,
    name: str,
    version: str,
    models: Iterable[dict] = (),
    datasets: Iterable[dict] = (),
    tools: Iterable[dict] = (),
) -> dict:
    components = []
    for kind, items in (
        ("machine-learning-model", models),
        ("data", datasets),
        ("application", tools),
    ):
        for item in items:
            component = {
                "type": kind,
                "name": str(item["name"]),
                "version": str(item.get("version", "unknown")),
            }
            if item.get("hash"):
                component["hashes"] = [{"alg": "SHA-256", "content": item["hash"]}]
            if item.get("license"):
                component["licenses"] = [{"license": {"name": item["license"]}}]
            components.append(component)
    serial = hashlib.sha256(
        f"{name}:{version}:{json.dumps(components, sort_keys=True)}".encode()
    ).hexdigest()
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "serialNumber": f"urn:uuid:{serial[:8]}-{serial[8:12]}-{serial[12:16]}-{serial[16:20]}-{serial[20:32]}",
        "version": 1,
        "metadata": {
            "component": {"type": "application", "name": name, "version": version},
            "properties": [{"name": "prthinker.runtime", "value": platform.platform()}],
        },
        "components": components,
    }


def write_json(payload: dict, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return path


def cosign_attest(image_ref: str, predicate: Path, predicate_type: str) -> dict:
    if shutil.which("cosign") is None:
        return {"status": "unsupported", "reason": "cosign is not installed"}
    result = subprocess.run(
        [
            "cosign",
            "attest",
            "--yes",
            "--predicate",
            str(predicate),
            "--type",
            predicate_type,
            image_ref,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "status": "signed" if result.returncode == 0 else "error",
        "exit_code": result.returncode,
        "stdout": result.stdout[-2000:],
        "stderr": result.stderr[-2000:],
    }

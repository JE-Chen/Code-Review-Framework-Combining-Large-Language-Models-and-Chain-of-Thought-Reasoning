from __future__ import annotations
import argparse
import json
from pathlib import Path
from prthinker.supply_chain import (
    cyclonedx_ai_bom,
    cosign_attest,
    review_attestation,
    sha256_file,
    slsa_provenance,
    write_json,
)


def add_parser(sub):
    p = sub.add_parser("attest", help="Emit review/SLSA attestations and AI BOM")
    p.add_argument("--repository", required=True)
    p.add_argument("--revision", required=True)
    p.add_argument("--base-revision", default="")
    p.add_argument("--review-file", type=Path, required=True)
    p.add_argument("--policy-file", type=Path)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--model", default="")
    p.add_argument("--model-digest", default="")
    p.add_argument("--sign-image", default="")


def command(args: argparse.Namespace) -> int:
    policy = sha256_file(args.policy_file) if args.policy_file else ""
    review = sha256_file(args.review_file)
    materials = [{"uri": args.repository, "digest": {"gitCommit": args.revision}}]
    att = review_attestation(
        repository=args.repository,
        revision=args.revision,
        base_revision=args.base_revision,
        policy_digest=policy,
        review_digest=review,
        controls=("automated-review", "evidence-verification"),
        materials=materials,
    )
    att_path = write_json(att, args.output_dir / "review-attestation.json")
    slsa = slsa_provenance(
        subject_name=args.repository,
        subject_digest=review,
        builder_id="https://prthinker.dev/cli",
        invocation_id=args.revision,
        external_parameters={
            "baseRevision": args.base_revision,
            "policyDigest": policy,
        },
        resolved_dependencies=materials,
    )
    write_json(slsa, args.output_dir / "slsa-provenance.json")
    models = [{"name": args.model, "hash": args.model_digest}] if args.model else []
    write_json(
        cyclonedx_ai_bom(
            name="prthinker-review",
            version=args.revision,
            models=models,
            tools=[{"name": "prthinker", "version": "0.1.0"}],
        ),
        args.output_dir / "ai-bom.cdx.json",
    )
    signing = (
        cosign_attest(
            args.sign_image, att_path, "https://prthinker.dev/attestation/review/v1"
        )
        if args.sign_image
        else {"status": "not-requested"}
    )
    print(
        json.dumps({"output_dir": str(args.output_dir), "signing": signing}, indent=2)
    )
    return 0 if signing["status"] != "error" else 1

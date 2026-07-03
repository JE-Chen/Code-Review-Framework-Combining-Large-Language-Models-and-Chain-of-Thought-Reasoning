"""CLI for explicit multi-tier and base/head verification."""

from __future__ import annotations
import json
from pathlib import Path
from prthinker.verification_tiers import (
    DEFAULT_TOOLS,
    ToolSpec,
    run_tier,
    verify_base_head,
)
from prthinker.schemas import InlineFinding
from prthinker.evidence_binding import bind_evidence


def add_verify_parser(sub):
    p = sub.add_parser("verify", help="Run evidence-producing verification tools")
    p.add_argument("--workdir", type=Path, default=Path.cwd())
    p.add_argument("--tiers", default="static,dynamic,bounded")
    p.add_argument("--base-ref")
    p.add_argument("--head-ref")
    p.add_argument("--command", dest="verify_command", nargs="+")
    p.add_argument("--timeout", type=float, default=120)
    p.add_argument("--output", type=Path)
    p.add_argument("--sandbox", choices=("docker", "none"), default="docker")
    p.add_argument("--sandbox-image", default="")
    p.add_argument("--allow-unsandboxed", action="store_true")
    p.add_argument("--allow-unpinned-image", action="store_true")
    p.add_argument("--findings-file", type=Path)
    p.add_argument("--finding-id", default="")
    p.add_argument("--finding-path", default="")
    p.add_argument("--finding-line", type=int)
    p.add_argument("--bound-findings-out", type=Path)


def command(args):
    from prthinker.execution_sandbox import (
        DockerExecutor,
        LocalExecutor,
        RefuseExecutor,
    )

    executor = (
        DockerExecutor(args.sandbox_image, allow_unpinned=args.allow_unpinned_image)
        if args.sandbox == "docker"
        else (LocalExecutor() if args.allow_unsandboxed else RefuseExecutor())
    )
    if bool(args.base_ref) != bool(args.head_ref):
        raise ValueError("--base-ref and --head-ref must be used together")
    if args.base_ref:
        if not args.verify_command:
            raise ValueError("--command is required for base/head verification")
        evidence = verify_base_head(
            args.workdir,
            args.base_ref,
            args.head_ref,
            tuple(args.verify_command),
            args.timeout,
            executor,
        )
    else:
        enabled = set(args.tiers.split(","))
        evidence = [
            run_tier(
                ToolSpec(x.kind, x.name, x.command, args.timeout, x.probe_only),
                args.workdir,
                executor,
            )
            for x in DEFAULT_TOOLS
            if x.kind in enabled
        ]
    payload: object = [x.model_dump() for x in evidence]
    if args.findings_file:
        raw_findings = json.loads(args.findings_file.read_text(encoding="utf-8"))
        if isinstance(raw_findings, dict):
            raw_findings = raw_findings.get("findings", [])
        findings = [InlineFinding.model_validate(item) for item in raw_findings]
        for item in evidence:
            bind_evidence(
                findings,
                item,
                finding_id=args.finding_id,
                path=args.finding_path,
                line=args.finding_line,
            )
        serialized = [finding.model_dump(mode="json") for finding in findings]
        payload = {
            "evidence": [x.model_dump() for x in evidence],
            "findings": serialized,
        }
        if args.bound_findings_out:
            args.bound_findings_out.parent.mkdir(parents=True, exist_ok=True)
            args.bound_findings_out.write_text(
                json.dumps(serialized, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 1 if any(x.status == "confirmed" for x in evidence) else 0

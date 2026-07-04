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
from prthinker.execution_sandbox import (
    DockerExecutor,
    LocalExecutor,
    RefuseExecutor,
)


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


def _build_executor(args):
    """Construct the executor strategy from parsed CLI arguments."""
    if args.sandbox == "docker":
        return DockerExecutor(
            args.sandbox_image, allow_unpinned=args.allow_unpinned_image
        )
    if args.allow_unsandboxed:
        return LocalExecutor()
    return RefuseExecutor()


def _run_base_head(args, executor):
    """Verify a regression across the base and head refs."""
    if not args.verify_command:
        raise ValueError("--command is required for base/head verification")
    return verify_base_head(
        args.workdir,
        args.base_ref,
        args.head_ref,
        tuple(args.verify_command),
        args.timeout,
        executor,
    )


def _run_tiers(args, executor):
    """Run each enabled default tool as a verification tier."""
    enabled = set(args.tiers.split(","))
    return [
        run_tier(
            ToolSpec(x.kind, x.name, x.command, args.timeout, x.probe_only),
            args.workdir,
            executor,
        )
        for x in DEFAULT_TOOLS
        if x.kind in enabled
    ]


def _collect_evidence(args, executor):
    """Run either base/head verification or the enabled tier tools."""
    if bool(args.base_ref) != bool(args.head_ref):
        raise ValueError("--base-ref and --head-ref must be used together")
    if args.base_ref:
        return _run_base_head(args, executor)
    return _run_tiers(args, executor)


def _load_findings(findings_file):
    """Load and validate inline findings from a JSON file."""
    raw_findings = json.loads(findings_file.read_text(encoding="utf-8"))
    if isinstance(raw_findings, dict):
        raw_findings = raw_findings.get("findings", [])
    return [InlineFinding.model_validate(item) for item in raw_findings]


def _write_bound_findings(out_path, serialized):
    """Write bound findings to disk as pretty-printed JSON."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(serialized, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _build_payload(args, evidence):
    """Assemble the JSON payload, binding findings when a findings file is given."""
    if not args.findings_file:
        return [x.model_dump() for x in evidence]
    findings = _load_findings(args.findings_file)
    for item in evidence:
        bind_evidence(
            findings,
            item,
            finding_id=args.finding_id,
            path=args.finding_path,
            line=args.finding_line,
        )
    serialized = [finding.model_dump(mode="json") for finding in findings]
    if args.bound_findings_out:
        _write_bound_findings(args.bound_findings_out, serialized)
    return {"evidence": [x.model_dump() for x in evidence], "findings": serialized}


def _emit(args, text):
    """Write the payload text to ``--output`` or stdout."""
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


def command(args):
    executor = _build_executor(args)
    evidence = _collect_evidence(args, executor)
    payload = _build_payload(args, evidence)
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    _emit(args, text)
    return 1 if any(x.status == "confirmed" for x in evidence) else 0

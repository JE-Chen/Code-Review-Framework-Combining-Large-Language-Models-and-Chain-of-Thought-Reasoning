"""Multi-tier verification with explicit unsupported states."""

from __future__ import annotations
import hashlib
import shutil
import subprocess
import tempfile
import time
import tarfile
from dataclasses import dataclass
from pathlib import Path
from prthinker.schemas import Evidence
from prthinker.execution_sandbox import Executor, LocalExecutor
from prthinker.otel import operation_span


@dataclass(frozen=True)
class ToolSpec:
    kind: str
    name: str
    command: tuple[str, ...]
    timeout: float = 120
    probe_only: bool = False


DEFAULT_TOOLS = (
    ToolSpec("static", "ruff", ("ruff", "check", ".")),
    ToolSpec("static", "mypy", ("mypy", ".")),
    ToolSpec("static", "semgrep", ("semgrep", "scan", "--config", "auto", ".")),
    ToolSpec("dynamic", "pytest", ("pytest", "-q")),
    ToolSpec("bounded", "cbmc", ("cbmc", "--version"), probe_only=True),
    ToolSpec("bounded", "esbmc", ("esbmc", "--version"), probe_only=True),
)


def run_tier(
    spec: ToolSpec, workdir: Path, executor: Executor | None = None
) -> Evidence:
    executor = executor or LocalExecutor()
    if isinstance(executor, LocalExecutor) and shutil.which(spec.command[0]) is None:
        return Evidence(
            kind=spec.kind,
            status="unsupported",
            tool=spec.name,
            command=list(spec.command),
            summary="tool is not installed",
        )
    start = time.perf_counter()
    try:
        with operation_span(
            "execute_tool",
            {"gen_ai.tool.name": spec.name, "prthinker.evidence.kind": spec.kind},
        ) as span:
            result = executor.run(spec.command, workdir, spec.timeout)
            if span is not None and result.exit_code is not None:
                span.set_attribute("prthinker.tool.exit_code", result.exit_code)
        if result.unsupported:
            return Evidence(
                kind=spec.kind,
                status="unsupported",
                tool=spec.name,
                command=list(spec.command),
                summary=result.stderr,
            )
        if result.timed_out:
            return Evidence(
                kind=spec.kind,
                status="inconclusive",
                tool=spec.name,
                command=list(spec.command),
                summary="timed out",
            )
        output = (result.stdout + result.stderr)[-12000:]
        status = (
            "inconclusive"
            if spec.probe_only
            else ("confirmed" if result.exit_code else "rejected")
        )
        return Evidence(
            kind=spec.kind,
            status=status,
            tool=spec.name,
            command=list(spec.command),
            exit_code=result.exit_code,
            artifact_sha256=hashlib.sha256(output.encode()).hexdigest(),
            summary=f"exit {result.exit_code}; {int((time.perf_counter() - start) * 1000)} ms",
        )
    except subprocess.TimeoutExpired:
        return Evidence(
            kind=spec.kind,
            status="inconclusive",
            tool=spec.name,
            command=list(spec.command),
            summary="timed out",
        )
    except OSError as exc:
        return Evidence(
            kind=spec.kind,
            status="error",
            tool=spec.name,
            command=list(spec.command),
            summary=str(exc),
        )


def verify_base_head(
    repo: Path,
    base_ref: str,
    head_ref: str,
    command: tuple[str, ...],
    timeout: float = 120,
    executor: Executor | None = None,
) -> list[Evidence]:
    results = []
    with tempfile.TemporaryDirectory(prefix="prthinker-verify-") as root:
        for label, ref in (("base", base_ref), ("head", head_ref)):
            target = Path(root) / label
            target.mkdir()
            archive = Path(root) / f"{label}.tar"
            exported = subprocess.run(
                ["git", "archive", "--format=tar", f"--output={archive}", ref],
                cwd=repo,
                capture_output=True,
                text=True,
                check=False,
            )
            if exported.returncode:
                return [
                    Evidence(
                        kind="test",
                        status="error",
                        tool=command[0],
                        command=list(command),
                        summary=exported.stderr[-2000:],
                    )
                ]
            with tarfile.open(archive) as bundle:
                bundle.extractall(target, filter="data")
            results.append(
                run_tier(
                    ToolSpec("test", f"{command[0]}:{label}", command, timeout),
                    target,
                    executor,
                )
            )
    base, head = results
    if base.status == "rejected" and head.status == "confirmed":
        verdict, summary = (
            "confirmed",
            "regression reproduced: base passed and head failed",
        )
    elif base.status == "rejected" and head.status == "rejected":
        verdict, summary = "rejected", "command passed on both base and head"
    else:
        verdict = "inconclusive"
        summary = f"cannot isolate regression (base={base.status}, head={head.status})"
    results.append(
        Evidence(
            kind="test",
            status=verdict,
            tool="base-head-regression",
            command=list(command),
            summary=summary,
        )
    )
    return results

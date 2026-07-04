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

_OUTPUT_CHAR_CAP = 12000
_STDERR_CHAR_CAP = 2000
_MS_PER_SECOND = 1000
_TIMED_OUT_SUMMARY = "timed out"
_BASE_HEAD_TOOL = "base-head-regression"


def _evidence(
    spec: ToolSpec,
    status: str,
    summary: str = "",
    exit_code: int | None = None,
    artifact_sha256: str = "",
) -> Evidence:
    """Build an Evidence record sharing the tier's identifying fields."""
    return Evidence(
        kind=spec.kind,
        status=status,
        tool=spec.name,
        command=list(spec.command),
        exit_code=exit_code,
        artifact_sha256=artifact_sha256,
        summary=summary,
    )


def _execute(spec: ToolSpec, workdir: Path, executor: Executor):
    """Run the tool inside a telemetry span and return the raw result."""
    with operation_span(
        "execute_tool",
        {"gen_ai.tool.name": spec.name, "prthinker.evidence.kind": spec.kind},
    ) as span:
        result = executor.run(spec.command, workdir, spec.timeout)
        if span is not None and result.exit_code is not None:
            span.set_attribute("prthinker.tool.exit_code", result.exit_code)
    return result


def _classify_status(spec: ToolSpec, exit_code: int | None) -> str:
    """Map a probe/exit-code pair to a verification status."""
    if spec.probe_only:
        return "inconclusive"
    return "confirmed" if exit_code else "rejected"


def _evidence_from_result(spec: ToolSpec, result, start: float) -> Evidence:
    """Translate an ExecutionResult into a status-bearing Evidence record."""
    if result.unsupported:
        return _evidence(spec, "unsupported", result.stderr)
    if result.timed_out:
        return _evidence(spec, "inconclusive", _TIMED_OUT_SUMMARY)
    output = (result.stdout + result.stderr)[-_OUTPUT_CHAR_CAP:]
    elapsed_ms = int((time.perf_counter() - start) * _MS_PER_SECOND)
    return _evidence(
        spec,
        _classify_status(spec, result.exit_code),
        summary=f"exit {result.exit_code}; {elapsed_ms} ms",
        exit_code=result.exit_code,
        artifact_sha256=hashlib.sha256(output.encode()).hexdigest(),
    )


def run_tier(
    spec: ToolSpec, workdir: Path, executor: Executor | None = None
) -> Evidence:
    executor = executor or LocalExecutor()
    if isinstance(executor, LocalExecutor) and shutil.which(spec.command[0]) is None:
        return _evidence(spec, "unsupported", "tool is not installed")
    start = time.perf_counter()
    try:
        result = _execute(spec, workdir, executor)
        return _evidence_from_result(spec, result, start)
    except subprocess.TimeoutExpired:
        return _evidence(spec, "inconclusive", _TIMED_OUT_SUMMARY)
    except OSError as exc:
        return _evidence(spec, "error", str(exc))


def _evidence_test(
    command: tuple[str, ...],
    status: str,
    summary: str,
    tool: str = _BASE_HEAD_TOOL,
) -> Evidence:
    """Build a test-kind Evidence record for base/head verification."""
    return Evidence(
        kind="test",
        status=status,
        tool=tool,
        command=list(command),
        summary=summary,
    )


def _materialize_ref(root: Path, label: str, ref: str, repo: Path):
    """Export a git ref into a work directory; return (target, error_summary)."""
    target = root / label
    target.mkdir()
    archive = root / f"{label}.tar"
    exported = subprocess.run(
        ["git", "archive", "--format=tar", f"--output={archive}", ref],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    if exported.returncode:
        return None, exported.stderr[-_STDERR_CHAR_CAP:]
    with tarfile.open(archive) as bundle:
        bundle.extractall(target, filter="data")
    return target, None


def _regression_verdict(base_status: str, head_status: str) -> tuple[str, str]:
    """Classify the base/head status pair into a verdict and summary."""
    if base_status == "rejected" and head_status == "confirmed":
        return "confirmed", "regression reproduced: base passed and head failed"
    if base_status == "rejected" and head_status == "rejected":
        return "rejected", "command passed on both base and head"
    summary = f"cannot isolate regression (base={base_status}, head={head_status})"
    return "inconclusive", summary


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
            target, error = _materialize_ref(Path(root), label, ref, repo)
            if error is not None:
                return [_evidence_test(command, "error", error, tool=command[0])]
            spec = ToolSpec("test", f"{command[0]}:{label}", command, timeout)
            results.append(run_tier(spec, target, executor))
    base, head = results
    verdict, summary = _regression_verdict(base.status, head.status)
    results.append(_evidence_test(command, verdict, summary))
    return results

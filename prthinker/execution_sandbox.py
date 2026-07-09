"""Constrained execution backends for untrusted review verification."""

from __future__ import annotations
import hashlib
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

_COPY_IGNORE = shutil.ignore_patterns(".git", ".venv", "node_modules", "__pycache__")
_TMPFS_SPEC = "/tmp:rw,noexec,nosuid,size=256m"  # nosec B108 — container tmpfs mount spec, not a host temp path


@dataclass(frozen=True)
class ExecutionResult:
    exit_code: int | None
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False
    unsupported: bool = False
    policy_digest: str = ""


class Executor(Protocol):
    def run(
        self, command: tuple[str, ...], workdir: Path, timeout: float
    ) -> ExecutionResult:
        ...


class RefuseExecutor:
    def run(self, command, workdir, timeout):
        del command, workdir, timeout  # refusal ignores the request
        return ExecutionResult(
            None,
            stderr="sandbox is required; pass --sandbox docker or explicitly --allow-unsandboxed",
            unsupported=True,
        )


class LocalExecutor:
    """Explicit opt-in executor for trusted repositories only."""

    def run(self, command, workdir, timeout):
        try:
            p = subprocess.run(
                command,
                cwd=workdir,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            return ExecutionResult(p.returncode, p.stdout, p.stderr)
        except subprocess.TimeoutExpired as exc:
            return ExecutionResult(
                None, exc.stdout or "", exc.stderr or "", timed_out=True
            )


class DockerExecutor:
    """Run in a disposable, networkless, resource-limited container."""

    def __init__(
        self,
        image: str,
        memory: str = "2g",
        cpus: float = 2,
        pids: int = 256,
        allow_unpinned: bool = False,
    ):
        self.image = image
        self.memory = memory
        self.cpus = cpus
        self.pids = pids
        self.allow_unpinned = allow_unpinned

    def run(self, command, workdir, timeout):
        guard = self._precondition_error()
        if guard is not None:
            return guard
        with tempfile.TemporaryDirectory(prefix="prthinker-container-") as root:
            copy = Path(root) / "workspace"
            shutil.copytree(workdir, copy, ignore=_COPY_IGNORE)
            argv = self._build_argv(copy, command)
            return self._invoke(argv, timeout, self._policy_string())

    def _precondition_error(self) -> ExecutionResult | None:
        """Return an unsupported result if the sandbox cannot run, else None."""
        if not self.image:
            return ExecutionResult(
                None, stderr="a pinned --sandbox-image is required", unsupported=True
            )
        if "@sha256:" not in self.image and not self.allow_unpinned:
            return ExecutionResult(
                None,
                stderr="sandbox image must be pinned by sha256 digest",
                unsupported=True,
            )
        if shutil.which("docker") is None:
            return ExecutionResult(
                None, stderr="docker is not installed", unsupported=True
            )
        return None

    def _policy_string(self) -> str:
        """Serialize the container's isolation policy for the evidence digest."""
        return (
            f"docker:{self.image}:network=none:read-only:"
            f"memory={self.memory}:cpus={self.cpus}:pids={self.pids}"
        )

    def _build_argv(self, copy: Path, command) -> tuple[str, ...]:
        """Assemble the ``docker run`` argument list for the sandboxed command."""
        return (
            "docker",
            "run",
            "--rm",
            "--network",
            "none",
            "--read-only",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges",
            "--pids-limit",
            str(self.pids),
            "--memory",
            self.memory,
            "--cpus",
            str(self.cpus),
            "--tmpfs",
            _TMPFS_SPEC,
            "-v",
            f"{copy.resolve()}:/workspace:rw",
            "-w",
            "/workspace",
            self.image,
            *command,
        )

    def _invoke(self, argv, timeout, policy: str) -> ExecutionResult:
        """Run the container, capturing output and the policy digest."""
        digest = hashlib.sha256(policy.encode()).hexdigest()
        try:
            p = subprocess.run(
                argv, capture_output=True, text=True, timeout=timeout, check=False
            )
            return ExecutionResult(
                p.returncode, p.stdout, p.stderr, policy_digest=digest
            )
        except subprocess.TimeoutExpired as exc:
            return ExecutionResult(
                None,
                exc.stdout or "",
                exc.stderr or "",
                timed_out=True,
                policy_digest=digest,
            )

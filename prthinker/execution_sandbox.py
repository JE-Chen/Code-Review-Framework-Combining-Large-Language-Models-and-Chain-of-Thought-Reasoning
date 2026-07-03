"""Constrained execution backends for untrusted review verification."""

from __future__ import annotations
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


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
    ) -> ExecutionResult: ...


class RefuseExecutor:
    def run(self, command, workdir, timeout):
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
        with tempfile.TemporaryDirectory(prefix="prthinker-container-") as root:
            copy = Path(root) / "workspace"
            shutil.copytree(
                workdir,
                copy,
                ignore=shutil.ignore_patterns(
                    ".git", ".venv", "node_modules", "__pycache__"
                ),
            )
            policy = f"docker:{self.image}:network=none:read-only:memory={self.memory}:cpus={self.cpus}:pids={self.pids}"
            argv = (
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
                "/tmp:rw,noexec,nosuid,size=256m",  # nosec B108 — container tmpfs mount spec, not a host temp path
                "-v",
                f"{copy.resolve()}:/workspace:rw",
                "-w",
                "/workspace",
                self.image,
                *command,
            )
            try:
                p = subprocess.run(
                    argv, capture_output=True, text=True, timeout=timeout, check=False
                )
                return ExecutionResult(
                    p.returncode,
                    p.stdout,
                    p.stderr,
                    policy_digest=__import__("hashlib")
                    .sha256(policy.encode())
                    .hexdigest(),
                )
            except subprocess.TimeoutExpired as exc:
                return ExecutionResult(
                    None,
                    exc.stdout or "",
                    exc.stderr or "",
                    timed_out=True,
                    policy_digest=__import__("hashlib")
                    .sha256(policy.encode())
                    .hexdigest(),
                )

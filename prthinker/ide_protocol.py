"""Version-one JSONL protocol for cancellable IDE review and approved patches."""

from __future__ import annotations

import hashlib
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Literal

import httpx
from pydantic import BaseModel, ConfigDict, Field

from prthinker.benchmark_execution import CountingRetriever
from prthinker.pipeline import CoTPipeline, PerFileReviewOptions
from prthinker.rag import NoOpRetriever
from prthinker.redaction import redact


class IDERequest(BaseModel):
    """All commands are versioned and reject unspecified input fields."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    protocol_version: Literal[1] = 1
    request_id: str = Field(min_length=1, max_length=200)
    operation: Literal["review", "cancel", "apply_patch", "verify"]
    diff: str = ""
    workdir: str = ""
    target_request_id: str = ""
    path: str = ""
    original_sha256: str = ""
    replacement: str = ""
    approved: bool = False
    command: tuple[str, ...] = ()


def safe_target(workdir: Path, relative: str) -> Path:
    if not relative or PurePosixPath(relative).is_absolute() or PureWindowsPath(relative).root:
        raise ValueError("IDE paths must be repository-relative")
    path = Path(relative)
    if PureWindowsPath(relative).drive or ".." in path.parts or ".git" in path.parts:
        raise ValueError("unsafe IDE path")
    target = workdir / path
    if target.is_symlink() or not target.resolve().is_relative_to(workdir.resolve()):
        raise ValueError("IDE path escapes repository")
    return target


def apply_approved_patch(request: IDERequest) -> dict:
    if not request.approved:
        raise ValueError("patch application requires explicit approval")
    target = safe_target(Path(request.workdir), request.path)
    original = target.read_bytes()
    if hashlib.sha256(original).hexdigest() != request.original_sha256:
        raise ValueError("stale patch: file content changed")
    replacement = request.replacement.encode("utf-8")
    if len(replacement) > 1_000_000:
        raise ValueError("patch exceeds size limit")
    if target.suffix == ".py":
        import ast
        ast.parse(request.replacement)
    temporary = target.with_name(target.name + ".prthinker.tmp")
    with temporary.open("xb") as handle:
        handle.write(replacement)
    try:
        temporary.chmod(target.stat().st_mode)
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)
    return {"path": request.path, "sha256": hashlib.sha256(replacement).hexdigest()}


class IDEServer:
    """Keep cancellation responsive while one review runs in a worker thread."""

    def __init__(self, backend_factory, emit, *, max_new_tokens=4096, executor=None,
                 retriever_factory=None, steps=None):
        self.backend_factory, self.emit = backend_factory, emit
        self.max_new_tokens, self.executor = max_new_tokens, executor
        self.retriever_factory = retriever_factory or NoOpRetriever
        self.steps = steps
        self.pool = ThreadPoolExecutor(max_workers=1)
        self.jobs = {}
        self.seen = set()
        self.lock = threading.RLock()

    def event(self, request_id, kind, **data):
        with self.lock:
            self.emit({"protocol_version": 1, "request_id": request_id, "event": kind, **data})

    def submit(self, request: IDERequest):
        with self.lock:
            if request.request_id in self.seen:
                raise ValueError("duplicate request ID")
            self.seen.add(request.request_id)
        if request.operation == "cancel":
            job = self.jobs.get(request.target_request_id)
            if job:
                job.set()
            self.event(request.request_id, "terminal", status="completed" if job else "unsupported")
        elif request.operation == "review":
            cancellation = threading.Event()
            self.jobs[request.request_id] = cancellation
            self.pool.submit(self._review, request, cancellation)
        else:
            self.pool.submit(self._command, request)

    def _review(self, request, cancellation):
        backend = None
        try:
            self.event(request.request_id, "progress", stage="started")
            backend = self.backend_factory()
            retriever = CountingRetriever(self.retriever_factory())
            options_kwargs = {"steps": self.steps} if self.steps is not None else {}
            pipeline = CoTPipeline(backend, retriever, max_new_tokens=self.max_new_tokens,
                                   cancel_event=cancellation, **options_kwargs)
            options = PerFileReviewOptions(inline_review=True,
                                            on_file_done=lambda file: self._file_done(request, file))
            result = pipeline.run_per_file(redact(request.diff)[0], options)
            self.event(request.request_id, "terminal",
                       status="cancelled" if cancellation.is_set() else "completed",
                       findings=len(result.inline_findings), retrieved_documents=retriever.count)
        except (RuntimeError, ValueError, OSError, httpx.HTTPError) as exc:
            self.event(request.request_id, "terminal", status="cancelled" if cancellation.is_set() else "failed",
                       reason=redact(str(exc))[0])
        finally:
            if backend:
                backend.close()
            self.jobs.pop(request.request_id, None)

    def _file_done(self, request, file):
        self.event(request.request_id, "progress", stage="file_completed", path=file.path)
        for finding in file.inline_findings:
            self.event(request.request_id, "finding", finding=finding.model_dump(mode="json"))
            if finding.suggestion:
                self.event(request.request_id, "patch_proposal", path=file.path,
                           line=finding.line, suggestion=finding.suggestion, requires_approval=True)

    def _command(self, request):
        try:
            if request.operation == "apply_patch":
                result = apply_approved_patch(request)
                self.event(request.request_id, "terminal", status="completed", result=result)
                return
            if not self.executor or not request.command:
                self.event(request.request_id, "terminal", status="unsupported", reason="verification executor and command required")
                return
            result = self.executor.run(request.command, Path(request.workdir), 120)
            self.event(request.request_id, "verification", exit_code=result.exit_code,
                       timed_out=result.timed_out, unsupported=result.unsupported)
            status = "unsupported" if result.unsupported else "completed" if result.exit_code == 0 else "failed"
            self.event(request.request_id, "terminal", status=status)
        except (RuntimeError, ValueError, OSError, SyntaxError) as exc:
            self.event(request.request_id, "terminal", status="failed", reason=redact(str(exc))[0])

    def close(self):
        for job in list(self.jobs.values()):
            job.set()
        self.pool.shutdown(wait=True, cancel_futures=False)


def add_parser(sub, common):
    root = sub.add_parser("ide", parents=[common], help="Versioned JSONL review protocol over stdin/stdout")
    root.add_argument("--sandbox", choices=("docker", "none"), default="docker")
    root.add_argument("--sandbox-image", default="")
    root.add_argument("--allow-unsandboxed", action="store_true")
    root.add_argument("--allow-unpinned-image", action="store_true")


def command(args):
    import sys

    from prthinker.backends import create_backend
    from prthinker.cli_review import _build_config, _build_retriever
    from prthinker.verify_cli import _build_executor

    for stream in (sys.stdin, sys.stdout):
        configure = getattr(stream, "reconfigure", None)
        if configure:
            configure(encoding="utf-8")

    config = _build_config(args)
    def emit(event):
        sys.stdout.write(json.dumps(event, ensure_ascii=False) + "\n")
        sys.stdout.flush()
    server = IDEServer(lambda: create_backend(config), emit, max_new_tokens=config.max_new_tokens,
                       executor=_build_executor(args), steps=config.steps,
                       retriever_factory=lambda: _build_retriever(args, config))
    try:
        for line in sys.stdin:
            try:
                server.submit(IDERequest.model_validate_json(line))
            except (ValueError, TypeError) as exc:
                emit({"protocol_version": 1, "event": "protocol_error", "reason": redact(str(exc))[0]})
    finally:
        server.close()
    return 0

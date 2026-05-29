"""FastAPI inference server.

Three endpoints:
    POST /ask     - one-shot generation (kept for backwards compatibility).
    POST /rag     - retrieve RAG rules for a query. Lets a thin runner do
                    RAG without bundling the embedding model.
    POST /review  - full CoT pipeline (RAG + 5 steps, optionally per-file
                    + inline findings). One round-trip from the runner.

Model + RAG index load once at import time per the project's perf rules.
"""

from __future__ import annotations

import gc
import logging
import os
import threading
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path

import torch

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse

from prthinker.accepted import (
    AcceptedExamplesRetriever,
    AcceptedExamplesStore,
)
from prthinker.backends.local import LocalQwen3Backend
from prthinker.config import LocalBackendConfig
from prthinker.dismissed import DismissedExamplesStore, DismissedFilter
from prthinker.pipeline import CoTPipeline, ReviewCancelledError
from prthinker.rag import FaissRAGRetriever
from prthinker.schemas import (
    AskRequest,
    JobStatus,
    RagRequest,
    RagResponse,
    ReviewJobStatusResponse,
    ReviewJobSubmitResponse,
    ReviewRequest,
    ReviewResponse,
    StepOutput,
)

log = logging.getLogger("prthinker.server")

RUN_ON = "Qwen/Qwen3-Coder-30B-A3B-Instruct"
_LORA_BY_MODEL: dict[str, str] = {
    "Qwen/Qwen3-1.7B": "../train/outputs-lora-qwen3-1.7b",
    "Qwen/Qwen2.5-Coder-7B-Instruct": "../train/outputs-lora-qwen2.5-coder-7b",
    "Qwen/Qwen3-Coder-30B-A3B-Instruct": "/home/nknul40s/LLM_Research/codes/train/outputs-lora-qwen3-coder-30b",
}
_DEFAULT_LORA = "../train/outputs-lora-qwen3-30b"

app = FastAPI(title="CoT Reviewer Inference Server")

# ---------------------------------------------------------------------------
# One-time module-level initialization (per project perf rules).
# ---------------------------------------------------------------------------

_backend = LocalQwen3Backend(
    LocalBackendConfig(
        model_name=RUN_ON,
        lora_path=_LORA_BY_MODEL.get(RUN_ON, _DEFAULT_LORA),
    )
)
_retriever = FaissRAGRetriever(threshold=0.7)


def _build_dismissed_filter() -> DismissedFilter | None:
    raw_path = os.environ.get("PRTHINKER_DISMISSED_PATH", "").strip()
    if not raw_path:
        return None
    store = DismissedExamplesStore(Path(raw_path))
    if len(store) == 0:
        log.info("Dismissed store at %s is empty — filter disabled", raw_path)
        return None
    threshold = float(os.environ.get("PRTHINKER_DISMISSED_THRESHOLD", "0.85") or 0.85)
    return DismissedFilter(store, threshold=threshold, path_scoped=False)


_dismissed_filter = _build_dismissed_filter()


def _build_accepted_retriever() -> AcceptedExamplesRetriever | None:
    raw_path = os.environ.get("PRTHINKER_ACCEPTED_PATH", "").strip()
    if not raw_path:
        return None
    store = AcceptedExamplesStore(Path(raw_path))
    if len(store) == 0:
        log.info("Accepted store at %s is empty — exemplars disabled", raw_path)
        return None
    threshold = float(os.environ.get("PRTHINKER_ACCEPTED_THRESHOLD", "0.6") or 0.6)
    k = int(os.environ.get("PRTHINKER_ACCEPTED_TOP_K", "3") or 3)
    return AcceptedExamplesRetriever(store, k=k, threshold=threshold)


_accepted_retriever = _build_accepted_retriever()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "model": RUN_ON}


@app.post("/ask", response_class=PlainTextResponse)
def ask(req: AskRequest) -> str:
    return _backend.generate(req.prompt, max_new_tokens=req.max_new_tokens)


@app.post("/rag", response_model=RagResponse)
def rag(req: RagRequest) -> RagResponse:
    retriever = FaissRAGRetriever(threshold=req.threshold)
    docs = retriever.retrieve(req.query)
    return RagResponse(docs=docs)


# Cap the diff sent to the pipeline so KV cache + activations stay
# within ~3-4 GiB headroom on a single L40S. CoT prompts wrap the diff
# with system instructions + RAG docs + extra rules; total context is
# bounded above by tokens-in-diff + ~1.5x for the wrapping. 6000 keeps
# the worst case under 16K total context.
_MAX_DIFF_TOKENS = 6000
_TRUNCATION_NOTICE = (
    "\n\n... [diff truncated server-side to fit GPU memory budget;"
    " review covers the prefix above only]\n"
)


def _truncate_diff(diff: str) -> str:
    tokenizer = getattr(_backend, "_tokenizer", None)
    if tokenizer is None:
        return diff
    encoded = tokenizer(diff, add_special_tokens=False).input_ids
    if len(encoded) <= _MAX_DIFF_TOKENS:
        return diff
    kept = tokenizer.decode(encoded[:_MAX_DIFF_TOKENS], skip_special_tokens=True)
    log.warning(
        "Diff truncated from %d to %d tokens",
        len(encoded),
        _MAX_DIFF_TOKENS,
    )
    return kept + _TRUNCATION_NOTICE


def _execute_review(
    req: ReviewRequest,
    cancel_event: "threading.Event | None" = None,
) -> ReviewResponse:
    """Synchronous CoT review. Shared by `/review` and the async job worker."""
    code_diff = _truncate_diff(req.code_diff)

    retriever = (
        FaissRAGRetriever(threshold=req.rag_threshold)
        if req.rag_enabled
        else _NoOpRetriever()
    )
    pipeline = CoTPipeline(
        backend=_backend,
        retriever=retriever,
        steps=tuple(req.steps or ()),
        max_new_tokens=req.max_new_tokens,
        extra_rules=tuple(req.extra_rules),
        dismissed_filter=_dismissed_filter,
        accepted_retriever=_accepted_retriever,
        cancel_event=cancel_event,
    )

    if req.file_path is not None:
        file_result = pipeline.run_for_file(req.file_path, code_diff)
        return ReviewResponse(
            code_diff=code_diff,
            rag_docs=file_result.rag_docs,
            steps=[StepOutput(name=k, output=v)
                   for k, v in file_result.step_outputs.items()],
            inline_findings=file_result.inline_findings,
        )

    result = pipeline.run(code_diff)
    return ReviewResponse(
        code_diff=result.code_diff,
        rag_docs=result.rag_docs,
        steps=[StepOutput(name=k, output=v) for k, v in result.step_outputs.items()],
        inline_findings=[],
    )


@app.post("/review", response_model=ReviewResponse)
def review(req: ReviewRequest) -> ReviewResponse:
    if not req.code_diff.strip():
        raise HTTPException(status_code=400, detail="code_diff is empty")
    try:
        return _execute_review(req)
    finally:
        _release_gpu_memory()


# ---------------------------------------------------------------------------
# Async job pattern for long-running reviews.
#
# Cloudflare's free/pro/business proxy aborts any single HTTP request at
# 100s. A 30B MoE CoT review runs for minutes, so the synchronous /review
# endpoint cannot survive the edge. Clients behind such a proxy submit
# the job, then poll for the result — each individual HTTP call returns
# in well under the 100s budget.
# ---------------------------------------------------------------------------

_JOB_TTL_SECONDS = 3600
# A running job whose result endpoint has not been polled for this long
# is presumed abandoned (matrix runner was cancelled, lost network, etc.).
# The sweeper sets its cancel_event so the worker bails out at the next
# step boundary instead of finishing inference no one will read.
_IDLE_TIMEOUT_SECONDS = 180
_SWEEPER_INTERVAL_SECONDS = 30


@dataclass
class _Job:
    status: JobStatus = "pending"
    result: ReviewResponse | None = None
    error: str | None = None
    created_at: float = field(default_factory=time.time)
    last_polled_at: float = field(default_factory=time.time)
    cancel_event: threading.Event = field(default_factory=threading.Event)


_JOBS: dict[str, _Job] = {}
_JOBS_LOCK = threading.Lock()


def _evict_stale_jobs_locked() -> None:
    """Drop jobs older than the TTL. Caller must hold _JOBS_LOCK."""
    now = time.time()
    stale = [
        jid for jid, j in _JOBS.items()
        if now - j.created_at > _JOB_TTL_SECONDS
    ]
    for jid in stale:
        del _JOBS[jid]


def _sweep_idle_jobs() -> None:
    """Background sweeper: cancel running jobs that nobody is polling.

    The matrix runner polls every 5 seconds, so 180 s of silence almost
    certainly means the runner was cancelled (concurrency
    cancel-in-progress, manual cancel, hung CI) and there is no point
    burning GPU on a review nobody will read.
    """
    while True:
        time.sleep(_SWEEPER_INTERVAL_SECONDS)
        now = time.time()
        with _JOBS_LOCK:
            for jid, job in _JOBS.items():
                if job.status != "running":
                    continue
                if job.cancel_event.is_set():
                    continue
                if now - job.last_polled_at > _IDLE_TIMEOUT_SECONDS:
                    log.warning(
                        "Job %s idle for %.0fs; setting cancel_event",
                        jid,
                        now - job.last_polled_at,
                    )
                    job.cancel_event.set()


threading.Thread(target=_sweep_idle_jobs, daemon=True).start()


def _release_gpu_memory() -> None:
    """Drop intermediate tensors and return reserved CUDA blocks to the OS.

    Per-file review accumulates KV cache + activations on the GPU; without
    this the cache hangs on between jobs and the next allocation OOMs even
    when free VRAM looks adequate.
    """
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def _run_review_job(job_id: str, req: ReviewRequest) -> None:
    with _JOBS_LOCK:
        job = _JOBS.get(job_id)
        if job is None:
            return
        job.status = "running"
        cancel_event = job.cancel_event
    try:
        result = _execute_review(req, cancel_event=cancel_event)
        with _JOBS_LOCK:
            job = _JOBS.get(job_id)
            if job is not None:
                job.status = "done"
                job.result = result
    except ReviewCancelledError:
        log.info("Review job %s cancelled by client", job_id)
        with _JOBS_LOCK:
            job = _JOBS.get(job_id)
            if job is not None:
                job.status = "cancelled"
    except Exception as exc:
        log.exception("Review job %s failed", job_id)
        with _JOBS_LOCK:
            job = _JOBS.get(job_id)
            if job is not None:
                job.status = "error"
                job.error = f"{type(exc).__name__}: {exc}"
    finally:
        _release_gpu_memory()


@app.post("/review/submit", response_model=ReviewJobSubmitResponse)
def review_submit(req: ReviewRequest) -> ReviewJobSubmitResponse:
    if not req.code_diff.strip():
        raise HTTPException(status_code=400, detail="code_diff is empty")
    job_id = uuid.uuid4().hex
    with _JOBS_LOCK:
        _evict_stale_jobs_locked()
        _JOBS[job_id] = _Job()
    threading.Thread(
        target=_run_review_job,
        args=(job_id, req),
        daemon=True,
    ).start()
    return ReviewJobSubmitResponse(job_id=job_id)


@app.get("/review/result/{job_id}", response_model=ReviewJobStatusResponse)
def review_result(job_id: str) -> ReviewJobStatusResponse:
    with _JOBS_LOCK:
        job = _JOBS.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="job not found")
        # Heartbeat for the idle sweeper — as long as a client polls
        # within _IDLE_TIMEOUT_SECONDS the worker keeps running.
        job.last_polled_at = time.time()
        return ReviewJobStatusResponse(
            job_id=job_id,
            status=job.status,
            result=job.result,
            error=job.error,
        )


@app.post("/review/cancel/{job_id}")
def review_cancel(job_id: str) -> dict[str, str | bool]:
    """Mark a running job for cancellation.

    Sets the worker's ``cancel_event``; the pipeline picks it up at the
    next step boundary (inference itself is uninterruptible) and the
    job ends with ``status="cancelled"``. Already-terminal jobs are
    left alone and the endpoint reports the current status.
    """
    with _JOBS_LOCK:
        job = _JOBS.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="job not found")
        if job.status in ("done", "error", "cancelled"):
            return {"job_id": job_id, "cancelled": False, "status": job.status}
        job.cancel_event.set()
        return {"job_id": job_id, "cancelled": True, "status": job.status}


class _NoOpRetriever:
    def retrieve(self, prompt: str) -> list[str]:
        return []

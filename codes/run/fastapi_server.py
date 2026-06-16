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

from codes.util.server_metrics import observe_review
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
    AskJobStatusResponse,
    AskJobSubmitResponse,
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

# PRTHINKER_MODEL_NAME selects the served model (same env the CLI's
# local backend uses); the gemma4 compose overlay sets it to
# google/gemma-4-31B-it. PRTHINKER_LORA_PATH overrides the adapter
# lookup below for deploys whose adapter lives outside _LORA_BY_MODEL.
RUN_ON = os.environ.get(
    "PRTHINKER_MODEL_NAME", "Qwen/Qwen3-Coder-30B-A3B-Instruct"
)

# This server is the qwen-era deployment: keep its original embedding
# index (Qwen3-Embedding-4B @ 0.7) unless the operator overrides
# EMB_MODEL. faiss_util loads lazily at retriever construction below, so
# this setdefault still wins. New local-Gemma deployments default to
# EmbeddingGemma instead (READMEs/local_gemma_deployment.md).
os.environ.setdefault("EMB_MODEL", "Qwen/Qwen3-Embedding-4B")

_LORA_BY_MODEL: dict[str, str] = {
    "Qwen/Qwen3-1.7B": "../train/outputs-lora-qwen3-1.7b",
    "Qwen/Qwen2.5-Coder-7B-Instruct": "../train/outputs-lora-qwen2.5-coder-7b",
    "Qwen/Qwen3-Coder-30B-A3B-Instruct": "../train/outputs-lora-qwen3-coder-30b",
    # Dense Gemma 4 — needs transformers>=5.7 (gemma4 model_type), which
    # the Qwen3-A3B deploy's <5 pin forbids; serve it from its own image.
    "google/gemma-4-31B-it": "../train/outputs-qlora-gemma-4-31b-it",
}
_DEFAULT_LORA = "../train/outputs-lora-qwen3-30b"

app = FastAPI(title="CoT Reviewer Inference Server")

# Expose Prometheus-format metrics at /metrics so the monitoring
# compose overlay (prometheus + grafana + dcgm + cadvisor) can scrape
# per-endpoint request count / latency / status without touching the
# pipeline. Instrumentation is lazy-imported so a runner-profile
# install does not have to pull in the dependency.
try:
    from prometheus_fastapi_instrumentator import Instrumentator
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")
except ImportError:
    log.info("prometheus_fastapi_instrumentator not installed; /metrics disabled")

# ---------------------------------------------------------------------------
# One-time module-level initialization (per project perf rules).
# ---------------------------------------------------------------------------

_backend = LocalQwen3Backend(
    LocalBackendConfig(
        model_name=RUN_ON,
        lora_path=os.environ.get("PRTHINKER_LORA_PATH")
        or _LORA_BY_MODEL.get(RUN_ON, _DEFAULT_LORA),
    )
)


def _warm_rag_index() -> None:
    """Build the FAISS index at boot instead of on the first request.

    Constructing a ``FaissRAGRetriever`` imports ``codes.util.faiss_util``,
    whose module body loads the embedding model and builds the rule index
    exactly once. Triggering that here means the boot probe exercises the
    embedding stack and the first ``/review`` / ``/rag`` does not pay the
    one-off index-build cost. The retriever instance is intentionally
    discarded — every request builds its own with the request's threshold;
    only the import-time side effect is wanted.
    """
    FaissRAGRetriever(threshold=0.7)


_warm_rag_index()


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


@observe_review
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
        max_step_result_chars=int(
            os.environ.get("PRTHINKER_MAX_STEP_RESULT_CHARS", "6000") or "6000"
        ),
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


def _cancel_if_idle(jid: str, job: "_Job | _AskJob", now: float, label: str) -> None:
    """Set a running job's cancel_event if it has been idle past the timeout."""
    if job.status != "running":
        return
    if job.cancel_event.is_set():
        return
    idle_for = now - job.last_polled_at
    if idle_for > _IDLE_TIMEOUT_SECONDS:
        log.warning(
            "%s job %s idle for %.0fs; setting cancel_event",
            label,
            jid,
            idle_for,
        )
        job.cancel_event.set()


def _sweep_table_once(
    lock: threading.Lock,
    jobs: "dict[str, _Job] | dict[str, _AskJob]",
    label: str,
    now: float,
) -> None:
    """Cancel every idle running job in one job table under its lock."""
    with lock:
        for jid, job in jobs.items():
            _cancel_if_idle(jid, job, now, label)


def _sweep_idle_jobs() -> None:
    """Background sweeper: cancel running jobs that nobody is polling.

    The matrix runner polls every 5 seconds, so 180 s of silence almost
    certainly means the runner was cancelled (concurrency
    cancel-in-progress, manual cancel, hung CI) and there is no point
    burning GPU on a review nobody will read. Both /review and /ask
    job tables share the same idle policy.
    """
    while True:
        time.sleep(_SWEEPER_INTERVAL_SECONDS)
        now = time.time()
        _sweep_table_once(_JOBS_LOCK, _JOBS, "Review", now)
        _sweep_table_once(_ASK_JOBS_LOCK, _ASK_JOBS, "Ask", now)


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


# ---------------------------------------------------------------------------
# Async job pattern for /ask.
#
# Mirrors the /review submit + poll pattern. A long single-prompt
# generation (e.g. the aggregate's PR-wide overall-summary synthesis
# with max_new_tokens in the tens of thousands) easily exceeds the
# 100 s Cloudflare idle timeout that the synchronous /ask cannot
# survive. /ask/submit returns a job id; /ask/result/{id} is polled
# every few seconds so each round-trip fits inside the proxy budget.
# ---------------------------------------------------------------------------


@dataclass
class _AskJob:
    status: JobStatus = "pending"
    result: str | None = None
    error: str | None = None
    created_at: float = field(default_factory=time.time)
    last_polled_at: float = field(default_factory=time.time)
    cancel_event: threading.Event = field(default_factory=threading.Event)


_ASK_JOBS: dict[str, _AskJob] = {}
_ASK_JOBS_LOCK = threading.Lock()


def _evict_stale_ask_jobs_locked() -> None:
    now = time.time()
    stale = [
        jid for jid, j in _ASK_JOBS.items()
        if now - j.created_at > _JOB_TTL_SECONDS
    ]
    for jid in stale:
        del _ASK_JOBS[jid]


def _run_ask_job(job_id: str, req: AskRequest) -> None:
    with _ASK_JOBS_LOCK:
        job = _ASK_JOBS.get(job_id)
        if job is None:
            return
        job.status = "running"
        cancel_event = job.cancel_event
    try:
        text = _backend.generate(
            req.prompt,
            max_new_tokens=req.max_new_tokens,
            cancel_event=cancel_event,
        )
        with _ASK_JOBS_LOCK:
            job = _ASK_JOBS.get(job_id)
            if job is not None:
                job.status = "done"
                job.result = text
    except ReviewCancelledError:
        log.info("Ask job %s cancelled by client", job_id)
        with _ASK_JOBS_LOCK:
            job = _ASK_JOBS.get(job_id)
            if job is not None:
                job.status = "cancelled"
    except Exception as exc:
        log.exception("Ask job %s failed", job_id)
        with _ASK_JOBS_LOCK:
            job = _ASK_JOBS.get(job_id)
            if job is not None:
                job.status = "error"
                job.error = f"{type(exc).__name__}: {exc}"
    finally:
        _release_gpu_memory()


@app.post("/ask/submit", response_model=AskJobSubmitResponse)
def ask_submit(req: AskRequest) -> AskJobSubmitResponse:
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="prompt is empty")
    job_id = uuid.uuid4().hex
    with _ASK_JOBS_LOCK:
        _evict_stale_ask_jobs_locked()
        _ASK_JOBS[job_id] = _AskJob()
    threading.Thread(
        target=_run_ask_job,
        args=(job_id, req),
        daemon=True,
    ).start()
    return AskJobSubmitResponse(job_id=job_id)


@app.get("/ask/result/{job_id}", response_model=AskJobStatusResponse)
def ask_result(job_id: str) -> AskJobStatusResponse:
    with _ASK_JOBS_LOCK:
        job = _ASK_JOBS.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="job not found")
        job.last_polled_at = time.time()
        return AskJobStatusResponse(
            job_id=job_id,
            status=job.status,
            result=job.result,
            error=job.error,
        )


@app.post("/ask/cancel/{job_id}")
def ask_cancel(job_id: str) -> dict[str, str | bool]:
    with _ASK_JOBS_LOCK:
        job = _ASK_JOBS.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="job not found")
        if job.status in ("done", "error", "cancelled"):
            return {"job_id": job_id, "cancelled": False, "status": job.status}
        job.cancel_event.set()
        return {"job_id": job_id, "cancelled": True, "status": job.status}


class _NoOpRetriever:
    def retrieve(self, prompt: str) -> list[str]:  # pylint: disable=unused-argument  # retriever interface signature
        return []

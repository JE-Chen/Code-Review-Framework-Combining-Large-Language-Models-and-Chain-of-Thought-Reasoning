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

import logging
import os
import threading
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse

from prthinker.accepted import (
    AcceptedExamplesRetriever,
    AcceptedExamplesStore,
)
from prthinker.backends.local import LocalQwen3Backend
from prthinker.config import LocalBackendConfig
from prthinker.dismissed import DismissedExamplesStore, DismissedFilter
from prthinker.pipeline import CoTPipeline
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


def _execute_review(req: ReviewRequest) -> ReviewResponse:
    """Synchronous CoT review. Shared by `/review` and the async job worker."""
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
    )

    if req.file_path is not None:
        file_result = pipeline.run_for_file(req.file_path, req.code_diff)
        return ReviewResponse(
            code_diff=req.code_diff,
            rag_docs=file_result.rag_docs,
            steps=[StepOutput(name=k, output=v)
                   for k, v in file_result.step_outputs.items()],
            inline_findings=file_result.inline_findings,
        )

    result = pipeline.run(req.code_diff)
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
    return _execute_review(req)


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


@dataclass
class _Job:
    status: JobStatus = "pending"
    result: ReviewResponse | None = None
    error: str | None = None
    created_at: float = field(default_factory=time.time)


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


def _run_review_job(job_id: str, req: ReviewRequest) -> None:
    with _JOBS_LOCK:
        job = _JOBS.get(job_id)
        if job is None:
            return
        job.status = "running"
    try:
        result = _execute_review(req)
        with _JOBS_LOCK:
            job = _JOBS.get(job_id)
            if job is not None:
                job.status = "done"
                job.result = result
    except Exception as exc:
        log.exception("Review job %s failed", job_id)
        with _JOBS_LOCK:
            job = _JOBS.get(job_id)
            if job is not None:
                job.status = "error"
                job.error = f"{type(exc).__name__}: {exc}"


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
        return ReviewJobStatusResponse(
            job_id=job_id,
            status=job.status,
            result=job.result,
            error=job.error,
        )


class _NoOpRetriever:
    def retrieve(self, prompt: str) -> list[str]:
        return []

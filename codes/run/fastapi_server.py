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
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse

from reviewmind.accepted import (
    AcceptedExamplesRetriever,
    AcceptedExamplesStore,
)
from reviewmind.backends.local import LocalQwen3Backend
from reviewmind.config import LocalBackendConfig
from reviewmind.dismissed import DismissedExamplesStore, DismissedFilter
from reviewmind.pipeline import CoTPipeline
from reviewmind.rag import FaissRAGRetriever
from reviewmind.schemas import (
    AskRequest,
    RagRequest,
    RagResponse,
    ReviewRequest,
    ReviewResponse,
    StepOutput,
)

log = logging.getLogger("reviewmind.server")

RUN_ON = "Qwen/Qwen3-Coder-30B-A3B-Instruct"
_LORA_BY_MODEL: dict[str, str] = {
    "Qwen/Qwen3-1.7B": "../train/outputs-lora-qwen3-1.7b",
    "Qwen/Qwen2.5-Coder-7B-Instruct": "../train/outputs-lora-qwen2.5-coder-7b",
    "Qwen/Qwen3-Coder-30B-A3B-Instruct": "../train/outputs-lora-qwen3-coder-30b",
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
    raw_path = os.environ.get("REVIEWMIND_DISMISSED_PATH", "").strip()
    if not raw_path:
        return None
    store = DismissedExamplesStore(Path(raw_path))
    if len(store) == 0:
        log.info("Dismissed store at %s is empty — filter disabled", raw_path)
        return None
    threshold = float(os.environ.get("REVIEWMIND_DISMISSED_THRESHOLD", "0.85") or 0.85)
    return DismissedFilter(store, threshold=threshold, path_scoped=False)


_dismissed_filter = _build_dismissed_filter()


def _build_accepted_retriever() -> AcceptedExamplesRetriever | None:
    raw_path = os.environ.get("REVIEWMIND_ACCEPTED_PATH", "").strip()
    if not raw_path:
        return None
    store = AcceptedExamplesStore(Path(raw_path))
    if len(store) == 0:
        log.info("Accepted store at %s is empty — exemplars disabled", raw_path)
        return None
    threshold = float(os.environ.get("REVIEWMIND_ACCEPTED_THRESHOLD", "0.6") or 0.6)
    k = int(os.environ.get("REVIEWMIND_ACCEPTED_TOP_K", "3") or 3)
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


@app.post("/review", response_model=ReviewResponse)
def review(req: ReviewRequest) -> ReviewResponse:
    if not req.code_diff.strip():
        raise HTTPException(status_code=400, detail="code_diff is empty")

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


class _NoOpRetriever:
    def retrieve(self, prompt: str) -> list[str]:
        return []

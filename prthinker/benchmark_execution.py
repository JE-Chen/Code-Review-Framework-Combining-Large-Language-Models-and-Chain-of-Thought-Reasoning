"""Interchangeable prompt and full-review strategies for benchmark sessions."""

from __future__ import annotations

import json
from dataclasses import dataclass

from prthinker.backends.base import InferenceBackend
from prthinker.benchmark_measurement import MeasuredBackend
from prthinker.benchmark_session import CaseExecution, UnsupportedCaseError
from prthinker.pipeline import CoTPipeline
from prthinker.pipeline_types import PerFileReviewOptions
from prthinker.rag import NoOpRetriever, RAGRetriever


class CountingRetriever(RAGRetriever):
    """Count documents actually returned for each case, including zero hits."""

    def __init__(self, inner: RAGRetriever):
        self.inner = inner
        self.count = 0

    def retrieve(self, prompt: str) -> list[str]:
        docs = self.inner.retrieve(prompt)
        self.count += len(docs)
        return docs


@dataclass
class PromptExecution:
    backend: InferenceBackend
    max_new_tokens: int

    def __call__(self, case) -> CaseExecution:
        result = self.backend.generate_result(case.prompt, self.max_new_tokens)
        usage = result.usage
        return CaseExecution(result.text, 0,
                             usage.prompt_tokens if usage else None,
                             usage.completion_tokens if usage else None)


class ReviewExecution:
    """Use the production per-file pipeline without dataset labels in prompts."""

    def __init__(self, backend, controls: dict, retriever=None):
        self.backend = MeasuredBackend(backend)
        self.retriever = CountingRetriever(retriever or NoOpRetriever())
        self.controls = controls

    def __call__(self, case) -> CaseExecution:
        if "diff --git " not in case.prompt and "--- " not in case.prompt:
            raise UnsupportedCaseError("full review requires a unified diff")
        self.retriever.count = 0
        self.backend.reset()
        pipeline = CoTPipeline(
            self.backend, self.retriever,
            steps=tuple(self.controls.get("steps", ())),
            max_new_tokens=self.controls["max_new_tokens"],
            extra_rules=tuple(self.controls.get("extra_rules", ())),
        )
        options = PerFileReviewOptions(**self.controls.get("review_options", {"inline_review": True}))
        result = pipeline.run_per_file(case.prompt, options)
        findings = [finding.model_dump(mode="json") for finding in result.inline_findings]
        payload = {"findings": findings, "step_outputs": result.step_outputs}
        return CaseExecution(json.dumps(payload, ensure_ascii=False), self.retriever.count, **self.backend.metrics())

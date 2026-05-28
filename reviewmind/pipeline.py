"""Pipeline orchestrator — Template Method over registered review steps.

Two modes:

* ``run(diff)`` — one prompt sweep over the whole diff.
* ``run_per_file(diff)`` — parse the unified diff and run a sweep per file,
  optionally appending an InlineFindingsStep per file for line-level
  review comments.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from reviewmind.accepted import AcceptedExamplesRetriever, format_examples_block
from reviewmind.backends.base import InferenceBackend
from reviewmind import api_consistency
from reviewmind.counterfactual import parse_counterfactuals
from reviewmind.diff import FileDiff, parse_unified_diff
from reviewmind.dismissed import DismissedFilter
from reviewmind.findings import build_provenance_block, parse_inline_findings
from reviewmind.review_cache import CacheKey, ReviewCache
from reviewmind.judge import parse_verdict
from reviewmind.rag import RAGRetriever
from reviewmind.schemas import (
    ApiDriftFinding,
    CounterfactualBlock,
    InlineFinding,
    JudgeVerdict,
)
from reviewmind.self_review import (
    apply_self_review,
    parse_drop_indices,
    render_findings_block,
)
from reviewmind.steps import (
    CounterfactualStep,
    InlineFindingsStep,
    JudgeStep,
    ReviewContext,
    ReviewStep,
    resolve_steps,
)

log = logging.getLogger(__name__)


@dataclass
class ReviewResult:
    code_diff: str
    rag_docs: list[str]
    step_outputs: dict[str, str] = field(default_factory=dict)
    inline_findings: list[InlineFinding] = field(default_factory=list)
    per_file: list["FileReviewResult"] = field(default_factory=list)
    counterfactuals: list[CounterfactualBlock] = field(default_factory=list)
    api_drift: list[ApiDriftFinding] = field(default_factory=list)

    @property
    def total_summary(self) -> str | None:
        return self.step_outputs.get("total_summary")


@dataclass
class FileReviewResult:
    path: str
    rag_docs: list[str]
    step_outputs: dict[str, str]
    inline_findings: list[InlineFinding]
    verdict: JudgeVerdict | None = None
    is_binary: bool = False
    is_deleted: bool = False
    counterfactuals: list[CounterfactualBlock] = field(default_factory=list)

    @property
    def total_summary(self) -> str | None:
        return self.step_outputs.get("total_summary")


class CoTPipeline:
    def __init__(
        self,
        backend: InferenceBackend,
        retriever: RAGRetriever,
        steps: tuple[str, ...] = (),
        max_new_tokens: int = 32768,
        extra_rules: tuple[str, ...] = (),
        dismissed_filter: DismissedFilter | None = None,
        accepted_retriever: AcceptedExamplesRetriever | None = None,
        stream: bool = False,
        stream_sink: "object | None" = None,
    ) -> None:
        self._backend = backend
        self._retriever = retriever
        self._step_classes = resolve_steps(steps)
        self._max_new_tokens = max_new_tokens
        self._extra_rules = tuple(extra_rules)
        self._dismissed_filter = dismissed_filter
        self._accepted_retriever = accepted_retriever
        self._stream = stream
        # File-like with .write(str); stderr by default when stream=True.
        self._stream_sink = stream_sink

    def _merge_rules(self, retrieved: list[str]) -> list[str]:
        # Always-on team rules are appended after RAG-retrieved rules so the
        # template builder treats them uniformly. Order preserves precedence:
        # RAG context first, then team-specific overrides.
        return list(retrieved) + list(self._extra_rules)

    # ---------- single-pass mode --------------------------------------------

    def run(
        self,
        code_diff: str,
        output_dir: Path | None = None,
    ) -> ReviewResult:
        if output_dir is not None:
            output_dir.mkdir(parents=True, exist_ok=True)

        rag_docs = self._merge_rules(self._retriever.retrieve(code_diff))
        ctx = ReviewContext(code_diff=code_diff, rag_docs=rag_docs)
        self._run_steps(ctx, self._step_classes, output_dir)

        return ReviewResult(
            code_diff=code_diff,
            rag_docs=rag_docs,
            step_outputs=dict(ctx.results),
        )

    # ---------- single-file mode (used by /review when file_path is set) ----

    def run_for_file(
        self,
        file_path: str,
        diff_text: str,
        *,
        inline_review: bool = True,
        max_findings: int = 10,
    ) -> "FileReviewResult":
        """Run all configured steps against one file's diff.

        Used by the FastAPI `/review` endpoint and by `run_per_file`.
        """
        files = parse_unified_diff(diff_text)
        fd = files[0] if files else FileDiff(path=file_path, raw=diff_text)
        # Force the path so callers can override what the diff reports.
        fd.path = file_path

        extra: tuple[type[ReviewStep], ...] = (
            (InlineFindingsStep,) if inline_review else ()
        )
        return self._run_one_file(
            fd,
            self._step_classes + extra,
            max_findings_per_file=max_findings,
            output_dir=None,
        )

    # ---------- per-file mode -----------------------------------------------

    def run_per_file(
        self,
        diff_text: str,
        *,
        inline_review: bool = False,
        judge: bool = False,
        self_correct: bool = False,
        counterfactual: bool = False,
        provenance: bool = False,
        api_consistency_check: bool = False,
        max_findings_per_file: int = 10,
        skip_binary: bool = True,
        output_dir: Path | None = None,
        dialogue_block: str = "",
        review_cache: "ReviewCache | None" = None,
        cache_repo: str = "",
        cache_pr_number: int = 0,
        verify_suggestions: bool = False,
        verify_workdir: Path | None = None,
        verify_cmd: str = "",
        verify_timeout: float = 60.0,
    ) -> ReviewResult:
        """Run the full step sequence once per file in the diff.

        When `inline_review` is True, append an `InlineFindingsStep` to each
        file's run and aggregate the parsed findings into the result.
        """
        file_diffs = parse_unified_diff(diff_text)
        if not file_diffs:
            log.warning("Diff had no parseable files")
            return ReviewResult(code_diff=diff_text, rag_docs=[])

        extra: tuple[type[ReviewStep], ...] = ()
        if inline_review:
            extra += (InlineFindingsStep,)
        if counterfactual:
            if not inline_review:
                raise ValueError(
                    "counterfactual step requires inline_review (it operates "
                    "on the findings list)"
                )
            extra += (CounterfactualStep,)
        if judge:
            extra += (JudgeStep,)
        all_steps = self._step_classes + extra

        per_file_results: list[FileReviewResult] = []
        aggregated_findings: list[InlineFinding] = []
        aggregated_counterfactuals: list[CounterfactualBlock] = []
        aggregated_steps: dict[str, str] = {}

        for fd in file_diffs:
            if skip_binary and fd.is_binary:
                log.info("Skipping binary file %s", fd.path)
                continue
            if fd.is_deleted:
                log.info("Skipping deleted file %s", fd.path)
                continue

            cache_key: CacheKey | None = None
            if review_cache is not None and cache_pr_number > 0 and inline_review:
                cache_key = CacheKey(
                    pr_number=cache_pr_number,
                    repo=cache_repo,
                    file_path=fd.path,
                    hunk_sha256=fd.content_sha256(),
                )
                cached = review_cache.get(cache_key)
                if cached is not None:
                    log.info(
                        "Differential review: reusing %d cached finding(s) for %s",
                        len(cached), fd.path,
                    )
                    file_result = FileReviewResult(
                        path=fd.path,
                        rag_docs=[],
                        step_outputs={},
                        inline_findings=cached,
                        is_binary=fd.is_binary,
                        is_deleted=fd.is_deleted,
                    )
                    per_file_results.append(file_result)
                    aggregated_findings.extend(cached)
                    continue

            file_out_dir = (
                output_dir / _sanitize(fd.path) if output_dir else None
            )
            file_result = self._run_one_file(
                fd,
                all_steps,
                max_findings_per_file=max_findings_per_file,
                output_dir=file_out_dir,
                self_correct=self_correct,
                dialogue_block=dialogue_block,
                provenance=provenance,
            )
            if cache_key is not None:
                review_cache.put(
                    cache_key,
                    file_result.inline_findings,
                    backend=self._backend.backend_kind(),
                    model=self._backend.model_name(),
                )
            if verify_suggestions and verify_workdir is not None and verify_cmd:
                file_result = self._verify_suggestions(
                    file_result,
                    workdir=verify_workdir,
                    verify_cmd=verify_cmd,
                    timeout_seconds=verify_timeout,
                )
            per_file_results.append(file_result)
            aggregated_findings.extend(file_result.inline_findings)
            aggregated_counterfactuals.extend(file_result.counterfactuals)
            for name, output in file_result.step_outputs.items():
                # Concatenate per-file outputs for the consolidated comment.
                key = f"{fd.path}::{name}"
                aggregated_steps[key] = output

        api_drift: list[ApiDriftFinding] = []
        if api_consistency_check and api_consistency.is_mixed_language(file_diffs):
            log.info("Mixed-language PR detected → running api-consistency step")
            prompt = api_consistency.build_prompt(file_diffs)
            raw = self._backend.generate(prompt, max_new_tokens=self._max_new_tokens)
            aggregated_steps["api_consistency"] = raw
            allowed = {fd.path for fd in file_diffs}
            api_drift = api_consistency.parse_drift_findings(
                raw, allowed_paths=allowed,
            )

        return ReviewResult(
            code_diff=diff_text,
            rag_docs=[],
            step_outputs=aggregated_steps,
            inline_findings=aggregated_findings,
            per_file=per_file_results,
            counterfactuals=aggregated_counterfactuals,
            api_drift=api_drift,
        )

    # ---------- internals ---------------------------------------------------

    def _run_one_file(
        self,
        fd: FileDiff,
        step_classes: tuple[type[ReviewStep], ...],
        *,
        max_findings_per_file: int,
        output_dir: Path | None,
        self_correct: bool = False,
        dialogue_block: str = "",
        provenance: bool = False,
    ) -> FileReviewResult:
        rag_docs = self._merge_rules(self._retriever.retrieve(fd.raw))
        positive_examples_block = ""
        n_accepted_examples = 0
        if self._accepted_retriever is not None:
            examples = list(
                self._accepted_retriever.top_k(fd.raw, path=fd.path)
            )
            n_accepted_examples = len(examples)
            positive_examples_block = format_examples_block(examples)

        provenance_block = ""
        if provenance:
            provenance_block = build_provenance_block(
                rag_docs=rag_docs,
                n_accepted_examples=n_accepted_examples,
            )

        ctx = ReviewContext(
            code_diff=fd.raw,
            rag_docs=rag_docs,
            file_path=fd.path,
            max_findings=max_findings_per_file,
            positive_examples_block=positive_examples_block,
            dialogue_block=dialogue_block,
            provenance_block=provenance_block,
        )
        self._run_steps(ctx, step_classes, output_dir)

        findings: list[InlineFinding] = []
        if "inline_findings" in ctx.results:
            findings = parse_inline_findings(
                ctx.results["inline_findings"],
                path=fd.path,
                allowed_lines=fd.commentable_lines(),
                n_rag_rules=len(rag_docs) if provenance else 0,
                n_accepted_examples=n_accepted_examples if provenance else 0,
            )
            if self._dismissed_filter is not None and findings:
                findings = self._dismissed_filter.filter(findings)
            if self_correct and findings:
                findings = self._self_correct(fd, findings, ctx)
                # Stash the self-review raw output for traceability.
                # ``self_review`` step output is already inside ``ctx.results``.

        verdict: JudgeVerdict | None = None
        if "judge" in ctx.results:
            verdict = parse_verdict(ctx.results["judge"])

        counterfactuals: list[CounterfactualBlock] = []
        if "counterfactual" in ctx.results and findings:
            counterfactuals = parse_counterfactuals(
                ctx.results["counterfactual"], total_findings=len(findings),
            )

        return FileReviewResult(
            path=fd.path,
            rag_docs=rag_docs,
            step_outputs=dict(ctx.results),
            inline_findings=findings,
            verdict=verdict,
            is_binary=fd.is_binary,
            is_deleted=fd.is_deleted,
            counterfactuals=counterfactuals,
        )

    def _verify_suggestions(
        self,
        file_result: "FileReviewResult",
        *,
        workdir: Path,
        verify_cmd: str,
        timeout_seconds: float,
    ) -> "FileReviewResult":
        """Run each finding's ``suggestion`` block in a sandbox and
        attach the verification result to the finding.

        Side-effect surface is fenced inside :mod:`reviewmind.sandbox`;
        this method just walks the findings and merges the results back
        into the per-file payload.
        """
        from reviewmind.sandbox import verify_suggestion
        from reviewmind.schemas import SuggestionVerification

        new_findings: list[InlineFinding] = []
        for f in file_result.inline_findings:
            if f.suggestion is None:
                new_findings.append(f)
                continue
            outcome = verify_suggestion(
                f,
                workdir=workdir,
                verify_cmd=verify_cmd,
                timeout_seconds=timeout_seconds,
            )
            verification = SuggestionVerification(
                status=outcome.status,
                verify_cmd=outcome.verify_cmd,
                duration_ms=outcome.duration_ms,
                reason=outcome.reason,
            )
            new_findings.append(f.model_copy(update={"verification": verification}))
            log.info(
                "verify_suggestions: %s:%d -> %s (%dms)",
                f.path, f.line, outcome.status, outcome.duration_ms,
            )
        return FileReviewResult(
            path=file_result.path,
            rag_docs=file_result.rag_docs,
            step_outputs=file_result.step_outputs,
            inline_findings=new_findings,
            verdict=file_result.verdict,
            is_binary=file_result.is_binary,
            is_deleted=file_result.is_deleted,
            counterfactuals=file_result.counterfactuals,
        )

    def _self_correct(
        self,
        fd: FileDiff,
        findings: list[InlineFinding],
        ctx: ReviewContext,
    ) -> list[InlineFinding]:
        """Second-pass noise filter — drop findings the model flags itself.

        One extra backend call per file. The model sees a numbered list of
        the surviving findings (after dismissed filter) and returns the
        indices it considers noise. We never drop everything: a malformed
        response yields the original list unchanged, on the principle that
        a wrongly-posted finding is recoverable but a silently-dropped one
        is not.
        """
        from codes.run.CoT_Prompts.finding_self_review import (
            FINDING_SELF_REVIEW_TEMPLATE,
        )

        prompt = FINDING_SELF_REVIEW_TEMPLATE.format(
            file_path=fd.path,
            numbered_findings=render_findings_block(findings),
            code_diff=fd.raw,
        )
        raw = self._backend.generate(prompt, max_new_tokens=self._max_new_tokens)
        ctx.results["self_review"] = raw

        drop = parse_drop_indices(raw, total=len(findings))
        if not drop:
            return findings
        kept = apply_self_review(findings, drop)
        log.info(
            "Self-review dropped %d/%d findings on %s",
            len(drop), len(findings), fd.path,
        )
        return kept

    def _generate_streaming(
        self, step_name: str, prompt: str, file_path: str | None
    ) -> str:
        """Drive ``backend.stream_generate`` and mirror chunks to the sink.

        Falls back to ``stderr`` when no explicit sink was passed. Returns
        the concatenated full text just like ``backend.generate``.
        """
        import sys

        sink = self._stream_sink or sys.stderr
        header = (
            f"\n[{step_name}"
            + (f" :: {file_path}" if file_path else "")
            + "]\n"
        )
        sink.write(header)
        chunks: list[str] = []
        for chunk in self._backend.stream_generate(
            prompt, max_new_tokens=self._max_new_tokens
        ):
            chunks.append(chunk)
            sink.write(chunk)
            flush = getattr(sink, "flush", None)
            if callable(flush):
                flush()
        sink.write("\n")
        return "".join(chunks)

    def _run_steps(
        self,
        ctx: ReviewContext,
        step_classes: tuple[type[ReviewStep], ...],
        output_dir: Path | None,
    ) -> None:
        if output_dir is not None:
            output_dir.mkdir(parents=True, exist_ok=True)
        for step_cls in step_classes:
            step: ReviewStep = step_cls()
            log.info("Running step: %s (file=%s)", step.name, ctx.file_path)
            prompt = step.build_prompt(ctx)
            if self._stream:
                output = self._generate_streaming(step.name, prompt, ctx.file_path)
            else:
                output = self._backend.generate(
                    prompt, max_new_tokens=self._max_new_tokens
                )
            ctx.results[step.name] = output
            if output_dir is not None:
                (output_dir / f"{step.name}_result.md").write_text(
                    output, encoding="utf-8"
                )


def _sanitize(path: str) -> str:
    return path.replace("/", "__").replace("\\", "__")


__all__ = ["CoTPipeline", "ReviewContext", "ReviewResult", "FileReviewResult"]

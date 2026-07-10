"""Step-execution engine + finding post-processing for the CoT pipeline.

Split out of :mod:`prthinker.pipeline` to keep that module under the
file-length limit. The methods here are mixed into
:class:`prthinker.pipeline.CoTPipeline` via :class:`PipelineExecutionMixin`;
they run entirely against ``self`` state set in ``CoTPipeline.__init__`` and
must not be called except as bound methods of a pipeline instance.
"""

from __future__ import annotations

import hashlib
import logging
import sys
import time
from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING

from prthinker.otel import operation_span
from prthinker.step_dag import DagNode, execute_detailed
from prthinker.self_review import (
    apply_self_review,
    parse_drop_indices,
    render_findings_block,
)

if TYPE_CHECKING:
    from prthinker.diff import FileDiff
    from prthinker.pipeline_types import FileReviewResult
    from prthinker.schemas import InlineFinding
    from prthinker.steps import ReviewContext, ReviewStep

# Keep the pipeline logger name so log records read identically to when
# these methods lived in prthinker.pipeline.
log = logging.getLogger("prthinker.pipeline")


class PipelineExecutionMixin:
    """Step scheduling, streaming, verification and self-correction methods."""

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

        Side-effect surface is fenced inside :mod:`prthinker.sandbox`;
        this method just walks the findings and merges the results back
        into the per-file payload.
        """
        from prthinker.sandbox import verify_suggestion
        from prthinker.schemas import SuggestionVerification

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
                f.path,
                f.line,
                outcome.status,
                outcome.duration_ms,
            )
        return replace(file_result, inline_findings=new_findings)

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
        from prthinker.prompts.finding_self_review import (
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
            len(drop),
            len(findings),
            fd.path,
        )
        return kept

    def _generate_streaming(
        self,
        step_name: str,
        prompt: str,
        file_path: str | None,
        *,
        max_new_tokens: int | None = None,
    ) -> str:
        """Drive ``backend.stream_generate`` and mirror chunks to the sink.

        Falls back to ``stderr`` when no explicit sink was passed. Returns
        the concatenated full text just like ``backend.generate``.
        """
        sink = self._stream_sink or sys.stderr
        header = f"\n[{step_name}" + (f" :: {file_path}" if file_path else "") + "]\n"
        sink.write(header)
        chunks: list[str] = []
        for chunk in self._backend.stream_generate(
            prompt, max_new_tokens=max_new_tokens or self._max_new_tokens
        ):
            chunks.append(chunk)
            sink.write(chunk)
            flush = getattr(sink, "flush", None)
            if callable(flush):
                flush()
        sink.write("\n")
        return "".join(chunks)

    def _execute_step(
        self,
        step_cls: type[ReviewStep],
        ctx: ReviewContext,
        output_dir: Path | None,
        *,
        stream: bool = False,
        record_trajectory: bool = False,
    ) -> str:
        """Run one step against ``ctx`` and return the capped output.

        Shared by the sequential loop and the DAG node runner: build the
        prompt, invoke the backend inside an ``invoke_agent`` span,
        persist the raw output to ``{step.name}_result.md`` when an
        output directory is set, and cap the in-pipeline copy. The caller
        decides where the capped result lands (``ctx.results`` for the
        sequential loop, the node result for the DAG).
        """
        step: ReviewStep = step_cls()
        prompt = step.build_prompt(ctx)
        # Reduced review depths cap generation so a runaway decode on a
        # small file cannot burn minutes of GPU time; None keeps the
        # pipeline-wide budget.
        budget = min(self._max_new_tokens, ctx.gen_budget or self._max_new_tokens)
        started = time.perf_counter()
        with operation_span(
            "invoke_agent",
            {"prthinker.step.name": step.name,
             "prthinker.file.path": ctx.file_path or ""},
        ):
            if stream:
                output = self._generate_streaming(
                    step.name, prompt, ctx.file_path, max_new_tokens=budget
                )
            else:
                output = self._backend.generate(
                    prompt,
                    max_new_tokens=budget,
                    cancel_event=self._cancel_event,
                )
        if record_trajectory:
            self._record_step_trajectory(step.name, prompt, ctx, started)
        if output_dir is not None:
            (output_dir / f"{step.name}_result.md").write_text(
                output, encoding="utf-8"
            )
        return self._cap_step_result(output)

    def _record_step_trajectory(
        self,
        step_name: str,
        prompt: str,
        ctx: ReviewContext,
        started: float,
    ) -> None:
        """Append the step's trajectory event when a sink is attached."""
        if not self._trajectory:
            return
        self._trajectory.record(
            "step",
            content=prompt,
            path=ctx.file_path,
            tool=step_name,
            status="ok",
            duration_ms=(time.perf_counter() - started) * 1000,
        )

    def _run_steps(
        self,
        ctx: ReviewContext,
        step_classes: tuple[type[ReviewStep], ...],
        output_dir: Path | None,
    ) -> None:
        if output_dir is not None:
            output_dir.mkdir(parents=True, exist_ok=True)
        if self._step_dependencies:
            self._run_steps_dag(ctx, step_classes, output_dir)
            return
        for step_cls in self._order_steps(step_classes):
            self._check_cancel()
            log.info("Running step: %s (file=%s)", step_cls.name, ctx.file_path)
            ctx.results[step_cls.name] = self._execute_step(
                step_cls,
                ctx,
                output_dir,
                stream=self._stream,
                record_trajectory=True,
            )

    def _step_config(self, step_name: str) -> dict:
        """Return a step's dependency config, normalising the raw tuple form."""
        raw = self._step_dependencies.get(step_name, ())
        return raw if isinstance(raw, dict) else {"depends_on": raw}

    def _step_depends_on(self, step_name: str) -> tuple[str, ...]:
        """Return the declared dependency step names for one step."""
        return tuple(self._step_config(step_name).get("depends_on", ()))

    def _make_step_runner(self, step_cls, ctx, output_dir):
        """Return the DAG node body that runs one step against a snapshot."""

        def run(snapshot, cls=step_cls):
            local = replace(ctx, results=dict(snapshot))
            return self._execute_step(cls, local, output_dir)

        return run

    def _make_dag_node(self, step_cls, ctx, output_dir) -> DagNode:
        """Build a typed DAG node for one step from its dependency config."""
        config = self._step_config(step_cls.name)
        required_result = str(config.get("when_result", ""))
        timeout = config.get("timeout_seconds")
        return DagNode(
            step_cls.name,
            self._make_step_runner(step_cls, ctx, output_dir),
            self._step_depends_on(step_cls.name),
            when=(lambda results, key=required_result: bool(results.get(key)))
            if required_result else None,
            retries=max(0, int(config.get("retries", 0))),
            timeout_seconds=float(timeout) if timeout is not None else None,
            cache_key=self._dag_cache_key(step_cls.name, ctx)
            if config.get("cache", False) else None,
        )

    def _dag_cache_key(self, name, ctx):
        """Return a cache-key function keyed by step name, diff and prior results."""
        return lambda results: hashlib.sha256(
            f"{name}:{ctx.code_diff}:{sorted(results)}".encode()
        ).hexdigest()

    def _run_steps_dag(self, ctx, step_classes, output_dir) -> None:
        """Execute explicitly configured independent steps through typed DAG."""
        names = {step.name for step in step_classes}
        nodes = [
            self._make_dag_node(step_cls, ctx, output_dir)
            for step_cls in step_classes
        ]
        execution = execute_detailed(
            nodes,
            initial=ctx.results,
            cache=self._dag_cache,
            max_workers=1 if self._stream else self._backend.max_concurrency(),
        )
        ctx.results.update(
            {key: value for key, value in execution.results.items()
             if key in names and value is not None}
        )

    def _order_steps(self, step_classes: tuple[type[ReviewStep], ...]):
        """Topologically order configured steps while preserving stable order."""
        if not self._step_dependencies:
            return step_classes
        by_name = {step.name: step for step in step_classes}
        unknown = {
            dep
            for name in self._step_dependencies
            for dep in self._step_depends_on(name)
        } - by_name.keys()
        if unknown:
            raise ValueError(f"unknown step dependencies: {sorted(unknown)}")
        return self._toposort_steps(step_classes)

    def _toposort_steps(self, step_classes: tuple[type[ReviewStep], ...]):
        """Return steps in dependency order, raising on a cyclic step DAG."""
        pending = list(step_classes)
        ordered: list[type[ReviewStep]] = []
        completed: set[str] = set()
        while pending:
            ready = [
                step for step in pending
                if set(self._step_depends_on(step.name)) <= completed
            ]
            if not ready:
                raise ValueError("cyclic step DAG")
            for step in ready:
                pending.remove(step)
                ordered.append(step)
                completed.add(step.name)
        return tuple(ordered)

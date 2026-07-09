"""Review step Registry.

Each step is a `ReviewStep` subclass that knows how to build its prompt from
the current `ReviewContext`. Steps self-register via `@register_step` so
adding a new one does not require editing the pipeline.

Built-in steps re-use the CoT prompt templates bundled at
`prthinker/prompts/` so the runner is self-contained and importable
without the project-specific `codes` tree. Those templates are a mirror
of the canonical corpus at `codes/run/CoT_Prompts/`; keep the two in
sync (see CLAUDE.md "Prompt Templates Are the Source of Truth").
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import ClassVar

from prthinker.prompts.code_smell_detector import CODE_SMELL_DETECTOR_TEMPLATE
from prthinker.prompts.counterfactual_review import COUNTERFACTUAL_REVIEW_TEMPLATE
from prthinker.prompts.first_code_review import FIRST_CODE_REVIEW_TEMPLATE
from prthinker.prompts.first_summary_prompt import FIRST_SUMMARY_TEMPLATE
from prthinker.prompts.global_rule import build_global_rule_template
from prthinker.prompts.inline_findings import INLINE_FINDINGS_TEMPLATE
from prthinker.prompts.judge_step import JUDGE_STEP_TEMPLATE
from prthinker.prompts.linter import LINTER_TEMPLATE
from prthinker.prompts.total_summary import TOTAL_SUMMARY_TEMPLATE
from prthinker.prompts.walkthrough import WALKTHROUGH_TEMPLATE


@dataclass
class ReviewContext:
    code_diff: str
    rag_docs: list[str]
    results: dict[str, str] = field(default_factory=dict)
    file_path: str | None = None
    max_findings: int = 10
    positive_examples_block: str = ""
    dialogue_block: str = ""
    provenance_block: str = ""
    # Cross-file context retrieved from the repository (empty unless the
    # pipeline was given a repo retriever); prepended to step prompts.
    repo_context_block: str = ""


class ReviewStep(ABC):
    """Template Method: subclasses provide `name` and `build_prompt`."""

    name: ClassVar[str] = ""

    @abstractmethod
    def build_prompt(self, ctx: ReviewContext) -> str:
        ...


_REGISTRY: list[type[ReviewStep]] = []


def register_step(cls: type[ReviewStep]) -> type[ReviewStep]:
    if not cls.name:
        raise ValueError(f"{cls.__name__}.name must be set")
    if any(existing.name == cls.name for existing in _REGISTRY):
        raise ValueError(f"Step {cls.name!r} already registered")
    _REGISTRY.append(cls)
    return cls


def registered_steps() -> tuple[type[ReviewStep], ...]:
    return tuple(_REGISTRY)


def resolve_steps(names: tuple[str, ...]) -> tuple[type[ReviewStep], ...]:
    """Return step classes matching `names` in the given order.

    Empty `names` returns all registered steps in declaration order.
    Raises ValueError on unknown names — fail fast.
    """
    if not names:
        return registered_steps()
    by_name = {cls.name: cls for cls in _REGISTRY}
    missing = [n for n in names if n not in by_name]
    if missing:
        known = ", ".join(sorted(by_name))
        raise ValueError(f"Unknown step(s): {missing}. Registered: {known}")
    return tuple(by_name[n] for n in names)


# ---------------------------------------------------------------------------
# Built-in steps — wrap existing CoT prompt templates.
# ---------------------------------------------------------------------------


def _prepend_repo_context(ctx: ReviewContext, prompt: str) -> str:
    """Prefix a step prompt with retrieved cross-file context, if any."""
    if ctx.repo_context_block:
        return f"{ctx.repo_context_block}\n\n{prompt}"
    return prompt


def _wrap(ctx: ReviewContext, prompt: str) -> str:
    body = build_global_rule_template(prompt=prompt, rag_rules=ctx.rag_docs)
    return _prepend_repo_context(ctx, body)


@register_step
class FirstSummaryStep(ReviewStep):
    name = "first_summary"

    def build_prompt(self, ctx: ReviewContext) -> str:
        return _wrap(
            ctx,
            FIRST_SUMMARY_TEMPLATE.format(code_diff=ctx.code_diff),
        )


@register_step
class FirstCodeReviewStep(ReviewStep):
    name = "first_code_review"

    def build_prompt(self, ctx: ReviewContext) -> str:
        return _wrap(
            ctx,
            FIRST_CODE_REVIEW_TEMPLATE.format(code_diff=ctx.code_diff),
        )


@register_step
class LinterStep(ReviewStep):
    name = "linter"

    def build_prompt(self, ctx: ReviewContext) -> str:
        return _wrap(
            ctx,
            LINTER_TEMPLATE.format(code_diff=ctx.code_diff),
        )


@register_step
class CodeSmellStep(ReviewStep):
    name = "code_smell"

    def build_prompt(self, ctx: ReviewContext) -> str:
        return _wrap(
            ctx,
            CODE_SMELL_DETECTOR_TEMPLATE.format(code_diff=ctx.code_diff),
        )


# Substituted for pruned analysis steps so the total-summary prompt can
# tell "intentionally skipped" apart from "empty output". The wording is
# referenced verbatim in TOTAL_SUMMARY_TEMPLATE — keep the two in sync.
SKIPPED_STEP_NOTE = "(step skipped at this review depth)"


@register_step
class TotalSummaryStep(ReviewStep):
    """Aggregates all prior step outputs. Must run last.

    Tolerates a partially-pruned chain (adaptive step planning): absent
    inputs are marked with :data:`SKIPPED_STEP_NOTE` so the model bases
    its conclusion on the evidence that exists. At least one input must
    be present — with nothing to aggregate the step is meaningless.
    """

    name = "total_summary"

    _REQUIRES: ClassVar[tuple[str, ...]] = (
        "first_code_review",
        "first_summary",
        "linter",
        "code_smell",
    )

    def build_prompt(self, ctx: ReviewContext) -> str:
        if not any(k in ctx.results for k in self._REQUIRES):
            raise ValueError(
                "total_summary requires at least one prior step result out of "
                f"{list(self._REQUIRES)} but none were run"
            )
        return _wrap(
            ctx,
            TOTAL_SUMMARY_TEMPLATE.format(
                first_code_review=ctx.results.get(
                    "first_code_review", SKIPPED_STEP_NOTE
                ),
                first_summary=ctx.results.get("first_summary", SKIPPED_STEP_NOTE),
                linter_result=ctx.results.get("linter", SKIPPED_STEP_NOTE),
                code_smell_result=ctx.results.get("code_smell", SKIPPED_STEP_NOTE),
                code_diff=ctx.code_diff,
            ),
        )


class InlineFindingsStep(ReviewStep):
    """Per-file step: emits JSON findings the runner parses into inline comments.

    Not auto-registered — it requires `ctx.file_path` to be set, so the
    per-file pipeline mode opts into it explicitly via `extra_steps`.
    """

    name = "inline_findings"

    def build_prompt(self, ctx: ReviewContext) -> str:
        if not ctx.file_path:
            raise ValueError("InlineFindingsStep requires ctx.file_path")
        # Skip the global-rule wrap so the output is more likely to be raw JSON.
        prompt = INLINE_FINDINGS_TEMPLATE.format(
            file_path=ctx.file_path,
            code_diff=ctx.code_diff,
            max_findings=ctx.max_findings,
            positive_examples=ctx.positive_examples_block,
            dialogue_block=ctx.dialogue_block,
            provenance_block=ctx.provenance_block,
        )
        return _prepend_repo_context(ctx, prompt)


class WalkthroughStep(ReviewStep):
    """Per-file step: a short narrative of what the change does and why.

    Orientation, not judgement — it produces the model-generated
    counterpart to the deterministic, commit-message-based PR overview, so
    a reviewer can read *what each file change means* before diving into
    the findings. Not auto-registered: the per-file pipeline opts in via
    the ``--walkthrough`` flag. It depends on nothing but the diff, so it
    can run with or without inline review.
    """

    name = "walkthrough"

    def build_prompt(self, ctx: ReviewContext) -> str:
        if not ctx.file_path:
            raise ValueError("WalkthroughStep requires ctx.file_path")
        return WALKTHROUGH_TEMPLATE.format(
            file_path=ctx.file_path,
            code_diff=ctx.code_diff,
        )


class CounterfactualStep(ReviewStep):
    """Per-file step: surface competing alternative implementations for
    findings that look like design choices.

    Runs after :class:`InlineFindingsStep` because it consumes the
    parsed findings list as its input. Not auto-registered: pipelines
    opt in explicitly via the ``--counterfactual`` flag.
    """

    name = "counterfactual"

    _REQUIRES: ClassVar[tuple[str, ...]] = ("inline_findings",)

    def build_prompt(self, ctx: ReviewContext) -> str:
        if not ctx.file_path:
            raise ValueError("CounterfactualStep requires ctx.file_path")
        missing = [k for k in self._REQUIRES if k not in ctx.results]
        if missing:
            raise ValueError(
                f"counterfactual step needs prior steps {missing} but they were not run"
            )
        findings_json = ctx.results.get("inline_findings", "[]").strip()
        return COUNTERFACTUAL_REVIEW_TEMPLATE.format(
            code_diff=ctx.code_diff,
            findings_block=findings_json,
        )


class JudgeStep(ReviewStep):
    """Self-assessment step — outputs a JSON ``JudgeVerdict``.

    Not auto-registered: it consumes the prior step results plus the
    parsed inline findings, so the per-file pipeline mode opts in
    explicitly via ``extra_steps`` only when ``--judge`` is set.
    """

    name = "judge"

    _REQUIRES: ClassVar[tuple[str, ...]] = ("total_summary",)

    def build_prompt(self, ctx: ReviewContext) -> str:
        if not ctx.file_path:
            raise ValueError("JudgeStep requires ctx.file_path")
        missing = [k for k in self._REQUIRES if k not in ctx.results]
        if missing:
            raise ValueError(
                f"judge step needs prior steps {missing} but they were not run"
            )
        inline_findings_json = ctx.results.get("inline_findings", "[]").strip()
        # Skip the global-rule wrap so the model is more likely to emit raw JSON.
        return JUDGE_STEP_TEMPLATE.format(
            file_path=ctx.file_path,
            total_summary=ctx.results["total_summary"],
            inline_findings_json=inline_findings_json,
            code_diff=ctx.code_diff,
        )


__all__ = [
    "ReviewContext",
    "ReviewStep",
    "InlineFindingsStep",
    "CounterfactualStep",
    "JudgeStep",
    "WalkthroughStep",
    "register_step",
    "registered_steps",
    "resolve_steps",
]

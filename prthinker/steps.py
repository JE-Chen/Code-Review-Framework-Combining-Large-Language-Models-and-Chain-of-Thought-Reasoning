"""Review step Registry.

Each step is a `ReviewStep` subclass that knows how to build its prompt from
the current `ReviewContext`. Steps self-register via `@register_step` so
adding a new one does not require editing the pipeline.

Built-in steps re-use the prompt templates already defined under
`codes/run/CoT_Prompts/` — they are the single source of truth.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import ClassVar


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

# Prompt-template imports live below the @register_step decorator so the
# registry exists before the step subclasses below try to register.
from codes.run.CoT_Prompts.code_smell_detector import CODE_SMELL_DETECTOR_TEMPLATE  # noqa: E402
from codes.run.CoT_Prompts.counterfactual_review import (  # noqa: E402
    COUNTERFACTUAL_REVIEW_TEMPLATE,
)
from codes.run.CoT_Prompts.first_code_review import FIRST_CODE_REVIEW_TEMPLATE  # noqa: E402
from codes.run.CoT_Prompts.first_summary_prompt import FIRST_SUMMARY_TEMPLATE  # noqa: E402
from codes.run.CoT_Prompts.global_rule import build_global_rule_template  # noqa: E402
from codes.run.CoT_Prompts.inline_findings import INLINE_FINDINGS_TEMPLATE  # noqa: E402
from codes.run.CoT_Prompts.judge_step import JUDGE_STEP_TEMPLATE  # noqa: E402
from codes.run.CoT_Prompts.linter import LINTER_TEMPLATE  # noqa: E402
from codes.run.CoT_Prompts.total_summary import TOTAL_SUMMARY_TEMPLATE  # noqa: E402


def _wrap(prompt: str, rag_docs: list[str]) -> str:
    return build_global_rule_template(prompt=prompt, rag_rules=rag_docs)


@register_step
class FirstSummaryStep(ReviewStep):
    name = "first_summary"

    def build_prompt(self, ctx: ReviewContext) -> str:
        return _wrap(
            FIRST_SUMMARY_TEMPLATE.format(code_diff=ctx.code_diff),
            ctx.rag_docs,
        )


@register_step
class FirstCodeReviewStep(ReviewStep):
    name = "first_code_review"

    def build_prompt(self, ctx: ReviewContext) -> str:
        return _wrap(
            FIRST_CODE_REVIEW_TEMPLATE.format(code_diff=ctx.code_diff),
            ctx.rag_docs,
        )


@register_step
class LinterStep(ReviewStep):
    name = "linter"

    def build_prompt(self, ctx: ReviewContext) -> str:
        return _wrap(
            LINTER_TEMPLATE.format(code_diff=ctx.code_diff),
            ctx.rag_docs,
        )


@register_step
class CodeSmellStep(ReviewStep):
    name = "code_smell"

    def build_prompt(self, ctx: ReviewContext) -> str:
        return _wrap(
            CODE_SMELL_DETECTOR_TEMPLATE.format(code_diff=ctx.code_diff),
            ctx.rag_docs,
        )


@register_step
class TotalSummaryStep(ReviewStep):
    """Aggregates all prior step outputs. Must run last."""

    name = "total_summary"

    _REQUIRES: ClassVar[tuple[str, ...]] = (
        "first_code_review",
        "first_summary",
        "linter",
        "code_smell",
    )

    def build_prompt(self, ctx: ReviewContext) -> str:
        missing = [k for k in self._REQUIRES if k not in ctx.results]
        if missing:
            raise ValueError(
                f"total_summary requires prior steps {missing} but they were not run"
            )
        return _wrap(
            TOTAL_SUMMARY_TEMPLATE.format(
                first_code_review=ctx.results["first_code_review"],
                first_summary=ctx.results["first_summary"],
                linter_result=ctx.results["linter"],
                code_smell_result=ctx.results["code_smell"],
                code_diff=ctx.code_diff,
            ),
            ctx.rag_docs,
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
        return INLINE_FINDINGS_TEMPLATE.format(
            file_path=ctx.file_path,
            code_diff=ctx.code_diff,
            max_findings=ctx.max_findings,
            positive_examples=ctx.positive_examples_block,
            dialogue_block=ctx.dialogue_block,
            provenance_block=ctx.provenance_block,
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
    "register_step",
    "registered_steps",
    "resolve_steps",
]

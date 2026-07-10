"""Value objects for the CoT pipeline — result and per-file option dataclasses.

Split out of :mod:`prthinker.pipeline` to keep that module under the
file-length limit. :mod:`prthinker.pipeline` re-exports the public
``ReviewResult`` / ``FileReviewResult`` / ``PerFileReviewOptions`` /
``ReviewCancelledError`` names from here, so callers and tests continue to
reach them through ``prthinker.pipeline``. This module holds only data
definitions; it must not import :mod:`prthinker.pipeline` (which would form a
cycle) — every non-schema reference below stays a lazy string annotation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from prthinker.schemas import (
    ApiDriftFinding,
    CounterfactualBlock,
    DependencyUpgradeFinding,
    DiffEntropySummary,
    InlineFinding,
    JudgeVerdict,
    PersonaConflict,
    PersonaReview,
    PRClassification,
)

if TYPE_CHECKING:
    from prthinker.review_cache import ReviewCache
    from prthinker.steps import ReviewStep


@dataclass
class ReviewResult:
    code_diff: str
    rag_docs: list[str]
    step_outputs: dict[str, str] = field(default_factory=dict)
    inline_findings: list[InlineFinding] = field(default_factory=list)
    per_file: list["FileReviewResult"] = field(default_factory=list)
    counterfactuals: list[CounterfactualBlock] = field(default_factory=list)
    api_drift: list[ApiDriftFinding] = field(default_factory=list)
    pr_classification: PRClassification | None = None
    dep_upgrades: list[DependencyUpgradeFinding] = field(default_factory=list)
    persona_reviews: list[PersonaReview] = field(default_factory=list)
    persona_conflicts: list[PersonaConflict] = field(default_factory=list)
    diff_entropy: DiffEntropySummary | None = None

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
        # Reduced-depth plans substitute the compact single-call review
        # for the analysis chain; renderers read it through the same
        # property so every report keeps working unchanged.
        return self.step_outputs.get("total_summary") or self.step_outputs.get(
            "compact_review"
        )


class ReviewCancelledError(Exception):
    """Raised when a CoT review is interrupted via ``cancel_event``.

    The pipeline checks the event between steps; once it is set, the
    current step finishes (since ``model.generate`` is uninterruptible
    in C) and the loop bails out before starting the next.
    """


@dataclass(frozen=True)
class _ClassifyOutcome:
    """Optional PR-type classification plus the budget-adjusted knobs."""

    classification: "PRClassification | None"
    inline_review: bool
    max_findings_per_file: int
    dialogue_block: str


@dataclass(frozen=True)
class _FileRunFlags:
    """Optional per-file behaviour toggles passed to ``_run_one_file``."""

    self_correct: bool = False
    dialogue_block: str = ""
    provenance: bool = False
    reproducibility_check: bool = False


@dataclass(frozen=True)
class _PerFileOptions:
    """Per-file review knobs threaded through the per-file loop."""

    all_steps: tuple[type["ReviewStep"], ...]
    max_findings_per_file: int
    output_dir: Path | None
    self_correct: bool
    dialogue_block: str
    provenance: bool
    reproducibility_check: bool
    skip_binary: bool
    inline_review: bool
    review_cache: "ReviewCache | None"
    cache_repo: str
    cache_pr_number: int
    risk_by_path: dict
    verify_suggestions: bool
    verify_workdir: Path | None
    verify_cmd: str
    verify_timeout: float
    parallelism: int
    step_plan: str = "full"


@dataclass
class _AggregatedFiles:
    """Per-file results accumulated across one run of the per-file loop."""

    per_file_results: list["FileReviewResult"] = field(default_factory=list)
    inline_findings: list[InlineFinding] = field(default_factory=list)
    counterfactuals: list[CounterfactualBlock] = field(default_factory=list)
    step_outputs: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class _AggregateExtras:
    """Cross-file extra-step outputs aggregated after the per-file loop."""

    dep_upgrades: list[DependencyUpgradeFinding] = field(default_factory=list)
    persona_reviews: list[PersonaReview] = field(default_factory=list)
    persona_conflicts: list[PersonaConflict] = field(default_factory=list)
    api_drift: list[ApiDriftFinding] = field(default_factory=list)


@dataclass(frozen=True)
class PerFileReviewOptions:
    """Cohesive optional knobs for :meth:`CoTPipeline.run_per_file`.

    Groups every per-file toggle into one immutable value object so the
    public entry point keeps a small, stable signature. Defaults mirror the
    historical keyword defaults, so an empty ``PerFileReviewOptions()`` runs
    the base step sweep with no extras enabled.
    """

    inline_review: bool = False
    judge: bool = False
    self_correct: bool = False
    counterfactual: bool = False
    walkthrough: bool = False
    provenance: bool = False
    api_consistency_check: bool = False
    max_findings_per_file: int = 10
    skip_binary: bool = True
    output_dir: Path | None = None
    dialogue_block: str = ""
    review_cache: "ReviewCache | None" = None
    cache_repo: str = ""
    cache_pr_number: int = 0
    verify_suggestions: bool = False
    verify_workdir: Path | None = None
    verify_cmd: str = ""
    verify_timeout: float = 60.0
    pr_classify: bool = False
    pr_title: str = ""
    pr_body: str = ""
    reproducibility_check: bool = False
    dep_upgrade_check: bool = False
    persona_set: tuple[str, ...] = ()
    risk_weighted: bool = False
    risk_workdir: Path | None = None
    diff_entropy_check: bool = False
    review_modes: tuple[str, ...] = ()
    on_file_done: "object | None" = None
    parallelism: int = 1
    # "full" runs every configured step on every file; "adaptive" scales
    # the chain per file via prthinker.step_planner.plan_steps.
    step_plan: str = "full"

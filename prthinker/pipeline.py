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

from prthinker import (
    api_consistency,
    dep_upgrade,
    diff_entropy,
    personas,
    pr_classifier,
    risk_score,
)
from prthinker.accepted import AcceptedExamplesRetriever, format_examples_block
from prthinker.review_modes import run_review_modes
from prthinker.backends.base import InferenceBackend
from prthinker.counterfactual import parse_counterfactuals
from prthinker.diff import FileDiff, parse_unified_diff
from prthinker.dismissed import DismissedFilter
from prthinker.findings import build_provenance_block, parse_inline_findings
from prthinker.judge import parse_verdict
from prthinker.rag import RAGRetriever
from prthinker.review_cache import CacheKey, ReviewCache
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
from prthinker.self_review import (
    apply_self_review,
    parse_drop_indices,
    render_findings_block,
)
from prthinker.steps import (
    CounterfactualStep,
    InlineFindingsStep,
    JudgeStep,
    ReviewContext,
    ReviewStep,
    WalkthroughStep,
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
        return self.step_outputs.get("total_summary")


class ReviewCancelledError(Exception):
    """Raised when a CoT review is interrupted via ``cancel_event``.

    The pipeline checks the event between steps; once it is set, the
    current step finishes (since ``model.generate`` is uninterruptible
    in C) and the loop bails out before starting the next.
    """


def _invoke_on_file_done(
    on_file_done: "object | None", file_result: "FileReviewResult"
) -> None:
    """Call the per-file-done hook, swallowing failures so persistence
    issues never abort the pipeline.
    """
    if on_file_done is None:
        return
    try:
        on_file_done(file_result)  # type: ignore[misc]
    except Exception as exc:  # noqa: BLE001 — hook must never break the run
        log.warning(
            "on_file_done hook failed for %s (ignored): %s",
            file_result.path, exc,
        )


# Char-level cap applied to a step's output BEFORE it is read by the
# next step's build_prompt. The CoT pipeline's final ``total_summary``
# step concatenates every prior step's output into one prompt; with the
# default ``max_new_tokens=32768`` each prior step can emit ~120 KB, so
# the final prompt grows to hundreds of thousands of tokens and triggers
# OOM in attention (~300 GiB for 50K tokens × 64 heads). 6000 chars is
# roughly 1500 tokens, leaving a comfortable budget for the system
# prompt + RAG docs + final generation. Tune via the
# ``PRTHINKER_MAX_STEP_RESULT_CHARS`` env var (server side).
_DEFAULT_MAX_STEP_RESULT_CHARS = 6000


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

    all_steps: tuple[type[ReviewStep], ...]
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
        cancel_event: "object | None" = None,
        max_step_result_chars: int = _DEFAULT_MAX_STEP_RESULT_CHARS,
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
        # threading.Event-like; checked between steps so server-side
        # cancel (client disconnect, idle-poll sweep) preempts at the
        # next step boundary instead of running to completion.
        self._cancel_event = cancel_event
        # See _DEFAULT_MAX_STEP_RESULT_CHARS — 0 disables the cap.
        self._max_step_result_chars = max(0, int(max_step_result_chars))

    def _check_cancel(self) -> None:
        if self._cancel_event is not None and self._cancel_event.is_set():
            raise ReviewCancelledError("Review cancelled by client")

    def _cap_step_result(self, output: str) -> str:
        """Char-truncate a step's output before downstream steps read it.

        See ``_DEFAULT_MAX_STEP_RESULT_CHARS`` for the rationale.
        Full text still hits disk via ``--output-dir`` and is returned
        in the API response; only the in-pipeline ``ctx.results`` copy
        is truncated.
        """
        cap = self._max_step_result_chars
        if cap <= 0 or len(output) <= cap:
            return output
        return output[:cap] + "\n\n... [truncated]\n"

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
        options: "PerFileReviewOptions | None" = None,
    ) -> ReviewResult:
        """Run the full step sequence once per file in the diff.

        When ``options.inline_review`` is True, append an
        ``InlineFindingsStep`` to each file's run and aggregate the parsed
        findings into the result.
        """
        opts = options or PerFileReviewOptions()
        file_diffs = parse_unified_diff(diff_text)
        if not file_diffs:
            log.warning("Diff had no parseable files")
            return ReviewResult(code_diff=diff_text, rag_docs=[])

        outcome = self._classify_outcome(diff_text, opts)
        per_file_opts = self._build_per_file_opts(file_diffs, opts, outcome)
        agg = self._review_each_file(file_diffs, per_file_opts, opts.on_file_done)

        extras = self._run_aggregate_extras(
            diff_text, file_diffs, opts, agg.step_outputs,
        )
        return ReviewResult(
            code_diff=diff_text,
            rag_docs=[],
            step_outputs=agg.step_outputs,
            inline_findings=agg.inline_findings,
            per_file=agg.per_file_results,
            counterfactuals=agg.counterfactuals,
            api_drift=extras.api_drift,
            pr_classification=outcome.classification,
            dep_upgrades=extras.dep_upgrades,
            persona_reviews=extras.persona_reviews,
            persona_conflicts=extras.persona_conflicts,
            diff_entropy=(
                self._compute_entropy_summary(file_diffs)
                if opts.diff_entropy_check else None
            ),
        )

    # ---------- internals ---------------------------------------------------

    def _classify_outcome(
        self, diff_text: str, opts: "PerFileReviewOptions",
    ) -> _ClassifyOutcome:
        """Classify the PR (when enabled) or echo the caller's knobs back."""
        if opts.pr_classify:
            return self._classify_pr(
                diff_text, opts.pr_title, opts.pr_body,
                opts.inline_review, opts.max_findings_per_file,
                opts.dialogue_block,
            )
        return _ClassifyOutcome(
            None, opts.inline_review, opts.max_findings_per_file,
            opts.dialogue_block,
        )

    def _build_per_file_opts(
        self,
        file_diffs: list[FileDiff],
        opts: "PerFileReviewOptions",
        outcome: _ClassifyOutcome,
    ) -> _PerFileOptions:
        """Fold the caller options and classifier outcome into the loop knobs."""
        risk_by_path = (
            self._compute_risk_by_path(file_diffs, opts.risk_workdir)
            if opts.risk_weighted and opts.risk_workdir is not None
            else {}
        )
        return _PerFileOptions(
            all_steps=self._build_step_sequence(
                outcome.inline_review, opts.counterfactual, opts.judge,
                opts.walkthrough,
            ),
            max_findings_per_file=outcome.max_findings_per_file,
            output_dir=opts.output_dir,
            self_correct=opts.self_correct,
            dialogue_block=outcome.dialogue_block,
            provenance=opts.provenance,
            reproducibility_check=opts.reproducibility_check,
            skip_binary=opts.skip_binary,
            inline_review=outcome.inline_review,
            review_cache=opts.review_cache,
            cache_repo=opts.cache_repo,
            cache_pr_number=opts.cache_pr_number,
            risk_by_path=risk_by_path,
            verify_suggestions=opts.verify_suggestions,
            verify_workdir=opts.verify_workdir,
            verify_cmd=opts.verify_cmd,
            verify_timeout=opts.verify_timeout,
        )

    def _run_aggregate_extras(
        self,
        diff_text: str,
        file_diffs: list[FileDiff],
        opts: "PerFileReviewOptions",
        aggregated_steps: dict[str, str],
    ) -> "_AggregateExtras":
        """Run the cross-file extra steps (dep / persona / api / review modes)."""
        dep_upgrades = (
            self._run_dep_upgrades(file_diffs, aggregated_steps)
            if opts.dep_upgrade_check else []
        )
        persona_reviews, persona_conflicts = (
            self._run_personas(opts.persona_set, diff_text, aggregated_steps)
            if opts.persona_set else ([], [])
        )
        api_drift = (
            self._run_api_consistency(file_diffs, aggregated_steps)
            if opts.api_consistency_check else []
        )
        if opts.review_modes:
            aggregated_steps.update(
                run_review_modes(
                    self._backend, diff_text, opts.review_modes,
                    self._max_new_tokens,
                )
            )
        return _AggregateExtras(
            dep_upgrades=dep_upgrades,
            persona_reviews=persona_reviews,
            persona_conflicts=persona_conflicts,
            api_drift=api_drift,
        )

    def _review_each_file(
        self,
        file_diffs: list[FileDiff],
        opts: _PerFileOptions,
        on_file_done: "object | None",
    ) -> _AggregatedFiles:
        """Review every file in the diff and accumulate the aggregated state."""
        agg = _AggregatedFiles()
        for fd in file_diffs:
            fr = self._review_single_file(fd, opts)
            agg.per_file_results.append(fr)
            agg.inline_findings.extend(fr.inline_findings)
            agg.counterfactuals.extend(fr.counterfactuals)
            for name, output in fr.step_outputs.items():
                # Namespace each per-file output for the consolidated comment.
                agg.step_outputs[f"{fd.path}::{name}"] = output
            _invoke_on_file_done(on_file_done, fr)
        return agg

    def _classify_pr(
        self,
        diff_text: str,
        pr_title: str,
        pr_body: str,
        inline_review: bool,
        max_findings_per_file: int,
        dialogue_block: str,
    ) -> _ClassifyOutcome:
        """Classify the PR type and fold the classifier's budget into the knobs."""
        log.info("Classifying PR type")
        classify_prompt = pr_classifier.build_prompt(
            diff_text=diff_text, title=pr_title, body=pr_body,
        )
        raw_classify = self._backend.generate(
            classify_prompt, max_new_tokens=self._max_new_tokens,
        )
        parsed = pr_classifier.parse_classification(raw_classify)
        budget = pr_classifier.budget_for(parsed.pr_type)
        log.info(
            "PR classified as %s -> inline=%s, max_findings=%d",
            parsed.pr_type.value, budget.run_inline_findings,
            budget.max_findings_per_file,
        )
        # Override caller knobs with the classifier's budget; caller can
        # still pass --no-pr-classify to bypass entirely.
        if budget.max_findings_per_file > 0:
            max_findings_per_file = budget.max_findings_per_file
        if budget.focus_hint:
            dialogue_block = (dialogue_block + "\n\n" + budget.focus_hint).strip()
        return _ClassifyOutcome(
            classification=PRClassification(
                pr_type=parsed.pr_type.value, reason=parsed.reason,
            ),
            inline_review=inline_review and budget.run_inline_findings,
            max_findings_per_file=max_findings_per_file,
            dialogue_block=dialogue_block,
        )

    def _build_step_sequence(
        self, inline_review: bool, counterfactual: bool, judge: bool,
        walkthrough: bool = False,
    ) -> tuple[type[ReviewStep], ...]:
        """Append the optional walkthrough / inline / counterfactual / judge steps."""
        extra: tuple[type[ReviewStep], ...] = ()
        if walkthrough:
            extra += (WalkthroughStep,)
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
        return self._step_classes + extra

    def _compute_entropy_summary(
        self, file_diffs: list[FileDiff],
    ) -> DiffEntropySummary:
        """Compute the diff-entropy ("diff bomb") summary for the PR."""
        e = diff_entropy.compute_entropy(file_diffs)
        log.info(
            "diff_entropy: %d file(s) +%d/-%d score=%.2f verdict=%s",
            e.file_count, e.added_lines, e.removed_lines, e.score, e.verdict,
        )
        return DiffEntropySummary(
            file_count=e.file_count,
            added_lines=e.added_lines,
            removed_lines=e.removed_lines,
            dispersion_entropy=e.dispersion_entropy,
            score=e.score,
            verdict=e.verdict,
        )

    def _compute_risk_by_path(
        self, file_diffs: list[FileDiff], risk_workdir: Path,
    ) -> dict[str, risk_score.RiskScore]:
        """Score reviewable files by change risk, keyed by path."""
        paths = [
            fd.path for fd in file_diffs if not fd.is_binary and not fd.is_deleted
        ]
        scores = risk_score.compute_risk_scores(paths, workdir=risk_workdir)
        log.info(
            "risk_score: computed for %d file(s); top: %s",
            len(scores),
            [(s.path, round(s.score, 2))
             for s in sorted(scores, key=lambda x: -x.score)[:3]],
        )
        return {s.path: s for s in scores}

    def _cache_key_for(
        self, fd: FileDiff, opts: _PerFileOptions,
    ) -> "CacheKey | None":
        """Differential-review cache key for a file, or None if not cacheable."""
        if opts.review_cache is None or opts.cache_pr_number <= 0 or not opts.inline_review:
            return None
        return CacheKey(
            pr_number=opts.cache_pr_number,
            repo=opts.cache_repo,
            file_path=fd.path,
            hunk_sha256=fd.content_sha256(),
        )

    def _effective_max(self, fd: FileDiff, opts: _PerFileOptions) -> int:
        """Risk-weighted per-file findings budget."""
        if fd.path not in opts.risk_by_path:
            return opts.max_findings_per_file
        budget = risk_score.budget_for_file(
            opts.risk_by_path[fd.path].score,
            base_budget=opts.max_findings_per_file,
        )
        log.debug(
            "risk_score: %s score=%.2f budget=%d",
            fd.path, opts.risk_by_path[fd.path].score, budget,
        )
        return budget

    def _skipped_file_result(self, fd: FileDiff) -> FileReviewResult:
        """Marked, finding-less result for a binary/deleted skipped file."""
        reason = "binary" if fd.is_binary else "deleted"
        log.info("Recording %s file %s as skipped", reason, fd.path)
        return FileReviewResult(
            path=fd.path, rag_docs=[], step_outputs={}, inline_findings=[],
            is_binary=fd.is_binary, is_deleted=fd.is_deleted,
        )

    def _cached_file_result(
        self, fd: FileDiff, cache_key: "CacheKey", opts: _PerFileOptions,
    ) -> "FileReviewResult | None":
        """Differential-review cache hit for a file, or None on a miss."""
        cached = opts.review_cache.get(cache_key)
        if cached is None:
            return None
        log.info(
            "Differential review: reusing %d cached finding(s) for %s",
            len(cached), fd.path,
        )
        return FileReviewResult(
            path=fd.path, rag_docs=[], step_outputs={},
            inline_findings=cached,
            is_binary=fd.is_binary, is_deleted=fd.is_deleted,
        )

    def _run_and_cache_file(
        self, fd: FileDiff, cache_key: "CacheKey | None", opts: _PerFileOptions,
    ) -> FileReviewResult:
        """Run the steps for a file, persist to cache, then verify suggestions."""
        file_out_dir = opts.output_dir / _sanitize(fd.path) if opts.output_dir else None
        file_result = self._run_one_file(
            fd,
            opts.all_steps,
            max_findings_per_file=self._effective_max(fd, opts),
            output_dir=file_out_dir,
            flags=_FileRunFlags(
                self_correct=opts.self_correct,
                dialogue_block=opts.dialogue_block,
                provenance=opts.provenance,
                reproducibility_check=opts.reproducibility_check,
            ),
        )
        if cache_key is not None:
            opts.review_cache.put(
                cache_key, file_result.inline_findings,
                backend=self._backend.backend_kind(),
                model=self._backend.model_name(),
            )
        return self._maybe_verify(file_result, opts)

    def _maybe_verify(
        self, file_result: FileReviewResult, opts: _PerFileOptions,
    ) -> FileReviewResult:
        """Verify suggestions in a sandbox when verification is configured."""
        verify_enabled = (
            opts.verify_suggestions
            and opts.verify_workdir is not None
            and bool(opts.verify_cmd)
        )
        if not verify_enabled:
            return file_result
        return self._verify_suggestions(
            file_result,
            workdir=opts.verify_workdir,
            verify_cmd=opts.verify_cmd,
            timeout_seconds=opts.verify_timeout,
        )

    def _review_single_file(
        self, fd: FileDiff, opts: _PerFileOptions,
    ) -> FileReviewResult:
        """Review one file: skip binary/deleted, reuse cache, else run steps.

        Binary / deleted files still yield a marked, finding-less result so
        every touched file appears in the summary (an absent file reads as
        "never looked at").
        """
        if (opts.skip_binary and fd.is_binary) or fd.is_deleted:
            return self._skipped_file_result(fd)

        cache_key = self._cache_key_for(fd, opts)
        if cache_key is not None:
            cached = self._cached_file_result(fd, cache_key, opts)
            if cached is not None:
                return cached

        return self._run_and_cache_file(fd, cache_key, opts)

    def _run_dep_upgrades(
        self,
        file_diffs: list[FileDiff],
        aggregated_steps: dict[str, str],
    ) -> list[DependencyUpgradeFinding]:
        """Run the dependency-upgrade impact step, recording raw outputs."""
        dep_upgrades: list[DependencyUpgradeFinding] = []
        for up in dep_upgrade.detect_upgrades(file_diffs):
            log.info(
                "dep-upgrade: %s %s %s -> %s",
                up.ecosystem, up.package, up.old_version, up.new_version,
            )
            prompt = dep_upgrade.build_prompt(up, file_diffs)
            raw = self._backend.generate(
                prompt, max_new_tokens=self._max_new_tokens,
            )
            aggregated_steps[f"dep_upgrade::{up.package}::{up.new_version}"] = raw
            dep_upgrades.extend(dep_upgrade.parse_impact(raw, upgrade=up))
        return dep_upgrades

    def _run_personas(
        self,
        persona_set: tuple[str, ...],
        diff_text: str,
        aggregated_steps: dict[str, str],
    ) -> tuple[list[PersonaReview], list[PersonaConflict]]:
        """Run the selected reviewer personas and surface their conflicts."""
        selected = self._resolve_personas(persona_set)
        log.info("personas: running %s", [p.value for p in selected])
        persona_outputs: dict[personas.Persona, str] = {}
        reviews: list[PersonaReview] = []
        for p in selected:
            parts = personas.build_persona_prompt(p, diff_text=diff_text)
            raw = self._backend.generate(
                parts.prompt, max_new_tokens=self._max_new_tokens,
            )
            persona_outputs[p] = raw
            aggregated_steps[f"persona::{p.value}"] = raw
            reviews.append(PersonaReview(persona=p.value, output=raw))
        conflicts: list[PersonaConflict] = []
        if len(selected) >= 2:
            conflict_prompt = personas.build_conflict_prompt(persona_outputs)
            conflict_raw = self._backend.generate(
                conflict_prompt, max_new_tokens=self._max_new_tokens,
            )
            aggregated_steps["persona::conflicts"] = conflict_raw
            conflicts = personas.parse_conflicts(
                conflict_raw, valid_personas=set(selected),
            )
        return reviews, conflicts

    def _run_api_consistency(
        self,
        file_diffs: list[FileDiff],
        aggregated_steps: dict[str, str],
    ) -> list[ApiDriftFinding]:
        """Run the cross-language API-drift step on mixed-language diffs."""
        if not api_consistency.is_mixed_language(file_diffs):
            return []
        log.info("Mixed-language PR detected → running api-consistency step")
        prompt = api_consistency.build_prompt(file_diffs)
        raw = self._backend.generate(prompt, max_new_tokens=self._max_new_tokens)
        aggregated_steps["api_consistency"] = raw
        return api_consistency.parse_drift_findings(
            raw, allowed_paths={fd.path for fd in file_diffs},
        )

    def _accepted_examples(self, fd: FileDiff) -> tuple[int, str]:
        """Retrieve positive examples for a file; return (count, block)."""
        if self._accepted_retriever is None:
            return 0, ""
        examples = list(self._accepted_retriever.top_k(fd.raw, path=fd.path))
        return len(examples), format_examples_block(examples)

    def _parse_findings(
        self,
        raw: str,
        fd: FileDiff,
        rag_docs: list[str],
        n_accepted_examples: int,
        provenance: bool,
    ) -> list[InlineFinding]:
        """Parse a raw inline-findings response with provenance bookkeeping."""
        return parse_inline_findings(
            raw,
            path=fd.path,
            allowed_lines=fd.commentable_lines(),
            n_rag_rules=len(rag_docs) if provenance else 0,
            n_accepted_examples=n_accepted_examples if provenance else 0,
        )

    def _reproducibility_label(
        self,
        findings: list[InlineFinding],
        ctx: ReviewContext,
        fd: FileDiff,
        rag_docs: list[str],
        n_accepted_examples: int,
        provenance: bool,
    ) -> list[InlineFinding]:
        """Re-query the inline step once and label findings by agreement."""
        from reviewmind import reproducibility

        # Rebuild the same prompt and re-query the model. With
        # non-deterministic backends we get a second sample; with
        # temperature=0 backends the two passes agree and everything is
        # labelled "stable" — also the right answer.
        inline_prompt = InlineFindingsStep().build_prompt(ctx)
        second_raw = self._backend.generate(
            inline_prompt, max_new_tokens=self._max_new_tokens,
        )
        second = self._parse_findings(
            second_raw, fd, rag_docs, n_accepted_examples, provenance,
        )
        return reproducibility.label_findings(findings, second)

    def _collect_findings(
        self,
        fd: FileDiff,
        ctx: ReviewContext,
        rag_docs: list[str],
        n_accepted_examples: int,
        *,
        provenance: bool,
        reproducibility_check: bool,
        self_correct: bool,
    ) -> list[InlineFinding]:
        """Parse, reproducibility-label, dismiss-filter and self-correct findings."""
        if "inline_findings" not in ctx.results:
            return []
        findings = self._parse_findings(
            ctx.results["inline_findings"], fd, rag_docs,
            n_accepted_examples, provenance,
        )
        if reproducibility_check:
            findings = self._reproducibility_label(
                findings, ctx, fd, rag_docs, n_accepted_examples, provenance,
            )
        if self._dismissed_filter is not None and findings:
            findings = self._dismissed_filter.filter(findings)
        if self_correct and findings:
            # Stash the self-review raw output for traceability; the
            # ``self_review`` step output is already inside ``ctx.results``.
            findings = self._self_correct(fd, findings, ctx)
        return findings

    def _run_one_file(
        self,
        fd: FileDiff,
        step_classes: tuple[type[ReviewStep], ...],
        *,
        max_findings_per_file: int,
        output_dir: Path | None,
        flags: "_FileRunFlags | None" = None,
    ) -> FileReviewResult:
        flags = flags or _FileRunFlags()
        rag_docs = self._merge_rules(self._retriever.retrieve(fd.raw))
        n_accepted_examples, positive_examples_block = self._accepted_examples(fd)

        provenance_block = ""
        if flags.provenance:
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
            dialogue_block=flags.dialogue_block,
            provenance_block=provenance_block,
        )
        self._run_steps(ctx, step_classes, output_dir)

        findings = self._collect_findings(
            fd, ctx, rag_docs, n_accepted_examples,
            provenance=flags.provenance,
            reproducibility_check=flags.reproducibility_check,
            self_correct=flags.self_correct,
        )

        verdict, counterfactuals = self._parse_judge_and_counterfactuals(ctx, findings)

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

    @staticmethod
    def _parse_judge_and_counterfactuals(
        ctx: ReviewContext, findings: list,
    ) -> "tuple[JudgeVerdict | None, list[CounterfactualBlock]]":
        """Parse the judge verdict and counterfactual blocks from step results."""
        verdict: JudgeVerdict | None = None
        if "judge" in ctx.results:
            verdict = parse_verdict(ctx.results["judge"])

        counterfactuals: list[CounterfactualBlock] = []
        if "counterfactual" in ctx.results and findings:
            counterfactuals = parse_counterfactuals(
                ctx.results["counterfactual"], total_findings=len(findings),
            )
        return verdict, counterfactuals

    def _resolve_personas(
        self, persona_set: tuple[str, ...],
    ) -> list["personas.Persona"]:
        """Translate user-supplied persona names into the enum.

        ``("all",)`` expands to every persona; unknown names raise
        ``ValueError`` so a typo doesn't silently cost a backend call.
        """
        if not persona_set:
            return []
        if len(persona_set) == 1 and persona_set[0].lower() == "all":
            return list(personas.Persona)
        by_value = {p.value: p for p in personas.Persona}
        out: list[personas.Persona] = []
        for raw in persona_set:
            key = raw.strip().lower()
            if key not in by_value:
                raise ValueError(
                    f"Unknown persona {raw!r}. "
                    f"Known: {sorted(by_value)}"
                )
            out.append(by_value[key])
        return out

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
            self._check_cancel()
            step: ReviewStep = step_cls()
            log.info("Running step: %s (file=%s)", step.name, ctx.file_path)
            prompt = step.build_prompt(ctx)
            if self._stream:
                output = self._generate_streaming(step.name, prompt, ctx.file_path)
            else:
                output = self._backend.generate(
                    prompt,
                    max_new_tokens=self._max_new_tokens,
                    cancel_event=self._cancel_event,
                )
            ctx.results[step.name] = self._cap_step_result(output)
            if output_dir is not None:
                (output_dir / f"{step.name}_result.md").write_text(
                    output, encoding="utf-8"
                )


def _sanitize(path: str) -> str:
    return path.replace("/", "__").replace("\\", "__")


__all__ = [
    "CoTPipeline",
    "ReviewContext",
    "ReviewResult",
    "FileReviewResult",
    "PerFileReviewOptions",
]

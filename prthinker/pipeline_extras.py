"""Cross-file / aggregate extra steps for the CoT pipeline.

Split out of :mod:`prthinker.pipeline` to keep that module under the
file-length limit. The methods here are mixed into
:class:`prthinker.pipeline.CoTPipeline` via
:class:`PipelineAggregateExtrasMixin`; they run entirely against ``self``
state set in ``CoTPipeline.__init__`` and must not be called except as
bound methods of a pipeline instance.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from prthinker import (
    api_consistency,
    dep_upgrade,
    diff_entropy,
    personas,
    pr_classifier,
)
from prthinker.pipeline_types import _AggregateExtras, _ClassifyOutcome
from prthinker.review_modes import run_review_modes
from prthinker.schemas import (
    ApiDriftFinding,
    DependencyUpgradeFinding,
    DiffEntropySummary,
    PersonaConflict,
    PersonaReview,
    PRClassification,
)

if TYPE_CHECKING:
    from prthinker.diff import FileDiff
    from prthinker.pipeline_types import PerFileReviewOptions

# Keep the pipeline logger name so log records read identically to when
# these methods lived in prthinker.pipeline.
log = logging.getLogger("prthinker.pipeline")


class PipelineAggregateExtrasMixin:
    """PR classification, diff entropy and cross-file extra-step methods."""

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
            if opts.dep_upgrade_check
            else []
        )
        persona_reviews, persona_conflicts = (
            self._run_personas(opts.persona_set, diff_text, aggregated_steps)
            if opts.persona_set
            else ([], [])
        )
        api_drift = (
            self._run_api_consistency(file_diffs, aggregated_steps)
            if opts.api_consistency_check
            else []
        )
        if opts.review_modes:
            aggregated_steps.update(
                run_review_modes(
                    self._backend,
                    diff_text,
                    opts.review_modes,
                    self._max_new_tokens,
                )
            )
        return _AggregateExtras(
            dep_upgrades=dep_upgrades,
            persona_reviews=persona_reviews,
            persona_conflicts=persona_conflicts,
            api_drift=api_drift,
        )

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
            diff_text=diff_text,
            title=pr_title,
            body=pr_body,
        )
        raw_classify = self._backend.generate(
            classify_prompt,
            max_new_tokens=self._max_new_tokens,
        )
        parsed = pr_classifier.parse_classification(raw_classify)
        budget = pr_classifier.budget_for(parsed.pr_type)
        log.info(
            "PR classified as %s -> inline=%s, max_findings=%d",
            parsed.pr_type.value,
            budget.run_inline_findings,
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
                pr_type=parsed.pr_type.value,
                reason=parsed.reason,
            ),
            inline_review=inline_review and budget.run_inline_findings,
            max_findings_per_file=max_findings_per_file,
            dialogue_block=dialogue_block,
        )

    def _compute_entropy_summary(
        self,
        file_diffs: list[FileDiff],
    ) -> DiffEntropySummary:
        """Compute the diff-entropy ("diff bomb") summary for the PR."""
        e = diff_entropy.compute_entropy(file_diffs)
        log.info(
            "diff_entropy: %d file(s) +%d/-%d score=%.2f verdict=%s",
            e.file_count,
            e.added_lines,
            e.removed_lines,
            e.score,
            e.verdict,
        )
        return DiffEntropySummary(
            file_count=e.file_count,
            added_lines=e.added_lines,
            removed_lines=e.removed_lines,
            dispersion_entropy=e.dispersion_entropy,
            score=e.score,
            verdict=e.verdict,
        )

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
                up.ecosystem,
                up.package,
                up.old_version,
                up.new_version,
            )
            prompt = dep_upgrade.build_prompt(up, file_diffs)
            raw = self._backend.generate(
                prompt,
                max_new_tokens=self._max_new_tokens,
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
                parts.prompt,
                max_new_tokens=self._max_new_tokens,
            )
            persona_outputs[p] = raw
            aggregated_steps[f"persona::{p.value}"] = raw
            reviews.append(PersonaReview(persona=p.value, output=raw))
        conflicts: list[PersonaConflict] = []
        if len(selected) >= 2:
            conflict_prompt = personas.build_conflict_prompt(persona_outputs)
            conflict_raw = self._backend.generate(
                conflict_prompt,
                max_new_tokens=self._max_new_tokens,
            )
            aggregated_steps["persona::conflicts"] = conflict_raw
            conflicts = personas.parse_conflicts(
                conflict_raw,
                valid_personas=set(selected),
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
            raw,
            allowed_paths={fd.path for fd in file_diffs},
        )

    def _resolve_personas(
        self,
        persona_set: tuple[str, ...],
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
                raise ValueError(f"Unknown persona {raw!r}. Known: {sorted(by_value)}")
            out.append(by_value[key])
        return out

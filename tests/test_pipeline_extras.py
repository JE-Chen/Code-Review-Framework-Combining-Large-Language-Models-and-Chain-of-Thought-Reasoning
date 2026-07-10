"""``PipelineAggregateExtrasMixin`` — cross-file extras via ``CoTPipeline``.

Covers the aggregate-extras dispatcher, PR classification budgets, diff
entropy, persona runs / conflicts, api-consistency gating and persona-name
resolution, all driven through a ``FakeBackend``.
"""

from __future__ import annotations

import json

import pytest

from prthinker.personas import Persona
from prthinker.pipeline import CoTPipeline, PerFileReviewOptions
from prthinker.rag import NoOpRetriever

from tests.conftest import FakeBackend

_STEPS_PER_FILE = 5

_ONE_FILE_DIFF = (
    "diff --git a/a.py b/a.py\n"
    "--- a/a.py\n+++ b/a.py\n@@ -1 +1,2 @@\n x\n+y\n"
)


def _pipeline(backend: FakeBackend) -> CoTPipeline:
    return CoTPipeline(backend=backend, retriever=NoOpRetriever())


# ----- _run_aggregate_extras dispatcher ----------------------------------

def test_all_extras_disabled_yields_empty_extras() -> None:
    backend = FakeBackend(["s"] * _STEPS_PER_FILE)
    result = _pipeline(backend).run_per_file(
        _ONE_FILE_DIFF, PerFileReviewOptions(inline_review=False)
    )
    assert result.dep_upgrades == []
    assert result.persona_reviews == []
    assert result.persona_conflicts == []
    assert result.api_drift == []
    assert result.diff_entropy is None
    assert len(backend.calls) == _STEPS_PER_FILE  # no extra backend calls


# ----- diff entropy -------------------------------------------------------

def test_diff_entropy_check_populates_summary() -> None:
    backend = FakeBackend(["s"] * _STEPS_PER_FILE)
    result = _pipeline(backend).run_per_file(
        _ONE_FILE_DIFF,
        PerFileReviewOptions(inline_review=False, diff_entropy_check=True),
    )
    assert result.diff_entropy is not None
    assert result.diff_entropy.file_count == 1
    assert result.diff_entropy.added_lines == 1
    assert result.diff_entropy.verdict == "focused"


# ----- PR classification --------------------------------------------------

def test_pr_classify_applies_docs_budget() -> None:
    # DOCS budget: run_inline_findings=False, max_findings_per_file=0 —
    # so the inline step never runs even though the caller asked for it.
    classify = json.dumps({"type": "docs", "reason": "readme only"})
    backend = FakeBackend([classify] + ["s"] * _STEPS_PER_FILE)
    result = _pipeline(backend).run_per_file(
        _ONE_FILE_DIFF,
        PerFileReviewOptions(inline_review=True, pr_classify=True),
    )
    assert result.pr_classification is not None
    assert result.pr_classification.pr_type == "docs"
    assert result.pr_classification.reason == "readme only"
    # 1 classify call + 5 base steps, no inline_findings step.
    assert len(backend.calls) == 1 + _STEPS_PER_FILE
    assert "inline_findings" not in result.per_file[0].step_outputs


def test_pr_classify_bugfix_budget_overrides_max_findings() -> None:
    classify = json.dumps({"type": "bugfix", "reason": "off-by-one"})
    inline_payload = "[]"
    backend = FakeBackend(
        [classify] + ["s"] * _STEPS_PER_FILE + [inline_payload]
    )
    pipeline = _pipeline(backend)
    pipeline.run_per_file(
        _ONE_FILE_DIFF,
        PerFileReviewOptions(inline_review=True, pr_classify=True),
    )
    # BUGFIX budget caps findings at 4 and appends its focus hint to the
    # dialogue block; both surface in the inline-findings prompt.
    inline_prompt = backend.calls[-1][0]
    assert "4" in inline_prompt


# ----- personas -------------------------------------------------------------

def test_personas_run_and_conflicts_are_parsed() -> None:
    conflict_payload = json.dumps([{
        "personas": ["security", "performance"],
        "summary": "hashing rate limit trades CPU for safety",
        "resolution": "weigh DOS risk vs throughput",
    }])
    backend = FakeBackend(
        ["s"] * _STEPS_PER_FILE
        + ["sec review", "perf review", conflict_payload]
    )
    result = _pipeline(backend).run_per_file(
        _ONE_FILE_DIFF,
        PerFileReviewOptions(
            inline_review=False,
            persona_set=("security", "performance"),
        ),
    )
    assert [r.persona for r in result.persona_reviews] == [
        "security", "performance",
    ]
    assert result.step_outputs["persona::security"] == "sec review"
    assert result.step_outputs["persona::conflicts"] == conflict_payload
    assert len(result.persona_conflicts) == 1
    assert result.persona_conflicts[0].personas == ["security", "performance"]


def test_single_persona_skips_conflict_call() -> None:
    backend = FakeBackend(["s"] * _STEPS_PER_FILE + ["sec review"])
    result = _pipeline(backend).run_per_file(
        _ONE_FILE_DIFF,
        PerFileReviewOptions(inline_review=False, persona_set=("security",)),
    )
    assert len(result.persona_reviews) == 1
    assert result.persona_conflicts == []
    # 5 steps + 1 persona; no conflict-arbitration call for a single lens.
    assert len(backend.calls) == _STEPS_PER_FILE + 1


# ----- persona-name resolution ---------------------------------------------

def test_resolve_personas_all_expands_to_every_persona() -> None:
    pipeline = _pipeline(FakeBackend())
    assert pipeline._resolve_personas(("all",)) == list(Persona)


def test_resolve_personas_empty_returns_empty() -> None:
    pipeline = _pipeline(FakeBackend())
    assert pipeline._resolve_personas(()) == []


def test_resolve_personas_normalises_case_and_spacing() -> None:
    pipeline = _pipeline(FakeBackend())
    assert pipeline._resolve_personas((" Security ",)) == [Persona.SECURITY]


def test_resolve_personas_unknown_name_raises() -> None:
    pipeline = _pipeline(FakeBackend())
    with pytest.raises(ValueError, match="Unknown persona"):
        pipeline._resolve_personas(("security", "typo"))


# ----- api consistency -------------------------------------------------------

def test_api_consistency_skipped_for_single_language_diff() -> None:
    backend = FakeBackend(["s"] * _STEPS_PER_FILE)
    result = _pipeline(backend).run_per_file(
        _ONE_FILE_DIFF,
        PerFileReviewOptions(inline_review=False, api_consistency_check=True),
    )
    # Single-language PR → the mixed-language gate short-circuits without
    # spending a backend call.
    assert result.api_drift == []
    assert len(backend.calls) == _STEPS_PER_FILE
    assert "api_consistency" not in result.step_outputs


# ----- dep upgrades ----------------------------------------------------------

def test_dep_upgrade_check_runs_impact_step() -> None:
    dep_diff = (
        "diff --git a/requirements.txt b/requirements.txt\n"
        "--- a/requirements.txt\n+++ b/requirements.txt\n"
        "@@ -1 +1 @@\n-requests==2.31.0\n+requests==2.32.0\n"
    )
    impact = json.dumps([])
    backend = FakeBackend(["s"] * _STEPS_PER_FILE + [impact])
    result = _pipeline(backend).run_per_file(
        dep_diff,
        PerFileReviewOptions(inline_review=False, dep_upgrade_check=True),
    )
    assert "dep_upgrade::requests::2.32.0" in result.step_outputs
    assert result.dep_upgrades == []
    assert len(backend.calls) == _STEPS_PER_FILE + 1

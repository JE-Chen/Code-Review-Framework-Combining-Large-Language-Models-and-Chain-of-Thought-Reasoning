"""Adaptive step planning: tier classification, pruning, and pipeline wiring."""

from __future__ import annotations

import pytest

from prthinker.diff import FileDiff
from prthinker.pipeline import CoTPipeline, PerFileReviewOptions
from prthinker.step_planner import (
    TIER_DEEP,
    TIER_SKIP,
    TIER_STANDARD,
    TIER_TRIVIAL,
    changed_line_count,
    classify_depth,
    is_whitespace_only_change,
    plan_steps,
)
from prthinker.steps import (
    CounterfactualStep,
    InlineFindingsStep,
    JudgeStep,
    ReviewContext,
    TotalSummaryStep,
    WalkthroughStep,
    registered_steps,
)


class NoOpRetriever:
    def retrieve(self, query: str) -> list[str]:
        del query
        return []


def _diff(path: str, added: int = 1, removed: int = 0) -> FileDiff:
    lines = [f"--- a/{path}", f"+++ b/{path}", "@@ -1,9 +1,9 @@"]
    lines += [f"+line {i}" for i in range(added)]
    lines += [f"-old {i}" for i in range(removed)]
    return FileDiff(path=path, raw="\n".join(lines))


def _full_chain() -> tuple:
    return registered_steps() + (InlineFindingsStep,)


# ---------------------------------------------------------------------------
# changed_line_count
# ---------------------------------------------------------------------------


def test_changed_line_count_counts_both_sides_and_skips_headers():
    fd = _diff("a.py", added=3, removed=2)
    assert changed_line_count(fd) == 5


def test_changed_line_count_empty_diff():
    assert changed_line_count(FileDiff(path="a.py", raw="")) == 0


# ---------------------------------------------------------------------------
# classify_depth
# ---------------------------------------------------------------------------


def test_trivial_at_five_changed_lines_standard_at_six():
    assert classify_depth(_diff("a.py", added=5)) == TIER_TRIVIAL
    assert classify_depth(_diff("a.py", added=6)) == TIER_STANDARD


def test_deep_boundary_at_two_hundred_changed_lines():
    assert classify_depth(_diff("a.py", added=199)) == TIER_STANDARD
    assert classify_depth(_diff("a.py", added=200)) == TIER_DEEP


def test_docs_and_config_files_are_trivial_regardless_of_size():
    assert classify_depth(_diff("README.md", added=500)) == TIER_TRIVIAL
    assert classify_depth(_diff("ci/config.YAML", added=300)) == TIER_TRIVIAL


def test_high_risk_overrides_tiny_diff():
    assert classify_depth(_diff("auth.py", added=3), risk=0.7) == TIER_DEEP


def test_risk_below_threshold_does_not_escalate():
    assert classify_depth(_diff("a.py", added=50), risk=0.69) == TIER_STANDARD


def test_high_risk_overrides_docs_suffix():
    assert classify_depth(_diff("README.md", added=2), risk=0.9) == TIER_DEEP


def test_lockfiles_and_generated_paths_skip_review():
    assert classify_depth(_diff("package-lock.json", added=500)) == TIER_SKIP
    assert classify_depth(_diff("poetry.lock", added=3)) == TIER_SKIP
    assert classify_depth(_diff("vendor/lib/mod.py", added=50)) == TIER_SKIP
    assert classify_depth(_diff("assets/app.min.js", added=1)) == TIER_SKIP
    assert classify_depth(_diff("proto/gen_pb2.py", added=9)) == TIER_SKIP


def test_lookalike_paths_are_not_skipped():
    # Suffix must match exactly; "unlocked.py" or "distX/" are real code.
    assert classify_depth(_diff("distribution/mod.py", added=50)) == TIER_STANDARD
    assert classify_depth(_diff("src/lockfile_parser.py", added=50)) == TIER_STANDARD


def test_high_risk_overrides_generated_skip():
    assert classify_depth(_diff("vendor/lib/mod.py", added=3), risk=0.9) == TIER_DEEP


def test_whitespace_only_change_is_skip():
    raw = "\n".join(
        [
            "--- a/mod.py",
            "+++ b/mod.py",
            "@@ -1,2 +1,2 @@",
            "-def f(x):  return x",
            "+def f(x):",
            "+    return x",
        ]
    )
    fd = FileDiff(path="mod.py", raw=raw)
    assert is_whitespace_only_change(fd) is False  # split line ≠ same content
    reformat = "\n".join(
        [
            "--- a/mod.py",
            "+++ b/mod.py",
            "@@ -1,1 +1,1 @@",
            "-x=1",
            "+x = 1",
        ]
    )
    fd2 = FileDiff(path="mod.py", raw=reformat)
    assert is_whitespace_only_change(fd2) is True
    assert classify_depth(fd2) == TIER_SKIP


def test_content_change_is_not_whitespace_only():
    fd = _diff("mod.py", added=2, removed=1)
    assert is_whitespace_only_change(fd) is False


def test_empty_diff_is_not_whitespace_only():
    assert is_whitespace_only_change(FileDiff(path="a.py", raw="")) is False


# ---------------------------------------------------------------------------
# plan_steps
# ---------------------------------------------------------------------------


def test_deep_keeps_every_configured_step():
    steps = _full_chain()
    plan = plan_steps(_diff("a.py", added=200), steps)
    assert plan.tier == TIER_DEEP
    assert plan.steps == steps
    assert plan.skipped == ()


def test_trivial_keeps_only_output_steps():
    plan = plan_steps(_diff("a.py", added=1), _full_chain())
    assert plan.tier == TIER_TRIVIAL
    assert [cls.name for cls in plan.steps] == ["inline_findings"]
    assert "first_summary" in plan.skipped
    assert "total_summary" in plan.skipped


def test_trivial_keeps_walkthrough_when_configured():
    steps = registered_steps() + (WalkthroughStep, InlineFindingsStep)
    plan = plan_steps(_diff("a.py", added=1), steps)
    assert [cls.name for cls in plan.steps] == ["walkthrough", "inline_findings"]


def test_trivial_chain_only_falls_back_to_compact_review():
    plan = plan_steps(_diff("a.py", added=1), registered_steps())
    assert [cls.name for cls in plan.steps] == ["compact_review"]


def test_trivial_drops_judge_and_counterfactual():
    steps = registered_steps() + (InlineFindingsStep, CounterfactualStep, JudgeStep)
    plan = plan_steps(_diff("a.py", added=1), steps)
    names = [cls.name for cls in plan.steps]
    assert names == ["inline_findings"]
    assert "judge" in plan.skipped  # requires total_summary, which was pruned
    assert "counterfactual" in plan.skipped  # design exploration is deep-tier work


def test_standard_keeps_counterfactual_with_inline_present():
    steps = registered_steps() + (InlineFindingsStep, CounterfactualStep)
    plan = plan_steps(_diff("a.py", added=50), steps)
    assert "counterfactual" in [cls.name for cls in plan.steps]


def test_skip_tier_plans_zero_steps():
    plan = plan_steps(_diff("poetry.lock", added=100), _full_chain())
    assert plan.tier == TIER_SKIP
    assert plan.steps == ()
    assert set(plan.skipped) == {cls.name for cls in _full_chain()}


def test_standard_with_inline_merges_into_one_unified_call():
    plan = plan_steps(_diff("a.py", added=50), _full_chain())
    assert plan.tier == TIER_STANDARD
    assert [cls.name for cls in plan.steps] == ["unified_review"]
    assert "inline_findings" in plan.skipped
    assert "total_summary" in plan.skipped


def test_standard_without_inline_uses_compact_review():
    plan = plan_steps(_diff("a.py", added=50), registered_steps())
    assert plan.tier == TIER_STANDARD
    assert [cls.name for cls in plan.steps] == ["compact_review"]


def test_standard_with_counterfactual_keeps_two_call_shape():
    steps = registered_steps() + (InlineFindingsStep, CounterfactualStep)
    plan = plan_steps(_diff("a.py", added=50), steps)
    names = [cls.name for cls in plan.steps]
    assert names == ["compact_review", "inline_findings", "counterfactual"]


def test_standard_drops_judge_with_total_summary_pruned():
    steps = registered_steps() + (InlineFindingsStep, JudgeStep)
    plan = plan_steps(_diff("a.py", added=50), steps)
    assert "judge" not in [cls.name for cls in plan.steps]
    assert "judge" in plan.skipped


def test_no_compact_substitute_without_analysis_steps():
    plan = plan_steps(_diff("a.py", added=50), (InlineFindingsStep,))
    assert [cls.name for cls in plan.steps] == ["inline_findings"]


def test_compact_review_prompt_contains_diff():
    from prthinker.steps import CompactReviewStep

    prompt = CompactReviewStep().build_prompt(
        ReviewContext(code_diff="+the-changed-line", rag_docs=[])
    )
    assert "+the-changed-line" in prompt
    assert "Conclusion" in prompt


# ---------------------------------------------------------------------------
# TotalSummaryStep tolerance of pruned inputs
# ---------------------------------------------------------------------------


def test_total_summary_fills_skipped_inputs_with_placeholder():
    ctx = ReviewContext(
        code_diff="+x",
        rag_docs=[],
        results={
            "first_code_review": "review out",
            "linter": "lint out",
            "code_smell": "smell out",
        },
    )
    prompt = TotalSummaryStep().build_prompt(ctx)
    assert "(step skipped at this review depth)" in prompt
    assert "review out" in prompt


def test_total_summary_raises_when_no_prior_step_ran():
    ctx = ReviewContext(code_diff="+x", rag_docs=[], results={})
    with pytest.raises(ValueError, match="at least one prior step"):
        TotalSummaryStep().build_prompt(ctx)


# ---------------------------------------------------------------------------
# Pipeline integration (FakeBackend)
# ---------------------------------------------------------------------------

_TWO_FILE_DIFF = "\n".join(
    [
        "diff --git a/README.md b/README.md",
        "--- a/README.md",
        "+++ b/README.md",
        "@@ -1,2 +1,2 @@",
        "+docs tweak",
        "diff --git a/mod.py b/mod.py",
        "--- a/mod.py",
        "+++ b/mod.py",
        "@@ -1,60 +1,60 @@",
    ]
    + [f"+line {i}" for i in range(50)]
)


def _result_for(result, path):
    return next(fr for fr in result.per_file if fr.path == path)


def test_run_per_file_adaptive_scales_steps_per_file(fake_backend):
    pipeline = CoTPipeline(backend=fake_backend, retriever=NoOpRetriever())
    result = pipeline.run_per_file(
        _TWO_FILE_DIFF,
        PerFileReviewOptions(inline_review=True, step_plan="adaptive"),
    )
    docs = _result_for(result, "README.md")
    code = _result_for(result, "mod.py")
    assert docs.step_outputs["step_plan"] == TIER_TRIVIAL
    assert "first_summary" not in docs.step_outputs
    assert "inline_findings" in docs.step_outputs
    assert code.step_outputs["step_plan"] == TIER_STANDARD
    assert "first_summary" not in code.step_outputs
    # Standard + inline runs the merged single-call step; its payload is
    # fanned back out to the historical keys.
    assert "unified_review" in code.step_outputs
    assert "compact_review" in code.step_outputs
    assert "inline_findings" in code.step_outputs
    # Renderers read the compact output through the same property.
    assert code.total_summary == code.step_outputs["compact_review"]


_UNIFIED_PAYLOAD = (
    '{"summary": "One risky rename.", "verdict": "comment", "findings": '
    '[{"line": 3, "severity": "warning", "comment": "Possible bug."}]}'
)


def test_unified_review_payload_parses_into_findings(fake_backend):
    from tests.conftest import FakeBackend

    backend = FakeBackend([_UNIFIED_PAYLOAD])
    pipeline = CoTPipeline(backend=backend, retriever=NoOpRetriever())
    diff = "\n".join(
        ["diff --git a/mod.py b/mod.py", "--- a/mod.py", "+++ b/mod.py",
         "@@ -1,60 +1,60 @@"]
        + [f"+line {i}" for i in range(50)]
    )
    result = pipeline.run_per_file(
        diff,
        PerFileReviewOptions(inline_review=True, step_plan="adaptive"),
    )
    assert len(backend.calls) == 1  # ONE model call for the whole file
    fr = result.per_file[0]
    assert [f.comment for f in fr.inline_findings] == ["Possible bug."]
    assert fr.inline_findings[0].severity == "warning"
    assert "One risky rename." in fr.total_summary
    assert "Verdict: comment" in fr.total_summary


def test_skip_tier_makes_zero_model_calls(fake_backend):
    pipeline = CoTPipeline(backend=fake_backend, retriever=NoOpRetriever())
    diff = "\n".join(
        ["diff --git a/poetry.lock b/poetry.lock", "--- a/poetry.lock",
         "+++ b/poetry.lock", "@@ -1,9 +1,9 @@"]
        + [f"+pkg{i} = 1.0" for i in range(9)]
    )
    result = pipeline.run_per_file(
        diff,
        PerFileReviewOptions(inline_review=True, step_plan="adaptive"),
    )
    assert fake_backend.calls == []  # not a single generate
    fr = result.per_file[0]
    assert fr.step_outputs == {"step_plan": "skip"}
    assert fr.inline_findings == []


def test_run_per_file_default_full_plan_is_unchanged(fake_backend):
    pipeline = CoTPipeline(backend=fake_backend, retriever=NoOpRetriever())
    result = pipeline.run_per_file(
        _TWO_FILE_DIFF,
        PerFileReviewOptions(inline_review=True),
    )
    docs = _result_for(result, "README.md")
    assert "step_plan" not in docs.step_outputs
    assert "first_summary" in docs.step_outputs
    assert "total_summary" in docs.step_outputs

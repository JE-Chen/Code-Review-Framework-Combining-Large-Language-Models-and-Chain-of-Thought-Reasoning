"""Tests for the depth-eval harness (prthinker.depth_eval)."""

from __future__ import annotations

import pytest

from prthinker.backends.base import Usage
from prthinker.depth_eval import (
    CountingBackend,
    DepthEvalReport,
    DiffComparison,
    ModeUsage,
    PipelineProbe,
    format_markdown,
    match_findings,
    run_depth_comparison,
)
from prthinker.pipeline import CoTPipeline, PerFileReviewOptions
from prthinker.schemas import InlineFinding
from tests.conftest import FakeBackend


class _NoOpRetriever:
    def retrieve(self, _text: str) -> list[str]:
        return []


def _finding(path="mod.py", line=5, severity="warning", comment="x"):
    return InlineFinding(path=path, line=line, severity=severity, comment=comment)


# ---------------------------------------------------------------------------
# match_findings
# ---------------------------------------------------------------------------


def test_match_exact_finding_id():
    full = [_finding(comment="same remark")]
    adaptive = [_finding(comment="same remark")]
    outcome = match_findings(full, adaptive)
    assert outcome.matched == 1
    assert outcome.missing == ()
    assert outcome.extra == ()


def test_match_within_line_window():
    outcome = match_findings(
        [_finding(line=5, comment="a bug")],
        [_finding(line=7, comment="same bug, other words")],
    )
    assert outcome.matched == 1
    assert outcome.missing == () and outcome.extra == ()


def test_match_rejects_beyond_line_window():
    outcome = match_findings(
        [_finding(line=5, comment="a bug")],
        [_finding(line=8, comment="same bug, other words")],
    )
    assert outcome.matched == 0
    assert len(outcome.missing) == 1
    assert len(outcome.extra) == 1


def test_match_severity_mismatch_not_matched():
    outcome = match_findings(
        [_finding(line=5, severity="error", comment="a bug")],
        [_finding(line=5, severity="warning", comment="a bug variant")],
    )
    assert outcome.matched == 0
    assert len(outcome.missing) == 1 and len(outcome.extra) == 1


def test_match_path_mismatch_not_matched():
    outcome = match_findings(
        [_finding(path="a.py", line=5, comment="a bug")],
        [_finding(path="b.py", line=5, comment="a bug too")],
    )
    assert outcome.matched == 0


def test_match_prefers_nearest_candidate():
    near = _finding(line=6, comment="near")
    far = _finding(line=7, comment="far")
    outcome = match_findings([_finding(line=5, comment="target")], [far, near])
    assert outcome.matched == 1
    # The nearer candidate pairs; the farther one is left over as extra.
    assert outcome.extra == (far,)


def test_match_missing_and_extra_classification():
    full = [
        _finding(line=3, severity="warning", comment="kept"),
        _finding(line=30, severity="error", comment="dropped by adaptive"),
    ]
    adaptive = [
        _finding(line=4, severity="warning", comment="kept, moved a line"),
        _finding(line=40, severity="info", comment="adaptive-only note"),
    ]
    outcome = match_findings(full, adaptive)
    assert outcome.matched == 1
    assert [f.comment for f in outcome.missing] == ["dropped by adaptive"]
    assert [f.comment for f in outcome.extra] == ["adaptive-only note"]


def test_match_empty_inputs():
    outcome = match_findings([], [])
    assert outcome.matched == 0 and outcome.missing == () and outcome.extra == ()
    only_adaptive = match_findings([], [_finding()])
    assert len(only_adaptive.extra) == 1


def test_match_custom_line_window_boundary():
    full = [_finding(line=10, comment="x1")]
    assert match_findings(full, [_finding(line=11, comment="y1")], line_window=1).matched == 1
    assert match_findings(full, [_finding(line=12, comment="y2")], line_window=1).matched == 0


# ---------------------------------------------------------------------------
# CountingBackend
# ---------------------------------------------------------------------------


def test_counting_backend_counts_calls_and_estimates_tokens():
    inner = FakeBackend(["abcd" * 5])
    backend = CountingBackend(inner)
    assert backend.snapshot() == (0, 0)
    backend.generate("p" * 20, 100)
    calls, tokens = backend.snapshot()
    assert calls == 1
    assert tokens == (20 + 20) // 4


def test_counting_backend_prefers_reported_usage():
    inner = FakeBackend(
        ["out"], usage_per_call=[Usage(prompt_tokens=7, completion_tokens=3)]
    )
    backend = CountingBackend(inner)
    backend.generate("prompt", 100)
    assert backend.snapshot() == (1, 10)


def test_counting_backend_delegates_identity():
    inner = FakeBackend(kind="fakekind", model="fake-model")
    backend = CountingBackend(inner)
    assert backend.backend_kind() == "fakekind"
    assert backend.model_name() == "fake-model"
    assert backend.max_concurrency() == 1


# ---------------------------------------------------------------------------
# run_depth_comparison — option validation
# ---------------------------------------------------------------------------


def _unused_factory(_mode: str) -> PipelineProbe:
    raise AssertionError("factory must not be called when validation fails")


def test_rejects_wrong_full_step_plan():
    with pytest.raises(ValueError, match="options_full.step_plan"):
        run_depth_comparison(
            _unused_factory,
            ["+x"],
            PerFileReviewOptions(step_plan="adaptive"),
            PerFileReviewOptions(step_plan="adaptive"),
        )


def test_rejects_wrong_adaptive_step_plan():
    with pytest.raises(ValueError, match="options_adaptive.step_plan"):
        run_depth_comparison(
            _unused_factory,
            ["+x"],
            PerFileReviewOptions(step_plan="full"),
            PerFileReviewOptions(step_plan="full"),
        )


def test_rejects_enabled_review_cache():
    with pytest.raises(ValueError, match="review_cache"):
        run_depth_comparison(
            _unused_factory,
            ["+x"],
            PerFileReviewOptions(step_plan="full", review_cache=object()),
            PerFileReviewOptions(step_plan="adaptive"),
        )


# ---------------------------------------------------------------------------
# run_depth_comparison — end-to-end with FakeBackend
# ---------------------------------------------------------------------------

_DIFF = "\n".join(
    ["diff --git a/mod.py b/mod.py", "--- a/mod.py", "+++ b/mod.py",
     "@@ -1,60 +1,60 @@"]
    + [f"+line {i}" for i in range(50)]
)

_FULL_FINDINGS_JSON = (
    '[{"line": 3, "severity": "warning", "comment": "Possible bug."},'
    ' {"line": 10, "severity": "error", "comment": "Null deref."}]'
)

# Standard tier merges analysis + findings into one unified-review call.
_ADAPTIVE_UNIFIED_JSON = (
    '{"summary": "One risky change.", "verdict": "comment", "findings":'
    ' [{"line": 4, "severity": "warning", "comment": "Possible bug nearby."}]}'
)


def _scripted_factory(record: dict):
    """Factory yielding a fresh FakeBackend-driven pipeline per mode."""
    responses = {
        # Five default analysis steps, then the inline-findings pass.
        "full": ["s1", "s2", "s3", "s4", "s5", _FULL_FINDINGS_JSON],
        "adaptive": [_ADAPTIVE_UNIFIED_JSON],
    }

    def build(mode: str) -> PipelineProbe:
        record.setdefault("modes", []).append(mode)
        backend = CountingBackend(FakeBackend(responses[mode]))
        pipeline = CoTPipeline(backend=backend, retriever=_NoOpRetriever())
        return PipelineProbe(
            pipeline=pipeline,
            usage_snapshot=backend.snapshot,
            close=lambda: record.setdefault("closed", []).append(mode),
        )

    return build


def _run_scripted_comparison(record: dict) -> DepthEvalReport:
    return run_depth_comparison(
        _scripted_factory(record),
        [_DIFF],
        PerFileReviewOptions(inline_review=True, step_plan="full"),
        PerFileReviewOptions(inline_review=True, step_plan="adaptive"),
    )


def test_end_to_end_report_numbers():
    report = _run_scripted_comparison({})
    assert report.full_findings == 2
    assert report.adaptive_findings == 1
    assert report.matched == 1
    assert report.adaptive_missing == 1
    assert report.adaptive_extra == 0
    assert report.gate_full == 2 and report.gate_matched == 1
    assert report.gate_recall == pytest.approx(0.5)
    assert report.tier_counts == {"standard": 1}


def test_end_to_end_call_and_token_accounting():
    report = _run_scripted_comparison({})
    assert report.full_usage.calls == 6
    assert report.adaptive_usage.calls == 1
    assert report.adaptive_usage.calls < report.full_usage.calls
    assert report.full_usage.tokens > 0
    assert report.adaptive_usage.tokens > 0
    (diff,) = report.diffs
    assert diff.full_usage.calls == 6 and diff.adaptive_usage.calls == 1


def test_end_to_end_builds_one_pipeline_per_mode_and_closes_both():
    record: dict = {}
    _run_scripted_comparison(record)
    assert record["modes"] == ["full", "adaptive"]
    assert sorted(record["closed"]) == ["adaptive", "full"]


def test_end_to_end_markdown_renders():
    text = format_markdown(_run_scripted_comparison({}))
    assert text.startswith("# Review depth evaluation")
    assert "Diffs compared: 1" in text
    assert "| Findings | 2 | 1 |" in text
    assert "| Model calls | 6 | 1 |" in text
    assert "Gate-severity recall (error/warning): 0.50 (1/2)" in text
    assert "| standard | 1 |" in text


# ---------------------------------------------------------------------------
# format_markdown / report aggregation on synthetic rows
# ---------------------------------------------------------------------------


def _comparison(index=0, **overrides) -> DiffComparison:
    base = dict(
        index=index,
        full_findings=0,
        adaptive_findings=0,
        matched=0,
        adaptive_missing=0,
        adaptive_extra=0,
        gate_full=0,
        gate_matched=0,
        tier_counts={},
        full_usage=ModeUsage(),
        adaptive_usage=ModeUsage(),
    )
    base.update(overrides)
    return DiffComparison(**base)


def test_report_aggregates_across_diffs():
    report = DepthEvalReport(
        diffs=(
            _comparison(0, full_findings=2, matched=1, gate_full=1, gate_matched=1,
                        tier_counts={"skip": 1}, full_usage=ModeUsage(6, 100),
                        adaptive_usage=ModeUsage(1, 10)),
            _comparison(1, full_findings=3, matched=2, gate_full=2, gate_matched=1,
                        tier_counts={"skip": 1, "deep": 2},
                        full_usage=ModeUsage(12, 200),
                        adaptive_usage=ModeUsage(8, 80)),
        )
    )
    assert report.full_findings == 5
    assert report.matched == 3
    assert report.gate_recall == pytest.approx(2 / 3)
    assert report.tier_counts == {"skip": 2, "deep": 2}
    assert report.full_usage == ModeUsage(18, 300)
    assert report.adaptive_usage == ModeUsage(9, 90)


def test_gate_recall_is_one_when_no_gate_findings():
    assert DepthEvalReport(diffs=()).gate_recall == 1.0


def test_format_markdown_empty_report():
    text = format_markdown(DepthEvalReport(diffs=()))
    assert "Diffs compared: 0" in text
    assert "_No files were reviewed._" in text
    assert "Gate-severity recall (error/warning): 1.00 (0/0)" in text


def test_format_markdown_orders_tiers_shallow_to_deep():
    report = DepthEvalReport(
        diffs=(
            _comparison(0, tier_counts={"full": 1, "skip": 2, "standard": 3}),
        )
    )
    text = format_markdown(report)
    assert (
        text.index("| skip | 2 |")
        < text.index("| standard | 3 |")
        < text.index("| full | 1 |")
    )

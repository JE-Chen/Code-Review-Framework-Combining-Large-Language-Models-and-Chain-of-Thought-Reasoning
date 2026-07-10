"""Unit tests for the summary-breakdown helper in ``prthinker.cli_review_emit``.

``_inline_post_breakdown`` reports how many findings actually land on a diff
hunk (and will be posted as inline comments) versus the raw total. The count
is derived from the off-diff list rather than parsing the diff a second time,
so these tests lock the partition invariant: ``posted == total - len(off)``.

``_gate_inputs`` precomputes the calibrated (gate findings, abstained) pair
once per publish so ``_gate_line`` and ``_close_review_gate`` never each
re-run the per-finding calibration queries.
"""

from __future__ import annotations

from types import SimpleNamespace

from prthinker.cli_review_emit import (
    _close_review_gate,
    _gate_inputs,
    _gate_line,
    _inline_post_breakdown,
)
from prthinker.schemas import InlineFinding

# Single-file diff whose new side carries exactly lines 1 and 2 of a.py.
_DIFF = (
    "diff --git a/a.py b/a.py\n"
    "--- a/a.py\n"
    "+++ b/a.py\n"
    "@@ -0,0 +1,2 @@\n"
    "+first\n"
    "+second\n"
)


def _finding(**kw) -> InlineFinding:
    base = {"path": "a.py", "line": 1, "comment": "x"}
    base.update(kw)
    return InlineFinding(**base)


def test_inline_post_breakdown_disabled_returns_empty():
    """With inline review off, nothing is posted and the breakdown is inert."""
    args = SimpleNamespace(inline_review=False)
    result = SimpleNamespace(inline_findings=[_finding()], code_diff=_DIFF)
    assert _inline_post_breakdown(args, result) == (None, ())


def test_inline_post_breakdown_missing_flag_treated_as_disabled():
    """An args namespace without the flag defaults to disabled (getattr)."""
    args = SimpleNamespace()
    result = SimpleNamespace(inline_findings=[_finding()], code_diff=_DIFF)
    assert _inline_post_breakdown(args, result) == (None, ())


def test_inline_post_breakdown_counts_on_diff_and_collects_off_diff():
    """posted_count = total - off_diff; off-diff findings are returned in order."""
    on1 = _finding(path="a.py", line=1)
    on2 = _finding(path="a.py", line=2)
    off_line = _finding(path="a.py", line=99)        # inside file, off the hunk
    off_file = _finding(path="missing.py", line=1)   # file not in the diff
    args = SimpleNamespace(inline_review=True)
    result = SimpleNamespace(
        inline_findings=[on1, on2, off_line, off_file],
        code_diff=_DIFF,
    )

    posted_count, off_diff = _inline_post_breakdown(args, result)

    assert posted_count == 2
    assert off_diff == (off_line, off_file)


def test_inline_post_breakdown_all_on_diff():
    """No off-diff findings → posted_count equals the total, off_diff empty."""
    args = SimpleNamespace(inline_review=True)
    findings = [_finding(line=1), _finding(line=2)]
    result = SimpleNamespace(inline_findings=findings, code_diff=_DIFF)

    posted_count, off_diff = _inline_post_breakdown(args, result)

    assert posted_count == 2
    assert off_diff == ()


def test_inline_post_breakdown_all_off_diff():
    """Every finding off the diff → posted_count is zero, all returned as off."""
    args = SimpleNamespace(inline_review=True)
    findings = [_finding(line=50), _finding(path="other.py", line=1)]
    result = SimpleNamespace(inline_findings=findings, code_diff=_DIFF)

    posted_count, off_diff = _inline_post_breakdown(args, result)

    assert posted_count == 0
    assert off_diff == tuple(findings)


def test_inline_post_breakdown_no_findings():
    """Empty finding list → zero posted, empty off-diff (no diff parse needed)."""
    args = SimpleNamespace(inline_review=True)
    result = SimpleNamespace(inline_findings=[], code_diff=_DIFF)
    assert _inline_post_breakdown(args, result) == (0, ())


# --- _gate_inputs: compute-once calibrated gate scoring -----------------------


def test_gate_inputs_none_when_not_gating():
    """gate_on == none → no tuple, so the calibration store is never opened."""
    args = SimpleNamespace(gate_on="none", calibration_gate=True)
    result = SimpleNamespace(inline_findings=[_finding()])
    assert _gate_inputs(args, result) is None


def test_gate_inputs_passthrough_without_calibration_gate():
    """Gating without --calibration-gate keeps every finding, abstains none."""
    findings = [_finding(severity="error")]
    args = SimpleNamespace(gate_on="error", calibration_gate=False)
    result = SimpleNamespace(inline_findings=findings)
    assert _gate_inputs(args, result) == (findings, 0)


def test_gate_line_uses_precomputed_calibrated_tuple():
    """A supplied (findings, abstained) tuple is used verbatim — no recompute."""
    kept = [_finding(severity="warning")]
    args = SimpleNamespace(gate_on="error", calibration_gate=False)
    # result.inline_findings deliberately disagrees with the precomputed
    # tuple; the line must reflect the tuple (1 warning, 2 abstained).
    result = SimpleNamespace(
        inline_findings=[_finding(severity="error"), _finding(severity="error")]
    )

    line = _gate_line(args, result, None, (kept, 2))

    assert "success" in line
    assert "0 error, 1 warning" in line
    assert "calibration abstained 2" in line


def test_close_review_gate_uses_precomputed_calibrated_tuple():
    """The gate close scores the precomputed findings, not the raw result."""
    closed: dict[str, object] = {}

    class _Adapter:
        def close_gate(self, handle, gate_result):
            closed["handle"] = handle
            closed["conclusion"] = gate_result.conclusion

    args = SimpleNamespace(gate_on="error", check_annotations=False)
    result = SimpleNamespace(inline_findings=[_finding(severity="error")])
    handle = object()

    _close_review_gate(args, _Adapter(), result, handle, ([], 1))

    assert closed["handle"] is handle
    # The precomputed (empty) finding list wins over the raw error finding.
    assert closed["conclusion"] == "success"


def test_close_review_gate_noop_without_handle():
    """No opened gate → nothing to close, even with findings present."""
    class _Adapter:
        def close_gate(self, handle, gate_result):  # pragma: no cover
            raise AssertionError("close_gate must not be called")

    args = SimpleNamespace(gate_on="error", check_annotations=False)
    result = SimpleNamespace(inline_findings=[_finding(severity="error")])
    _close_review_gate(args, _Adapter(), result, None, None)

"""Gate evaluation — the boolean logic that decides if a PR can merge."""

from __future__ import annotations

from prthinker.checks import evaluate_gate
from prthinker.schemas import InlineFinding


def _f(line: int, severity: str) -> InlineFinding:
    return InlineFinding(
        path="x.py", line=line, severity=severity, comment="c",
    )


def test_no_findings_always_success() -> None:
    for gate in ("none", "warning", "error"):
        result = evaluate_gate([], gate_on=gate)
        assert result.conclusion == "success"
        assert result.error_count == 0


def test_gate_none_passes_regardless() -> None:
    findings = [_f(1, "error"), _f(2, "warning"), _f(3, "info")]
    result = evaluate_gate(findings, gate_on="none")
    assert result.conclusion == "success"


def test_gate_error_blocks_only_on_errors() -> None:
    assert evaluate_gate([_f(1, "warning")], gate_on="error").conclusion == "success"
    assert evaluate_gate([_f(1, "error")], gate_on="error").conclusion == "failure"


def test_gate_warning_blocks_on_warning_or_error() -> None:
    assert evaluate_gate([_f(1, "info")], gate_on="warning").conclusion == "success"
    assert evaluate_gate([_f(1, "warning")], gate_on="warning").conclusion == "failure"
    assert evaluate_gate([_f(1, "error")], gate_on="warning").conclusion == "failure"


def test_counts_are_split_by_severity() -> None:
    findings = [_f(1, "error"), _f(2, "warning"), _f(3, "warning"), _f(4, "info")]
    result = evaluate_gate(findings, gate_on="error")
    assert result.error_count == 1
    assert result.warning_count == 2
    assert result.info_count == 1


# --- check-run annotations ---------------------------------------------------

def test_annotations_off_by_default() -> None:
    result = evaluate_gate([_f(1, "error")], gate_on="error")
    assert result.annotations == []


def test_annotations_built_when_requested() -> None:
    findings = [_f(10, "error"), _f(20, "warning"), _f(30, "info")]
    result = evaluate_gate(findings, gate_on="error", with_annotations=True)
    levels = [a["annotation_level"] for a in result.annotations]
    assert levels == ["failure", "warning", "notice"]
    first = result.annotations[0]
    assert first["path"] == "x.py"
    assert first["start_line"] == 10 and first["end_line"] == 10
    assert first["message"] == "c"


def test_annotation_multiline_uses_start_line() -> None:
    f = InlineFinding(path="x.py", line=12, start_line=10, severity="error", comment="c")
    result = evaluate_gate([f], gate_on="error", with_annotations=True)
    ann = result.annotations[0]
    assert ann["start_line"] == 10 and ann["end_line"] == 12


def test_annotation_batches_split_at_50() -> None:
    from prthinker.checks import _annotation_batches
    assert _annotation_batches([]) == [[]]
    one = _annotation_batches([{"a": 1}] * 50)
    assert len(one) == 1 and len(one[0]) == 50
    two = _annotation_batches([{"a": 1}] * 51)
    assert len(two) == 2 and len(two[0]) == 50 and len(two[1]) == 1

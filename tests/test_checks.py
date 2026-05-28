"""Gate evaluation — the boolean logic that decides if a PR can merge."""

from __future__ import annotations

from reviewmind.checks import evaluate_gate
from reviewmind.schemas import InlineFinding


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

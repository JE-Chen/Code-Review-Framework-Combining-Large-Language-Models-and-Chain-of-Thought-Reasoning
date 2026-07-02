"""Tests for the multi-model finding-arbitration layer.

Covers the vote-combination strategies (including the tie boundary), the
lenient vote parsing, the fail-open posture of :class:`FindingArbitrator`,
and the CLI wiring (``apply_arbitration``) driven by ``FakeBackend``s.
"""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from tests.conftest import FakeBackend
from prthinker import cli_review_helpers
from prthinker.arbitration import (
    AnyConfirmStrategy,
    FindingArbitrator,
    MajorityStrategy,
    STRATEGY_NAMES,
    UnanimousStrategy,
    build_arbitration_prompt,
    create_arbitration_strategy,
    parse_votes,
)
from prthinker.pipeline import FileReviewResult, ReviewResult
from prthinker.schemas import InlineFinding


def _finding(path: str = "a.py", line: int = 3, comment: str = "bug") -> InlineFinding:
    return InlineFinding(path=path, line=line, severity="warning", comment=comment)


def _votes(*verdicts: str) -> str:
    return json.dumps(
        [{"id": i, "verdict": v} for i, v in enumerate(verdicts, start=1)]
    )


# ----- strategies -----------------------------------------------------------


def test_majority_keeps_on_more_confirms() -> None:
    assert MajorityStrategy().keep(confirms=2, rejects=1)


def test_majority_keeps_on_tie() -> None:
    # Boundary: a tie fails open — arbitration only drops on clear signal.
    assert MajorityStrategy().keep(confirms=1, rejects=1)


def test_majority_drops_when_rejects_win() -> None:
    assert not MajorityStrategy().keep(confirms=1, rejects=2)


def test_unanimous_drops_on_single_reject() -> None:
    assert not UnanimousStrategy().keep(confirms=5, rejects=1)


def test_unanimous_keeps_when_no_reject() -> None:
    assert UnanimousStrategy().keep(confirms=1, rejects=0)


def test_any_keeps_on_single_confirm() -> None:
    assert AnyConfirmStrategy().keep(confirms=1, rejects=5)


def test_any_drops_without_confirm() -> None:
    assert not AnyConfirmStrategy().keep(confirms=0, rejects=1)


def test_factory_builds_each_registered_strategy() -> None:
    for name in STRATEGY_NAMES:
        assert create_arbitration_strategy(name).name == name


def test_factory_unknown_name_raises() -> None:
    with pytest.raises(ValueError, match="unknown arbitration strategy"):
        create_arbitration_strategy("nope")


# ----- prompt template -------------------------------------------------------


def test_prompt_numbers_findings_and_embeds_diff() -> None:
    prompt = build_arbitration_prompt(
        "diff --git a/a.py b/a.py",
        [_finding(comment="first"), _finding(line=9, comment="second")],
    )
    assert "1. [warning] a.py:3 — first" in prompt
    assert "2. [warning] a.py:9 — second" in prompt
    assert "diff --git a/a.py b/a.py" in prompt


# ----- vote parsing -----------------------------------------------------------


def test_parse_votes_happy_path() -> None:
    assert parse_votes(_votes("confirm", "reject"), 2) == {1: True, 2: False}


def test_parse_votes_strips_code_fence() -> None:
    raw = "```json\n" + _votes("confirm") + "\n```"
    assert parse_votes(raw, 1) == {1: True}


def test_parse_votes_ignores_out_of_range_ids() -> None:
    raw = json.dumps([
        {"id": 0, "verdict": "reject"},
        {"id": 3, "verdict": "reject"},
        {"id": 1, "verdict": "confirm"},
    ])
    assert parse_votes(raw, 2) == {1: True}


def test_parse_votes_ignores_unknown_verdicts_and_shapes() -> None:
    raw = json.dumps([
        {"id": 1, "verdict": "maybe"},
        "not a dict",
        {"id": "1", "verdict": "confirm"},
    ])
    assert parse_votes(raw, 2) == {}


def test_parse_votes_no_array_abstains() -> None:
    assert parse_votes("I think they are all fine.", 3) == {}


def test_parse_votes_malformed_json_abstains() -> None:
    assert parse_votes("[{'single': 'quotes'}]", 1) == {}


def test_parse_votes_duplicate_id_keeps_last() -> None:
    raw = json.dumps([
        {"id": 1, "verdict": "confirm"},
        {"id": 1, "verdict": "reject"},
    ])
    assert parse_votes(raw, 1) == {1: False}


# ----- FindingArbitrator -------------------------------------------------------


def test_arbitrator_requires_backends() -> None:
    with pytest.raises(ValueError, match="at least one backend"):
        FindingArbitrator((), MajorityStrategy())


def test_arbitrate_empty_findings_makes_no_calls() -> None:
    backend = FakeBackend()
    outcome = FindingArbitrator([backend], MajorityStrategy()).arbitrate(
        [], "diff"
    )
    assert outcome.kept == [] and outcome.dropped == []
    assert backend.calls == []


def test_arbitrate_majority_drops_rejected_finding() -> None:
    backends = [
        FakeBackend([_votes("confirm", "reject")]),
        FakeBackend([_votes("confirm", "reject")]),
        FakeBackend([_votes("reject", "confirm")]),
    ]
    findings = [_finding(comment="real"), _finding(line=9, comment="noise")]
    outcome = FindingArbitrator(backends, MajorityStrategy()).arbitrate(
        findings, "diff"
    )
    assert [f.comment for f in outcome.kept] == ["real"]
    assert [f.comment for f in outcome.dropped] == ["noise"]
    assert outcome.tallies == {1: (2, 1), 2: (1, 2)}


def test_arbitrate_failing_backend_abstains() -> None:
    class _BoomBackend(FakeBackend):
        def generate(self, prompt, max_new_tokens, *, cancel_event=None):
            raise RuntimeError("down")

    backends = [_BoomBackend(), FakeBackend([_votes("reject")])]
    outcome = FindingArbitrator(backends, MajorityStrategy()).arbitrate(
        [_finding()], "diff"
    )
    # The healthy arbiter's reject is the only countable vote → dropped.
    assert outcome.kept == [] and len(outcome.dropped) == 1


def test_arbitrate_zero_votes_fails_open() -> None:
    backends = [FakeBackend(["no json here"])]
    findings = [_finding()]
    outcome = FindingArbitrator(backends, UnanimousStrategy()).arbitrate(
        findings, "diff"
    )
    assert outcome.kept == findings


def test_arbitrate_passes_budget_and_prompt() -> None:
    backend = FakeBackend([_votes("confirm")])
    FindingArbitrator([backend], MajorityStrategy(), max_new_tokens=77).arbitrate(
        [_finding()], "DIFF-SENTINEL"
    )
    prompt, max_new_tokens = backend.calls[0]
    assert "DIFF-SENTINEL" in prompt
    assert max_new_tokens == 77


# ----- CLI wiring (apply_arbitration) ----------------------------------------


def _args(**overrides: object) -> SimpleNamespace:
    defaults = {
        "arbitration": True,
        "arbitration_backends": "remote",
        "arbitration_strategy": "majority",
        "arbitration_max_new_tokens": 256,
        "remote_url": "https://backend.example",
        "remote_timeout": 30.0,
        "remote_api_key": None,
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _result(*findings: InlineFinding) -> ReviewResult:
    return ReviewResult(
        code_diff="diff",
        rag_docs=[],
        inline_findings=list(findings),
        per_file=[
            FileReviewResult(
                path="a.py", rag_docs=[], step_outputs={},
                inline_findings=list(findings),
            )
        ],
    )


def test_apply_arbitration_disabled_is_noop(monkeypatch) -> None:
    def _fail(config):
        raise AssertionError("no backend should be built")

    monkeypatch.setattr(cli_review_helpers, "create_backend", _fail)
    result = _result(_finding())
    cli_review_helpers.apply_arbitration(_args(arbitration=False), result)
    assert len(result.inline_findings) == 1


def test_apply_arbitration_empty_backends_keeps_findings(monkeypatch) -> None:
    result = _result(_finding())
    cli_review_helpers.apply_arbitration(
        _args(arbitration_backends=""), result
    )
    assert len(result.inline_findings) == 1


def test_apply_arbitration_unknown_kind_exits() -> None:
    with pytest.raises(SystemExit, match="unknown arbitration backend kind"):
        cli_review_helpers.apply_arbitration(
            _args(arbitration_backends="quantum"), _result(_finding())
        )


def test_apply_arbitration_drops_rejected_and_syncs_per_file(
    monkeypatch,
) -> None:
    backend = FakeBackend([_votes("reject")])
    monkeypatch.setattr(
        cli_review_helpers, "create_backend", lambda config: backend
    )
    result = _result(_finding())
    cli_review_helpers.apply_arbitration(_args(), result)
    assert result.inline_findings == []
    assert result.per_file[0].inline_findings == []


def test_apply_arbitration_keeps_confirmed(monkeypatch) -> None:
    backend = FakeBackend([_votes("confirm")])
    monkeypatch.setattr(
        cli_review_helpers, "create_backend", lambda config: backend
    )
    result = _result(_finding())
    cli_review_helpers.apply_arbitration(_args(), result)
    assert len(result.inline_findings) == 1
    assert len(result.per_file[0].inline_findings) == 1


def test_apply_arbitration_builds_configured_kind(monkeypatch) -> None:
    seen_configs = []

    def _capture(config):
        seen_configs.append(config)
        return FakeBackend([_votes("confirm")])

    monkeypatch.setattr(cli_review_helpers, "create_backend", _capture)
    cli_review_helpers.apply_arbitration(_args(), _result(_finding()))
    assert [c.backend.value for c in seen_configs] == ["remote"]
    assert seen_configs[0].remote.url == "https://backend.example"

"""Pure-logic tests for the PR-type classifier."""

from __future__ import annotations

import json

import pytest

from prthinker.pr_classifier import (
    Classification,
    PRType,
    ReviewBudget,
    budget_for,
    build_prompt,
    parse_classification,
)


# ----- prompt builder ---------------------------------------------------

def test_build_prompt_includes_title_body_and_diff() -> None:
    prompt = build_prompt(
        diff_text="diff --git a/x b/x\n+hello\n",
        title="Fix log injection",
        body="Closes #42",
    )
    assert "Fix log injection" in prompt
    assert "Closes #42" in prompt
    assert "+hello" in prompt


def test_build_prompt_handles_missing_meta() -> None:
    prompt = build_prompt(diff_text="diff x")
    assert "(no title)" in prompt
    assert "(no description)" in prompt


def test_build_prompt_truncates_long_diff() -> None:
    long = "a" * 50_000
    prompt = build_prompt(diff_text=long, diff_chars=200)
    # The excerpt must be capped; original 50k chars not included verbatim.
    assert "a" * 50_000 not in prompt
    assert "a" * 200 in prompt


# ----- parser -----------------------------------------------------------

def test_parse_clean_payload() -> None:
    raw = json.dumps({"type": "bugfix", "reason": "Fixes off-by-one"})
    out = parse_classification(raw)
    assert out.pr_type is PRType.BUGFIX
    assert out.reason == "Fixes off-by-one"


def test_parse_inside_fenced_block() -> None:
    raw = '```json\n{"type": "feature", "reason": "Adds new endpoint"}\n```'
    out = parse_classification(raw)
    assert out.pr_type is PRType.FEATURE


def test_parse_unknown_type_falls_through_to_unknown() -> None:
    raw = json.dumps({"type": "not_a_real_type", "reason": "?"})
    out = parse_classification(raw)
    assert out.pr_type is PRType.UNKNOWN


def test_parse_garbage_returns_unknown() -> None:
    assert parse_classification("not json").pr_type is PRType.UNKNOWN
    assert parse_classification("").pr_type is PRType.UNKNOWN
    assert parse_classification("[]").pr_type is PRType.UNKNOWN


def test_parse_missing_reason_is_empty() -> None:
    raw = json.dumps({"type": "refactor"})
    out = parse_classification(raw)
    assert out.pr_type is PRType.REFACTOR
    assert out.reason == ""


# ----- budget mapping ---------------------------------------------------

@pytest.mark.parametrize(
    "pr_type, run_inline, max_findings_min",
    [
        (PRType.BUGFIX,  True, 1),
        (PRType.FEATURE, True, 5),
        (PRType.REFACTOR, True, 10),
        (PRType.DOCS,    False, 0),
        (PRType.CHORE,   True, 1),
        (PRType.UNKNOWN, True, 5),
    ],
)
def test_budget_for_each_type(
    pr_type: PRType, run_inline: bool, max_findings_min: int,
) -> None:
    b = budget_for(pr_type)
    assert isinstance(b, ReviewBudget)
    assert b.run_inline_findings is run_inline
    assert b.max_findings_per_file >= max_findings_min


def test_docs_pr_skips_inline() -> None:
    assert budget_for(PRType.DOCS).run_inline_findings is False


def test_bugfix_has_focus_hint_about_regression() -> None:
    assert "regression" in budget_for(PRType.BUGFIX).focus_hint.lower()


# ----- Classification dataclass ----------------------------------------

def test_classification_is_frozen() -> None:
    c = Classification(pr_type=PRType.BUGFIX, reason="x")
    try:
        c.reason = "y"  # type: ignore[misc]
    except Exception:
        return
    raise AssertionError("Classification should be frozen")

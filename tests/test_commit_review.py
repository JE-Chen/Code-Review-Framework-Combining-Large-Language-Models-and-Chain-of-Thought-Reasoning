"""Tests for the commit-message review prompt builder + parser.

Same defensive parser stance as :mod:`prthinker.counterfactual`: malformed
output drops nothing real; we never crash the pipeline on a bad reply.
"""

from __future__ import annotations

import json

from prthinker.commit_review import (
    CommitMessageNote,
    build_prompt,
    parse_review,
)


# ----- build_prompt -----------------------------------------------------

def test_build_prompt_includes_each_message() -> None:
    messages = ["feat: add thing", "fixed the bug", "wip"]
    prompt = build_prompt(messages)
    for message in messages:
        assert message in prompt


def test_build_prompt_numbers_messages_zero_based() -> None:
    prompt = build_prompt(["a", "b"])
    assert "Message 0" in prompt
    assert "Message 1" in prompt


def test_build_prompt_reports_count() -> None:
    prompt = build_prompt(["a", "b", "c"])
    assert "3 commit message" in prompt


def test_build_prompt_empty_list() -> None:
    prompt = build_prompt([])
    assert "0 commit message" in prompt


# ----- parse_review: happy path -----------------------------------------

def test_parse_clean_json_array() -> None:
    payload = json.dumps([
        {"message_index": 0, "issue": "vague subject", "suggestion": "be specific"},
        {"message_index": 2, "issue": "not imperative", "suggestion": "use add"},
    ])
    notes = parse_review(payload)
    assert notes == [
        CommitMessageNote(0, "vague subject", "be specific"),
        CommitMessageNote(2, "not imperative", "use add"),
    ]


def test_parse_fenced_json_block() -> None:
    raw = (
        "Here are the issues:\n```json\n"
        '[{"message_index": 1, "issue": "too long", "suggestion": "trim it"}]\n'
        "```\n"
    )
    notes = parse_review(raw)
    assert notes == [CommitMessageNote(1, "too long", "trim it")]


def test_parse_bare_fence_block() -> None:
    raw = '```\n[{"message_index": 0, "issue": "x", "suggestion": "y"}]\n```'
    assert parse_review(raw) == [CommitMessageNote(0, "x", "y")]


# ----- parse_review: empty / no-JSON ------------------------------------

def test_parse_empty_string_returns_empty() -> None:
    assert parse_review("") == []


def test_parse_whitespace_returns_empty() -> None:
    assert parse_review("   \n  ") == []


def test_parse_empty_array_returns_empty() -> None:
    assert parse_review("[]") == []


def test_parse_no_json_returns_empty() -> None:
    assert parse_review("All commit messages look fine to me.") == []


def test_parse_invalid_json_returns_empty() -> None:
    assert parse_review("[{not valid json}]") == []


def test_parse_non_array_json_returns_empty() -> None:
    assert parse_review('{"message_index": 0}') == []


# ----- parse_review: skips malformed entries ----------------------------

def test_parse_skips_malformed_entries() -> None:
    payload = json.dumps([
        {"message_index": 0, "issue": "ok", "suggestion": "fix"},
        "not a dict",
        {"message_index": "one", "issue": "bad index", "suggestion": "s"},
        {"message_index": 1, "issue": 42, "suggestion": "non-string issue"},
        {"message_index": 2, "suggestion": "missing issue key"},
        {"message_index": 3, "issue": "good", "suggestion": "keep"},
    ])
    notes = parse_review(payload)
    assert notes == [
        CommitMessageNote(0, "ok", "fix"),
        CommitMessageNote(3, "good", "keep"),
    ]


def test_parse_rejects_bool_index() -> None:
    # bool is an int subclass; it must not pass as a message_index.
    payload = json.dumps([
        {"message_index": True, "issue": "x", "suggestion": "y"},
    ])
    assert parse_review(payload) == []


def test_parse_all_malformed_returns_empty() -> None:
    payload = json.dumps(["a", 1, None, {"issue": "no index"}])
    assert parse_review(payload) == []


# ----- schema -----------------------------------------------------------

def test_note_is_frozen() -> None:
    note = CommitMessageNote(0, "i", "s")
    try:
        note.issue = "changed"  # type: ignore[misc]
    except Exception:
        return
    raise AssertionError("CommitMessageNote should be frozen")

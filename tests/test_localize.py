"""Tests for the localization prompt builder + defensive parser.

Same defensive parser stance as :mod:`prthinker.commit_review`: a length
mismatch or malformed reply yields ``[]`` so the caller keeps the original
comments unchanged. We never crash the pipeline on a bad reply.
"""

from __future__ import annotations

import json

from prthinker.localize import (
    build_localization_prompt,
    parse_localized,
)


# ----- build_localization_prompt ----------------------------------------

def test_prompt_embeds_each_comment() -> None:
    comments = ["Use isinstance here", "Avoid bare except", "Add a docstring"]
    prompt = build_localization_prompt(comments, "zh-TW")
    for comment in comments:
        assert comment in prompt


def test_prompt_embeds_target_language() -> None:
    prompt = build_localization_prompt(["x"], "Traditional Chinese")
    assert "Traditional Chinese" in prompt


def test_prompt_numbers_comments_zero_based() -> None:
    prompt = build_localization_prompt(["a", "b"], "fr")
    assert "Comment 0" in prompt
    assert "Comment 1" in prompt


def test_prompt_reports_count() -> None:
    prompt = build_localization_prompt(["a", "b", "c"], "de")
    assert "3 code-review comment" in prompt


def test_prompt_empty_list() -> None:
    prompt = build_localization_prompt([], "ja")
    assert "0 code-review comment" in prompt
    assert "ja" in prompt


# ----- parse_localized: happy path --------------------------------------

def test_parse_clean_json_array() -> None:
    payload = json.dumps(["翻譯一", "翻譯二"])
    assert parse_localized(payload, expected=2) == ["翻譯一", "翻譯二"]


def test_parse_preserves_order() -> None:
    payload = json.dumps(["first", "second", "third"])
    assert parse_localized(payload, expected=3) == ["first", "second", "third"]


def test_parse_fenced_json_block() -> None:
    raw = 'Here you go:\n```json\n["traduction"]\n```\nDone.'
    assert parse_localized(raw, expected=1) == ["traduction"]


def test_parse_fenced_without_language_tag() -> None:
    raw = '```\n["a", "b"]\n```'
    assert parse_localized(raw, expected=2) == ["a", "b"]


# ----- parse_localized: round-trip --------------------------------------

def test_round_trip_through_json() -> None:
    items = ["comment one", "comment two", "comment three"]
    raw = json.dumps(items)
    assert parse_localized(raw, expected=len(items)) == items


# ----- parse_localized: mismatch / error / empty ------------------------

def test_parse_too_few_returns_empty() -> None:
    payload = json.dumps(["only one"])
    assert parse_localized(payload, expected=2) == []


def test_parse_too_many_returns_empty() -> None:
    payload = json.dumps(["a", "b", "c"])
    assert parse_localized(payload, expected=2) == []


def test_parse_non_json_returns_empty() -> None:
    assert parse_localized("this is not json at all", expected=1) == []


def test_parse_malformed_json_returns_empty() -> None:
    assert parse_localized('["unterminated", "arr', expected=2) == []


def test_parse_non_string_element_returns_empty() -> None:
    payload = json.dumps(["ok", 42])
    assert parse_localized(payload, expected=2) == []


def test_parse_empty_string_returns_empty() -> None:
    assert parse_localized("", expected=1) == []


def test_parse_non_array_json_returns_empty() -> None:
    assert parse_localized('{"not": "an array"}', expected=1) == []


# ----- parse_localized: boundaries --------------------------------------

def test_parse_empty_array_with_zero_expected() -> None:
    assert parse_localized("[]", expected=0) == []


def test_parse_empty_array_with_nonzero_expected() -> None:
    assert parse_localized("[]", expected=1) == []


def test_parse_single_element_boundary() -> None:
    assert parse_localized(json.dumps(["x"]), expected=1) == ["x"]

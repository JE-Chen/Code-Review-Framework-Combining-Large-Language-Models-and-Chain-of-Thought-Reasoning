"""Tests for the shared fence/prose-tolerant JSON extraction helpers.

These lock the balanced-scanner contract that every model-output parser
now shares: it must survive reasoning prose, non-JSON code fences, and
trailing text (the three shapes the old greedy regex mis-parsed) while
still abstaining cleanly on garbage.
"""

from __future__ import annotations

import json

from prthinker.lenient_json import (
    extract_json_array,
    extract_json_object,
    iter_json_arrays,
)


# ----- extract_json_array ---------------------------------------------------


def test_array_happy_path() -> None:
    assert extract_json_array('[{"id": 1}]') == [{"id": 1}]


def test_array_empty_reply_is_empty_list() -> None:
    assert extract_json_array("") == []
    assert extract_json_array("   \n ") == []


def test_array_explicit_empty_array() -> None:
    assert extract_json_array("[]") == []


def test_array_amid_prose() -> None:
    assert extract_json_array("noise [1, 2, 3] trailing") == [1, 2, 3]


def test_array_after_reasoning() -> None:
    raw = "Let me think. Finding 1 holds.\nFinal:\n[1, 2]"
    assert extract_json_array(raw) == [1, 2]


def test_array_ignores_non_json_code_fence() -> None:
    raw = "```python\nx = foo(bar[0], baz)\n```\n[1, 2, 3]"
    assert extract_json_array(raw) == [1, 2, 3]


def test_array_trailing_text_after_array() -> None:
    assert extract_json_array("[1, 2]\n\nHope this helps!") == [1, 2]


def test_array_last_valid_wins() -> None:
    raw = "example [1, 1]\nactual answer: [2, 2]"
    assert extract_json_array(raw) == [2, 2]


def test_array_bracket_inside_string() -> None:
    raw = json.dumps([{"note": "a]b[c"}])
    assert extract_json_array(raw) == [{"note": "a]b[c"}]


def test_array_nested_arrays_kept_whole() -> None:
    assert extract_json_array("[[1, 2], [3]]") == [[1, 2], [3]]


def test_array_no_array_returns_none() -> None:
    assert extract_json_array("no json here") is None


def test_array_unclosed_bracket_returns_none() -> None:
    assert extract_json_array('[{"id": 1}') is None


def test_array_object_only_returns_none() -> None:
    assert extract_json_array('{"a": 1}') is None


def test_array_fenced_json() -> None:
    assert extract_json_array('```json\n[{"id": 2}]\n```') == [{"id": 2}]


# ----- extract_json_object --------------------------------------------------


def test_object_happy_path() -> None:
    assert extract_json_object('{"a": 1}') == {"a": 1}


def test_object_fenced() -> None:
    assert extract_json_object('```json\n{"a": 1}\n```') == {"a": 1}


def test_object_after_prose_and_example() -> None:
    raw = 'context {"draft": true}\nanswer: {"type": "bug"}'
    assert extract_json_object(raw) == {"type": "bug"}


def test_object_nested_kept_whole() -> None:
    assert extract_json_object('{"a": {"b": 1}}') == {"a": {"b": 1}}


def test_object_brace_inside_string() -> None:
    assert extract_json_object('{"note": "a}b{c"}') == {"note": "a}b{c"}


def test_object_none_when_absent() -> None:
    assert extract_json_object("no object here") is None


def test_object_array_only_returns_none() -> None:
    assert extract_json_object("[1, 2, 3]") is None


# ----- iter_json_arrays -----------------------------------------------------


def test_iter_json_arrays_yields_each_top_level_span() -> None:
    assert list(iter_json_arrays("[1] and [2, 3]")) == ["[1]", "[2, 3]"]


def test_iter_json_arrays_none_when_no_bracket() -> None:
    assert list(iter_json_arrays("plain text")) == []

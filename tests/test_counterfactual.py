"""Tests for the counterfactual-review schema + parser.

Same defensive parser stance as :mod:`reviewmind.findings`: malformed
output drops nothing real; we never crash the pipeline on a bad
counterfactual step.
"""

from __future__ import annotations

import json

from reviewmind.counterfactual import parse_counterfactuals
from reviewmind.schemas import CounterfactualBlock, CounterfactualOption


# ----- schema -----------------------------------------------------------

def test_option_default_tradeoffs_is_empty_dict() -> None:
    opt = CounterfactualOption(label="x", rationale="r")
    assert opt.tradeoffs == {}


def test_block_validates_finding_index_negative_rejected() -> None:
    # Pydantic enforces ge=0 on finding_index.
    try:
        CounterfactualBlock(finding_index=-1, options=[])
    except Exception:
        return
    raise AssertionError("finding_index=-1 should be rejected")


# ----- parser: happy paths ----------------------------------------------

def test_parse_clean_json_array() -> None:
    payload = json.dumps([
        {
            "finding_index": 0,
            "options": [
                {"label": "A", "rationale": "ra"},
                {"label": "B", "rationale": "rb",
                 "tradeoffs": {"performance": "O(n) vs O(n log n)"}},
            ],
        },
    ])
    blocks = parse_counterfactuals(payload, total_findings=1)
    assert len(blocks) == 1
    assert blocks[0].finding_index == 0
    assert blocks[0].options[1].tradeoffs == {"performance": "O(n) vs O(n log n)"}


def test_parse_inside_fenced_block() -> None:
    payload = (
        "Here you go:\n```json\n"
        + json.dumps([{
            "finding_index": 1,
            "options": [
                {"label": "A", "rationale": "ra"},
                {"label": "B", "rationale": "rb"},
            ],
        }])
        + "\n```"
    )
    blocks = parse_counterfactuals(payload, total_findings=3)
    assert [b.finding_index for b in blocks] == [1]


# ----- parser: filtering ------------------------------------------------

def test_parser_drops_out_of_range_indices() -> None:
    payload = json.dumps([
        {"finding_index": 0, "options": [
            {"label": "A", "rationale": "."},
            {"label": "B", "rationale": "."},
        ]},
        {"finding_index": 99, "options": [
            {"label": "A", "rationale": "."},
            {"label": "B", "rationale": "."},
        ]},
    ])
    blocks = parse_counterfactuals(payload, total_findings=1)
    assert [b.finding_index for b in blocks] == [0]


def test_parser_drops_single_option_blocks() -> None:
    payload = json.dumps([{
        "finding_index": 0,
        "options": [{"label": "only", "rationale": "."}],
    }])
    blocks = parse_counterfactuals(payload, total_findings=1)
    assert blocks == []


# ----- parser: safety ---------------------------------------------------

def test_parser_returns_empty_on_garbage() -> None:
    assert parse_counterfactuals("not json at all", total_findings=5) == []
    assert parse_counterfactuals('{"unrelated": 1}', total_findings=5) == []
    assert parse_counterfactuals("[]", total_findings=5) == []


def test_parser_returns_empty_when_no_findings_to_anchor() -> None:
    payload = json.dumps([{
        "finding_index": 0,
        "options": [
            {"label": "A", "rationale": "."},
            {"label": "B", "rationale": "."},
        ],
    }])
    assert parse_counterfactuals(payload, total_findings=0) == []


def test_parser_drops_malformed_entries_but_keeps_valid() -> None:
    payload = json.dumps([
        "not a dict",
        {"finding_index": "not-an-int", "options": []},
        {
            "finding_index": 0,
            "options": [
                {"label": "A", "rationale": "."},
                {"label": "B", "rationale": "."},
            ],
        },
    ])
    blocks = parse_counterfactuals(payload, total_findings=1)
    assert [b.finding_index for b in blocks] == [0]

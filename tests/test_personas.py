"""Personas — prompt builder + conflict parser."""

from __future__ import annotations

import json

from prthinker.personas import (
    Persona,
    build_conflict_prompt,
    build_persona_prompt,
    parse_conflicts,
)
from prthinker.schemas import PersonaConflict


# ----- per-persona prompt builder ---------------------------------------

def test_build_persona_prompt_includes_lens_and_diff() -> None:
    parts = build_persona_prompt(Persona.SECURITY, diff_text="+hello\n")
    assert parts.persona is Persona.SECURITY
    assert "security" in parts.prompt.lower()
    assert "+hello" in parts.prompt


def test_each_persona_prompt_mentions_its_own_lens() -> None:
    for p in Persona:
        prompt = build_persona_prompt(p, diff_text="x").prompt
        # Each persona's prompt should at minimum mention the persona's
        # own lens by name.
        assert p.value.replace("_", " ") in prompt.lower() \
               or p.value in prompt.lower()


# ----- conflict prompt + parser -----------------------------------------

def _all_personas() -> set[Persona]:
    return set(Persona)


def test_build_conflict_prompt_lists_each_persona_output() -> None:
    outputs = {
        Persona.SECURITY:    "find injection",
        Persona.PERFORMANCE: "loop is O(n^2)",
    }
    prompt = build_conflict_prompt(outputs)
    assert "`security`" in prompt
    assert "`performance`" in prompt
    assert "find injection" in prompt


def test_parse_clean_conflict() -> None:
    raw = json.dumps([{
        "personas":   ["security", "performance"],
        "summary":    "rate-limit hash trades CPU for safety",
        "resolution": "team should weigh DOS risk vs throughput",
    }])
    out = parse_conflicts(raw, valid_personas=_all_personas())
    assert len(out) == 1
    assert isinstance(out[0], PersonaConflict)
    assert out[0].personas == ["security", "performance"]


def test_parse_inside_fenced_block() -> None:
    raw = '```json\n[{"personas":["security","readability"],"summary":"s","resolution":"r"}]\n```'
    out = parse_conflicts(raw, valid_personas=_all_personas())
    assert len(out) == 1


def test_parser_drops_single_persona_entries() -> None:
    raw = json.dumps([
        {"personas": ["security"], "summary": "lonely", "resolution": "x"},
        {
            "personas": ["security", "performance"],
            "summary": "real conflict",
            "resolution": "x",
        },
    ])
    out = parse_conflicts(raw, valid_personas=_all_personas())
    assert [c.summary for c in out] == ["real conflict"]


def test_parser_drops_unknown_persona_names() -> None:
    raw = json.dumps([{
        "personas": ["security", "not_a_persona"],
        "summary": "x",
        "resolution": "y",
    }])
    # After filtering, only "security" remains → less than 2 → dropped.
    out = parse_conflicts(raw, valid_personas=_all_personas())
    assert out == []


def test_parser_returns_empty_on_garbage() -> None:
    assert parse_conflicts("not json", valid_personas=_all_personas()) == []
    assert parse_conflicts("[]", valid_personas=_all_personas()) == []


def test_parser_drops_malformed_dicts() -> None:
    raw = json.dumps([
        "not a dict",
        {"personas": ["security", "performance"]},  # missing summary
        {
            "personas": ["security", "performance"],
            "summary": "kept",
            "resolution": "x",
        },
    ])
    out = parse_conflicts(raw, valid_personas=_all_personas())
    assert [c.summary for c in out] == ["kept"]

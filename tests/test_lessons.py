"""Tests for the derived-lessons store + parser.

Pure logic — the backend.generate() side of derive_lessons() is
exercised in the integration tests (with the existing FakeBackend);
here we test the parser + the store roundtrip.
"""

from __future__ import annotations

import json
from pathlib import Path

from prthinker.lessons import (
    LessonRule,
    LessonsStore,
    build_derive_prompt,
    format_lessons_block,
    parse_lessons,
)


# ----- prompt builder ---------------------------------------------------

def test_build_derive_prompt_renders_both_corpora() -> None:
    class _D:
        def __init__(self, path, comment, reason):
            self.path = path
            self.comment = comment
            self.reason = reason

    class _A:
        def __init__(self, path, comment, pr_number):
            self.path = path
            self.comment = comment
            self.pr_number = pr_number

    prompt = build_derive_prompt(
        dismissed=[_D("a.py", "noisy log", "false positive")],
        accepted=[_A("b.py", "use logger.info", 42)],
        max_rules=3,
    )
    assert "noisy log" in prompt
    assert "use logger.info" in prompt
    assert "false positive" in prompt
    assert "#42" in prompt or "PR" in prompt


def test_build_derive_prompt_handles_empty_corpora() -> None:
    prompt = build_derive_prompt(dismissed=[], accepted=[])
    assert "no dismissed" in prompt
    assert "no accepted" in prompt


# ----- parser -----------------------------------------------------------

def test_parse_lessons_clean_payload() -> None:
    raw = json.dumps([{
        "name": "log-level-irrelevant",
        "trigger": "diff adds a logger.debug call",
        "action": "do not flag the logging level as wrong",
    }])
    out = parse_lessons(raw, source_prs=(42, 43))
    assert len(out) == 1
    assert out[0].name == "log-level-irrelevant"
    assert out[0].derived_from_pr_numbers == (42, 43)
    assert out[0].ts > 0


def test_parse_lessons_drops_incomplete_entries() -> None:
    raw = json.dumps([
        {"name": "x", "trigger": "y"},  # missing action
        {"trigger": "y", "action": "z"},  # missing name
        {"name": "a", "trigger": "b", "action": "c"},  # complete
    ])
    out = parse_lessons(raw, source_prs=())
    assert [r.name for r in out] == ["a"]


def test_parse_lessons_inside_fenced_block() -> None:
    raw = (
        '```json\n'
        + json.dumps([{"name": "n", "trigger": "t", "action": "a"}])
        + '\n```'
    )
    out = parse_lessons(raw, source_prs=())
    assert len(out) == 1


def test_parse_lessons_returns_empty_on_garbage() -> None:
    assert parse_lessons("not json", source_prs=()) == []
    assert parse_lessons("[]", source_prs=()) == []


# ----- store roundtrip --------------------------------------------------

def test_store_append_then_iterate(tmp_path: Path) -> None:
    store = LessonsStore(tmp_path / "lessons.jsonl")
    store.append(LessonRule(name="r1", trigger="t1", action="a1", ts=1.0))
    store.append(LessonRule(name="r2", trigger="t2", action="a2", ts=2.0))
    out = list(store)
    assert [r.name for r in out] == ["r1", "r2"]


def test_store_reload_from_disk(tmp_path: Path) -> None:
    path = tmp_path / "lessons.jsonl"
    s1 = LessonsStore(path)
    s1.append(LessonRule(name="r1", trigger="t1", action="a1"))
    s2 = LessonsStore(path)
    assert [r.name for r in s2] == ["r1"]


def test_store_skips_malformed_rows(tmp_path: Path) -> None:
    path = tmp_path / "lessons.jsonl"
    path.write_text(
        "not json\n"
        + json.dumps({"name": "n", "trigger": "t", "action": "a"}) + "\n"
        + "\n",  # blank
        encoding="utf-8",
    )
    store = LessonsStore(path)
    assert [r.name for r in store] == ["n"]


# ----- format block -----------------------------------------------------

def test_format_lessons_block_empty_returns_empty_string() -> None:
    assert format_lessons_block([]) == ""


def test_format_lessons_block_includes_each_rule() -> None:
    rules = [
        LessonRule(name="r1", trigger="t1", action="a1"),
        LessonRule(name="r2", trigger="t2", action="a2"),
    ]
    block = format_lessons_block(rules)
    assert "r1" in block and "r2" in block
    assert "t1" in block and "a2" in block


def test_lesson_rule_is_frozen() -> None:
    r = LessonRule(name="n", trigger="t", action="a")
    try:
        r.name = "x"  # type: ignore[misc]
    except Exception:
        return
    raise AssertionError("LessonRule should be frozen")

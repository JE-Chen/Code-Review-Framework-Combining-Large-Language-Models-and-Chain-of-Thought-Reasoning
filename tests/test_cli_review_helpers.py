"""``prthinker.cli_review_helpers`` — shared adapter construction + lessons tail."""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from prthinker.cli_review_helpers import (
    _dialogue_from_lessons,
    build_platform_adapter,
)


def _adapter_args(**overrides: object) -> argparse.Namespace:
    base: dict[str, object] = {
        "platform": "github",
        "platform_base_url": None,
        "repo": "owner/repo",
        "github_token": "tok",
        "pr_number": 7,
        "marker": "<!--prthinker-->",
    }
    base.update(overrides)
    return argparse.Namespace(**base)


# --- build_platform_adapter ----------------------------------------------------

def test_build_platform_adapter_forwards_args(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, object] = {}
    sentinel = object()

    def _fake(kind, **kwargs):
        seen["kind"] = kind
        seen.update(kwargs)
        return sentinel

    monkeypatch.setattr("prthinker.platforms.create_platform_adapter", _fake)
    adapter = build_platform_adapter(_adapter_args())

    assert adapter is sentinel
    assert seen["kind"].value == "github"
    assert seen["repo"] == "owner/repo"
    assert seen["token"] == "tok"  # nosec B105 - test fixture, not a credential
    assert seen["pr_number"] == 7
    assert seen["comment_marker"] == "<!--prthinker-->"
    assert seen["base_url"] is None


def test_build_platform_adapter_passes_base_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: dict[str, object] = {}
    monkeypatch.setattr(
        "prthinker.platforms.create_platform_adapter",
        lambda kind, **kwargs: seen.update(kwargs),
    )
    build_platform_adapter(
        _adapter_args(platform="gitlab", platform_base_url="https://gl.example/api/v4")
    )
    assert seen["base_url"] == "https://gl.example/api/v4"


def test_build_platform_adapter_rejects_unknown_platform() -> None:
    with pytest.raises(ValueError):
        build_platform_adapter(_adapter_args(platform="sourcehut"))


# --- _dialogue_from_lessons tail selection -------------------------------------

def _write_lessons(path: Path, names: list[str]) -> None:
    from prthinker.lessons import LessonRule, LessonsStore

    store = LessonsStore(path)
    for name in names:
        store.append(LessonRule(name=name, trigger=f"when {name}", action="do it"))


def test_dialogue_from_lessons_keeps_only_tail(tmp_path: Path) -> None:
    lessons_path = tmp_path / "lessons.jsonl"
    _write_lessons(lessons_path, ["first", "second", "third"])
    args = argparse.Namespace(lessons_path=str(lessons_path), lessons_top_k=2)

    block = _dialogue_from_lessons(args)

    assert "second" in block and "third" in block
    assert "first" not in block


def test_dialogue_from_lessons_top_k_larger_than_corpus(tmp_path: Path) -> None:
    lessons_path = tmp_path / "lessons.jsonl"
    _write_lessons(lessons_path, ["only"])
    args = argparse.Namespace(lessons_path=str(lessons_path), lessons_top_k=5)
    assert "only" in _dialogue_from_lessons(args)


def test_dialogue_from_lessons_missing_store_returns_empty(tmp_path: Path) -> None:
    args = argparse.Namespace(
        lessons_path=str(tmp_path / "absent.jsonl"), lessons_top_k=5
    )
    assert _dialogue_from_lessons(args) == ""

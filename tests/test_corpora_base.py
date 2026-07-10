"""Tests for the shared JSONL corpus store base + embedding helper."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

import pytest

from prthinker.corpora_base import JsonlCorpusStore, embed_store_comments


@dataclass
class _Row:
    key: str
    note: str = ""

    def to_jsonl(self) -> str:
        return json.dumps({"key": self.key, "note": self.note}, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict) -> "_Row":
        return cls(key=str(data.get("key", "")), note=str(data.get("note", "")))


class _Store(JsonlCorpusStore[_Row]):
    """Store subclass that records the load hooks for assertions."""

    def __init__(self, path: Path) -> None:
        self.malformed: list[str] = []
        self.loads = 0
        super().__init__(path, _Row.from_dict)

    def _on_malformed(self, raw: str) -> None:
        self.malformed.append(raw)

    def _on_loaded(self) -> None:
        self.loads += 1


# ----- load -------------------------------------------------------------

def test_missing_file_starts_empty(tmp_path: Path) -> None:
    store = _Store(tmp_path / "rows.jsonl")
    assert len(store) == 0
    assert list(store) == []
    assert store.loads == 0  # no file -> no load pass


def test_empty_file_loads_zero_rows(tmp_path: Path) -> None:
    path = tmp_path / "rows.jsonl"
    path.write_text("", encoding="utf-8")
    store = _Store(path)
    assert len(store) == 0
    assert store.loads == 1


def test_blank_lines_are_skipped(tmp_path: Path) -> None:
    path = tmp_path / "rows.jsonl"
    path.write_text(
        "\n" + json.dumps({"key": "a"}) + "\n\n" + json.dumps({"key": "b"}) + "\n",
        encoding="utf-8",
    )
    store = _Store(path)
    assert [r.key for r in store] == ["a", "b"]
    assert store.malformed == []


def test_malformed_line_invokes_hook_and_is_skipped(tmp_path: Path) -> None:
    path = tmp_path / "rows.jsonl"
    path.write_text(
        "not json\n" + json.dumps({"key": "ok"}) + "\n", encoding="utf-8"
    )
    store = _Store(path)
    assert [r.key for r in store] == ["ok"]
    assert store.malformed == ["not json"]


def test_on_loaded_hook_runs_once_per_construction(tmp_path: Path) -> None:
    path = tmp_path / "rows.jsonl"
    path.write_text(json.dumps({"key": "a"}) + "\n", encoding="utf-8")
    store = _Store(path)
    assert store.loads == 1


def test_unicode_round_trips(tmp_path: Path) -> None:
    path = tmp_path / "rows.jsonl"
    store = _Store(path)
    store.append(_Row(key="中文", note="註解"))
    reloaded = _Store(path)
    assert list(reloaded) == [_Row(key="中文", note="註解")]


# ----- append (append-only semantics) ------------------------------------

def test_append_then_reload_round_trips(tmp_path: Path) -> None:
    path = tmp_path / "rows.jsonl"
    store = _Store(path)
    store.append(_Row(key="a", note="1"))
    store.append(_Row(key="b", note="2"))
    assert len(store) == 2
    reloaded = _Store(path)
    assert list(reloaded) == [_Row(key="a", note="1"), _Row(key="b", note="2")]


def test_append_never_rewrites_existing_lines(tmp_path: Path) -> None:
    path = tmp_path / "rows.jsonl"
    first_line = json.dumps({"key": "old", "note": "keep"})
    path.write_text(first_line + "\n", encoding="utf-8")
    store = _Store(path)
    store.append(_Row(key="new"))
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines[0] == first_line  # historical row untouched
    assert len(lines) == 2


def test_append_creates_parent_directories(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "deep" / "rows.jsonl"
    store = _Store(path)
    store.append(_Row(key="a"))
    assert path.exists()


# ----- embed_store_comments ----------------------------------------------

@pytest.fixture
def fake_faiss(monkeypatch):
    """Install a deterministic ``codes.util.faiss_util`` stub."""
    calls: list[str] = []

    def get_embedding(text: str):
        calls.append(text)
        return f"vec:{text}"

    module = SimpleNamespace(get_embedding=get_embedding)
    monkeypatch.setitem(sys.modules, "codes.util.faiss_util", module)
    return calls


def test_embed_store_comments_pairs_rows_in_order(fake_faiss) -> None:
    rows = [SimpleNamespace(comment="one"), SimpleNamespace(comment="two")]
    pairs = embed_store_comments(rows)
    assert pairs == [(rows[0], "vec:one"), (rows[1], "vec:two")]
    assert fake_faiss == ["one", "two"]


def test_embed_store_comments_empty_input(fake_faiss) -> None:
    assert embed_store_comments([]) == []
    assert fake_faiss == []

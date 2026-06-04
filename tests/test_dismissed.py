"""Behaviour tests for the DismissedFilter similarity-based drop logic."""

from __future__ import annotations

import sys
from types import SimpleNamespace

import numpy as np
import pytest

from prthinker.dismissed import (
    DismissedExample,
    DismissedExamplesStore,
    DismissedFilter,
)
from prthinker.schemas import InlineFinding


@pytest.fixture
def fake_faiss(monkeypatch):
    """Install a deterministic ``codes.util.faiss_util`` stub via embeddings map."""
    embeddings: dict[str, np.ndarray] = {}

    def get_embedding(text: str) -> np.ndarray:
        return embeddings[text]

    module = SimpleNamespace(get_embedding=get_embedding)
    monkeypatch.setitem(sys.modules, "codes.util.faiss_util", module)
    return embeddings


def _unit(*components: float) -> np.ndarray:
    vec = np.array(components, dtype=float)
    norm = np.linalg.norm(vec)
    return vec / norm if norm else vec


def _store_with(tmp_path, examples: list[DismissedExample]) -> DismissedExamplesStore:
    store = DismissedExamplesStore(tmp_path / "dismissed.jsonl")
    for ex in examples:
        store.append(ex)
    return store


def _finding(path: str, line: int, comment: str) -> InlineFinding:
    return InlineFinding(path=path, line=line, comment=comment)


def test_filter_empty_findings_returns_empty(tmp_path):
    store = _store_with(tmp_path, [DismissedExample("a.py", "c", "r")])
    flt = DismissedFilter(store)
    assert flt.filter([]) == []


def test_filter_empty_store_returns_all(tmp_path):
    store = _store_with(tmp_path, [])
    flt = DismissedFilter(store)
    findings = [_finding("a.py", 1, "hello")]
    assert flt.filter(findings) == findings


def test_filter_drops_similar_finding(tmp_path, fake_faiss):
    store = _store_with(tmp_path, [DismissedExample("a.py", "noise", "false-positive")])
    fake_faiss["noise"] = _unit(1.0, 0.0)
    fake_faiss["very noisy"] = _unit(1.0, 0.0)  # identical direction -> sim 1.0
    flt = DismissedFilter(store, threshold=0.85)
    kept = flt.filter([_finding("a.py", 3, "very noisy")])
    assert kept == []


def test_filter_keeps_dissimilar_finding(tmp_path, fake_faiss):
    store = _store_with(tmp_path, [DismissedExample("a.py", "noise", "false-positive")])
    fake_faiss["noise"] = _unit(1.0, 0.0)
    fake_faiss["real bug"] = _unit(0.0, 1.0)  # orthogonal -> sim 0.0
    flt = DismissedFilter(store, threshold=0.85)
    finding = _finding("a.py", 3, "real bug")
    assert flt.filter([finding]) == [finding]


def test_filter_boundary_at_threshold_drops(tmp_path, fake_faiss):
    store = _store_with(tmp_path, [DismissedExample("a.py", "noise", "r")])
    fake_faiss["noise"] = _unit(1.0, 0.0)
    fake_faiss["candidate"] = _unit(1.0, 0.0)
    flt = DismissedFilter(store, threshold=1.0)  # sim == threshold -> dropped
    assert flt.filter([_finding("a.py", 1, "candidate")]) == []


def test_filter_path_scoped_ignores_other_files(tmp_path, fake_faiss):
    store = _store_with(tmp_path, [DismissedExample("other.py", "noise", "r")])
    fake_faiss["noise"] = _unit(1.0, 0.0)
    fake_faiss["candidate"] = _unit(1.0, 0.0)  # would be dropped if path matched
    flt = DismissedFilter(store, threshold=0.85, path_scoped=True)
    finding = _finding("a.py", 1, "candidate")
    assert flt.filter([finding]) == [finding]


def test_filter_path_scoped_drops_same_file(tmp_path, fake_faiss):
    store = _store_with(tmp_path, [DismissedExample("a.py", "noise", "r")])
    fake_faiss["noise"] = _unit(1.0, 0.0)
    fake_faiss["candidate"] = _unit(1.0, 0.0)
    flt = DismissedFilter(store, threshold=0.85, path_scoped=True)
    assert flt.filter([_finding("a.py", 1, "candidate")]) == []


def test_filter_picks_best_match_across_examples(tmp_path, fake_faiss):
    store = _store_with(
        tmp_path,
        [
            DismissedExample("a.py", "weak", "r1"),
            DismissedExample("a.py", "strong", "r2"),
        ],
    )
    fake_faiss["weak"] = _unit(1.0, 1.0)
    fake_faiss["strong"] = _unit(1.0, 0.0)
    fake_faiss["candidate"] = _unit(1.0, 0.0)  # exact match to "strong"
    flt = DismissedFilter(store, threshold=0.95)
    assert flt.filter([_finding("a.py", 1, "candidate")]) == []

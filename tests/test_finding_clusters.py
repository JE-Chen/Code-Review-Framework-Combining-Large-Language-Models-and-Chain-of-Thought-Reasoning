"""Tests for the cross-PR finding-cluster store + clustering pass.

We use small synthetic numpy embeddings so the cosine-similarity logic
is exercised without invoking any real embedding model.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from prthinker.finding_clusters import (
    FindingClusterStore,
    FindingFingerprint,
    format_clusters_block,
    greedy_cluster,
)


def _emb(*v: float) -> np.ndarray:
    return np.array(v, dtype="float32")


def _fp(
    *, pr: int = 1, file: str = "a.py", line: int = 1,
    comment: str = "comment", embedding: np.ndarray | None = None,
    ts: float = 1.0,
) -> FindingFingerprint:
    return FindingFingerprint(
        pr_number=pr, repo="o/r", file_path=file, line=line,
        comment=comment, norm_comment=comment.lower().strip(),
        embedding=embedding if embedding is not None else _emb(1, 0, 0),
        ts=ts,
    )


# ----- greedy clustering ------------------------------------------------

def test_no_fingerprints_returns_empty_list() -> None:
    assert greedy_cluster([]) == []


def test_singletons_below_min_size_are_dropped() -> None:
    diverse = [
        _fp(comment="a", embedding=_emb(1, 0, 0)),
        _fp(comment="b", embedding=_emb(0, 1, 0)),
        _fp(comment="c", embedding=_emb(0, 0, 1)),
    ]
    assert greedy_cluster(diverse, min_cluster_size=2) == []


def test_high_similarity_cluster_emerges() -> None:
    # 5 near-identical vectors should land in one cluster of size 5.
    pts = [
        _fp(comment=f"comment {i}", embedding=_emb(1, 0.01 * i, 0))
        for i in range(5)
    ]
    out = greedy_cluster(pts, similarity_threshold=0.85, min_cluster_size=3)
    assert len(out) == 1
    assert out[0].size == 5
    assert out[0].representative.startswith("comment ")


def test_two_separate_clusters_emerge() -> None:
    group_a = [_fp(comment=f"a{i}", embedding=_emb(1, 0, 0)) for i in range(3)]
    group_b = [_fp(comment=f"b{i}", embedding=_emb(0, 1, 0)) for i in range(3)]
    out = greedy_cluster(group_a + group_b, similarity_threshold=0.9, min_cluster_size=3)
    assert len(out) == 2
    assert {c.size for c in out} == {3}


def test_clusters_sorted_largest_first() -> None:
    small = [_fp(comment=f"s{i}", embedding=_emb(1, 0, 0)) for i in range(2)]
    big = [_fp(comment=f"b{i}", embedding=_emb(0, 1, 0)) for i in range(5)]
    out = greedy_cluster(small + big, similarity_threshold=0.95, min_cluster_size=2)
    assert [c.size for c in out] == [5, 2]


# ----- store roundtrip --------------------------------------------------

def test_store_add_then_load(tmp_path: Path) -> None:
    store = FindingClusterStore(tmp_path / "c.sqlite")
    store.add(
        pr_number=1, repo="o/r", file_path="a.py", line=1,
        comment="noisy log", embedding=_emb(1, 0, 0),
    )
    out = store.load()
    assert len(out) == 1
    assert out[0].pr_number == 1
    assert out[0].comment == "noisy log"
    np_close = np.allclose(out[0].embedding, _emb(1, 0, 0))
    assert np_close


def test_store_filter_by_repo(tmp_path: Path) -> None:
    store = FindingClusterStore(tmp_path / "c.sqlite")
    for repo in ("o/a", "o/b", "o/a"):
        store.add(
            pr_number=1, repo=repo, file_path="x.py", line=1,
            comment="c", embedding=_emb(1, 0, 0),
        )
    assert len(store.load(repo="o/a")) == 2
    assert len(store.load(repo="o/b")) == 1


def test_store_len_matches(tmp_path: Path) -> None:
    store = FindingClusterStore(tmp_path / "c.sqlite")
    assert len(store) == 0
    for i in range(3):
        store.add(
            pr_number=1, repo="o/r", file_path="x.py", line=i + 1,
            comment="c", embedding=_emb(1, 0, 0),
        )
    assert len(store) == 3


# ----- format block -----------------------------------------------------

def test_format_clusters_block_empty_returns_empty_string() -> None:
    assert format_clusters_block([]) == ""


def test_format_clusters_block_includes_size_and_rep() -> None:
    from prthinker.finding_clusters import FindingCluster
    members = [_fp(comment="noisy log", file="x.py") for _ in range(4)]
    cluster = FindingCluster(
        members=members, representative="noisy log statement", size=4,
    )
    block = format_clusters_block([cluster])
    assert "Recurring findings" in block
    assert "noisy log statement" in block
    assert "| 4 |" in block

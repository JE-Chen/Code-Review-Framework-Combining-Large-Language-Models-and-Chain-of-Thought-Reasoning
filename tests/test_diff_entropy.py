"""Diff entropy calculator — pure data over synthetic FileDiff lists."""

from __future__ import annotations

from prthinker.diff import FileDiff
from prthinker.diff_entropy import compute_entropy


def _fd(path: str, *, added: int = 0, removed: int = 0,
        is_binary: bool = False, is_deleted: bool = False) -> FileDiff:
    parts = [f"diff --git a/{path} b/{path}", "@@ +1 @@"]
    parts.extend(f"+a{i}" for i in range(added))
    parts.extend(f"-r{i}" for i in range(removed))
    return FileDiff(
        path=path, raw="\n".join(parts),
        is_binary=is_binary, is_deleted=is_deleted,
    )


def test_empty_diff_returns_focused() -> None:
    e = compute_entropy([])
    assert e.verdict == "focused"
    assert e.score == 0.0


def test_single_file_focused() -> None:
    e = compute_entropy([_fd("src/a.py", added=10, removed=2)])
    assert e.verdict == "focused"
    assert e.file_count == 1
    assert e.added_lines == 10
    assert e.removed_lines == 2


def test_many_files_same_dir_still_focused_ish() -> None:
    diffs = [_fd(f"src/a{i}.py", added=20) for i in range(8)]
    e = compute_entropy(diffs)
    # 8 files but all in one top-level dir → dispersion == 0
    assert e.dispersion_entropy == 0.0


def test_many_files_many_dirs_increases_dispersion() -> None:
    diffs = [
        _fd("backend/a.py", added=20),
        _fd("frontend/b.ts", added=20),
        _fd("docs/c.md", added=20),
        _fd("ops/d.sh", added=20),
    ]
    e = compute_entropy(diffs)
    assert e.dispersion_entropy > 1.0  # Shannon > 1 bit for 4 equal


def test_diff_bomb_classification() -> None:
    # 60 files spread across 6 top-level dirs, 100 added lines each.
    diffs = []
    for d in range(6):
        for i in range(10):
            diffs.append(_fd(f"dir{d}/file{i}.py", added=100))
    e = compute_entropy(diffs)
    assert e.verdict == "bomb"
    assert e.score >= 0.7


def test_binary_and_deleted_files_excluded() -> None:
    diffs = [
        _fd("src/a.py", added=10),
        _fd("img.png", is_binary=True),
        _fd("removed.py", is_deleted=True),
    ]
    e = compute_entropy(diffs)
    assert e.file_count == 1
    assert "img.png" not in (e.top_dir_distribution or {})


def test_thresholds_are_orderable() -> None:
    from prthinker.diff_entropy import DEFAULT_THRESHOLDS
    lo, hi = DEFAULT_THRESHOLDS
    assert 0 < lo < hi < 1


def test_top_dir_root_for_top_level_files() -> None:
    diffs = [_fd("README.md", added=10)]
    e = compute_entropy(diffs)
    # The only top dir is "README.md" (parts[0] of the path).
    assert e.top_dir_distribution == {"README.md": 1}


def test_score_monotone_in_size() -> None:
    small = compute_entropy([_fd("src/a.py", added=5)])
    big = compute_entropy(
        [_fd(f"src/{i}.py", added=200) for i in range(20)]
    )
    assert big.score > small.score

"""Pure-logic tests for the force-push differential review cache."""

from __future__ import annotations

import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from prthinker.diff import parse_unified_diff
from prthinker.review_cache import CacheKey, ReviewCache
from prthinker.schemas import InlineFinding


def _finding(line: int = 4, comment: str = "x") -> InlineFinding:
    return InlineFinding(
        path="a.py", line=line, severity="warning", comment=comment,
    )


# ----- store ------------------------------------------------------------

def test_get_returns_none_on_miss(tmp_path: Path) -> None:
    store = ReviewCache(tmp_path / "c.sqlite")
    key = CacheKey(pr_number=1, repo="o/r", file_path="a.py", hunk_sha256="abc")
    assert store.get(key) is None


def test_put_then_get_roundtrip(tmp_path: Path) -> None:
    store = ReviewCache(tmp_path / "c.sqlite")
    key = CacheKey(pr_number=1, repo="o/r", file_path="a.py", hunk_sha256="abc")
    store.put(key, [_finding(4), _finding(7)], backend="openai", model="gpt")
    out = store.get(key)
    assert out is not None
    assert [f.line for f in out] == [4, 7]


def test_put_replace_on_same_key(tmp_path: Path) -> None:
    store = ReviewCache(tmp_path / "c.sqlite")
    key = CacheKey(pr_number=1, repo="o/r", file_path="a.py", hunk_sha256="abc")
    store.put(key, [_finding(4)], backend="b", model="m")
    store.put(key, [_finding(99, "rewritten")], backend="b", model="m")
    out = store.get(key)
    assert out is not None
    assert out[0].line == 99
    assert out[0].comment == "rewritten"


def test_evict_pr_drops_all_files(tmp_path: Path) -> None:
    store = ReviewCache(tmp_path / "c.sqlite")
    for path in ("a.py", "b.py", "c.py"):
        key = CacheKey(pr_number=1, repo="o/r", file_path=path, hunk_sha256="h")
        store.put(key, [_finding()], backend="b", model="m")
    assert store.evict_pr(1, "o/r") == 3
    assert store.get(
        CacheKey(pr_number=1, repo="o/r", file_path="a.py", hunk_sha256="h")
    ) is None


def test_cross_pr_isolation(tmp_path: Path) -> None:
    store = ReviewCache(tmp_path / "c.sqlite")
    key_a = CacheKey(pr_number=1, repo="o/r", file_path="a.py", hunk_sha256="h")
    key_b = CacheKey(pr_number=2, repo="o/r", file_path="a.py", hunk_sha256="h")
    store.put(key_a, [_finding(10)], backend="b", model="m")
    # Same file + hash on a different PR must NOT see PR1's findings.
    assert store.get(key_b) is None


# ----- diff hashing -----------------------------------------------------

_TINY_DIFF = """\
diff --git a/foo.py b/foo.py
index 1..2 100644
--- a/foo.py
+++ b/foo.py
@@ -1,3 +1,4 @@
 import os
+import sys
 def f():
     return 1
"""


def test_content_sha256_stable() -> None:
    [fd1] = parse_unified_diff(_TINY_DIFF)
    [fd2] = parse_unified_diff(_TINY_DIFF)
    assert fd1.content_sha256() == fd2.content_sha256()


def test_content_sha256_changes_when_added_line_changes() -> None:
    [fd1] = parse_unified_diff(_TINY_DIFF)
    modified = _TINY_DIFF.replace("+import sys", "+import json")
    [fd2] = parse_unified_diff(modified)
    assert fd1.content_sha256() != fd2.content_sha256()


def test_content_sha256_ignores_removed_lines() -> None:
    # Two diffs that differ only in which lines they show as '-' but
    # leave the same new-side content should hash the same.
    base = """\
diff --git a/foo.py b/foo.py
--- a/foo.py
+++ b/foo.py
@@ -1,2 +1,2 @@
-old1
 unchanged
+added
"""
    other = """\
diff --git a/foo.py b/foo.py
--- a/foo.py
+++ b/foo.py
@@ -1,3 +1,2 @@
-old1
-old2
 unchanged
+added
"""
    [a] = parse_unified_diff(base)
    [b] = parse_unified_diff(other)
    assert a.content_sha256() == b.content_sha256()

# ----- thread-local connections ------------------------------------------

def test_connection_reused_within_a_thread(tmp_path: Path) -> None:
    store = ReviewCache(tmp_path / "c.sqlite")
    assert store._conn() is store._conn()  # lazy-created once, then cached


def test_each_thread_gets_its_own_connection(tmp_path: Path) -> None:
    store = ReviewCache(tmp_path / "c.sqlite")
    main_conn = store._conn()
    seen: list[object] = []

    def grab() -> None:
        seen.append(store._conn())

    thread = threading.Thread(target=grab)
    thread.start()
    thread.join()
    assert len(seen) == 1
    assert seen[0] is not main_conn


def test_put_get_across_thread_pool(tmp_path: Path) -> None:
    # get/put are called from the per-file ThreadPoolExecutor; rows
    # written by pool threads must be visible everywhere.
    store = ReviewCache(tmp_path / "c.sqlite")

    def put_one(index: int) -> None:
        key = CacheKey(
            pr_number=1, repo="o/r", file_path=f"f{index}.py", hunk_sha256="h",
        )
        store.put(key, [_finding(index + 1)], backend="b", model="m")

    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(put_one, range(8)))

    def get_one(index: int) -> int:
        key = CacheKey(
            pr_number=1, repo="o/r", file_path=f"f{index}.py", hunk_sha256="h",
        )
        found = store.get(key)
        assert found is not None
        return found[0].line

    with ThreadPoolExecutor(max_workers=4) as pool:
        assert sorted(pool.map(get_one, range(8))) == list(range(1, 9))
    # And the main thread (a different connection) sees every row too.
    assert store.evict_pr(1, "o/r") == 8

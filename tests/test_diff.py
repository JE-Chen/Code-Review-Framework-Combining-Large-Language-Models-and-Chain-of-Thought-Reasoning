"""Diff parser — line tracking is what drives inline-comment validation.

Any off-by-one here means we either drop legit findings or send GitHub
comments on lines it will reject.
"""

from __future__ import annotations

import hashlib

from prthinker.diff import (
    FileDiff,
    _iter_new_side,
    iter_added_lines,
    new_side_content,
    parse_unified_diff,
)


def test_empty_diff_returns_no_files() -> None:
    assert parse_unified_diff("") == []
    assert parse_unified_diff("   \n   ") == []


def test_single_file_tracks_added_and_context_lines() -> None:
    diff = (
        "diff --git a/foo.py b/foo.py\n"
        "index 0000000..1111111 100644\n"
        "--- a/foo.py\n"
        "+++ b/foo.py\n"
        "@@ -1,3 +1,5 @@\n"
        " def hello():\n"
        "-    print('hi')\n"
        "+    print('hello')\n"
        "+    print('world')\n"
        "     return 0\n"
    )
    files = parse_unified_diff(diff)
    assert len(files) == 1
    f = files[0]
    assert f.path == "foo.py"
    # Context line + 2 added + final context = lines 1..4 on the new side.
    assert sorted(f.new_lines) == [1, 2, 3, 4]
    assert not f.is_binary
    assert not f.is_deleted


def test_new_file_lines_count_from_one() -> None:
    diff = (
        "diff --git a/bar.py b/bar.py\n"
        "new file mode 100644\n"
        "--- /dev/null\n"
        "+++ b/bar.py\n"
        "@@ -0,0 +1,2 @@\n"
        "+x = 1\n"
        "+y = 2\n"
    )
    files = parse_unified_diff(diff)
    assert len(files) == 1
    assert files[0].path == "bar.py"
    assert sorted(files[0].new_lines) == [1, 2]


def test_deleted_file_is_flagged() -> None:
    diff = (
        "diff --git a/gone.py b/gone.py\n"
        "deleted file mode 100644\n"
        "--- a/gone.py\n"
        "+++ /dev/null\n"
        "@@ -1,2 +0,0 @@\n"
        "-was_here = 1\n"
        "-also = 2\n"
    )
    files = parse_unified_diff(diff)
    assert len(files) == 1
    assert files[0].is_deleted


def test_binary_file_is_flagged() -> None:
    diff = (
        "diff --git a/logo.png b/logo.png\n"
        "Binary files a/logo.png and b/logo.png differ\n"
    )
    files = parse_unified_diff(diff)
    assert len(files) == 1
    assert files[0].is_binary


def test_multiple_files_split_independently() -> None:
    diff = (
        "diff --git a/a.py b/a.py\n"
        "--- a/a.py\n"
        "+++ b/a.py\n"
        "@@ -1 +1,2 @@\n"
        " x\n"
        "+y\n"
        "diff --git a/b.py b/b.py\n"
        "--- a/b.py\n"
        "+++ b/b.py\n"
        "@@ -10,1 +10,2 @@\n"
        " z\n"
        "+w\n"
    )
    files = parse_unified_diff(diff)
    assert [f.path for f in files] == ["a.py", "b.py"]
    assert sorted(files[0].new_lines) == [1, 2]
    # File b's hunk starts at new line 10.
    assert sorted(files[1].new_lines) == [10, 11]


def test_commentable_lines_matches_new_lines() -> None:
    diff = (
        "diff --git a/x.py b/x.py\n"
        "--- a/x.py\n"
        "+++ b/x.py\n"
        "@@ -1,2 +1,3 @@\n"
        " a\n"
        "+b\n"
        " c\n"
    )
    f = parse_unified_diff(diff)[0]
    assert f.commentable_lines() == f.new_lines == {1, 2, 3}


def test_new_side_content_maps_lines_to_text() -> None:
    diff = (
        "diff --git a/a.py b/a.py\n"
        "--- a/a.py\n"
        "+++ b/a.py\n"
        "@@ -1,2 +1,3 @@\n"
        " context\n"
        "-removed\n"
        "+added one\n"
        "+added two\n"
    )
    content = new_side_content(diff)
    # New side: line 1 = context, 2 = added one, 3 = added two.
    assert content["a.py"] == {1: "context", 2: "added one", 3: "added two"}


def test_new_side_content_empty_diff() -> None:
    assert new_side_content("") == {}

# ----- shared new-side walker (_iter_new_side) ---------------------------

_WALKER_DIFF = (
    "diff --git a/w.py b/w.py\n"
    "--- a/w.py\n"
    "+++ b/w.py\n"
    "@@ -1,2 +10,3 @@\n"
    " context\n"
    "-removed\n"
    "+added one\n"
    "+added two\n"
)


def test_iter_new_side_yields_numbered_content_and_added_flag() -> None:
    assert list(_iter_new_side(_WALKER_DIFF)) == [
        (10, "context", False),
        (11, "added one", True),
        (12, "added two", True),
    ]


def test_iter_new_side_skips_preamble_by_default() -> None:
    # '+++ b/…' is metadata and the '--- a/…' header never matches the
    # '+'/' ' checks; nothing before '@@' may leak into the walk.
    assert list(_iter_new_side("+loose add\n context\n")) == []


def test_iter_new_side_includes_preamble_when_asked() -> None:
    out = list(_iter_new_side("+loose add\n context\n", in_hunks_only=False))
    assert [(content, added) for _, content, added in out] == [
        ("loose add", True), ("context", False),
    ]


def test_iter_added_lines_emits_only_added_lines() -> None:
    assert iter_added_lines(_WALKER_DIFF) == [
        (11, "added one"), (12, "added two"),
    ]


def test_iter_added_lines_empty_for_deletion_only_hunk() -> None:
    diff = "@@ -1,2 +0,0 @@\n-gone\n-also gone\n"
    assert iter_added_lines(diff) == []


# ----- content_sha256 (differential-review cache key) --------------------

# Pinned digests: content_sha256 keys the differential-review cache, so
# its output must never change across refactors — a silent change would
# invalidate (or worse, falsely hit) every existing cache row.
_PINNED_DIFF = (
    "diff --git a/foo.py b/foo.py\n"
    "index 1..2 100644\n"
    "--- a/foo.py\n"
    "+++ b/foo.py\n"
    "@@ -1,3 +1,4 @@\n"
    " import os\n"
    "+import sys\n"
    " def f():\n"
    "     return 1\n"
)
_PINNED_SHA = "6415508cc0f5038bb644407455894057b994dbd0f18cef15c6fd414f42fe0339"
# sha256 of b"" — a raw with no new-side lines hashes the empty string.
_EMPTY_SHA = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def test_content_sha256_matches_pinned_digest() -> None:
    [fd] = parse_unified_diff(_PINNED_DIFF)
    assert fd.content_sha256() == _PINNED_SHA


def test_content_sha256_empty_and_headerless_raw() -> None:
    assert FileDiff(path="x", raw="").content_sha256() == _EMPTY_SHA
    # Header/metadata-only raw contributes no new-side lines.
    assert FileDiff(path="x", raw="just prose\n").content_sha256() == _EMPTY_SHA


def test_content_sha256_headerless_plus_lines_still_hash() -> None:
    # Historical behaviour: the hasher never gated on hunk headers, so
    # +/space lines in a raw without any '@@' still count.
    raw = "+added\n context\n-removed\n+++ b/x\n"
    expected = hashlib.sha256(b"added\ncontext").hexdigest()
    assert FileDiff(path="x", raw=raw).content_sha256() == expected

"""Diff parser — line tracking is what drives inline-comment validation.

Any off-by-one here means we either drop legit findings or send GitHub
comments on lines it will reject.
"""

from __future__ import annotations

from reviewmind.diff import parse_unified_diff


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

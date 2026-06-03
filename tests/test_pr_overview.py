"""Tests for the deterministic preliminary PR overview builder."""

from __future__ import annotations

from prthinker import pr_overview


def test_summarize_commit_types_groups_conventional_prefixes():
    msgs = ["feat: a", "fix: b", "feat(scope): c", "noise line", "chore: d"]
    out = pr_overview.summarize_commit_types(msgs)
    assert "feat (2)" in out
    assert "fix (1)" in out
    assert "chore (1)" in out


def test_summarize_commit_types_empty_when_no_conventional():
    assert pr_overview.summarize_commit_types(["random", "another"]) == ""


def test_summarize_changes_counts_dirs_and_extensions():
    paths = ["prthinker/a.py", "prthinker/b.py", "tests/c.py", "docs/d.rst"]
    out = pr_overview.summarize_changes(paths)
    assert out.startswith("4 file(s)")
    assert "`prthinker/`" in out
    assert ".py (3)" in out
    assert ".rst (1)" in out


def test_summarize_changes_handles_root_and_extensionless():
    out = pr_overview.summarize_changes(["README", "Makefile"])
    assert out.startswith("2 file(s)")
    # Extensionless files are not reported in the type breakdown.
    assert "—" not in out


def test_summarize_changes_empty():
    assert pr_overview.summarize_changes([]) == ""


def test_build_overview_block_full():
    msgs = ["feat: add x\n\nbody", "fix: correct y"]
    paths = ["prthinker/x.py", "tests/test_x.py"]
    block = pr_overview.build_overview_block(msgs, paths)
    text = "\n".join(block)
    assert "### 📋 What this PR does (preliminary)" in text
    assert "- **Changes:** 2 file(s)" in text
    assert "- **Commit types:** feat (1) · fix (1)" in text
    assert "- **Commits (2):**" in text
    # Only the subject line of a multi-line message is listed.
    assert "  - feat: add x" in text
    assert "body" not in text


def test_build_overview_block_caps_commit_list():
    msgs = [f"feat: change {i}" for i in range(20)]
    block = pr_overview.build_overview_block(msgs, ["a.py"])
    text = "\n".join(block)
    assert "- **Commits (20):**" in text
    assert "… and 5 more" in text


def test_build_overview_block_empty_when_no_data():
    assert pr_overview.build_overview_block([], []) == []


def test_build_overview_text_joins_or_empty():
    assert pr_overview.build_overview_text([], []) == ""
    text = pr_overview.build_overview_text(["feat: a"], ["a.py"])
    assert text.startswith("### 📋 What this PR does")

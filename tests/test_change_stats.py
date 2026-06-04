"""Tests for per-file change-size parsing (change_stats)."""

from __future__ import annotations

from prthinker.change_stats import ChangeStat, change_badge, compute_change_stats

_DIFF = (
    "diff --git a/a.py b/a.py\n"
    "--- a/a.py\n"
    "+++ b/a.py\n"
    "@@ -1,2 +1,3 @@\n"
    " context\n"
    "-old line\n"
    "+new line\n"
    "+another new\n"
    "@@ -10,0 +12,1 @@\n"
    "+tail\n"
    "diff --git a/b.py b/b.py\n"
    "--- a/b.py\n"
    "+++ b/b.py\n"
    "@@ -0,0 +1,1 @@\n"
    "+only added\n"
)


def test_compute_change_stats_counts_added_removed_hunks():
    stats = compute_change_stats(_DIFF)
    assert stats["a.py"] == ChangeStat(path="a.py", added=3, removed=1, hunks=2)
    assert stats["b.py"] == ChangeStat(path="b.py", added=1, removed=0, hunks=1)


def test_compute_change_stats_empty_diff():
    assert compute_change_stats("") == {}


def test_change_badge_includes_hunks_when_multiple():
    badge = change_badge(ChangeStat(path="a.py", added=3, removed=1, hunks=2))
    assert badge == "+3 −1 · 2 hunks"


def test_change_badge_omits_hunks_for_single_hunk():
    badge = change_badge(ChangeStat(path="b.py", added=1, removed=0, hunks=1))
    assert badge == "+1 −0"


def test_change_badge_empty_for_none_or_zero():
    assert change_badge(None) == ""
    assert change_badge(ChangeStat(path="x", added=0, removed=0, hunks=0)) == ""


def test_change_badge_uses_minus_sign_not_hyphen():
    # The U+2212 minus avoids being parsed as a markdown list bullet.
    badge = change_badge(ChangeStat(path="a", added=1, removed=2, hunks=1))
    assert "−2" in badge and "-2" not in badge

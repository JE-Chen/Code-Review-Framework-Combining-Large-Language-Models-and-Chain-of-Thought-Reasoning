"""Tests for inline ``# prthinker: ignore`` directive suppression."""

from __future__ import annotations

from prthinker import inline_ignore
from prthinker.schemas import InlineFinding

_DIFF = (
    "diff --git a/a.py b/a.py\n"
    "--- a/a.py\n"
    "+++ b/a.py\n"
    "@@ -0,0 +1,3 @@\n"
    "+clean = 1\n"
    "+risky = eval(x)  # prthinker: ignore\n"
    "+also = 2\n"
)


def _f(path: str, line: int) -> InlineFinding:
    return InlineFinding(path=path, line=line, comment="c", severity="warning")


def test_ignored_lines_detects_directive():
    out = inline_ignore.ignored_lines(_DIFF)
    assert out == {"a.py": {2}}


def test_ignored_lines_empty_diff():
    assert inline_ignore.ignored_lines("") == {}


def test_filter_drops_only_directive_line():
    findings = [_f("a.py", 1), _f("a.py", 2), _f("a.py", 3)]
    kept = inline_ignore.filter_inline_ignored(findings, _DIFF)
    assert [f.line for f in kept] == [1, 3]


def test_filter_keeps_other_files():
    findings = [_f("b.py", 2)]  # directive is in a.py, not b.py
    assert inline_ignore.filter_inline_ignored(findings, _DIFF) == findings


def test_filter_noop_on_empty_diff():
    findings = [_f("a.py", 2)]
    assert inline_ignore.filter_inline_ignored(findings, "") == findings


def test_directive_matches_case_and_spacing():
    diff = (
        "+++ b/x.py\n"
        "@@ -0,0 +1,1 @@\n"
        "+y = 1  // PRThinker:ignore[rule-7]\n"
    )
    assert inline_ignore.ignored_lines(diff) == {"x.py": {1}}

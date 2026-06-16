"""Unit tests for the summary-breakdown helper in ``prthinker.cli_review_emit``.

``_inline_post_breakdown`` reports how many findings actually land on a diff
hunk (and will be posted as inline comments) versus the raw total. The count
is derived from the off-diff list rather than parsing the diff a second time,
so these tests lock the partition invariant: ``posted == total - len(off)``.
"""

from __future__ import annotations

from types import SimpleNamespace

from prthinker.cli_review_emit import _inline_post_breakdown
from prthinker.schemas import InlineFinding

# Single-file diff whose new side carries exactly lines 1 and 2 of a.py.
_DIFF = (
    "diff --git a/a.py b/a.py\n"
    "--- a/a.py\n"
    "+++ b/a.py\n"
    "@@ -0,0 +1,2 @@\n"
    "+first\n"
    "+second\n"
)


def _finding(**kw) -> InlineFinding:
    base = {"path": "a.py", "line": 1, "comment": "x"}
    base.update(kw)
    return InlineFinding(**base)


def test_inline_post_breakdown_disabled_returns_empty():
    """With inline review off, nothing is posted and the breakdown is inert."""
    args = SimpleNamespace(inline_review=False)
    result = SimpleNamespace(inline_findings=[_finding()], code_diff=_DIFF)
    assert _inline_post_breakdown(args, result) == (None, ())


def test_inline_post_breakdown_missing_flag_treated_as_disabled():
    """An args namespace without the flag defaults to disabled (getattr)."""
    args = SimpleNamespace()
    result = SimpleNamespace(inline_findings=[_finding()], code_diff=_DIFF)
    assert _inline_post_breakdown(args, result) == (None, ())


def test_inline_post_breakdown_counts_on_diff_and_collects_off_diff():
    """posted_count = total - off_diff; off-diff findings are returned in order."""
    on1 = _finding(path="a.py", line=1)
    on2 = _finding(path="a.py", line=2)
    off_line = _finding(path="a.py", line=99)        # inside file, off the hunk
    off_file = _finding(path="missing.py", line=1)   # file not in the diff
    args = SimpleNamespace(inline_review=True)
    result = SimpleNamespace(
        inline_findings=[on1, on2, off_line, off_file],
        code_diff=_DIFF,
    )

    posted_count, off_diff = _inline_post_breakdown(args, result)

    assert posted_count == 2
    assert off_diff == (off_line, off_file)


def test_inline_post_breakdown_all_on_diff():
    """No off-diff findings → posted_count equals the total, off_diff empty."""
    args = SimpleNamespace(inline_review=True)
    findings = [_finding(line=1), _finding(line=2)]
    result = SimpleNamespace(inline_findings=findings, code_diff=_DIFF)

    posted_count, off_diff = _inline_post_breakdown(args, result)

    assert posted_count == 2
    assert off_diff == ()


def test_inline_post_breakdown_all_off_diff():
    """Every finding off the diff → posted_count is zero, all returned as off."""
    args = SimpleNamespace(inline_review=True)
    findings = [_finding(line=50), _finding(path="other.py", line=1)]
    result = SimpleNamespace(inline_findings=findings, code_diff=_DIFF)

    posted_count, off_diff = _inline_post_breakdown(args, result)

    assert posted_count == 0
    assert off_diff == tuple(findings)


def test_inline_post_breakdown_no_findings():
    """Empty finding list → zero posted, empty off-diff (no diff parse needed)."""
    args = SimpleNamespace(inline_review=True)
    result = SimpleNamespace(inline_findings=[], code_diff=_DIFF)
    assert _inline_post_breakdown(args, result) == (0, ())

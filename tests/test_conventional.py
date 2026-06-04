"""Tests for Conventional-Comments inline body formatting."""

from __future__ import annotations

from prthinker.conventional import conventional_prefix, format_inline_body
from prthinker.schemas import InlineFinding


def _f(**kw) -> InlineFinding:
    base = {"path": "a.py", "line": 1, "comment": "do thing"}
    base.update(kw)
    return InlineFinding(**base)


def test_prefix_maps_severity_to_conventional_label():
    assert conventional_prefix(_f(severity="error")) == "🔴 **issue:**"
    assert conventional_prefix(_f(severity="warning")) == "🟡 **suggestion:**"
    assert conventional_prefix(_f(severity="info")) == "🔵 **nitpick:**"


def test_prefix_decorates_with_category():
    prefix = conventional_prefix(_f(severity="error", category="security"))
    assert prefix == "🔴 **issue (security):**"


def test_format_body_includes_prefix_and_comment():
    body = format_inline_body(_f(severity="warning", comment="use logging"))
    assert body == "🟡 **suggestion:** use logging"


def test_format_body_appends_suggestion_block():
    body = format_inline_body(
        _f(severity="error", comment="null deref", suggestion="x = guard()")
    )
    assert body.startswith("🔴 **issue:** null deref")
    assert "```suggestion\nx = guard()\n```" in body


def test_prefix_falls_back_for_unknown_severity():
    # Pydantic constrains severity, but the mapping is defensive anyway;
    # model_construct bypasses validation to exercise the fallback.
    finding = InlineFinding.model_construct(
        path="a.py", line=1, comment="x", severity="weird"
    )
    assert conventional_prefix(finding) == "**weird:**"

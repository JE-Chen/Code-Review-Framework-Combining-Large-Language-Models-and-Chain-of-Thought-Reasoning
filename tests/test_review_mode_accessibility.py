"""Tests for the self-registering accessibility review mode."""

from __future__ import annotations

import prthinker.review_modes.accessibility as accessibility_mode
from prthinker.review_modes import available_modes, get_mode

_SAMPLE_DIFF = (
    "diff --git a/src/Login.tsx b/src/Login.tsx\n"
    "--- a/src/Login.tsx\n"
    "+++ b/src/Login.tsx\n"
    "@@ -1,3 +1,4 @@\n"
    "+    <img src=\"logo.png\" />\n"
    "+    <input type=\"text\" />\n"
)


def test_mode_is_registered() -> None:
    """Importing the module registers the accessibility mode."""
    assert "accessibility" in available_modes()
    mode = get_mode("accessibility")
    assert mode.description == "Accessibility (a11y) pass"
    assert mode.build_prompt is accessibility_mode.build_prompt


def test_prompt_contains_diff_and_domain_keywords() -> None:
    """The prompt embeds the diff and names at least two focus areas."""
    prompt = accessibility_mode.build_prompt(_SAMPLE_DIFF)
    assert isinstance(prompt, str)
    assert _SAMPLE_DIFF in prompt
    keywords = ("alt text", "ARIA", "keyboard", "contrast", "focus", "label")
    matched = [kw for kw in keywords if kw.lower() in prompt.lower()]
    assert len(matched) >= 2


def test_empty_diff_still_returns_nonempty_prompt() -> None:
    """An empty diff still yields a non-empty prompt string."""
    prompt = accessibility_mode.build_prompt("")
    assert isinstance(prompt, str)
    assert prompt.strip()

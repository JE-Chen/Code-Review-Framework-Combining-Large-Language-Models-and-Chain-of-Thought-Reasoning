"""Tests for the self-registering "security" review mode."""

from __future__ import annotations

import prthinker.review_modes.security  # noqa: F401  # import triggers registration
from prthinker.review_modes import available_modes, get_mode

_SAMPLE_DIFF = (
    "--- a/app/db.py\n"
    "+++ b/app/db.py\n"
    "@@ -1,3 +1,4 @@\n"
    '+query = "SELECT * FROM users WHERE name = " + user_input\n'
)


def test_mode_is_registered() -> None:
    """The security mode registers itself on import."""
    assert "security" in available_modes()
    mode = get_mode("security")
    assert mode.name == "security"
    assert mode.description


def test_build_prompt_contains_diff_and_keywords() -> None:
    """The prompt embeds the diff and at least two focus keywords."""
    prompt = get_mode("security").build_prompt(_SAMPLE_DIFF)
    assert isinstance(prompt, str)
    assert _SAMPLE_DIFF in prompt
    keywords = ("Injection", "SSRF", "XSS", "deserialization", "secrets")
    hits = sum(1 for word in keywords if word in prompt)
    assert hits >= 2


def test_empty_diff_still_returns_nonempty_prompt() -> None:
    """An empty diff yields a non-empty, well-formed prompt."""
    prompt = get_mode("security").build_prompt("")
    assert isinstance(prompt, str)
    assert prompt.strip()
    assert "[]" in prompt

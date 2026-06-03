"""Tests for the self-registering "performance" review mode."""

from __future__ import annotations

import prthinker.review_modes.performance  # noqa: F401  # pylint: disable=unused-import  # registration side-effect
from prthinker.review_modes import available_modes, get_mode

_SAMPLE_DIFF = (
    "--- a/app/orders.py\n"
    "+++ b/app/orders.py\n"
    "@@ -1,3 +1,5 @@\n"
    "+for order in orders:\n"
    "+    user = db.query(User).get(order.user_id)\n"
)


def test_mode_is_registered() -> None:
    """The performance mode self-registers on import."""
    assert "performance" in available_modes()
    mode = get_mode("performance")
    assert mode.description == "Performance pass"


def test_build_prompt_contains_diff_and_keywords() -> None:
    """Prompt embeds the diff and at least two domain focus keywords."""
    prompt = get_mode("performance").build_prompt(_SAMPLE_DIFF)
    assert isinstance(prompt, str)
    assert _SAMPLE_DIFF in prompt
    keywords = ("N+1", "O(n^2)", "blocking I/O", "pagination", "caching")
    hits = sum(1 for keyword in keywords if keyword in prompt)
    assert hits >= 2


def test_empty_diff_still_returns_prompt() -> None:
    """An empty diff still yields a non-empty prompt string."""
    prompt = get_mode("performance").build_prompt("")
    assert isinstance(prompt, str)
    assert prompt.strip()

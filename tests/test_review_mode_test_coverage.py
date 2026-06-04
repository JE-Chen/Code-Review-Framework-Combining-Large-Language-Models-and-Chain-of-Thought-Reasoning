"""Tests for the self-registering ``test-coverage`` review mode."""

from __future__ import annotations

import prthinker.review_modes.test_coverage as test_coverage_mode
from prthinker.review_modes import available_modes, get_mode

_SAMPLE_DIFF = """\
diff --git a/prthinker/widget.py b/prthinker/widget.py
@@ -1,3 +1,6 @@
 def divide(a, b):
-    return a / b
+    if b == 0:
+        raise ValueError("cannot divide by zero")
+    return a / b
"""

_FOCUS_KEYWORDS = ("test", "edge case", "error branch", "untested", "boundary")


def test_mode_is_registered() -> None:
    """Importing the module registers it under the expected name."""
    assert "test-coverage" in available_modes()
    mode = get_mode("test-coverage")
    assert mode.description == "Test-coverage pass"
    assert mode.build_prompt is test_coverage_mode.build_prompt


def test_build_prompt_embeds_diff_and_focus_keywords() -> None:
    """The prompt embeds the diff and at least two focus-list keywords."""
    prompt = test_coverage_mode.build_prompt(_SAMPLE_DIFF)
    assert isinstance(prompt, str)
    assert "raise ValueError" in prompt
    assert "divide" in prompt
    lower = prompt.lower()
    hits = sum(1 for kw in _FOCUS_KEYWORDS if kw in lower)
    assert hits >= 2


def test_build_prompt_requests_json_array_contract() -> None:
    """The prompt asks for a JSON array with the documented keys."""
    prompt = test_coverage_mode.build_prompt(_SAMPLE_DIFF)
    for token in ("path", "line", "severity", "comment", "[]"):
        assert token in prompt


def test_empty_diff_still_returns_non_empty_prompt() -> None:
    """An empty diff still yields a non-empty prompt string."""
    prompt = test_coverage_mode.build_prompt("")
    assert isinstance(prompt, str)
    assert prompt.strip()

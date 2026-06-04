"""Tests for the self-registering ``secret-scan`` review mode."""

from __future__ import annotations

import prthinker.review_modes.secret_scan as secret_scan
from prthinker.review_modes import available_modes, get_mode

_SAMPLE_DIFF = """\
diff --git a/config.py b/config.py
index 1111111..2222222 100644
--- a/config.py
+++ b/config.py
@@ -1,2 +1,3 @@
 SETTING = 1
+API_KEY = "AKIAIOSFODNN7EXAMPLE"
 OTHER = 2
"""


def test_mode_is_registered() -> None:
    assert "secret-scan" in available_modes()
    mode = get_mode("secret-scan")
    assert mode.name == "secret-scan"
    assert mode.build_prompt is secret_scan.build_prompt


def test_prompt_contains_diff_and_domain_keywords() -> None:
    prompt = secret_scan.build_prompt(_SAMPLE_DIFF)
    assert isinstance(prompt, str)
    assert 'API_KEY = "AKIAIOSFODNN7EXAMPLE"' in prompt
    keywords = ("API keys", "tokens", "Private keys", "Passwords", "Connection strings")
    matched = [kw for kw in keywords if kw in prompt]
    assert len(matched) >= 2


def test_empty_diff_still_returns_non_empty_prompt() -> None:
    prompt = secret_scan.build_prompt("")
    assert isinstance(prompt, str)
    assert prompt.strip()
    assert "secret-scan review pass" in prompt.lower()

"""Tests for the ``pii`` review mode registration and prompt builder."""

from __future__ import annotations

import prthinker.review_modes.pii as pii_mode
from prthinker.review_modes import available_modes, get_mode

_SAMPLE_DIFF = """\
--- a/app/log.py
+++ b/app/log.py
@@ -1,2 +1,3 @@
 def handle(user):
+    logger.info("user email=%s name=%s", user.email, user.name)
     return user
"""


def test_pii_mode_is_registered() -> None:
    assert "pii" in available_modes()
    mode = get_mode("pii")
    assert mode.name == "pii"
    assert mode.description == "PII-exposure pass"


def test_build_prompt_embeds_diff_and_keywords() -> None:
    prompt = pii_mode.build_prompt(_SAMPLE_DIFF)
    assert isinstance(prompt, str)
    assert "user.email" in prompt
    assert 'logger.info("user email=%s name=%s"' in prompt
    keywords = ("email", "names", "addresses", "government", "health", "financial")
    matched = [k for k in keywords if k in prompt]
    assert len(matched) >= 2


def test_empty_diff_returns_non_empty_prompt() -> None:
    prompt = pii_mode.build_prompt("")
    assert isinstance(prompt, str)
    assert prompt.strip()
    assert "PII" in prompt

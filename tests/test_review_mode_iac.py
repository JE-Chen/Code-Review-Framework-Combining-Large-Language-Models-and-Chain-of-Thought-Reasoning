"""Tests for the self-registering ``iac`` review mode."""

from __future__ import annotations

import prthinker.review_modes.iac  # noqa: F401  # import triggers registration
from prthinker.review_modes import available_modes, get_mode

_SAMPLE_DIFF = (
    "--- a/main.tf\n"
    "+++ b/main.tf\n"
    "@@ -1,3 +1,5 @@\n"
    '+resource "aws_s3_bucket" "data" {\n'
    '+  acl = "public-read"\n'
    "+}\n"
)

_DOMAIN_KEYWORDS = ("Terraform", "Kubernetes", "Dockerfile", "GitHub Actions")


def test_mode_is_registered() -> None:
    """The module's import side-effect registers the ``iac`` mode."""
    assert "iac" in available_modes()
    mode = get_mode("iac")
    assert mode.name == "iac"
    assert mode.description == "Infrastructure-as-code pass"


def test_prompt_embeds_diff_and_domain_keywords() -> None:
    """The built prompt contains the diff and at least two focus keywords."""
    prompt = get_mode("iac").build_prompt(_SAMPLE_DIFF)
    assert isinstance(prompt, str)
    assert _SAMPLE_DIFF in prompt
    hits = sum(1 for kw in _DOMAIN_KEYWORDS if kw in prompt)
    assert hits >= 2


def test_empty_diff_yields_nonempty_prompt() -> None:
    """An empty diff still produces a usable, non-empty prompt string."""
    prompt = get_mode("iac").build_prompt("")
    assert isinstance(prompt, str)
    assert prompt.strip() != ""

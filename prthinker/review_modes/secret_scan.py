"""Self-registering ``secret-scan`` review mode.

A focused whole-diff pass that hunts for credentials newly *added* in a
unified diff — API keys, tokens, private keys, passwords, connection
strings. This is distinct from :mod:`prthinker.redaction`, which only
scrubs known secret patterns out of a prompt *before* it is sent to a
backend; this mode asks the model to flag a committed secret so a human
can rotate it and rip it out of history.

Per ``paper_rule.md`` no-fabrication: this module only builds a prompt;
it makes no empirical claim about detection quality.
"""

from __future__ import annotations

from prthinker.review_modes._registry import register_mode

_SEVERITY_VALUES = "info/warning/error"
_EMPTY_ARRAY = "[]"

_FOCUS_CHECKLIST = (
    "- API keys and access keys (cloud provider keys, service keys)\n"
    "- Authentication tokens (OAuth, bearer, session, refresh tokens)\n"
    "- Private keys (RSA / EC / SSH / PGP key material, PEM blocks)\n"
    "- Passwords and passphrases (including default / example credentials)\n"
    "- Connection strings embedding inline credentials "
    "(database URLs, message-broker URIs, etc.)"
)

_INSTRUCTIONS = f"""\
# Secret-scan review pass

You are performing a focused secret-scan review pass. Consider ONLY the
unified diff supplied below — do not speculate about code that is not in
the diff.

Look specifically for secrets that are newly ADDED in this diff (lines
beginning with ``+``). When you find one, flag the exact added line:

{_FOCUS_CHECKLIST}

This pass is distinct from the redaction pass: redaction only scrubs
secret patterns out of a prompt before it is sent, whereas your job is
to surface a secret that has actually been committed so a human can
rotate it and remove it from history.

Reply with ONLY a JSON array (no surrounding prose, no markdown fences).
Each element is an object with at least these fields:

  {{
    "path":     "<file path from the diff>",
    "line":     <added line number as an integer>,
    "severity": "<one of: {_SEVERITY_VALUES}>",
    "comment":  "<one sentence: what was found and why it is a secret>"
  }}

If nothing in the diff is a newly added secret, reply with exactly the
empty array ``{_EMPTY_ARRAY}``."""


@register_mode("secret-scan", "Committed-secret pass")
def build_prompt(diff_text: str) -> str:
    """Build the secret-scan review prompt for a unified diff."""
    diff_block = diff_text.rstrip()
    return f"{_INSTRUCTIONS}\n\n## Diff\n\n```diff\n{diff_block}\n```\n"


__all__ = ["build_prompt"]

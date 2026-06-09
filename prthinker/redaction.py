"""Secret / PII redaction for diffs about to leave the repo.

When the runner is configured to call a paid third-party backend
(OpenAI, Anthropic, …), the PR diff payload may contain real secrets
that slipped past ``.gitignore`` — an ``.env`` file shown in the diff,
a hard-coded token in a test fixture, a JWT in a snapshot test. This
module scrubs them with conservative, well-known patterns BEFORE the
diff goes out, replacing each match with ``<REDACTED:<kind>>``.

Design notes:

* Patterns are conservative on purpose — false positives in a code
  review are noisy but recoverable. False negatives (a real secret
  leaking to a third-party API) are not.
* The detector reports *what kind* was found and *how many*, never the
  match content, so log lines are safe to ship.
* Redaction is idempotent: feeding an already-redacted string through
  again is a no-op.
* High-entropy generic-string detection is OUT of scope for this
  module — every project has different conventions for hex IDs vs
  secrets, so blanket entropy heuristics burn more than they save.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class _Pattern:
    kind: str
    regex: re.Pattern[str]


# Order matters when patterns overlap — more-specific patterns first.
_PATTERNS: tuple[_Pattern, ...] = (
    # PEM-style key blocks (whole block including BEGIN/END line).
    _Pattern(
        "private-key",
        re.compile(
            r"-----BEGIN [A-Z ]*PRIVATE KEY-----"
            r"[\s\S]+?"
            r"-----END [A-Z ]*PRIVATE KEY-----"
        ),
    ),
    # GitHub fine-grained PATs and classic tokens.
    _Pattern(
        "github-token",
        re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    ),
    # Anthropic keys — listed first because the OpenAI pattern below
    # would otherwise match the ``sk-`` prefix and steal these.
    _Pattern(
        "anthropic-key",
        re.compile(r"\bsk-ant-(?:api03-)?[A-Za-z0-9_-]{40,}\b"),
    ),
    # OpenAI keys (post-2023 standard format).
    _Pattern(
        "openai-key",
        re.compile(r"\bsk-(?!ant-)(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    ),
    # Stripe live/test keys — published format.
    _Pattern(
        "stripe-key",
        re.compile(r"\b[sr]k_(?:live|test)_[A-Za-z0-9]{24,}\b"),
    ),
    # AWS access keys (published 20-char IAM ID format).
    _Pattern(
        "aws-access-key-id",
        re.compile(r"\b(?:AKIA|ASIA|AIDA|AROA|AGPA|ANPA|ANVA)[0-9A-Z]{16}\b"),
    ),
    # Slack bot/user tokens.
    _Pattern(
        "slack-token",
        re.compile(r"\bxox[abprs]-[0-9]+-[0-9]+(?:-[0-9]+)?-[0-9a-zA-Z]+\b"),
    ),
    # Google Cloud API keys.
    _Pattern(
        "gcp-api-key",
        re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
    ),
    # Twilio account SIDs.
    _Pattern(
        "twilio-sid",
        re.compile(r"\bAC[a-f0-9]{32}\b"),
    ),
    # JWTs — three base64url segments separated by dots; header starts ``eyJ``.
    _Pattern(
        "jwt",
        re.compile(r"\beyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b"),
    ),
)


_REDACTED_RE = re.compile(r"<REDACTED:[a-z-]+>")


@dataclass(frozen=True)
class RedactionReport:
    """Count of redactions per kind. Safe to log — never includes content."""

    counts: dict[str, int]

    @property
    def total(self) -> int:
        return sum(self.counts.values())

    def __bool__(self) -> bool:
        return self.total > 0

    def summary(self) -> str:
        if not self.counts:
            return "no secrets redacted"
        parts = [f"{n}× {kind}" for kind, n in sorted(self.counts.items())]
        return "redacted " + ", ".join(parts)


def _make_sub(kind: str, placeholder: str, counts: dict[str, int]):
    """Build a substitution callback bound to one pattern's kind/placeholder.

    Factored out of ``redact`` so the closure captures the per-pattern values
    as explicit arguments rather than late-binding a loop variable.
    """

    def _sub(match: re.Match[str]) -> str:
        # Don't re-redact our own placeholders.
        if _REDACTED_RE.fullmatch(match.group(0)):
            return match.group(0)
        counts[kind] = counts.get(kind, 0) + 1
        return placeholder

    return _sub


def redact(text: str) -> tuple[str, RedactionReport]:
    """Apply every known pattern; return (scrubbed_text, report).

    Idempotent: anything already wrapped in ``<REDACTED:...>`` stays
    untouched on a second pass.
    """
    counts: dict[str, int] = {}
    redacted = text
    for pattern in _PATTERNS:
        placeholder = f"<REDACTED:{pattern.kind}>"
        redacted = pattern.regex.sub(_make_sub(pattern.kind, placeholder, counts), redacted)
    return redacted, RedactionReport(counts=counts)


def has_secrets(text: str) -> bool:
    """Cheap probe — useful before deciding whether to log a warning."""
    for pattern in _PATTERNS:
        if pattern.regex.search(text):
            return True
    return False


__all__ = ["redact", "has_secrets", "RedactionReport"]

"""Self-registering "security" review mode (focused SAST-style pass).

Builds a single whole-diff prompt that asks the model to review the
supplied unified diff for security weaknesses only and to emit findings
as a JSON array (or an empty array when nothing applies). The prompt is
the source of truth; this module is pure stdlib and runner-safe.
"""

from __future__ import annotations

from prthinker.review_modes._registry import register_mode

_JSON_ARRAY = "JSON array"

_FOCUS_CHECKLIST = (
    "- Injection: SQL, command, and path/traversal injection (CWE-89, "
    "CWE-78, CWE-22).\n"
    "- Authentication and authorization gaps: missing or broken access "
    "checks (CWE-862, CWE-287).\n"
    "- Unsafe deserialization of untrusted data (CWE-502).\n"
    "- Hardcoded secrets: API keys, tokens, passwords (CWE-798).\n"
    "- Server-Side Request Forgery / SSRF (CWE-918).\n"
    "- Cross-Site Scripting / XSS (CWE-79).\n"
    "- Cryptographic misuse: weak hashes, bad randomness, missing TLS "
    "verification (CWE-327, CWE-330)."
)

_OUTPUT_CONTRACT = (
    f"Return your findings as a {_JSON_ARRAY} of objects. Each object MUST "
    "have at least these keys: \"path\" (string), \"line\" (integer), "
    "\"severity\" (one of \"info\", \"warning\", \"error\"), and "
    "\"comment\" (string). Map each finding to a CWE ID in the comment "
    f"where possible. If nothing applies, return an empty {_JSON_ARRAY}: []."
)


@register_mode("security", "Security / SAST pass")
def build_prompt(diff_text: str) -> str:
    """Build the security review prompt for a unified diff."""
    return (
        "You are performing a focused security review pass on a code "
        "change. Consider ONLY the supplied unified diff below; do not "
        "speculate about code that is not shown.\n\n"
        "Look specifically for the following classes of weakness:\n"
        f"{_FOCUS_CHECKLIST}\n\n"
        f"{_OUTPUT_CONTRACT}\n\n"
        "Unified diff:\n"
        f"{diff_text}\n"
    )

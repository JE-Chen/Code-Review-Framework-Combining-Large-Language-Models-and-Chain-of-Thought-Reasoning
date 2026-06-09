"""Self-registering "performance" whole-diff review mode.

Registers a focused performance pass that asks the model to scan a
single unified diff for common performance anti-patterns and return
structured JSON findings. Runner-safe: pure stdlib string building only,
no heavy ML dependencies.

Per ``paper_rule.md`` no-fabrication: this module ships the prompt
mechanism only and makes no empirical claim about review quality.
"""

from __future__ import annotations

from prthinker.review_modes._registry import register_mode

_FOCUS_ITEMS = (
    "N+1 queries (a query issued once per item inside a loop)",
    "accidental O(n^2) or worse algorithmic complexity",
    "unbounded memory growth or repeated allocations inside loops",
    "blocking I/O (network, disk, locks) on hot paths",
    "missing pagination or caching where the data set is large",
    "redundant recomputation of values that could be hoisted or memoised",
)

_SEVERITY_VALUES = "info/warning/error"

_FINDINGS_SHAPE = (
    "Report findings as a JSON array of objects, each with at least: "
    '"path" (string), "line" (integer), '
    f'"severity" (one of {_SEVERITY_VALUES}), and "comment" (string). '
    "If nothing applies, return an empty array []."
)


def _format_focus_block() -> str:
    """Render the focus checklist as a numbered, newline-joined block."""
    return "\n".join(
        f"  {index}. {item}" for index, item in enumerate(_FOCUS_ITEMS, start=1)
    )


@register_mode("performance", "Performance pass")
def build_prompt(diff_text: str) -> str:
    """Build the performance review prompt for a unified diff."""
    focus_block = _format_focus_block()
    return (
        "You are doing a focused performance review pass.\n"
        "Consider ONLY the unified diff supplied below; do not assume any "
        "code or context outside it.\n\n"
        "Look specifically for:\n"
        f"{focus_block}\n\n"
        f"{_FINDINGS_SHAPE}\n\n"
        "Unified diff:\n"
        f"{diff_text}\n"
    )

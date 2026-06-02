"""Accessibility (a11y) review mode: a focused whole-diff pass.

Registers an opt-in review mode that asks the model to look at changed
frontend code (HTML / JSX / TSX) through an accessibility lens only —
missing alt text, unlabeled form controls, colour contrast, keyboard
navigation, ARIA misuse, and focus management. The prompt is the source
of truth and lives here; the pipeline runs it via the registry.

Per ``paper_rule.md`` no-fabrication: no claim is made about whether this
pass empirically improves accessibility outcomes. The contribution is the
focused-prompt mechanism, not a measured result.
"""

from __future__ import annotations

from prthinker.review_modes import register_mode

_SEVERITY_VALUES = "info/warning/error"
_EMPTY_ARRAY = "[]"

_FOCUS_CHECKLIST = (
    "- Missing or unhelpful alt text on images and media.\n"
    "- Unlabeled form controls (inputs, buttons, selects without an "
    "associated label or accessible name).\n"
    "- Colour-contrast problems between foreground text and its "
    "background.\n"
    "- Keyboard navigation: interactive elements that are not reachable "
    "or operable without a mouse.\n"
    "- ARIA misuse: wrong roles, redundant or conflicting aria-* "
    "attributes, invalid attribute values.\n"
    "- Focus management in changed frontend (HTML / JSX / TSX) code: "
    "lost, trapped, or unmanaged focus after interaction."
)

_OUTPUT_CONTRACT = (
    "Return your findings as a JSON array of objects. Each object must "
    "have at least these keys: \"path\" (string), \"line\" (integer), "
    f"\"severity\" (one of {_SEVERITY_VALUES}), and \"comment\" (string). "
    f"If nothing applies, return an empty array {_EMPTY_ARRAY}."
)


@register_mode("accessibility", "Accessibility (a11y) pass")
def build_prompt(diff_text: str) -> str:
    """Build the accessibility review prompt for a unified diff."""
    return (
        "You are performing a focused ACCESSIBILITY (a11y) review pass. "
        "Consider ONLY the supplied unified diff below — do not speculate "
        "about code that is not shown.\n\n"
        "Look specifically for the following accessibility problems in the "
        "changed frontend code:\n"
        f"{_FOCUS_CHECKLIST}\n\n"
        f"{_OUTPUT_CONTRACT}\n\n"
        "Unified diff:\n"
        f"{diff_text}"
    )


__all__ = ["build_prompt"]

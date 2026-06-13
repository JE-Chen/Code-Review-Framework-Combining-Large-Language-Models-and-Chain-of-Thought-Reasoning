"""Self-registering ``test-coverage`` whole-diff review mode.

Builds a prompt that asks the model for a focused test-coverage pass over
a single unified diff: changed or added behaviour lacking a test, untested
error branches and edge cases, plus concrete test-case suggestions. Output
is a JSON array of findings (or an empty array). The prompt is the source
of truth and lives here; the mode registers itself on import.
"""

from __future__ import annotations

from prthinker.review_modes._registry import register_mode

_FOCUS_CHECKLIST = (
    "- Changed or added behaviour that lacks a corresponding test.\n"
    "- Untested error branches (every `except` / failure path).\n"
    "- Untested edge cases: empty inputs, single-element inputs,\n"
    "  None / missing keys, boundary values just inside and just\n"
    "  outside any threshold.\n"
    "- Round-trips for serialisation that the diff adds or changes.\n"
    "- Concrete, runnable test cases that exercise the changed lines."
)

_JSON_CONTRACT = (
    "Reply with ONLY a JSON array, no surrounding prose and no markdown\n"
    "fences. Each element is an object with at least these keys:\n\n"
    '  {\n'
    '    "path":     "<file path from the diff>",\n'
    '    "line":     <integer line number on the changed side>,\n'
    '    "severity": "info" | "warning" | "error",\n'
    '    "comment":  "<what is untested and which test to add>"\n'
    "  }\n\n"
    "If nothing in this diff needs a test-coverage finding, reply with\n"
    "exactly an empty array: []."
)

_PROMPT_TEMPLATE = """\
# Test-coverage review pass

You are performing a focused test-coverage review pass. Consider ONLY
the supplied unified diff below — do not speculate about code that is
not shown.

For the changed lines, look for:

{checklist}

{contract}

## Diff

```diff
{diff_text}
```
"""


@register_mode("test-coverage", "Test-coverage pass")
def build_prompt(diff_text: str) -> str:
    """Build the test-coverage review prompt for a unified diff."""
    return _PROMPT_TEMPLATE.format(
        checklist=_FOCUS_CHECKLIST,
        contract=_JSON_CONTRACT,
        diff_text=diff_text.rstrip(),
    )


__all__ = ["build_prompt"]

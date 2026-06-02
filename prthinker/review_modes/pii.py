"""PII-exposure review mode.

Registers a focused ``pii`` whole-diff pass that asks the model to flag
personal data (emails, names, addresses, government IDs, health and
financial data) newly logged, persisted, or sent to third parties in the
supplied unified diff. The prompt is the source of truth and lives here.
"""

from __future__ import annotations

from prthinker.review_modes import register_mode

SEVERITY_LEVELS = "info/warning/error"
EMPTY_ARRAY = "[]"

_FOCUS_CHECKLIST = (
    "- email addresses\n"
    "- personal names\n"
    "- postal / physical addresses\n"
    "- government IDs (SSN, passport, national ID, tax ID)\n"
    "- health data (diagnoses, treatments, medical records)\n"
    "- financial data (card numbers, bank accounts, balances)"
)

_PROMPT_TEMPLATE = """\
# PII-exposure review pass

You are doing a focused PII (personally identifiable information) review
pass. Consider ONLY the unified diff supplied below — do not assume code
or context outside it.

Flag any personal data that is NEWLY logged, persisted (DB, file, cache),
or sent to third parties (HTTP calls, analytics, telemetry, external
services) in this diff. Look specifically for:

{checklist}

Report findings as a JSON array of objects, each with at least:

  {{
    "path":     "<file path from the diff>",
    "line":     <line number>,
    "severity": "<{severity_levels}>",
    "comment":  "<one sentence: what PII is exposed and how>"
  }}

If nothing in this diff exposes PII, output exactly ``{empty_array}``.
Output ONLY the JSON array — no surrounding prose, no markdown fences.

## Diff

```diff
{diff}
```
"""


@register_mode("pii", "PII-exposure pass")
def build_prompt(diff_text: str) -> str:
    """Build the pii review prompt for a unified diff."""
    return _PROMPT_TEMPLATE.format(
        checklist=_FOCUS_CHECKLIST,
        severity_levels=SEVERITY_LEVELS,
        empty_array=EMPTY_ARRAY,
        diff=diff_text.rstrip(),
    )


__all__ = ["build_prompt"]

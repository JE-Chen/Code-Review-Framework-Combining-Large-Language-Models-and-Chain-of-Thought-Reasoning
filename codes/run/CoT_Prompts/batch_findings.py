BATCH_FINDINGS_TEMPLATE = """
# Batched Inline Findings Extraction

You are reviewing several files from one Pull Request in a single pass.
Review each file as carefully as you would on its own — the batching is only
to save round-trips, not a signal that the changes are unimportant. For each
file, scan every added ('+') and unchanged-context (' ') line on the new side
of its diff and report the specific lines that warrant a reviewer comment.

Inspect each changed line for: correctness (logic errors, wrong condition,
off-by-one, wrong return value), edge cases (None / empty / zero / negative /
missing keys / unexpected types), error handling (unhandled or swallowed
exceptions, missing validation), resource and state safety (leaked handles,
mutable defaults, unclosed context managers), security (injection, hardcoded
secrets, unvalidated input, path traversal), API misuse, and maintainability
(unclear naming, duplication, magic numbers).

You MUST output ONLY a JSON array, with no surrounding prose, no markdown
fences, and no commentary. Each element must conform to:

  {{
    "path": "<exact file path, copied verbatim from the ## File headers below>",
    "line": <integer, 1-based new-file line number>,
    "start_line": <optional integer; first affected line for multi-line fixes>,
    "severity": "info" | "warning" | "error",
    "comment": "<one or two sentences, actionable, no fluff>",
    "original": "<optional: the exact source text being replaced>",
    "suggestion": "<optional: full replacement text — same rules as a single-file review>"
  }}

Rules:
- "path" MUST exactly match one of the file paths listed below; findings
  with any other path are discarded.
- Only include lines that appear as added ('+') or unchanged context (' ')
  on the new side of that file's diff. Never reference a removed line.
- Report every genuine issue the scan surfaces across all files; do not
  suppress a real issue because a change looks small.
- Every finding must trace to something concrete and visible in that file's
  diff. Do not invent issues the code does not support; when a file genuinely
  has no issues, simply emit nothing for it.
- Each diff shows only changed and nearby lines. Imports and definitions
  elsewhere in the file are still present even when not shown. NEVER report
  something as undefined, not imported, or missing because its definition is
  not visible — flag it only if the diff itself removes the definition. Do
  not raise speculative "could / might / may" concerns with no concrete
  trigger in the visible code.
- Keep at most {max_findings} findings per file — pick the highest-signal
  ones.

Severity guide:
- "error"   — likely bug, security risk, or correctness violation.
- "warning" — maintainability, readability, performance smell.
- "info"    — minor style nit or suggestion.

{files_block}
"""

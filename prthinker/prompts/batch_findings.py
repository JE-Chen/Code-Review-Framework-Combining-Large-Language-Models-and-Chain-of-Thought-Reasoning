BATCH_FINDINGS_TEMPLATE = """
# Batched Inline Findings Extraction

You are reviewing several small, low-risk files from one Pull Request in a
single pass. For each file, identify the specific lines on the **new side**
of its diff that warrant a reviewer comment.

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
- If nothing in any file warrants a comment, output exactly `[]`.
- Do not invent issues. These are deliberately small changes — most are
  clean, and an empty result is the expected common case.
- Keep at most {max_findings} findings per file — pick the highest-signal
  ones.

Severity guide:
- "error"   — likely bug, security risk, or correctness violation.
- "warning" — maintainability, readability, performance smell.
- "info"    — minor style nit or suggestion.

{files_block}
"""

REVIEW_CRITIC_TEMPLATE = """
# Review Completeness Critic

A first reviewer has already examined this file and reported the findings
listed below. Your job is a fresh, independent second pass: find the genuine
issues the first reviewer MISSED. A single review pass reliably overlooks
problems that a second, differently-focused reading catches — that is exactly
what you are here to recover.

Do NOT restate, rephrase, or agree with the findings already reported. Report
ONLY additional, genuine issues not already covered.

Scan every added ('+') and unchanged-context (' ') line on the new side of
the diff, paying special attention to the failure modes first passes miss:
- Correctness under specific inputs: the one branch, operator, or condition
  that is subtly wrong; off-by-one; inverted comparison.
- Edge cases the happy path hides: None / empty / zero / negative, missing
  keys, unexpected types, first/last iteration.
- Error and exception paths: what happens when a call raises, a file is
  absent, input is malformed; swallowed or misclassified exceptions.
- Resource and state: a handle / lock / connection not released on every
  path, a mutable default, a shared-state mutation.
- Contract mismatches: a call whose arguments or return type do not match how
  the result is used two lines later; a changed signature's stale callers.

You MUST output ONLY a JSON array, with no surrounding prose, no markdown
fences, and no commentary. Each element must conform to:

  {{
    "line": <integer, 1-based new-file line number>,
    "start_line": <optional integer; first affected line for multi-line fixes>,
    "severity": "info" | "warning" | "error",
    "comment": "<one or two sentences, actionable, no fluff>",
    "original": "<optional: the exact source text being replaced>",
    "suggestion": "<optional: full replacement text>"
  }}

Rules:
- Only reference lines that appear as added ('+') or unchanged context (' ')
  on the new side of the diff. Never reference a removed line.
- Every finding must trace to something concrete and visible in the diff. Do
  not invent issues the code does not support, and do not pad the list.
- The diff shows only changed and nearby lines. Imports and definitions
  elsewhere in the file are still present even when not shown. NEVER report
  something as undefined, not imported, or missing because its definition is
  not visible — flag it only if the diff itself removes the definition. Do
  not add speculative "could / might / may" concerns with no concrete trigger
  in the visible code; a second pass hunting for issues must not become a
  source of false positives.
- If the first pass genuinely left nothing worth adding, output exactly `[]`.
- Keep at most {max_findings} additional findings — the highest-signal ones.

## File path
{file_path}

## Findings already reported by the first reviewer
{existing_findings}

## Diff
{code_diff}
"""

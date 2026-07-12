INLINE_FINDINGS_TEMPLATE = """
# Inline Findings Extraction

You are reviewing a single file from a Pull Request. Re-read the code diff
below and identify the specific lines on the **new side** of the diff that
warrant a reviewer comment.

You MUST output ONLY a JSON array, with no surrounding prose, no markdown
fences, and no commentary. Each element must conform to:

  {{
    "line": <integer, 1-based new-file line number>,
    "start_line": <optional integer; first affected line for multi-line fixes>,
    "severity": "info" | "warning" | "error",
    "comment": "<one or two sentences, actionable, no fluff>",
    "original": "<optional: the exact source text being replaced>",
    "suggestion": "<optional: full replacement text — see rules below>"
  }}

Rules:
- Only include lines that appear as added ('+') or unchanged context (' ')
  on the new side of the diff. Never reference a removed line.
- If there is nothing worth commenting on, output exactly `[]`.
- Do not invent issues. Every finding must trace to something visible in
  the diff.
- The diff shows only changed and nearby lines. Imports, functions, classes,
  constants, and variables defined ELSEWHERE in the file are still present
  even though they are not shown here. NEVER report something as undefined,
  not imported, missing, or unused because its definition is not visible in
  the diff — flag it only if the diff itself removes or breaks the definition.
- Report only defects you can demonstrate from the code shown. Do not raise
  speculative "this could / might / may be a problem if ..." concerns that
  name no concrete trigger in the visible code.
- Keep at most {max_findings} findings — pick the highest-signal ones.

Severity guide:
- "error"   — likely bug, security risk, or correctness violation.
- "warning" — maintainability, readability, performance smell.
- "info"    — minor style nit or suggestion.

Suggestion rules (very important):
- Include `suggestion` ONLY when the fix is unambiguous and you are highly
  confident. When in doubt, omit it — a wrong suggestion is worse than no
  suggestion because reviewers may apply it blindly.
- The suggestion MUST be the FULL replacement for the affected line range,
  preserving indentation exactly. Do NOT include the leading '+' or '-' or
  the line number.
- For a single-line fix: set `line` only.
- For a multi-line fix: set `start_line` to the first line being replaced
  and `line` to the last. The suggestion must contain that many lines.
- Only emit `suggestion` when severity is "warning" or "error". Never for
  "info" — those should be advisory comments without a patch.
- If you include `suggestion`, also include `original` with the exact text
  being replaced (used for sanity checks).

{positive_examples}
{dialogue_block}
{provenance_block}
## File path
{file_path}

## Diff
{code_diff}
"""

# Optional add-on inserted into ``INLINE_FINDINGS_TEMPLATE`` via the
# ``{provenance_block}`` placeholder when ``--provenance`` is enabled.
# Tells the model how to attach an audit trail to each finding and
# lists the RAG rules + accepted examples by index so it can cite them.
PROVENANCE_INSTRUCTIONS_TEMPLATE = """
## Audit trail (provenance)

For every finding you emit, also include a ``provenance`` field whose
shape is:

  "provenance": {{
    "confidence": <optional float in [0, 1] — your own self-rated
                   calibration; advisory only, never used to drop your
                   finding silently>,
    "citations": [
      {{
        "kind": "rag_rule" | "accepted_example" | "diff_evidence",
        "index": <1-based integer; required for rag_rule and
                  accepted_example; omit for diff_evidence>,
        "lines": [<integer, ...>],   // only for diff_evidence
        "note":  "<one-line rationale tying this citation to the finding>"
      }}
    ]
  }}

Rules:
- Cite ONLY items that genuinely informed the finding. An empty
  ``citations`` list is acceptable and preferred over made-up citations.
- ``rag_rule`` and ``accepted_example`` indices must come from the
  numbered lists below. Out-of-range citations will be dropped.
- ``diff_evidence`` lines must be lines that actually appear on the
  new side of the diff (added or unchanged context).

{rag_rules_list}
{accepted_examples_list}
"""


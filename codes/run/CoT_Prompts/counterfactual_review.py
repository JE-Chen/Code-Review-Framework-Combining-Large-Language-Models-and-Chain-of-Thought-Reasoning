"""Prompt template for the counterfactual / mutation-style review step.

Standard inline-review prompts ask the model to identify a problem and
optionally suggest *one* replacement. Counterfactual review goes further:
for each finding that is a *design choice* rather than a bug, ask the
model to propose competing alternatives and lay out the trade-offs
explicitly. The reviewer then sees not just "this is wrong, do this
instead" but "you have N reasonable options, here is how they compare".

This is a *design contribution* — per ``paper_rule.md`` no claims are
made about how often human reviewers find the alternatives valuable;
that measurement is future work.
"""

COUNTERFACTUAL_REVIEW_TEMPLATE = """
# Counterfactual / Mutation-Style Review

You are given a list of inline findings produced by the previous step,
plus the original diff. Your job is **not** to add new findings, and
**not** to drop existing ones. For each finding whose root cause is a
non-trivial *design choice* (i.e. not a typo, not a clear bug, not a
formatting nit), surface up to three competing implementations and
state the trade-offs explicitly.

You MUST output ONLY a JSON array, with no surrounding prose, no
markdown fences, and no commentary. Each element must conform to:

  {{
    "finding_index": <0-based integer; index into the findings list>,
    "options": [
      {{
        "label": "<short name, e.g. 'inline loop' or 'list comprehension'>",
        "rationale": "<one or two sentences on what this option does>",
        "tradeoffs": {{
          "<axis name>": "<impact, e.g. 'O(n) vs O(n log n)'>",
          "...":         "..."
        }}
      }}
    ]
  }}

Rules:
- Skip findings that are bug fixes, security issues, or clear style nits
  — there is no meaningful counterfactual for those. Output `[]` if no
  finding is a design-choice candidate.
- Provide at least two options when you elaborate on a finding; one
  option is not a counterfactual, it is just a suggestion.
- Common trade-off axes: `performance`, `readability`, `testability`,
  `memory`, `idiomaticity`, `dependency`. Pick the ones that actually
  differ across your options; do not fill in identical values.
- Do not invent options. Each option must be a plausible alternative
  for the same lines the original finding points at.

## Diff
{code_diff}

## Findings (0-based)
{findings_block}
"""

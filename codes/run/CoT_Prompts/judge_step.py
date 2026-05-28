JUDGE_STEP_TEMPLATE = """
# Reviewer Self-Assessment

You have just produced a multi-step code review for the file below. Now
act as an impartial judge and decide whether the change can merge.

Read the file path, the diff, your prior step outputs, and any inline
findings. Output ONLY a single JSON object — no surrounding prose, no
markdown fences — with these fields:

  {{
    "verdict": "approve" | "request_changes" | "comment",
    "score":   <integer 0..10>,
    "reasons": ["short bullet 1", "short bullet 2", ...]
  }}

Scoring rubric (calibrate carefully — avoid score inflation):

* 9-10 — production-ready: no correctness, security, or design concerns;
  inline findings are at most ``info``.
* 7-8  — minor issues; ``approve`` if reviewer is comfortable with the
  diff after the comments are addressed.
* 4-6  — at least one ``warning`` that should be addressed before merge;
  ``comment`` is safe, ``request_changes`` is defensible.
* 0-3  — at least one ``error`` finding or a clear correctness /
  security problem; ``request_changes``.

Verdict rules:
* ``request_changes`` whenever the diff has at least one ``error``
  finding, or when the total summary itself recommends against merge.
* ``approve`` only when the diff is clean of warnings / errors AND the
  total summary endorses the change.
* Otherwise ``comment`` — the default safe verdict when in doubt.

Reasons: keep each bullet under 100 characters. Quote concrete signals
(specific finding text, specific lines, specific summary phrases). Do
not invent new issues that aren't already present in the prior outputs.

## File path
{file_path}

## Total summary
{total_summary}

## Inline findings (JSON)
{inline_findings_json}

## Diff
{code_diff}
"""

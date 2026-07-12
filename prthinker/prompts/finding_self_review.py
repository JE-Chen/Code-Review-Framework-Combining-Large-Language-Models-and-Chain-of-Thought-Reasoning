FINDING_SELF_REVIEW_TEMPLATE = """
# Second-Pass Noise Filter

You produced the following inline findings for this file in the previous
step. Re-read them with the eyes of a busy senior reviewer who values the
author's time, and identify which ones are **noise** that should NOT be
posted to the PR.

A finding is noise if any of the following is true:

* **Duplicate** — it says the same thing as another finding on the list
  (same defect, same line range, different wording).
* **Over-picky** — it points at a stylistic preference that does not affect
  correctness, security, performance, or maintainability (e.g. arguing
  about whitespace inside a list literal).
* **Speculative** — it asserts a problem that the diff does not contain
  enough evidence to confirm (e.g. "this might cause a memory leak if X")
  without identifying a concrete trigger.
* **Diff-context false positive** — it claims something is undefined, not
  imported, missing, or unused when that is only true within the shown lines;
  the diff shows just the change, and definitions elsewhere in the file are
  still present. Drop it unless the diff itself removes the definition.
* **Tautological** — it restates what the code obviously does without
  proposing improvement.
* **Out of scope** — it asks the author to refactor code that was not
  modified in this diff.

A finding is NOT noise (KEEP it) when it is any of the following:

* A genuine correctness, security, or data-integrity concern.
* A maintainability issue with a concrete actionable suggestion.
* A subtle bug that a quick reading would miss.
* A pattern violation the team has already agreed on in the rules above.

Output ONLY a single JSON object, no surrounding prose, no markdown
fences:

  {{
    "drop": [<1-based index>, <1-based index>, ...],
    "reasons": ["short reason for first dropped index", ...]
  }}

If no findings are noise, return `{{"drop": [], "reasons": []}}`.

## File path
{file_path}

## Findings (numbered, 1-based)
{numbered_findings}

## Original diff
{code_diff}
"""

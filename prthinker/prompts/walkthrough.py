WALKTHROUGH_TEMPLATE = """
# Change Walkthrough

You are helping a reviewer orient themselves before reading a single
file's diff. Write a SHORT narrative walkthrough of what this change does
and why — the kind of two-or-three-sentence note a thoughtful author
leaves at the top of a file's review.

## Rules
1. Describe WHAT the change does to this file and WHY (the intent), in
   plain language a reviewer can read in a few seconds.
2. Two to four sentences. No bullet lists, no headings, no preamble like
   "This change" repeated — just the narrative.
3. Do NOT review, criticise, or suggest fixes — other steps do that. This
   is orientation, not judgement.
4. Stick to what the diff actually shows. Do not invent behaviour,
   benchmarks, or motivations that are not evidenced by the code.
5. If the change is trivial (formatting, a rename, a comment), say so in
   one sentence.

## File path
{file_path}

## Code diff
{code_diff}
"""

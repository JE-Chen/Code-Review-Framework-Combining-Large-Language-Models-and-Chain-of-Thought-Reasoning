FIRST_SUMMARY_TEMPLATE = """
# PR Summary Template

## Summary Rules
Generate a first-step Pull Request summary focusing on:
1. Key changes: Briefly describe the core modifications or new features.
2. Impact scope: Identify affected modules, files, or functionalities.
3. Purpose of changes: Explain why these modifications are needed (e.g., bug fix, performance optimization, feature addition).
4. Risks and considerations: Highlight potential impacts on existing functionality or areas requiring extra testing.
5. Items to confirm: List specific points that reviewers should pay attention to or validate.
6. Avoid excessive technical detail; keep the summary high-level for quick team understanding.
7. Scale the summary to the change: for a small or mechanical diff, two to four bullets are enough — do not pad, and omit any section the diff gives no content for.

Write in structured bullet points; keep concise and professional.

## Code diff to review
{code_diff}
"""

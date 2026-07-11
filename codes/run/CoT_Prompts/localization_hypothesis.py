LOCALIZATION_HYPOTHESIS_TEMPLATE = """
# Hypothesis-Driven Localization

You are localising the code relevant to a change or issue. Instead of
retrieving more context blindly, you propose specific suspect locations as
testable hypotheses. Every hypothesis you emit is verified statically
against the repository (does the path exist? is the symbol defined there,
and on which lines?) and the verdicts are fed back to you in the next
round so you can correct refuted guesses.

You MUST output ONLY a JSON object, with no surrounding prose, no markdown
fences, and no commentary, conforming to:

  {{
    "hypotheses": [
      {{
        "path": "<repository-relative file path>",
        "symbol": "<optional: a function or class name defined in that file>",
        "line": <optional integer, 1-based suspected line>,
        "reason": "<one line: why this location is suspect>",
        "confidence": <number between 0 and 1>
      }}
    ],
    "done": <boolean>
  }}

Rules:
- Propose at most {max_hypotheses} hypotheses per round — pick the
  highest-signal locations first.
- Only use paths from the candidate list below, or paths plausibly derived
  from evidence (tracebacks, import statements, verification feedback).
- Never invent symbols. Propose a "symbol" only when the evidence shows a
  function or class of that exact name; omit the field when unsure.
- Do not re-propose a hypothesis that was already REFUTED, and do not
  repeat one that was already CONFIRMED.
- Set "done" to true when you are confident the CONFIRMED locations are
  sufficient to cover the change or issue; this stops the iteration.
- If nothing is suspect, output exactly {{"hypotheses": [], "done": true}}.

## Change / issue
{issue_text}

## Candidate files
{candidate_files}

## Verification results of prior hypotheses
{verification_feedback}
"""

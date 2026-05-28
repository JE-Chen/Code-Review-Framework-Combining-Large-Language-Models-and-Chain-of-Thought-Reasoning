"""PR-type classification — pick the right review depth for the right PR.

Most LLM reviewers run the same five-step pipeline against every PR.
A docs-only PR doesn't need inline_findings; a hotfix doesn't need a
refactor-grade design discussion; a refactor needs deeper equivalence
analysis than a small feature. This module lets the pipeline classify
the PR first and adapt downstream behaviour.

Design:

* :class:`PRType` — six categories. ``UNKNOWN`` is the safe-failure
  default; if the model fails to classify we fall back to the full
  review (i.e. behave as before).
* :func:`build_prompt` — render the classification prompt from the
  diff, PR title, and PR body. The prompt is JSON-only so parsing is
  trivial.
* :func:`parse_classification` — safe-failure JSON parser. Malformed
  output yields :class:`PRType.UNKNOWN`, never crashes.
* :func:`budget_for` — pure function mapping ``PRType`` to a budget
  hint (``max_findings``, ``run_inline``, ``focus``); pipeline consults
  it to adapt the downstream steps without hardcoding the matrix.

Per ``paper_rule.md``'s no-fabrication rule, this module makes no claim
about classification accuracy — only the mechanism is shipped.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from enum import Enum

log = logging.getLogger(__name__)


class PRType(str, Enum):
    """Six mutually-exclusive PR categories."""

    BUGFIX = "bugfix"
    FEATURE = "feature"
    REFACTOR = "refactor"
    DOCS = "docs"
    CHORE = "chore"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ReviewBudget:
    """Pure-data review-depth hint produced from a :class:`PRType`."""

    run_inline_findings: bool = True
    max_findings_per_file: int = 10
    # Free-form one-liner appended to the inline-findings prompt to
    # steer the model toward the concerns this PR type cares about.
    focus_hint: str = ""


_DEFAULT_BUDGETS: dict[PRType, ReviewBudget] = {
    # Hotfix: shallow + focused; reviewer cares about "is the right
    # spot fixed?" and "could this re-introduce a regression?", not
    # design quality.
    PRType.BUGFIX: ReviewBudget(
        run_inline_findings=True,
        max_findings_per_file=4,
        focus_hint=(
            "This PR is a bug fix. Focus on correctness of the fix, "
            "regression risk, and whether the fix targets the actual "
            "root cause rather than a symptom."
        ),
    ),
    PRType.FEATURE: ReviewBudget(
        run_inline_findings=True,
        max_findings_per_file=10,
        focus_hint=(
            "This PR adds a new feature. Look for missing tests, error "
            "paths, public-API consistency, and configuration knobs "
            "that should be exposed."
        ),
    ),
    # Refactor: deeper review on behavioural equivalence; tolerate more
    # findings because the design surface is wider.
    PRType.REFACTOR: ReviewBudget(
        run_inline_findings=True,
        max_findings_per_file=15,
        focus_hint=(
            "This PR is a refactor. Verify behavioural equivalence with "
            "the pre-change code; flag any subtle behaviour changes "
            "(error message text, exception types, ordering, lazy vs "
            "eager evaluation)."
        ),
    ),
    # Docs: skip inline_findings entirely — there is nothing on the
    # "new side" of the diff that benefits from line-level review.
    PRType.DOCS: ReviewBudget(
        run_inline_findings=False,
        max_findings_per_file=0,
        focus_hint=(
            "This PR is docs-only. Inline findings are skipped; the "
            "consolidated summary still runs."
        ),
    ),
    # Chore: dependency bumps, version pins, lint-config tweaks. Mid
    # budget; consider pairing with --dep-upgrade-check.
    PRType.CHORE: ReviewBudget(
        run_inline_findings=True,
        max_findings_per_file=5,
        focus_hint=(
            "This PR is a chore (config / dependency / build). Look for "
            "version pinning hygiene, supply-chain risk, CI surface "
            "changes; ignore stylistic nits."
        ),
    ),
    # Unknown: safe-failure default — behave as the unclassified
    # pipeline did before.
    PRType.UNKNOWN: ReviewBudget(
        run_inline_findings=True,
        max_findings_per_file=10,
        focus_hint="",
    ),
}


def budget_for(pr_type: PRType) -> ReviewBudget:
    """Return the canonical review budget for a PR type.

    Callers wanting to override can construct their own
    :class:`ReviewBudget` instead of mutating this map.
    """
    return _DEFAULT_BUDGETS.get(pr_type, _DEFAULT_BUDGETS[PRType.UNKNOWN])


PROMPT_TEMPLATE = """\
# PR Classification

Classify this Pull Request into one of six categories. Reply with ONLY
a JSON object of the form:

  {{ "type": "bugfix" | "feature" | "refactor" | "docs" | "chore" |
              "unknown",
     "reason": "<one short sentence explaining the choice>" }}

Categories:

* ``bugfix``  — fixes a reported defect or wrong behaviour.
* ``feature`` — adds new user-visible behaviour or API surface.
* ``refactor`` — restructures existing code without intending to
                 change observable behaviour.
* ``docs``    — only changes documentation, comments, or README files.
* ``chore``   — dependency bumps, version pins, config / build
                tweaks; nothing user-visible.
* ``unknown`` — none of the above fit cleanly.

## PR title
{title}

## PR body
{body}

## Diff (truncated to first {diff_chars} characters)
{diff_excerpt}
"""


def build_prompt(
    *, diff_text: str, title: str = "", body: str = "",
    diff_chars: int = 8000,
) -> str:
    """Render the classification prompt.

    The diff is truncated because classification only needs the *shape*
    of the change, not every line. A title + body is normally enough
    for the model to be right.
    """
    excerpt = (diff_text or "")[:diff_chars]
    return PROMPT_TEMPLATE.format(
        title=(title or "(no title)").strip(),
        body=(body or "(no description)").strip(),
        diff_chars=diff_chars,
        diff_excerpt=excerpt,
    )


_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)
_OBJECT_RE = re.compile(r"\{[\s\S]*?\}")


@dataclass(frozen=True)
class Classification:
    pr_type: PRType
    reason: str = ""


def parse_classification(raw_output: str) -> Classification:
    """Best-effort parse of the model's classification reply.

    Returns ``Classification(PRType.UNKNOWN, ...)`` on any failure —
    same safe-failure posture as the inline-findings parser.
    """
    body = raw_output.strip()
    fence = _FENCE_RE.search(body)
    if fence:
        body = fence.group(1).strip()
    match = _OBJECT_RE.search(body)
    if match is None:
        log.warning("pr_classifier parser: no JSON object found")
        return Classification(pr_type=PRType.UNKNOWN)
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        log.warning("pr_classifier parser: JSON decode failed (%s)", exc)
        return Classification(pr_type=PRType.UNKNOWN)
    if not isinstance(data, dict):
        return Classification(pr_type=PRType.UNKNOWN)
    raw_kind = str(data.get("type", "")).strip().lower()
    try:
        pr_type = PRType(raw_kind)
    except ValueError:
        log.debug("pr_classifier: unknown type %r", raw_kind)
        return Classification(pr_type=PRType.UNKNOWN, reason=str(data.get("reason", "")))
    return Classification(
        pr_type=pr_type, reason=str(data.get("reason", "")).strip(),
    )


__all__ = [
    "Classification",
    "PROMPT_TEMPLATE",
    "PRType",
    "ReviewBudget",
    "build_prompt",
    "budget_for",
    "parse_classification",
]

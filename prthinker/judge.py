"""Parse and aggregate ``JudgeStep`` outputs.

The judge prompt asks for one JSON object per file. Parsing is lenient
(same posture as :mod:`prthinker.findings`): strip optional code
fences, locate the outermost ``{ ... }``, validate with Pydantic, fall
back to the safe default verdict on any failure rather than blowing up
the review.
"""

from __future__ import annotations

import logging
import re
from typing import Iterable

from pydantic import ValidationError

from prthinker.findings import extract_lenient_json
from prthinker.schemas import JudgeVerdict, Verdict

log = logging.getLogger(__name__)

_OBJ_RE = re.compile(r"\{[\s\S]*\}")

VERDICT_APPROVE: Verdict = "approve"
VERDICT_REQUEST_CHANGES: Verdict = "request_changes"
VERDICT_COMMENT: Verdict = "comment"

_GITHUB_EVENT = {
    VERDICT_APPROVE: "APPROVE",
    VERDICT_REQUEST_CHANGES: "REQUEST_CHANGES",
    VERDICT_COMMENT: "COMMENT",
}

# Mid-scale score so the safe default neither approves nor blocks.
_FALLBACK_SCORE = 5
_REASON_UNPARSEABLE = "unparseable judge output"


def _fallback_verdict(reason: str) -> JudgeVerdict:
    """Safe default verdict used whenever the judge output is unusable."""
    return JudgeVerdict(
        verdict=VERDICT_COMMENT, score=_FALLBACK_SCORE, reasons=[reason]
    )


def parse_verdict(raw: str) -> JudgeVerdict:
    """Best-effort parse; return the safe ``comment`` default on failure."""
    result = extract_lenient_json(raw, pattern=_OBJ_RE)
    if not result.matched:
        log.warning("Judge output had no JSON object: %r", raw[:200])
        return _fallback_verdict(_REASON_UNPARSEABLE)
    if result.decode_error is not None:
        log.warning("Judge JSON decode failed: %s", result.decode_error)
        return _fallback_verdict(_REASON_UNPARSEABLE)

    try:
        return JudgeVerdict.model_validate(result.data)
    except ValidationError as exc:
        log.warning("Judge verdict failed schema: %s", exc)
        return _fallback_verdict("invalid judge verdict")


def aggregate(verdicts: Iterable[JudgeVerdict]) -> Verdict:
    """Combine per-file verdicts into one PR-level decision.

    Conservative ordering: a single ``request_changes`` wins; if every
    file approves we approve; otherwise we fall back to ``comment``.
    """
    items = list(verdicts)
    if not items:
        return VERDICT_COMMENT
    if any(v.verdict == VERDICT_REQUEST_CHANGES for v in items):
        return VERDICT_REQUEST_CHANGES
    if all(v.verdict == VERDICT_APPROVE for v in items):
        return VERDICT_APPROVE
    return VERDICT_COMMENT


def to_github_event(verdict: Verdict) -> str:
    """Map our internal verdict to the GitHub Review API's ``event`` value."""
    return _GITHUB_EVENT[verdict]


__all__ = [
    "parse_verdict",
    "aggregate",
    "to_github_event",
]

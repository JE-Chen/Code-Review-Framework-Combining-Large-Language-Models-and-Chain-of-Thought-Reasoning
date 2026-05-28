"""Parse and aggregate ``JudgeStep`` outputs.

The judge prompt asks for one JSON object per file. Parsing is lenient
(same posture as :mod:`prthinker.findings`): strip optional code
fences, locate the outermost ``{ ... }``, validate with Pydantic, fall
back to the safe default verdict on any failure rather than blowing up
the review.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Iterable

from pydantic import ValidationError

from prthinker.schemas import JudgeVerdict, Verdict

log = logging.getLogger(__name__)

_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)
_OBJ_RE = re.compile(r"\{[\s\S]*\}")

_GITHUB_EVENT = {
    "approve": "APPROVE",
    "request_changes": "REQUEST_CHANGES",
    "comment": "COMMENT",
}


def parse_verdict(raw: str) -> JudgeVerdict:
    """Best-effort parse; return the safe ``comment`` default on failure."""
    body = raw.strip()
    fence = _FENCE_RE.search(body)
    if fence:
        body = fence.group(1).strip()
    match = _OBJ_RE.search(body)
    if match is None:
        log.warning("Judge output had no JSON object: %r", raw[:200])
        return JudgeVerdict(verdict="comment", score=5, reasons=["unparseable judge output"])

    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        log.warning("Judge JSON decode failed: %s", exc)
        return JudgeVerdict(verdict="comment", score=5, reasons=["unparseable judge output"])

    try:
        return JudgeVerdict.model_validate(data)
    except ValidationError as exc:
        log.warning("Judge verdict failed schema: %s", exc)
        return JudgeVerdict(verdict="comment", score=5, reasons=["invalid judge verdict"])


def aggregate(verdicts: Iterable[JudgeVerdict]) -> Verdict:
    """Combine per-file verdicts into one PR-level decision.

    Conservative ordering: a single ``request_changes`` wins; if every
    file approves we approve; otherwise we fall back to ``comment``.
    """
    items = list(verdicts)
    if not items:
        return "comment"
    if any(v.verdict == "request_changes" for v in items):
        return "request_changes"
    if all(v.verdict == "approve" for v in items):
        return "approve"
    return "comment"


def to_github_event(verdict: Verdict) -> str:
    """Map our internal verdict to the GitHub Review API's ``event`` value."""
    return _GITHUB_EVENT[verdict]


__all__ = [
    "parse_verdict",
    "aggregate",
    "to_github_event",
]

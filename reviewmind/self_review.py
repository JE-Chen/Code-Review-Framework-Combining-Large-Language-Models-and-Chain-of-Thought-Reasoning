"""Parse + apply the second-pass noise filter on inline findings.

The :class:`FindingSelfReviewStep` (see :mod:`reviewmind.steps`) runs
after ``inline_findings`` and asks the model to flag noise entries by
1-based index. This module turns the model output into a concrete list
of indices to drop, with the same conservative-fallback posture as the
findings parser: malformed output yields no drops rather than dropping
everything (better to post a noisy finding than to lose a real bug).
"""

from __future__ import annotations

import json
import logging
import re
from typing import Iterable

from reviewmind.schemas import InlineFinding

log = logging.getLogger(__name__)

_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)
_OBJ_RE = re.compile(r"\{[\s\S]*\}")


def parse_drop_indices(raw: str, *, total: int) -> set[int]:
    """Return the 0-based indices to drop, validated against the count.

    ``total`` is the number of findings the model was asked to review.
    Indices ≤ 0 or > total are silently ignored.
    """
    body = raw.strip()
    fence = _FENCE_RE.search(body)
    if fence:
        body = fence.group(1).strip()
    obj_match = _OBJ_RE.search(body)
    if obj_match is None:
        log.warning("self-review output had no JSON object: %r", raw[:200])
        return set()

    try:
        data = json.loads(obj_match.group(0))
    except json.JSONDecodeError as exc:
        log.warning("self-review JSON decode failed: %s", exc)
        return set()

    raw_indices = data.get("drop") if isinstance(data, dict) else None
    if not isinstance(raw_indices, list):
        return set()

    out: set[int] = set()
    for value in raw_indices:
        if not isinstance(value, int):
            continue
        # The prompt asks for 1-based indices; convert to 0-based.
        zero_based = value - 1
        if 0 <= zero_based < total:
            out.add(zero_based)
    return out


def apply_self_review(
    findings: list[InlineFinding],
    drop_indices: Iterable[int],
) -> list[InlineFinding]:
    """Return the findings list with `drop_indices` (0-based) removed."""
    drop = set(drop_indices)
    if not drop:
        return list(findings)
    return [f for i, f in enumerate(findings) if i not in drop]


def render_findings_block(findings: list[InlineFinding]) -> str:
    """Format findings as a numbered list for the self-review prompt."""
    lines: list[str] = []
    for i, f in enumerate(findings, start=1):
        lines.append(
            f"{i}. [{f.severity}] line {f.line}: "
            f"{f.comment.splitlines()[0][:200]}"
        )
    return "\n".join(lines) if lines else "(no findings)"


__all__ = [
    "parse_drop_indices",
    "apply_self_review",
    "render_findings_block",
]

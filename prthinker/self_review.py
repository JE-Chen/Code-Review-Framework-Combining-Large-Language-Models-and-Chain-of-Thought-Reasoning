"""Parse + apply the second-pass noise filter on inline findings.

The :class:`FindingSelfReviewStep` (see :mod:`prthinker.steps`) runs
after ``inline_findings`` and asks the model to flag noise entries by
1-based index. This module turns the model output into a concrete list
of indices to drop, with the same conservative-fallback posture as the
findings parser: malformed output yields no drops rather than dropping
everything (better to post a noisy finding than to lose a real bug).
"""

from __future__ import annotations

import logging
from typing import Iterable

from prthinker.lenient_json import extract_json_object
from prthinker.schemas import InlineFinding

log = logging.getLogger(__name__)

def _validated_zero_based_indices(
    raw_indices: list[object], *, total: int
) -> set[int]:
    """Return 1-based ints from raw_indices as in-range 0-based indices."""
    out: set[int] = set()
    for value in raw_indices:
        if not isinstance(value, int):
            continue
        # The prompt asks for 1-based indices; convert to 0-based.
        zero_based = value - 1
        if 0 <= zero_based < total:
            out.add(zero_based)
    return out


def parse_drop_indices(raw: str, *, total: int) -> set[int]:
    """Return the 0-based indices to drop, validated against the count.

    ``total`` is the number of findings the model was asked to review.
    Indices ≤ 0 or > total are silently ignored.
    """
    data = extract_json_object(raw, parser_name="self-review parser")
    raw_indices = data.get("drop") if isinstance(data, dict) else None
    if not isinstance(raw_indices, list):
        return set()
    return _validated_zero_based_indices(raw_indices, total=total)


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

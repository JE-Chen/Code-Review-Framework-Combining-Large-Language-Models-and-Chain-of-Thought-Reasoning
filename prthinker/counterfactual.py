"""Parse free-form model output into ``CounterfactualBlock`` items.

Mirrors :mod:`prthinker.findings` in spirit — code fences are stripped,
the outermost JSON array is extracted, malformed entries are silently
dropped (never crashing the run), and indices outside the findings
range are filtered.

Per ``paper_rule.md``'s no-fabrication HARD rule, this module emits no
metrics and makes no quality claims. The counterfactual feature is a
*design contribution*; whether human reviewers find the alternatives
useful is future work and is not measured here.
"""

from __future__ import annotations

import json
import logging
import re

from pydantic import ValidationError

from prthinker.schemas import CounterfactualBlock

log = logging.getLogger(__name__)

_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)
_ARRAY_RE = re.compile(r"\[[\s\S]*\]")


_MIN_OPTIONS = 2


def _strip_fences(text: str) -> str:
    match = _FENCE_RE.search(text)
    return match.group(1) if match else text


def _extract_json_array(body: str) -> list | None:
    """Extract the outermost JSON array from ``body``; ``None`` if absent."""
    match = _ARRAY_RE.search(body)
    if match is None:
        log.warning("counterfactual parser: no JSON array found in output")
        return None
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        log.warning("counterfactual parser: JSON decode failed (%s)", exc)
        return None
    return data if isinstance(data, list) else None


def _block_from_entry(entry: object) -> CounterfactualBlock | None:
    """Validate one raw entry into a block; ``None`` if malformed."""
    if not isinstance(entry, dict):
        return None
    try:
        return CounterfactualBlock.model_validate(entry)
    except ValidationError as exc:
        log.debug("Dropped malformed counterfactual %r: %s", entry, exc)
        return None


def _block_is_keepable(block: CounterfactualBlock, total_findings: int) -> bool:
    """Return whether ``block`` anchors a valid finding with enough options."""
    if not (0 <= block.finding_index < total_findings):
        log.debug(
            "Dropping counterfactual: finding_index %d out of range [0, %d)",
            block.finding_index, total_findings,
        )
        return False
    if len(block.options) < _MIN_OPTIONS:
        log.debug("Dropping counterfactual with <2 options")
        return False
    return True


def parse_counterfactuals(
    raw_output: str, *, total_findings: int,
) -> list[CounterfactualBlock]:
    """Best-effort parse. Drops blocks whose ``finding_index`` is out
    of the ``[0, total_findings)`` range.

    Returns ``[]`` if the model emitted nothing parseable — we never
    crash the pipeline on a malformed counterfactual step.
    """
    if total_findings <= 0:
        return []

    body = _strip_fences(raw_output).strip()
    if not body or body == "[]":
        return []

    data = _extract_json_array(body)
    if data is None:
        return []

    blocks: list[CounterfactualBlock] = []
    for entry in data:
        block = _block_from_entry(entry)
        if block is not None and _block_is_keepable(block, total_findings):
            blocks.append(block)
    return blocks


__all__ = ["parse_counterfactuals"]

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

import logging

from pydantic import ValidationError

from prthinker.lenient_json import extract_json_array
from prthinker.schemas import CounterfactualBlock

log = logging.getLogger(__name__)

_MIN_OPTIONS = 2


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

    data = extract_json_array(raw_output, parser_name="counterfactual parser")
    if not data:
        return []

    blocks: list[CounterfactualBlock] = []
    for entry in data:
        block = _block_from_entry(entry)
        if block is not None and _block_is_keepable(block, total_findings):
            blocks.append(block)
    return blocks


__all__ = ["parse_counterfactuals"]

"""Per-review cost estimation and a simple spend budget.

Wraps :mod:`prthinker.pricing` so callers get a plain ``float`` (USD) per
review and can cap a whole PR with :class:`CostBudget`. Unknown / unpriced
models cost ``0.0`` here so a budget never blocks on a price it cannot know.

Runner-safe: pure stdlib, no heavy ML or HTTP dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from prthinker.pricing import estimate_cost as _priced_cost


def estimate_cost(
    backend_kind: str,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
) -> float:
    """Return USD cost for the call, or ``0.0`` if the model is unpriced."""
    priced = _priced_cost(backend_kind, model, prompt_tokens, completion_tokens)
    if priced is None:
        return 0.0
    return priced


@dataclass
class CostBudget:
    """Accumulate per-review spend and report when a limit is reached."""

    _spent: float = field(default=0.0)

    def add(self, cost: float) -> float:
        """Add ``cost`` USD to the running total and return the new total."""
        if cost < 0.0:
            raise ValueError("cost must be non-negative")
        self._spent += cost
        return self._spent

    def spent(self) -> float:
        """Return the total USD accumulated so far."""
        return self._spent

    def over_budget(self, limit: float) -> bool:
        """Return ``True`` when spend has reached or passed ``limit`` USD."""
        if limit < 0.0:
            raise ValueError("limit must be non-negative")
        return self._spent >= limit


__all__ = ["estimate_cost", "CostBudget"]

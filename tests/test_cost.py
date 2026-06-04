"""Unit tests for :mod:`prthinker.cost`."""

from __future__ import annotations

import pytest

from prthinker.cost import CostBudget, estimate_cost
from prthinker.pricing import rate_for


def test_known_model_computes_prompt_and_completion_cost() -> None:
    backend, model = "openai", "gpt-4o"
    rate = rate_for(backend, model)
    assert rate is not None
    prompt_tokens, completion_tokens = 1_000_000, 500_000
    expected = (
        prompt_tokens * rate.input_per_mtok
        + completion_tokens * rate.output_per_mtok
    ) / 1_000_000
    assert estimate_cost(backend, model, prompt_tokens, completion_tokens) == expected


def test_unknown_model_returns_zero() -> None:
    assert estimate_cost("openai", "does-not-exist", 1000, 1000) == 0.0


def test_local_backend_is_unpriced_returns_zero() -> None:
    assert estimate_cost("local", "qwen3", 1000, 1000) == 0.0


def test_zero_tokens_returns_zero() -> None:
    assert estimate_cost("openai", "gpt-4o", 0, 0) == 0.0


def test_budget_accumulates() -> None:
    budget = CostBudget()
    assert budget.spent() == 0.0
    assert budget.add(1.50) == 1.50
    assert budget.add(0.50) == 2.00
    assert budget.spent() == 2.00


def test_over_budget_triggers_at_limit_boundary() -> None:
    budget = CostBudget()
    budget.add(5.0)
    assert budget.over_budget(5.0) is True   # at the boundary
    assert budget.over_budget(5.01) is False  # just inside
    assert budget.over_budget(4.99) is True   # just outside


def test_empty_budget_is_not_over_a_positive_limit() -> None:
    budget = CostBudget()
    assert budget.over_budget(1.0) is False
    assert budget.over_budget(0.0) is True  # zero limit is met by zero spend


def test_add_negative_cost_raises() -> None:
    budget = CostBudget()
    with pytest.raises(ValueError):
        budget.add(-1.0)


def test_over_budget_negative_limit_raises() -> None:
    budget = CostBudget()
    with pytest.raises(ValueError):
        budget.over_budget(-1.0)

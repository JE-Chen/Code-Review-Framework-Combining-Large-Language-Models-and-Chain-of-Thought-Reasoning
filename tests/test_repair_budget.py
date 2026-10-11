"""Timed-out and exhausted generation budgets cannot issue another call."""

import threading

import pytest

from prthinker.repair_review import BudgetBackend
from tests.conftest import FakeBackend


def test_call_budget_is_enforced():
    backend = FakeBackend(["first", "second"])
    budget = BudgetBackend(backend, 10, 1)
    assert budget.generate("prompt", 8) == "first"
    with pytest.raises(RuntimeError, match="budget"):
        budget.generate("prompt", 8)
    assert len(backend.calls) == 1


def test_timeout_requests_cancellation_and_prevents_reuse():
    cancelled = threading.Event()

    class Backend:
        def generate(self, _prompt, _limit, *, cancel_event):
            cancel_event.wait(2)
            cancelled.set()
            return "late"

    budget = BudgetBackend(Backend(), 0.02, 2)
    with pytest.raises(RuntimeError, match="timed out"):
        budget.generate("prompt", 8)
    assert cancelled.wait(1)
    with pytest.raises(RuntimeError, match="budget"):
        budget.generate("prompt", 8)

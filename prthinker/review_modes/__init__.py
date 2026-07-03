"""Opt-in review-mode registry (Registry pattern).

Each review mode contributes a prompt asking the model for a focused
whole-diff pass (security, performance, …). Modes register themselves
with ``@register_mode``; the pipeline runs the enabled ones and stores
each raw output as a step output keyed ``review_mode::<name>`` — no wire
schema change. Prompts are the source of truth and live in each mode
module under this package.

The registry primitives live in :mod:`prthinker.review_modes._registry`
so the self-registering mode modules can import ``register_mode`` without
re-entering this package's ``__init__`` (which imports those modules for
their registration side-effects).
"""

from __future__ import annotations

# Registry primitives, re-exported for the public API.
from prthinker.review_modes._registry import (
    STEP_PREFIX,
    ReviewMode,
    available_modes,
    get_mode,
    register_mode,
    run_review_modes,
)

# Built-in mode modules imported for their @register_mode side-effects.
from prthinker.review_modes import (  # noqa: F401  - registration side-effects
    accessibility,
    ai_generated,
    db_migration,
    iac,
    performance,
    refactoring,
    pii,
    secret_scan,
    security,
    test_coverage,
)

__all__ = [
    "STEP_PREFIX",
    "ReviewMode",
    "available_modes",
    "get_mode",
    "register_mode",
    "run_review_modes",
]

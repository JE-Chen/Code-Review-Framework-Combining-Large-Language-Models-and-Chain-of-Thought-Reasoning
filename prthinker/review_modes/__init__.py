"""Opt-in review-mode registry (Registry pattern).

Each review mode contributes a prompt asking the model for a focused
whole-diff pass (security, performance, …). Modes register themselves
with ``@register_mode``; the pipeline runs the enabled ones and stores
each raw output as a step output keyed ``review_mode::<name>`` — no wire
schema change. Prompts are the source of truth and live in each mode
module under this package.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass

STEP_PREFIX = "review_mode"

_PromptBuilder = Callable[[str], str]


@dataclass(frozen=True)
class ReviewMode:
    """A named, opt-in whole-diff review pass."""

    name: str
    description: str
    build_prompt: _PromptBuilder


_REGISTRY: dict[str, ReviewMode] = {}


def register_mode(name: str, description: str) -> Callable[[_PromptBuilder], _PromptBuilder]:
    """Register a review mode's prompt builder under ``name``."""
    def decorate(fn: _PromptBuilder) -> _PromptBuilder:
        if name in _REGISTRY:
            raise ValueError(f"review mode already registered: {name}")
        _REGISTRY[name] = ReviewMode(name=name, description=description, build_prompt=fn)
        return fn
    return decorate


def available_modes() -> tuple[str, ...]:
    """Return the sorted names of all registered review modes."""
    return tuple(sorted(_REGISTRY))


def get_mode(name: str) -> ReviewMode:
    """Return a registered mode, raising KeyError if unknown."""
    return _REGISTRY[name]


def run_review_modes(
    backend: object,
    diff_text: str,
    enabled: Iterable[str],
    max_new_tokens: int,
) -> dict[str, str]:
    """Run each enabled mode's prompt through the backend; return step outputs.

    Unknown mode names are skipped (the caller validates/warns). Output is
    keyed ``review_mode::<name>`` for the consolidated summary.
    """
    outputs: dict[str, str] = {}
    for name in sorted(set(enabled)):
        mode = _REGISTRY.get(name)
        if mode is None:
            continue
        raw = backend.generate(  # type: ignore[attr-defined]
            mode.build_prompt(diff_text), max_new_tokens=max_new_tokens
        )
        outputs[f"{STEP_PREFIX}::{name}"] = raw
    return outputs


# Built-in mode modules imported for their @register_mode side-effects.
from prthinker.review_modes import (  # noqa: E402,F401  - registration side-effects
    accessibility,
    db_migration,
    iac,
    performance,
    pii,
    secret_scan,
    security,
    test_coverage,
)

"""Paired bootstrap comparison for benchmark runs."""

from __future__ import annotations
import random
from dataclasses import dataclass
from statistics import mean

_CI_LOW = 0.025
_CI_HIGH = 0.975


@dataclass(frozen=True)
class PairedAblation:
    baseline: str
    treatment: str
    cases: int
    mean_f1_delta: float
    ci95: tuple[float, float]
    wins: int
    ties: int
    losses: int


def _paired_deltas(baseline, treatment):
    """Return per-case F1 deltas for paired runs, sorted by case ID."""
    a = {x.case_id: x for x in baseline}
    b = {x.case_id: x for x in treatment}
    if a.keys() != b.keys():
        raise ValueError("paired runs require identical case IDs")
    return [b[k].f1 - a[k].f1 for k in sorted(a)]


def _bootstrap_ci(deltas, bootstrap_samples, seed):
    """Return the 95% bootstrap CI for the mean of per-case deltas."""
    rng = random.Random(seed)  # nosec B311 — deterministic bootstrap resampling, not security
    boot = (
        sorted(
            mean(rng.choices(deltas, k=len(deltas)))
            for _ in range(max(1, bootstrap_samples))
        )
        if deltas
        else [0.0]
    )
    return (boot[int(_CI_LOW * (len(boot) - 1))], boot[int(_CI_HIGH * (len(boot) - 1))])


def compare_runs(
    baseline_name, baseline, treatment_name, treatment, bootstrap_samples=2000, seed=0
):
    """Compare two paired benchmark runs with a bootstrap CI over F1 deltas."""
    deltas = _paired_deltas(baseline, treatment)
    return PairedAblation(
        baseline_name,
        treatment_name,
        len(deltas),
        mean(deltas) if deltas else 0,
        _bootstrap_ci(deltas, bootstrap_samples, seed),
        sum(x > 0 for x in deltas),
        sum(x == 0 for x in deltas),
        sum(x < 0 for x in deltas),
    )

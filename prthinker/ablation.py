"""Paired bootstrap comparison for benchmark runs."""

from __future__ import annotations
import random
from dataclasses import dataclass
from statistics import mean


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


def compare_runs(
    baseline_name, baseline, treatment_name, treatment, bootstrap_samples=2000, seed=0
):
    a = {x.case_id: x for x in baseline}
    b = {x.case_id: x for x in treatment}
    if a.keys() != b.keys():
        raise ValueError("paired runs require identical case IDs")
    d = [b[k].f1 - a[k].f1 for k in sorted(a)]
    rng = random.Random(seed)  # nosec B311 — deterministic bootstrap resampling, not security
    boot = (
        sorted(mean(rng.choices(d, k=len(d))) for _ in range(max(1, bootstrap_samples)))
        if d
        else [0.0]
    )
    return PairedAblation(
        baseline_name,
        treatment_name,
        len(d),
        mean(d) if d else 0,
        (boot[int(0.025 * (len(boot) - 1))], boot[int(0.975 * (len(boot) - 1))]),
        sum(x > 0 for x in d),
        sum(x == 0 for x in d),
        sum(x < 0 for x in d),
    )

"""Paired signed-rank inference with deterministic confidence intervals."""

from __future__ import annotations

import math
import random
from statistics import mean, stdev


def wilcoxon(differences: list[float]) -> dict:
    """Two-sided signed-rank test, exact for up to 50 nonzero pairs."""
    if any(not math.isfinite(value) for value in differences):
        raise ValueError("paired differences must be finite")
    nonzero = sorted((abs(value), value > 0) for value in differences if value != 0)
    ranks = []
    index = 0
    while index < len(nonzero):
        end = index + 1
        while end < len(nonzero) and nonzero[end][0] == nonzero[index][0]:
            end += 1
        doubled_rank = index + 1 + end
        ranks.extend((doubled_rank, sign) for _, sign in nonzero[index:end])
        index = end
    positive = sum(rank for rank, sign in ranks if sign)
    total = sum(rank for rank, _ in ranks)
    if len(ranks) > 50:
        variance = sum(rank * rank for rank, _ in ranks) / 16
        distance = max(0, abs(positive / 2 - total / 4) - 0.5)
        probability = math.erfc(distance / math.sqrt(2 * variance))
        method = "two-sided signed-rank normal approximation with tie ranks and continuity correction"
    else:
        distribution = {0: 1}
        for rank, _ in ranks:
            updated = dict(distribution)
            for value, count in distribution.items():
                updated[value + rank] = updated.get(value + rank, 0) + count
            distribution = updated
        tail = sum(count for value, count in distribution.items() if value <= min(positive, total - positive))
        probability = min(1.0, 2 * tail / (2 ** len(ranks)))
        method = "exact conditional two-sided signed-rank"
    return {"statistic": min(positive, total - positive) / 2, "p_value": probability,
            "rank_biserial": (2 * positive - total) / total if total else 0.0,
            "nonzero_pairs": len(ranks), "method": method}


def holm(probabilities: list[float]) -> list[float]:
    if any(not math.isfinite(value) or not 0 <= value <= 1 for value in probabilities):
        raise ValueError("p-values must lie in [0, 1]")
    adjusted = [0.0] * len(probabilities)
    previous = 0.0
    for index, (original, probability) in enumerate(sorted(enumerate(probabilities), key=lambda item: item[1])):
        previous = min(1.0, max(previous, (len(probabilities) - index) * probability))
        adjusted[original] = previous
    return adjusted


def paired_summary(differences: list[float], *, samples=2000, seed=0) -> dict:
    if not differences:
        return {"pairs": 0, "mean_difference": None, "ci95": None, "p_value": None}
    rng = random.Random(seed)  # nosec B311 — deterministic resampling, not security
    bootstrap = sorted(mean(rng.choices(differences, k=len(differences))) for _ in range(max(1, samples)))
    standard = stdev(differences) if len(differences) > 1 else 0
    return {
        "pairs": len(differences), "mean_difference": mean(differences),
        "ci95": [bootstrap[int(0.025 * (len(bootstrap) - 1))], bootstrap[int(0.975 * (len(bootstrap) - 1))]],
        "paired_standardized_difference": mean(differences) / standard if standard else None,
        "wins": sum(value > 0 for value in differences), "ties": sum(value == 0 for value in differences),
        "losses": sum(value < 0 for value in differences), **wilcoxon(differences),
    }

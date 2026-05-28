"""Diff entropy / "diff bomb" detector.

Most LLM reviewers happily grind through a 1000-file diff and produce
review noise. The PR-size itself is a first-class review signal: huge
+ scattered diffs should be split before they are reviewed.

This module is pure-data: given the parsed ``FileDiff`` list it returns
a :class:`DiffEntropy` summary with three components:

* **size** — total number of files + lines.
* **dispersion** — Shannon entropy of the top-level-directory
  distribution. A diff that touches one feature directory has low
  dispersion; one that touches ten unrelated directories has high.
* **score** — a [0, 1] aggregate; values above the configured
  threshold trigger a "split this PR" warning at the top of the
  consolidated comment.

Per ``paper_rule.md`` no-fabrication: the thresholds are framework
defaults, not calibrated values; tune per repo.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import PurePosixPath

from prthinker.diff import FileDiff


@dataclass(frozen=True)
class DiffEntropy:
    """Pure-data PR shape summary."""

    file_count: int = 0
    added_lines: int = 0
    removed_lines: int = 0
    top_dir_distribution: dict[str, int] = None  # type: ignore[assignment]
    dispersion_entropy: float = 0.0
    score: float = 0.0
    verdict: str = "focused"  # focused / wide / bomb


# Defaults — chosen so a single-file PR scores near 0 and a 100-file
# 5000-line one touching every directory in a typical repo scores
# near 1. Real projects should tune.
DEFAULT_FILE_NORM = 50.0
DEFAULT_LINE_NORM = 2000.0
DEFAULT_THRESHOLDS = (0.4, 0.7)  # focused < 0.4 <= wide < 0.7 <= bomb


def _added_removed(file_diff: FileDiff) -> tuple[int, int]:
    """Count ``+`` and ``-`` lines on the diff body (excluding headers)."""
    added = removed = 0
    for line in file_diff.raw.splitlines():
        if line.startswith("+++") or line.startswith("---"):
            continue
        if line.startswith("+"):
            added += 1
        elif line.startswith("-"):
            removed += 1
    return added, removed


def _top_dir(path: str) -> str:
    parts = PurePosixPath(path).parts
    return parts[0] if parts else "(root)"


def _shannon(counts: list[int]) -> float:
    total = sum(counts)
    if total == 0:
        return 0.0
    p = [c / total for c in counts if c > 0]
    return -sum(pi * math.log2(pi) for pi in p)


def _tally_active(
    active: list[FileDiff],
) -> tuple[int, int, dict[str, int]]:
    """Sum +/- lines and group by top-level directory across ``active``."""
    add_total = rem_total = 0
    dir_counts: dict[str, int] = {}
    for fd in active:
        added, removed = _added_removed(fd)
        add_total += added
        rem_total += removed
        d = _top_dir(fd.path)
        dir_counts[d] = dir_counts.get(d, 0) + 1
    return add_total, rem_total, dir_counts


def _verdict_for(
    score: float, thresholds: tuple[float, float],
) -> str:
    lo, hi = thresholds
    if score < lo:
        return "focused"
    if score < hi:
        return "wide"
    return "bomb"


def compute_entropy(
    file_diffs: list[FileDiff],
    *,
    file_norm: float = DEFAULT_FILE_NORM,
    line_norm: float = DEFAULT_LINE_NORM,
    thresholds: tuple[float, float] = DEFAULT_THRESHOLDS,
) -> DiffEntropy:
    """Score the diff as focused / wide / bomb.

    ``file_norm`` / ``line_norm`` define the "this is a big PR"
    benchmark; the size component saturates at 1.0 once both are
    reached. The dispersion component is the Shannon entropy of the
    top-directory distribution normalised by ``log2(n_dirs)``.
    """
    active = [
        fd for fd in (file_diffs or [])
        if not fd.is_binary and not fd.is_deleted
    ]
    if not active:
        return DiffEntropy(top_dir_distribution={})

    add_total, rem_total, dir_counts = _tally_active(active)
    file_count = len(active)
    size_component = (
        min(1.0, file_count / file_norm) * 0.5
        + min(1.0, (add_total + rem_total) / line_norm) * 0.5
    )
    raw_entropy = _shannon(list(dir_counts.values()))
    n_dirs = len(dir_counts)
    dispersion = raw_entropy / math.log2(n_dirs) if n_dirs > 1 else 0.0
    score = min(1.0, 0.6 * size_component + 0.4 * dispersion)
    return DiffEntropy(
        file_count=file_count,
        added_lines=add_total,
        removed_lines=rem_total,
        top_dir_distribution=dict(sorted(dir_counts.items())),
        dispersion_entropy=raw_entropy,
        score=score,
        verdict=_verdict_for(score, thresholds),
    )


__all__ = ["DEFAULT_THRESHOLDS", "DiffEntropy", "compute_entropy"]

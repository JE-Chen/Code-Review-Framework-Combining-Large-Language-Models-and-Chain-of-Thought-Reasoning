"""Derive prthinker-managed PR labels from a review result.

Pure and model-free: labels are a function of the reviewed file count and
the worst finding severity, so they scan at the PR-list level without
opening the PR. Every label carries the :data:`MANAGED_PREFIX` so the
setter can reconcile them across runs without touching human labels.
"""

from __future__ import annotations

from prthinker.pipeline import ReviewResult

MANAGED_PREFIX = "prthinker/"

# (upper-bound-exclusive file count, bucket name); anything larger is "xl".
_SIZE_BUCKETS: tuple[tuple[int, str], ...] = (
    (5, "xs"), (20, "s"), (50, "m"), (150, "l"),
)


def _size_label(reviewed: int) -> str:
    for cap, name in _SIZE_BUCKETS:
        if reviewed < cap:
            return f"{MANAGED_PREFIX}size-{name}"
    return f"{MANAGED_PREFIX}size-xl"


def _status_label(result: ReviewResult) -> str:
    has_error = False
    has_warning = False
    for fr in result.per_file:
        for finding in fr.inline_findings:
            has_error = has_error or finding.severity == "error"
            has_warning = has_warning or finding.severity == "warning"
    if has_error:
        return f"{MANAGED_PREFIX}changes-requested"
    if has_warning:
        return f"{MANAGED_PREFIX}review-suggested"
    return f"{MANAGED_PREFIX}clean"


def compute_labels(result: ReviewResult) -> list[str]:
    """The managed labels for this review: one size bucket + one status."""
    reviewed = sum(
        1 for fr in result.per_file if not (fr.is_binary or fr.is_deleted)
    )
    return [_size_label(reviewed), _status_label(result)]


__all__ = ["compute_labels", "MANAGED_PREFIX"]

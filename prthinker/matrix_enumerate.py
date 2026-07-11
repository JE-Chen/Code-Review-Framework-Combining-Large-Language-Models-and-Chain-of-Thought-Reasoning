"""Enumerate-time matrix prefilter for the GitHub Actions workflow.

The ``enumerate`` job in ``.github/workflows/prthinker.yml`` decides which
PR files get a review shard. Beyond the exclude-glob and unchanged-blob
filters that live inline in the workflow, this module supplies the adaptive
step-plan prefilter: files whose per-file diff classifies as the ``skip``
tier (machine-generated paths such as lockfiles / vendored trees, and
whitespace-only reformatting) are excluded from the matrix entirely, so no
runner shard is ever spawned for them.

Runner-profile safe: :mod:`prthinker.step_planner` and
:mod:`prthinker.diff` are pure stdlib, so the enumerate job stays on the
``httpx + pydantic + PyYAML`` dependency surface.
"""

from __future__ import annotations

from prthinker.diff import FileDiff
from prthinker.step_planner import STEP_PLAN_ADAPTIVE, TIER_SKIP, classify_depth


def should_skip_shard(path: str, patch: str, step_plan: str) -> bool:
    """True when adaptive planning would skip this file's review entirely.

    ``patch`` is the unified diff GitHub's PR-files API returns for the
    file (empty for binary or oversized files — those are never
    prefiltered on content here; only a generated-path match can skip
    them). Only the ``skip`` tier is excluded: trivial / standard / deep
    files still get their shard, and any plan other than ``adaptive``
    disables the prefilter so the historical matrix is preserved.
    """
    if step_plan != STEP_PLAN_ADAPTIVE or not path:
        return False
    file_diff = FileDiff(path=path, raw=patch or "")
    return classify_depth(file_diff) == TIER_SKIP


__all__ = ["should_skip_shard"]

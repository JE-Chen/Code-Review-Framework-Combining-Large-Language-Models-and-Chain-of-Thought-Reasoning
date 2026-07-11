"""Tests for the enumerate-time adaptive step-plan matrix prefilter."""

from __future__ import annotations

from prthinker.matrix_enumerate import should_skip_shard
from prthinker.step_planner import STEP_PLAN_ADAPTIVE, STEP_PLAN_FULL

_CODE_PATCH = (
    "@@ -1,2 +1,3 @@\n"
    " def handler(payload):\n"
    "-    return payload.total\n"
    "+    total = payload.total\n"
    "+    return total * 2\n"
)

# Every added line differs from a removed line only in trailing whitespace.
_WHITESPACE_ONLY_PATCH = (
    "@@ -1,2 +1,2 @@\n"
    "-def handler(payload):  \n"
    "+def handler(payload):\n"
    "-    return payload.total\t\n"
    "+    return payload.total\n"
)

_LOCK_PATCH = (
    "@@ -1,3 +1,3 @@\n"
    '-    "left-pad": "1.0.0",\n'
    '+    "left-pad": "1.0.1",\n'
)


def test_lockfile_is_excluded() -> None:
    assert should_skip_shard("package-lock.json", _LOCK_PATCH, STEP_PLAN_ADAPTIVE)


def test_nested_lockfile_is_excluded() -> None:
    assert should_skip_shard("app/poetry.lock", _LOCK_PATCH, STEP_PLAN_ADAPTIVE)


def test_vendored_path_is_excluded() -> None:
    assert should_skip_shard("vendor/lib/util.js", _CODE_PATCH, STEP_PLAN_ADAPTIVE)


def test_code_file_is_kept() -> None:
    assert not should_skip_shard("src/handler.py", _CODE_PATCH, STEP_PLAN_ADAPTIVE)


def test_whitespace_only_change_is_excluded() -> None:
    assert should_skip_shard(
        "src/handler.py", _WHITESPACE_ONLY_PATCH, STEP_PLAN_ADAPTIVE
    )


def test_full_plan_disables_prefilter() -> None:
    assert not should_skip_shard("package-lock.json", _LOCK_PATCH, STEP_PLAN_FULL)
    assert not should_skip_shard(
        "src/handler.py", _WHITESPACE_ONLY_PATCH, STEP_PLAN_FULL
    )


def test_unknown_plan_disables_prefilter() -> None:
    assert not should_skip_shard("package-lock.json", _LOCK_PATCH, "")


def test_empty_patch_keeps_code_file() -> None:
    # Binary / oversized files arrive with no patch; content checks
    # cannot classify them, so the shard decides.
    assert not should_skip_shard("src/handler.py", "", STEP_PLAN_ADAPTIVE)


def test_empty_patch_still_excludes_generated_path() -> None:
    assert should_skip_shard("yarn.lock", "", STEP_PLAN_ADAPTIVE)


def test_empty_path_is_kept() -> None:
    assert not should_skip_shard("", _CODE_PATCH, STEP_PLAN_ADAPTIVE)

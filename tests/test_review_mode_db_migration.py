"""Tests for the self-registering ``db-migration`` review mode."""

from __future__ import annotations

import prthinker.review_modes.db_migration as db_migration_mode
from prthinker.review_modes import available_modes, get_mode

_SAMPLE_DIFF = (
    "diff --git a/migrations/0007.sql b/migrations/0007.sql\n"
    "@@ -0,0 +1,2 @@\n"
    "+ALTER TABLE users ADD COLUMN email TEXT NOT NULL;\n"
    "+DROP TABLE legacy_accounts;\n"
)


def test_mode_is_registered() -> None:
    assert "db-migration" in available_modes()
    mode = get_mode("db-migration")
    assert mode.description == "DB-migration pass"
    assert mode.build_prompt is db_migration_mode.build_prompt


def test_build_prompt_contains_diff_and_keywords() -> None:
    prompt = db_migration_mode.build_prompt(_SAMPLE_DIFF)
    assert isinstance(prompt, str)
    assert _SAMPLE_DIFF in prompt
    keywords = ("NOT NULL", "DESTRUCTIVE", "DOWN-migration", "INDEX", "DATA-LOSS")
    hits = [kw for kw in keywords if kw in prompt]
    assert len(hits) >= 2


def test_empty_diff_still_returns_nonempty_prompt() -> None:
    prompt = db_migration_mode.build_prompt("")
    assert isinstance(prompt, str)
    assert prompt.strip()

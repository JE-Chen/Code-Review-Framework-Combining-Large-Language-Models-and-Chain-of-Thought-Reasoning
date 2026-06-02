"""Self-registering ``db-migration`` review mode.

Contributes a focused whole-diff prompt that frames the model as a
database-migration reviewer. It inspects ONLY the supplied unified diff
for migration-specific hazards (destructive schema changes, unsafe
NOT NULL adds, locking long-running migrations, missing down-migrations,
data-loss risk, index changes) and returns findings as a JSON array.

Per ``paper_rule.md`` no-fabrication: this is a *design contribution*;
no claim is made about empirical detection quality.
"""

from __future__ import annotations

from prthinker.review_modes import register_mode

_SEVERITY_VALUES = "info/warning/error"
_EMPTY_ARRAY = "[]"

_FOCUS_CHECKLIST = (
    "- DESTRUCTIVE or irreversible schema changes (DROP TABLE, DROP COLUMN, "
    "TRUNCATE, type narrowing that loses data).\n"
    "- Adding a NOT NULL column WITHOUT a default (or a backfill) on an "
    "existing populated table.\n"
    "- LOCKING or long-running migrations on large tables (full table "
    "rewrites, blocking ALTERs, non-concurrent index builds).\n"
    "- Missing DOWN-migration / rollback path for an applied change.\n"
    "- DATA-LOSS risk (in-place transforms, deletes, lossy backfills).\n"
    "- INDEX changes (adds, drops, uniqueness changes) and their lock or "
    "query-plan impact."
)

_INSTRUCTIONS = (
    f"Report findings as a JSON array of objects, each with at least "
    f'"path", "line", "severity" ({_SEVERITY_VALUES}), and "comment". '
    f"If nothing in the focus list applies, return an empty array {_EMPTY_ARRAY}."
)


@register_mode("db-migration", "DB-migration pass")
def build_prompt(diff_text: str) -> str:
    """Build the db-migration review prompt for a unified diff."""
    return (
        "You are performing a focused DATABASE-MIGRATION review pass. "
        "Consider ONLY the supplied unified diff below; do not assume any "
        "code outside it. Look specifically for:\n"
        f"{_FOCUS_CHECKLIST}\n\n"
        f"{_INSTRUCTIONS}\n\n"
        "Unified diff:\n"
        f"{diff_text}\n"
    )


__all__ = ["build_prompt"]

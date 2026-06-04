"""Golden-set regression snapshots for prompt/behaviour drift detection.

This module persists the inline findings of a :class:`ReviewResult` as
stable, deterministic JSON and diffs a fresh result against a saved
snapshot. It is a framework-only drift detector: it reports which finding
keys appeared or disappeared, never scores or aggregate numbers (per
``paper_rule.md``). Pure stdlib, runner-safe.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover — typing-only import, runner-safe
    from prthinker.pipeline import ReviewResult

_ENCODING = "utf-8"
_KEY_PATH = "path"
_KEY_LINE = "line"
_KEY_SEVERITY = "severity"
_KEY_COMMENT = "comment"


@dataclass(frozen=True)
class SnapshotDiff:
    """Keys added to / removed from a golden snapshot by a fresh result."""

    added: list[str]
    removed: list[str]


def _finding_records(result: ReviewResult) -> list[dict[str, object]]:
    """Return the result's inline findings as sorted plain dict records."""
    records = [
        {
            _KEY_PATH: finding.path,
            _KEY_LINE: finding.line,
            _KEY_SEVERITY: finding.severity,
            _KEY_COMMENT: finding.comment,
        }
        for finding in result.inline_findings
    ]
    records.sort(
        key=lambda record: (
            record[_KEY_PATH],
            record[_KEY_LINE],
            record[_KEY_SEVERITY],
            record[_KEY_COMMENT],
        )
    )
    return records


def _record_key(record: dict[str, object]) -> str:
    """Build the identity key ``path::line::comment`` for a finding record."""
    return f"{record[_KEY_PATH]}::{record[_KEY_LINE]}::{record[_KEY_COMMENT]}"


def write_snapshot(result: ReviewResult, path: str) -> None:
    """Write the result's inline findings as stable, sorted JSON to ``path``."""
    records = _finding_records(result)
    with open(path, "w", encoding=_ENCODING) as handle:
        json.dump(records, handle, ensure_ascii=False, indent=2, sort_keys=True)


def _load_snapshot(path: str) -> list[dict[str, object]]:
    """Load saved snapshot records, treating a missing file as empty."""
    try:
        with open(path, encoding=_ENCODING) as handle:
            return json.load(handle)
    except FileNotFoundError:
        return []


def diff_snapshot(result: ReviewResult, path: str) -> SnapshotDiff:
    """Diff the result's findings against the saved snapshot by identity key."""
    current = {_record_key(record): record for record in _finding_records(result)}
    saved = {_record_key(record): record for record in _load_snapshot(path)}
    added = sorted(key for key in current if key not in saved)
    removed = sorted(key for key in saved if key not in current)
    return SnapshotDiff(added=added, removed=removed)

"""CSV exporter for review results.

A flat CSV is the lowest-friction way to triage a review in a spreadsheet
or pipe into ``awk`` / ``grep``: sort by severity, filter by path, tally
by rule. This writer emits one row per inline finding and per located
orientation signal, with a stable column header, quoting handled by the
stdlib ``csv`` module so a comment containing a comma or newline never
corrupts the file.

Runner-safe: stdlib ``csv`` + ``io`` plus the pure signal helper.
"""

from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import TYPE_CHECKING

from prthinker.signals import RULE_PREFIX, collect_signal_findings

if TYPE_CHECKING:
    from prthinker.pipeline import ReviewResult

_HEADER = ("type", "rule", "severity", "path", "line", "message")


def _finding_rows(result: "ReviewResult") -> list[tuple]:
    """One row per inline finding."""
    return [
        (
            "finding",
            f"{RULE_PREFIX}/{f.severity}",
            f.severity,
            f.path,
            f.line,
            f.comment,
        )
        for f in result.inline_findings
    ]


def _signal_rows(result: "ReviewResult") -> list[tuple]:
    """One row per located orientation signal."""
    rows: list[tuple] = []
    for signal in collect_signal_findings(result.code_diff or ""):
        if signal.path is None:
            continue
        rows.append(
            (
                "signal",
                f"{RULE_PREFIX}/{signal.rule_id}",
                signal.level,
                signal.path,
                signal.line if signal.line is not None else "",
                signal.message,
            )
        )
    return rows


def to_csv_string(result: "ReviewResult") -> str:
    """Render the findings + signals as a CSV document string."""
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer)
    writer.writerow(_HEADER)
    writer.writerows(_finding_rows(result) + _signal_rows(result))
    return buffer.getvalue()


def write_csv(result: "ReviewResult", out_path: "str | Path") -> None:
    """Serialize the findings + signals as CSV to ``out_path``."""
    # newline="" is required so the csv module controls line terminators.
    with Path(out_path).open("w", encoding="utf-8", newline="") as handle:
        handle.write(to_csv_string(result))


__all__ = ["to_csv_string", "write_csv"]

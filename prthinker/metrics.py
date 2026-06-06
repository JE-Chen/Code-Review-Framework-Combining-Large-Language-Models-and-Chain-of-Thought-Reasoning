"""Machine-readable metrics rollup for a review result.

The PR comment, SARIF, HTML, Code Quality, and JUnit outputs are all
*per-finding*. A dashboard or trend tracker instead wants one compact
record per review: how many findings by severity, how many of each
orientation signal, the diff size, and how many files were reviewed.
This exporter produces exactly that as a small JSON object so a CI step
can append it to a time series (or a Prometheus textfile collector can
scrape it) without re-deriving the numbers downstream.

Runner-safe: stdlib ``json`` plus the pure signal / change-stat helpers.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import TYPE_CHECKING

from prthinker.change_stats import compute_change_stats
from prthinker.signals import collect_signal_findings

if TYPE_CHECKING:
    from prthinker.pipeline import ReviewResult

METRICS_SCHEMA_VERSION = 1

_SEVERITIES = ("error", "warning", "info")


def _finding_counts(result: "ReviewResult") -> dict[str, int]:
    """Count inline findings per severity, always returning every bucket."""
    counts = {sev: 0 for sev in _SEVERITIES}
    for finding in result.inline_findings:
        key = finding.severity if finding.severity in counts else "info"
        counts[key] += 1
    return counts


def _diff_metrics(result: "ReviewResult") -> dict[str, int]:
    """Files-changed / added / removed totals from the diff."""
    stats = compute_change_stats(result.code_diff or "")
    return {
        "files_changed": len(stats),
        "added": sum(stat.added for stat in stats.values()),
        "removed": sum(stat.removed for stat in stats.values()),
    }


def _signal_metrics(result: "ReviewResult") -> dict[str, object]:
    """Orientation-signal totals: overall, by level, and by rule id."""
    signals = collect_signal_findings(result.code_diff or "")
    by_rule = Counter(signal.rule_id for signal in signals)
    by_level = Counter(signal.level for signal in signals)
    return {
        "total": len(signals),
        "by_level": dict(sorted(by_level.items())),
        "by_rule": dict(sorted(by_rule.items())),
    }


def compute_metrics(result: "ReviewResult") -> dict[str, object]:
    """Build the compact metrics rollup for one review result."""
    finding_counts = _finding_counts(result)
    return {
        "schema_version": METRICS_SCHEMA_VERSION,
        "files_reviewed": len(result.per_file),
        "diff": _diff_metrics(result),
        "findings": {
            "total": sum(finding_counts.values()),
            "by_severity": finding_counts,
        },
        "signals": _signal_metrics(result),
    }


def write_metrics(result: "ReviewResult", out_path: "str | Path") -> None:
    """Serialize the metrics rollup as JSON to ``out_path``."""
    with Path(out_path).open("w", encoding="utf-8") as handle:
        json.dump(compute_metrics(result), handle, indent=2, ensure_ascii=False)


__all__ = ["METRICS_SCHEMA_VERSION", "compute_metrics", "write_metrics"]

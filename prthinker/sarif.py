"""Pure SARIF 2.1.0 exporter for review results.

Maps a :class:`prthinker.pipeline.ReviewResult`'s inline findings onto a
SARIF 2.1.0 log object so the review output can be uploaded to GitHub code
scanning or any SARIF-aware viewer. Runner-safe: stdlib + ``json`` only,
no heavy ML imports.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from prthinker.pipeline import ReviewResult
    from prthinker.schemas import InlineFinding

SARIF_SCHEMA_URI = (
    "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/"
    "Schemas/sarif-schema-2.1.0.json"
)
SARIF_VERSION = "2.1.0"

# SARIF result levels. "note" is the catch-all for any severity that is
# not explicitly an error or a warning (SARIF only defines
# none/note/warning/error).
_LEVEL_ERROR = "error"
_LEVEL_WARNING = "warning"
_LEVEL_NOTE = "note"

# Severity strings used by :class:`InlineFinding` map onto SARIF levels.
_SEVERITY_TO_LEVEL: dict[str, str] = {
    "error": _LEVEL_ERROR,
    "warning": _LEVEL_WARNING,
}

# Stable ruleId prefix so every finding shares a recognisable namespace.
_RULE_ID_PREFIX = "prthinker"


def severity_to_level(severity: str) -> str:
    """Map an :class:`InlineFinding` severity onto a SARIF result level."""
    return _SEVERITY_TO_LEVEL.get(severity, _LEVEL_NOTE)


def _finding_to_result(finding: "InlineFinding") -> dict:
    """Build one SARIF ``results[]`` entry from an inline finding."""
    region: dict = {"startLine": finding.line}
    if finding.start_line is not None:
        region["startLine"] = finding.start_line
        region["endLine"] = finding.line
    location = {
        "physicalLocation": {
            "artifactLocation": {"uri": finding.path},
            "region": region,
        }
    }
    return {
        "ruleId": f"{_RULE_ID_PREFIX}/{finding.severity}",
        "level": severity_to_level(finding.severity),
        "message": {"text": finding.comment},
        "locations": [location],
    }


def _collect_rules(findings: "list[InlineFinding]") -> list[dict]:
    """Derive the deduplicated ``tool.driver.rules[]`` array from findings."""
    seen: dict[str, dict] = {}
    for finding in findings:
        rule_id = f"{_RULE_ID_PREFIX}/{finding.severity}"
        if rule_id not in seen:
            seen[rule_id] = {
                "id": rule_id,
                "name": finding.severity,
                "shortDescription": {
                    "text": f"prthinker {finding.severity} finding"
                },
                "defaultConfiguration": {
                    "level": severity_to_level(finding.severity)
                },
            }
    return list(seen.values())


def to_sarif(
    result: "ReviewResult",
    *,
    tool_name: str = "prthinker",
    tool_version: str = "0",
) -> dict:
    """Convert a :class:`ReviewResult` into a SARIF 2.1.0 log dict."""
    findings = list(result.inline_findings)
    results = [_finding_to_result(f) for f in findings]
    run = {
        "tool": {
            "driver": {
                "name": tool_name,
                "version": tool_version,
                "rules": _collect_rules(findings),
            }
        },
        "results": results,
    }
    return {
        "$schema": SARIF_SCHEMA_URI,
        "version": SARIF_VERSION,
        "runs": [run],
    }


def write_sarif(
    result: "ReviewResult",
    out_path: "str | Path",
    *,
    tool_name: str = "prthinker",
    tool_version: str = "0",
) -> None:
    """Serialize a :class:`ReviewResult` as SARIF JSON to ``out_path``."""
    sarif = to_sarif(result, tool_name=tool_name, tool_version=tool_version)
    with Path(out_path).open("w", encoding="utf-8") as handle:
        json.dump(sarif, handle, indent=2, ensure_ascii=False)


__all__ = ["severity_to_level", "to_sarif", "write_sarif"]

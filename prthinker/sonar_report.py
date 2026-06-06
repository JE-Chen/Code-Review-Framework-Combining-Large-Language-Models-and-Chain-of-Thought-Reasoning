"""SonarQube Generic Issue Data exporter for review results.

SonarQube imports externally-produced issues from a JSON file referenced
by ``sonar.externalIssuesReportPaths`` — a different schema from SARIF or
the GitLab CodeClimate format. Teams standardised on SonarQube get the
prthinker findings (and located orientation signals) in their quality
gate without adopting SARIF. This writer emits that ``{"issues": [...]}``
shape with the required ``engineId`` / ``ruleId`` / ``severity`` /
``type`` / ``primaryLocation`` fields.

Runner-safe: stdlib ``json`` plus the pure signal helper.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from prthinker.signals import collect_signal_findings

if TYPE_CHECKING:
    from prthinker.pipeline import ReviewResult
    from prthinker.schemas import InlineFinding

_ENGINE_ID = "prthinker"

# SonarQube severities and issue types are closed sets.
_SEVERITY = {
    "error": "CRITICAL",
    "warning": "MAJOR",
    "info": "INFO",
    "note": "INFO",
}
_DEFAULT_SEVERITY = "INFO"
_TYPE_BUG = "BUG"
_TYPE_SMELL = "CODE_SMELL"


def severity_to_sonar(severity: str) -> str:
    """Map a finding severity / signal level onto a SonarQube severity."""
    return _SEVERITY.get(severity, _DEFAULT_SEVERITY)


def _issue(rule_id: str, severity: str, issue_type: str, message: str,
           path: str, line: int) -> dict:
    """Build one SonarQube generic issue object."""
    return {
        "engineId": _ENGINE_ID,
        "ruleId": rule_id,
        "severity": severity,
        "type": issue_type,
        "primaryLocation": {
            "message": message,
            "filePath": path,
            # Callers always pass a 1-based line (findings are schema-bound
            # to >= 1; signals fall back to 1), which SonarQube requires.
            "textRange": {"startLine": line},
        },
    }


def _finding_issue(finding: "InlineFinding") -> dict:
    """Map one inline finding onto a SonarQube issue."""
    issue_type = _TYPE_BUG if finding.severity == "error" else _TYPE_SMELL
    return _issue(
        f"{_ENGINE_ID}/{finding.severity}",
        severity_to_sonar(finding.severity),
        issue_type,
        finding.comment,
        finding.path,
        finding.line,
    )


def _signal_issues(result: "ReviewResult") -> list[dict]:
    """Map located orientation signals onto SonarQube issues.

    Pathless navigation signals are skipped — SonarQube requires a
    ``filePath`` on every issue.
    """
    issues: list[dict] = []
    for signal in collect_signal_findings(result.code_diff or ""):
        if signal.path is None:
            continue
        issue_type = _TYPE_BUG if signal.level == "error" else _TYPE_SMELL
        issues.append(
            _issue(
                f"{_ENGINE_ID}/{signal.rule_id}",
                severity_to_sonar(signal.level),
                issue_type,
                signal.message,
                signal.path,
                signal.line or 1,
            )
        )
    return issues


def to_sonar(result: "ReviewResult") -> dict:
    """Convert a :class:`ReviewResult` into a SonarQube generic-issue dict."""
    issues = [_finding_issue(f) for f in result.inline_findings]
    issues += _signal_issues(result)
    return {"issues": issues}


def write_sonar(result: "ReviewResult", out_path: "str | Path") -> None:
    """Serialize a :class:`ReviewResult` as SonarQube issue JSON."""
    with Path(out_path).open("w", encoding="utf-8") as handle:
        json.dump(to_sonar(result), handle, indent=2, ensure_ascii=False)


__all__ = ["severity_to_sonar", "to_sonar", "write_sonar"]

"""GitLab Code Quality (CodeClimate) JSON exporter for review results.

GitLab CI renders a "Code Quality" widget on the merge request from a
CodeClimate-format JSON artifact: a flat array of issue objects, each with
a ``description``, a ``severity``, a stable ``fingerprint``, and a
``location`` (path + begin line). This exporter maps both the model
inline findings and the no-model orientation signals onto that schema so a
GitLab MR shows them inline without any GitLab-specific plumbing
elsewhere.

Runner-safe: stdlib ``json`` + ``hashlib`` only; the fingerprint hash is
``usedforsecurity=False`` (it is a dedup key, not a security token).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import TYPE_CHECKING

from prthinker.signals import collect_signal_findings

if TYPE_CHECKING:
    from prthinker.pipeline import ReviewResult
    from prthinker.schemas import InlineFinding

# CodeClimate severities are a closed set; map the project's three finding
# severities and the signal levels onto it.
_SEVERITY_TO_CODECLIMATE = {
    "error": "critical",
    "warning": "major",
    "info": "info",
    "note": "info",
}
_DEFAULT_SEVERITY = "info"
_RULE_PREFIX = "prthinker"


def severity_to_codeclimate(severity: str) -> str:
    """Map a finding severity / signal level onto a CodeClimate severity."""
    return _SEVERITY_TO_CODECLIMATE.get(severity, _DEFAULT_SEVERITY)


def _fingerprint(check_name: str, path: str, line: int, text: str) -> str:
    """Stable dedup key for an issue (GitLab requires a unique fingerprint)."""
    raw = f"{check_name}\0{path}\0{line}\0{text}".encode("utf-8")
    return hashlib.sha256(raw, usedforsecurity=False).hexdigest()


def _issue(
    check_name: str, severity: str, description: str, path: str, line: int
) -> dict:
    """Build one CodeClimate issue object."""
    return {
        "description": description,
        "check_name": check_name,
        "fingerprint": _fingerprint(check_name, path, line, description),
        "severity": severity,
        "location": {"path": path, "lines": {"begin": line}},
    }


def _finding_issue(finding: "InlineFinding") -> dict:
    """Map one inline finding onto a CodeClimate issue."""
    return _issue(
        f"{_RULE_PREFIX}/{finding.severity}",
        severity_to_codeclimate(finding.severity),
        finding.comment,
        finding.path,
        finding.line,
    )


def _signal_issues(result: "ReviewResult") -> list[dict]:
    """Map the located orientation signals onto CodeClimate issues.

    Signals without a line (file-level navigation hints) are anchored at
    line 1 so GitLab still attaches them to the file.
    """
    issues: list[dict] = []
    for signal in collect_signal_findings(result.code_diff or ""):
        if signal.path is None:
            continue
        issues.append(
            _issue(
                f"{_RULE_PREFIX}/{signal.rule_id}",
                severity_to_codeclimate(signal.level),
                signal.message,
                signal.path,
                signal.line or 1,
            )
        )
    return issues


def to_codequality(result: "ReviewResult") -> list[dict]:
    """Convert a :class:`ReviewResult` into a CodeClimate issue list."""
    issues = [_finding_issue(f) for f in result.inline_findings]
    issues += _signal_issues(result)
    return issues


def write_codequality(result: "ReviewResult", out_path: "str | Path") -> None:
    """Serialize a :class:`ReviewResult` as Code Quality JSON to ``out_path``."""
    payload = to_codequality(result)
    with Path(out_path).open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


__all__ = ["severity_to_codeclimate", "to_codequality", "write_codequality"]

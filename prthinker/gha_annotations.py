"""GitHub Actions workflow-command annotations for review results.

When a job prints ``::error file=app.py,line=10::message`` to its stdout,
GitHub renders it as an inline annotation on the PR's Files-changed tab
and in the run summary. Emitting findings (and located orientation
signals) this way puts them exactly where the author is already looking,
without the inline-review API's 422 fragility. This is complementary to
the SARIF upload: annotations are immediate and free, SARIF feeds the
Security tab.

Runner-safe: pure string building plus the signal helper. The strict
workflow-command escaping (``%``/CR/LF in data; additionally ``:``/``,``
in properties) is applied so a multi-line comment never breaks the
command.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from prthinker.signals import collect_signal_findings

if TYPE_CHECKING:
    from prthinker.pipeline import ReviewResult
    from prthinker.schemas import InlineFinding

# Finding severity / signal level -> workflow-command level.
_LEVEL = {
    "error": "error",
    "warning": "warning",
    "info": "notice",
    "note": "notice",
}
_DEFAULT_LEVEL = "notice"
_RULE_PREFIX = "prthinker"


def _escape_data(text: str) -> str:
    """Escape the message body of a workflow command."""
    return text.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def _escape_prop(text: str) -> str:
    """Escape a property value (file / title) of a workflow command."""
    return _escape_data(text).replace(":", "%3A").replace(",", "%2C")


def _command(level: str, title: str, message: str, path: str | None,
             line: int | None) -> str:
    """Assemble one ``::level prop=…::message`` workflow command."""
    props = [f"title={_escape_prop(title)}"]
    if path is not None:
        props.insert(0, f"file={_escape_prop(path)}")
        if line is not None:
            props.insert(1, f"line={line}")
    return f"::{level} {','.join(props)}::{_escape_data(message)}"


def _finding_command(finding: "InlineFinding") -> str:
    """Workflow command for one inline finding."""
    return _command(
        _LEVEL.get(finding.severity, _DEFAULT_LEVEL),
        f"{_RULE_PREFIX}/{finding.severity}",
        finding.comment,
        finding.path,
        finding.line,
    )


def _signal_commands(result: "ReviewResult") -> list[str]:
    """Workflow commands for the orientation signals."""
    return [
        _command(
            _LEVEL.get(signal.level, _DEFAULT_LEVEL),
            f"{_RULE_PREFIX}/{signal.rule_id}",
            signal.message,
            signal.path,
            signal.line,
        )
        for signal in collect_signal_findings(result.code_diff or "")
    ]


def to_gha_annotations(result: "ReviewResult") -> list[str]:
    """Return the workflow-command lines for every finding and signal."""
    return [_finding_command(f) for f in result.inline_findings] + (
        _signal_commands(result)
    )


def print_gha_annotations(result: "ReviewResult") -> None:
    """Write the workflow commands to stdout for GitHub Actions to render."""
    # Workflow commands MUST go to stdout (not the logger) for the runner
    # to parse them into inline annotations.
    for line in to_gha_annotations(result):
        sys.stdout.write(line + "\n")


__all__ = ["print_gha_annotations", "to_gha_annotations"]

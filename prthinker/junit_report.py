"""JUnit XML exporter for review results.

Most CI systems (GitHub Actions test-reporter, GitLab, Jenkins, CircleCI)
render a JUnit XML artifact as a test report. Emitting the review findings
in that shape lets a reviewer see them in the same panel as the unit
tests: one ``<testsuite>`` per changed file, one ``<testcase>`` per
finding, with an ``<error>`` for error-severity and a ``<failure>`` for
everything else. The no-model orientation signals ride along the same
way so a conflict marker or Trojan-Source glyph shows up as a failed
"test" too.

Runner-safe: builds the XML as text with every dynamic value escaped via
:func:`html.escape`; it never *parses* XML, so the stdlib-XML bandit
rules (B405-B411) do not apply.
"""

from __future__ import annotations

import html
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from prthinker.signals import collect_signal_findings

if TYPE_CHECKING:
    from prthinker.pipeline import ReviewResult
    from prthinker.schemas import InlineFinding

_KIND_ERROR = "error"
_KIND_FAILURE = "failure"
_NO_PATH = "(repo)"


@dataclass(frozen=True)
class _Case:
    """One rendered test case: which file, its name, kind, and message."""

    path: str
    name: str
    kind: str
    message: str


def _esc(text: object) -> str:
    """Escape a value for XML text or attribute use."""
    return html.escape(str(text), quote=True)


def _first_line(text: str) -> str:
    """First non-empty line of a comment, for the test-case name."""
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return ""


def _finding_case(finding: "InlineFinding") -> _Case:
    """Map one inline finding onto a test case."""
    kind = _KIND_ERROR if finding.severity == "error" else _KIND_FAILURE
    name = f"{finding.path}:{finding.line} {_first_line(finding.comment)}"
    return _Case(finding.path, name.strip(), kind, finding.comment)


def _signal_cases(result: "ReviewResult") -> list[_Case]:
    """Map the located orientation signals onto test cases."""
    cases: list[_Case] = []
    for signal in collect_signal_findings(result.code_diff or ""):
        path = signal.path or _NO_PATH
        kind = _KIND_ERROR if signal.level == "error" else _KIND_FAILURE
        loc = f"{path}:{signal.line}" if signal.line else path
        cases.append(
            _Case(path, f"{loc} {signal.name}", kind, signal.message)
        )
    return cases


def _all_cases(result: "ReviewResult") -> list[_Case]:
    """Findings + located signals as a flat case list."""
    return [_finding_case(f) for f in result.inline_findings] + _signal_cases(
        result
    )


def _group_by_path(cases: list[_Case]) -> dict[str, list[_Case]]:
    """Bucket cases by file path, preserving first-seen path order."""
    groups: dict[str, list[_Case]] = {}
    for case in cases:
        groups.setdefault(case.path, []).append(case)
    return groups


def _render_case(case: _Case) -> str:
    """Render one ``<testcase>`` with its nested failure/error element."""
    return (
        f'<testcase name="{_esc(case.name)}" '
        f'classname="{_esc(case.path)}">'
        f'<{case.kind} message="{_esc(_first_line(case.message))}">'
        f"{_esc(case.message)}</{case.kind}>"
        "</testcase>"
    )


def _render_suite(path: str, cases: list[_Case]) -> str:
    """Render one ``<testsuite>`` for a single file."""
    failures = sum(1 for c in cases if c.kind == _KIND_FAILURE)
    errors = sum(1 for c in cases if c.kind == _KIND_ERROR)
    body = "".join(_render_case(c) for c in cases)
    return (
        f'<testsuite name="{_esc(path)}" tests="{len(cases)}" '
        f'failures="{failures}" errors="{errors}">{body}</testsuite>'
    )


def to_junit_xml(result: "ReviewResult", *, suite_name: str = "prthinker") -> str:
    """Render a :class:`ReviewResult` as a JUnit XML document string."""
    cases = _all_cases(result)
    groups = _group_by_path(cases)
    failures = sum(1 for c in cases if c.kind == _KIND_FAILURE)
    errors = sum(1 for c in cases if c.kind == _KIND_ERROR)
    suites = "".join(_render_suite(p, cs) for p, cs in groups.items())
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        f'<testsuites name="{_esc(suite_name)}" tests="{len(cases)}" '
        f'failures="{failures}" errors="{errors}">{suites}</testsuites>\n'
    )


def write_junit(result: "ReviewResult", out_path: "str | Path") -> None:
    """Serialize a :class:`ReviewResult` as JUnit XML to ``out_path``."""
    with Path(out_path).open("w", encoding="utf-8") as handle:
        handle.write(to_junit_xml(result))


__all__ = ["to_junit_xml", "write_junit"]

"""Parse a ``.prthinkerignore`` file and suppress matching inline findings.

The ignore file is a small, line-oriented format read entirely with the
standard library so it stays runner-safe (no heavy ML imports). Each line is
one of:

* ``#`` comment or a blank line — skipped.
* ``rule:<id>`` — suppress any finding whose rule / category matches ``<id>``.
* ``severity:<level>`` — suppress any finding at ``<level>`` (info / warning /
  error).
* anything else — a :func:`fnmatch.fnmatch` glob matched against the finding
  ``path``.

A missing file yields an empty :class:`IgnoreSpec`, which keeps every finding.
"""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from prthinker.schemas import InlineFinding

_COMMENT_PREFIX = "#"
_RULE_PREFIX = "rule:"
_SEVERITY_PREFIX = "severity:"


@dataclass(frozen=True)
class IgnoreSpec:
    """An immutable set of suppression patterns parsed from ``.prthinkerignore``."""

    path_globs: tuple[str, ...] = field(default_factory=tuple)
    rules: frozenset[str] = field(default_factory=frozenset)
    severities: frozenset[str] = field(default_factory=frozenset)

    @property
    def is_empty(self) -> bool:
        """Return ``True`` when the spec carries no suppression patterns."""
        return not (self.path_globs or self.rules or self.severities)


def load_ignore(path: str | Path) -> IgnoreSpec:
    """Parse the ``.prthinkerignore`` at ``path`` into an :class:`IgnoreSpec`."""
    ignore_path = Path(path)
    if not ignore_path.is_file():
        return IgnoreSpec()

    path_globs: list[str] = []
    rules: set[str] = set()
    severities: set[str] = set()

    with ignore_path.open(encoding="utf-8") as handle:
        for raw_line in handle:
            _ingest_line(raw_line, path_globs, rules, severities)

    return IgnoreSpec(
        path_globs=tuple(path_globs),
        rules=frozenset(rules),
        severities=frozenset(severities),
    )


def _ingest_line(
    raw_line: str,
    path_globs: list[str],
    rules: set[str],
    severities: set[str],
) -> None:
    """Classify one stripped line into the appropriate suppression bucket."""
    line = raw_line.strip()
    if not line or line.startswith(_COMMENT_PREFIX):
        return
    if line.startswith(_RULE_PREFIX):
        value = line[len(_RULE_PREFIX) :].strip()
        if value:
            rules.add(value.lower())
        return
    if line.startswith(_SEVERITY_PREFIX):
        value = line[len(_SEVERITY_PREFIX) :].strip()
        if value:
            severities.add(value.lower())
        return
    path_globs.append(line)


def filter_findings(
    findings: list[InlineFinding],
    spec: IgnoreSpec,
) -> list[InlineFinding]:
    """Return only the findings that ``spec`` does not suppress."""
    if spec.is_empty:
        return list(findings)
    return [finding for finding in findings if not _is_suppressed(finding, spec)]


def _is_suppressed(finding: InlineFinding, spec: IgnoreSpec) -> bool:
    """Return ``True`` when any rule in ``spec`` suppresses ``finding``."""
    return (
        _path_suppressed(finding, spec)
        or _severity_suppressed(finding, spec)
        or _rule_suppressed(finding, spec)
    )


def _path_suppressed(finding: InlineFinding, spec: IgnoreSpec) -> bool:
    """Return ``True`` when the finding path matches any glob in ``spec``."""
    path = finding.path
    return any(fnmatch.fnmatch(path, glob) for glob in spec.path_globs)


def _severity_suppressed(finding: InlineFinding, spec: IgnoreSpec) -> bool:
    """Return ``True`` when the finding severity is suppressed by ``spec``."""
    return finding.severity.lower() in spec.severities


def _rule_suppressed(finding: InlineFinding, spec: IgnoreSpec) -> bool:
    """Return ``True`` when a suppressed rule id appears in the finding.

    ``InlineFinding`` carries no structured rule / category field, so the rule
    id is matched case-insensitively against the finding comment and against
    any provenance citation note.
    """
    if not spec.rules:
        return False
    haystacks = [finding.comment.lower()]
    provenance = finding.provenance
    if provenance is not None:
        haystacks.extend(citation.note.lower() for citation in provenance.citations)
    return any(rule in text for rule in spec.rules for text in haystacks)

"""Heuristic public-API-surface and semver-impact detector for Python diffs.

Scans the added / removed lines of each :class:`~prthinker.diff.FileDiff`
for top-level ``def`` / ``class`` signatures and classifies the change as a
``major`` / ``minor`` / ``patch`` semver impact. Pure stdlib (``re`` only);
runner-safe — never imports any heavy ML dependency.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from prthinker.diff import FileDiff

_IMPACT_MAJOR = "major"
_IMPACT_MINOR = "minor"
_IMPACT_PATCH = "patch"

# Matches a top-level ``def name(...)`` / ``class Name(...)`` with no
# leading indentation (top-level only) and captures the symbol name plus
# the rest of the signature line for change detection.
_SIGNATURE_RE = re.compile(r"^(?P<kind>def|class)\s+(?P<name>[A-Za-z_]\w*)(?P<rest>.*)$")


@dataclass(frozen=True)
class ApiSurfaceReport:
    """Immutable summary of public-API changes and their semver impact."""

    added: list[str]
    removed: list[str]
    changed: list[str]
    impact: str


def _is_public(name: str) -> bool:
    """Return True when `name` is a public symbol (no leading underscore)."""
    return not name.startswith("_")


def _parse_signature(content: str) -> tuple[str, str] | None:
    """Return (name, normalized-signature) for a top-level public def/class.

    `content` is a diff body line with its leading ``+``/``-`` already
    stripped. Returns None for indented lines, private names, or
    non-signature lines.
    """
    if content[:1].isspace():
        return None
    match = _SIGNATURE_RE.match(content)
    if match is None:
        return None
    name = match.group("name")
    if not _is_public(name):
        return None
    signature = f"{match.group('kind')} {name}{match.group('rest')}".rstrip()
    return name, signature


def _collect_signatures(raw: str, prefix: str) -> dict[str, str]:
    """Map public symbol name -> signature for lines starting with `prefix`."""
    signatures: dict[str, str] = {}
    skip = "+++" if prefix == "+" else "---"
    for line in raw.splitlines():
        if not line.startswith(prefix) or line.startswith(skip):
            continue
        parsed = _parse_signature(line[1:])
        if parsed is not None:
            name, signature = parsed
            signatures[name] = signature
    return signatures


def _classify(added: list[str], removed: list[str], changed: list[str]) -> str:
    """Classify the semver impact of an aggregated API-surface delta."""
    if removed or changed:
        return _IMPACT_MAJOR
    if added:
        return _IMPACT_MINOR
    return _IMPACT_PATCH


def compute_api_surface(file_diffs: list[FileDiff]) -> ApiSurfaceReport:
    """Compute the public-API surface delta and semver impact for `file_diffs`.

    Binary and deleted files are skipped. A public symbol present only on
    the new side is an addition (minor); present only on the old side is a
    removal (major); present on both with a different signature is a change
    (major). With no public-symbol movement the impact is patch.
    """
    added: list[str] = []
    removed: list[str] = []
    changed: list[str] = []

    for file_diff in file_diffs:
        if file_diff.is_binary or file_diff.is_deleted:
            continue
        new_sigs = _collect_signatures(file_diff.raw, "+")
        old_sigs = _collect_signatures(file_diff.raw, "-")
        for name, signature in new_sigs.items():
            if name not in old_sigs:
                added.append(name)
            elif old_sigs[name] != signature:
                changed.append(name)
        for name in old_sigs:
            if name not in new_sigs:
                removed.append(name)

    impact = _classify(added, removed, changed)
    return ApiSurfaceReport(added=added, removed=removed, changed=changed, impact=impact)


__all__ = ["ApiSurfaceReport", "compute_api_surface"]

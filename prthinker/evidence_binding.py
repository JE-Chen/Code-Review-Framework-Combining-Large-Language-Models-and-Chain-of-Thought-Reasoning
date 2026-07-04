"""Bind verification evidence to stable findings and compute revision deltas."""

from __future__ import annotations
from dataclasses import dataclass
from prthinker.schemas import Evidence, InlineFinding


def _normalize_path(path: str) -> str:
    """Normalise path separators to forward slashes for comparison."""
    return path.replace("\\", "/")


def _matches_line(finding: InlineFinding, line: int | None) -> bool:
    """True when `line` is unset or matches the finding's start/exact line."""
    return line is None or finding.start_line == line or finding.line == line


def _matches_location(
    finding: InlineFinding, path: str, line: int | None
) -> bool:
    """True when the finding sits at the given path and line."""
    if not path:
        return False
    if _normalize_path(finding.path) != _normalize_path(path):
        return False
    return _matches_line(finding, line)


def _finding_matches(
    finding: InlineFinding, finding_id: str, path: str, line: int | None
) -> bool:
    """True when the finding matches by id, or by location when no id given."""
    if finding_id:
        return finding.finding_id == finding_id
    return _matches_location(finding, path, line)


def bind_evidence(
    findings: list[InlineFinding],
    evidence: Evidence,
    *,
    finding_id: str = "",
    path: str = "",
    line: int | None = None,
) -> bool:
    for finding in findings:
        if _finding_matches(finding, finding_id, path, line):
            finding.evidence.append(
                evidence.model_copy(update={"finding_id": finding.finding_id})
            )
            return True
    return False


@dataclass(frozen=True)
class FindingDelta:
    introduced: tuple[str, ...]
    resolved: tuple[str, ...]
    persisting: tuple[str, ...]


def finding_delta(base: list[InlineFinding], head: list[InlineFinding]) -> FindingDelta:
    before = {f.finding_id for f in base}
    after = {f.finding_id for f in head}
    return FindingDelta(
        tuple(sorted(after - before)),
        tuple(sorted(before - after)),
        tuple(sorted(before & after)),
    )


def gateable(findings: list[InlineFinding]) -> list[InlineFinding]:
    """Only findings with confirmed evidence are eligible for evidence gates."""
    return [f for f in findings if any(e.status == "confirmed" for e in f.evidence)]

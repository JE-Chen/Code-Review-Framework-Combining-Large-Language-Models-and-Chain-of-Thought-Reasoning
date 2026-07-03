"""Bind verification evidence to stable findings and compute revision deltas."""

from __future__ import annotations
from dataclasses import dataclass
from prthinker.schemas import Evidence, InlineFinding


def bind_evidence(
    findings: list[InlineFinding],
    evidence: Evidence,
    *,
    finding_id: str = "",
    path: str = "",
    line: int | None = None,
) -> bool:
    for finding in findings:
        matches_id = finding_id and finding.finding_id == finding_id
        matches_location = (
            not finding_id
            and path
            and finding.path.replace("\\", "/") == path.replace("\\", "/")
            and (line is None or finding.start_line == line or finding.line == line)
        )
        if matches_id or matches_location:
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

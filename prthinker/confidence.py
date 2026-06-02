"""Confidence-based abstention filter for inline findings.

Opt-in, conservative post-processing: a finding is dropped ONLY when it
carries a self-rated provenance confidence that is present AND strictly
below ``min_confidence``. Findings without a confidence are always kept,
matching the project's safe-failure posture (drop nothing real on parse
errors or low confidence). Pure stdlib; runner-safe.
"""

from __future__ import annotations

from prthinker.schemas import InlineFinding


def _finding_confidence(finding: InlineFinding) -> float | None:
    """Return the provenance confidence for a finding, or ``None`` if absent."""
    provenance = finding.provenance
    if provenance is None:
        return None
    return provenance.confidence


def filter_by_confidence(
    findings: list[InlineFinding], min_confidence: float
) -> list[InlineFinding]:
    """Drop findings whose provenance confidence is present and below the floor.

    A finding is removed only when it has an explicit provenance confidence
    that is strictly less than ``min_confidence``. Findings with no
    provenance, or provenance without a confidence value, are always kept.
    """
    kept: list[InlineFinding] = []
    for finding in findings:
        confidence = _finding_confidence(finding)
        if confidence is not None and confidence < min_confidence:
            continue
        kept.append(finding)
    return kept

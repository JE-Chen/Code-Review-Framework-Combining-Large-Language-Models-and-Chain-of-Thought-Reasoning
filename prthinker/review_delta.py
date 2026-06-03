"""Track findings across review runs to report a new-vs-resolved delta.

Line numbers shift between pushes, so a finding's identity is its
``(path, severity, normalized-comment)`` fingerprint rather than its
location. The fingerprint set from the previous run is persisted in the
per-PR state dir (which CI restores across pushes) and compared against
the current run to surface progress without re-reading the whole review.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from prthinker.schemas import InlineFinding

_DIGEST_LEN = 16


@dataclass(frozen=True)
class ReviewDelta:
    new: int
    resolved: int
    carried: int


def fingerprint(finding: InlineFinding) -> str:
    """Location-independent identity of a finding."""
    norm = " ".join(finding.comment.strip().lower().split())
    digest = hashlib.sha256(norm.encode("utf-8")).hexdigest()[:_DIGEST_LEN]
    return f"{finding.path}|{finding.severity}|{digest}"


def fingerprints(findings: list[InlineFinding]) -> list[str]:
    return sorted({fingerprint(f) for f in findings})


def compute_delta(
    previous: set[str], current_findings: list[InlineFinding]
) -> ReviewDelta:
    current = {fingerprint(f) for f in current_findings}
    return ReviewDelta(
        new=len(current - previous),
        resolved=len(previous - current),
        carried=len(current & previous),
    )


def load_fingerprints(path: Path) -> set[str] | None:
    """Previous run's fingerprints, or None when there is no prior run."""
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return set(data.get("fingerprints", []))


def save_fingerprints(path: Path, findings: list[InlineFinding]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"fingerprints": fingerprints(findings)}, indent=2),
        encoding="utf-8",
    )


def format_delta(delta: ReviewDelta) -> str:
    """Human-readable ``+2 new · 3 resolved · 5 carried`` line."""
    return (
        f"+{delta.new} new · {delta.resolved} resolved · "
        f"{delta.carried} carried"
    )


__all__ = [
    "ReviewDelta",
    "compute_delta",
    "fingerprint",
    "fingerprints",
    "format_delta",
    "load_fingerprints",
    "save_fingerprints",
]

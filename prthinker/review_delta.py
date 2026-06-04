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


def _first_line(text: str, cap: int = 120) -> str:
    head = (text or "").strip().splitlines()[0] if (text or "").strip() else ""
    return head if len(head) <= cap else head[: cap - 1] + "…"


def records(findings: list[InlineFinding]) -> list[dict]:
    """De-duplicated finding records (fingerprint + display fields)."""
    by_fp: dict[str, dict] = {}
    for f in findings:
        fp = fingerprint(f)
        by_fp.setdefault(fp, {
            "fp": fp,
            "path": f.path,
            "severity": f.severity,
            "comment": _first_line(f.comment),
        })
    return list(by_fp.values())


def resolved_records(
    previous: list[dict], current_findings: list[InlineFinding]
) -> list[dict]:
    """Previous-run records whose finding is gone this run."""
    current = {fingerprint(f) for f in current_findings}
    return [r for r in previous if r.get("fp") not in current]


def compute_delta(
    previous: set[str], current_findings: list[InlineFinding]
) -> ReviewDelta:
    current = {fingerprint(f) for f in current_findings}
    return ReviewDelta(
        new=len(current - previous),
        resolved=len(previous - current),
        carried=len(current & previous),
    )


def _load(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def load_fingerprints(path: Path) -> set[str] | None:
    """Previous run's fingerprints, or None when there is no prior run."""
    data = _load(path)
    return None if data is None else set(data.get("fingerprints", []))


def load_records(path: Path) -> list[dict]:
    """Previous run's finding records (empty when missing or pre-records)."""
    data = _load(path)
    return [] if data is None else list(data.get("records", []))


def save_fingerprints(path: Path, findings: list[InlineFinding]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {"fingerprints": fingerprints(findings), "records": records(findings)},
            indent=2,
        ),
        encoding="utf-8",
    )


def format_delta(delta: ReviewDelta) -> str:
    """Human-readable ``+2 new · 3 resolved · 5 carried`` line."""
    return (
        f"+{delta.new} new · {delta.resolved} resolved · "
        f"{delta.carried} carried"
    )


def new_records(
    previous: set[str], current_findings: list[InlineFinding]
) -> list[dict]:
    """De-duplicated records for findings absent from the previous run."""
    return [r for r in records(current_findings) if r.get("fp") not in previous]


def format_new_block(new: list[dict]) -> str:
    """Collapsed list of findings that first appeared in this run."""
    if not new:
        return ""
    lines = [
        f"<details><summary>🆕 New since last review ({len(new)})</summary>",
        "",
    ]
    for rec in new:
        path = rec.get("path", "?")
        comment = rec.get("comment", "")
        lines.append(f"- 🆕 `{path}` — {comment}")
    lines += ["", "</details>"]
    return "\n".join(lines)


def format_resolved_block(resolved: list[dict]) -> str:
    """Collapsed, struck-through list of findings resolved since last run."""
    if not resolved:
        return ""
    lines = [
        f"<details><summary>✅ Resolved since last review ({len(resolved)})"
        "</summary>",
        "",
    ]
    for rec in resolved:
        path = rec.get("path", "?")
        comment = rec.get("comment", "")
        lines.append(f"- ~~`{path}` — {comment}~~")
    lines += ["", "</details>"]
    return "\n".join(lines)


__all__ = [
    "ReviewDelta",
    "compute_delta",
    "fingerprint",
    "fingerprints",
    "format_delta",
    "format_new_block",
    "format_resolved_block",
    "load_fingerprints",
    "load_records",
    "new_records",
    "records",
    "resolved_records",
    "save_fingerprints",
]

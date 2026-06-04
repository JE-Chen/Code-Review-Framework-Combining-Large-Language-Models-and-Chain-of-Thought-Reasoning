"""Cross-file / cross-step de-duplication of inline review findings.

Collapses near-duplicate :class:`~prthinker.schemas.InlineFinding` entries that
share the same ``(path, line)`` location and a normalized-equal comment, while
preserving the overall input order. Pure, stdlib-only, runner-safe.
"""

from __future__ import annotations

import re

from prthinker.schemas import InlineFinding, Severity

_WHITESPACE_RE = re.compile(r"\s+")
_TRAILING_PUNCT_RE = re.compile(r"[\s.,;:!?]+$")

# Higher rank wins when two findings collapse into one.
_SEVERITY_RANK: dict[Severity, int] = {"info": 0, "warning": 1, "error": 2}


def _normalize_message(message: str) -> str:
    """Lowercase a comment, collapse whitespace, and strip trailing punctuation."""
    collapsed = _WHITESPACE_RE.sub(" ", message).strip().lower()
    return _TRAILING_PUNCT_RE.sub("", collapsed)


def _severity_rank(finding: InlineFinding) -> int:
    """Return the comparison rank of a finding's severity (higher is more severe)."""
    return _SEVERITY_RANK.get(finding.severity, 0)


def dedupe_findings(findings: list[InlineFinding]) -> list[InlineFinding]:
    """Collapse near-duplicate findings, keeping the most severe per location/message.

    Two findings are considered duplicates when they share the same ``path``,
    the same ``line``, and a normalized-equal ``comment``. On collapse the
    finding with the highest severity is kept; ties keep the first one seen.
    Non-duplicate findings retain their original relative order.
    """
    kept: list[InlineFinding] = []
    index_by_key: dict[tuple[str, int, str], int] = {}
    for finding in findings:
        key = (finding.path, finding.line, _normalize_message(finding.comment))
        existing_index = index_by_key.get(key)
        if existing_index is None:
            index_by_key[key] = len(kept)
            kept.append(finding)
            continue
        if _severity_rank(finding) > _severity_rank(kept[existing_index]):
            kept[existing_index] = finding
    return kept

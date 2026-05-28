"""Reviewer disagreement / reproducibility signal.

Pure-data comparison of two passes of the inline-findings step. A
finding that appears in *both* passes (same path + line + normalised
comment) gets the ``stable`` label; one that appears in only one pass
gets ``low``. Findings unique to the second pass are also surfaced
(labelled ``low``) so the reviewer doesn't silently lose them.

This is a cheap proxy for model uncertainty that doesn't depend on
provider-specific logprobs — works against any of the four backends.

Per ``paper_rule.md`` no-fabrication: this module reports raw match /
mismatch, not a calibrated probability.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from reviewmind.schemas import InlineFinding

log = logging.getLogger(__name__)


_WORD_RE = re.compile(r"\w+", re.UNICODE)


def _normalise(comment: str) -> str:
    """Lower-case, whitespace-collapsed, punctuation-stripped form of
    ``comment`` used as the equality key across passes.
    """
    tokens = _WORD_RE.findall(comment.lower())
    return " ".join(tokens)


@dataclass(frozen=True)
class _FindingKey:
    path: str
    line: int
    norm_comment: str


def _key(f: InlineFinding) -> _FindingKey:
    return _FindingKey(
        path=f.path, line=f.line, norm_comment=_normalise(f.comment),
    )


def label_findings(
    first_pass: list[InlineFinding],
    second_pass: list[InlineFinding],
) -> list[InlineFinding]:
    """Return ``first_pass ∪ second_pass`` annotated with
    ``reproducibility`` set to ``"stable"`` for findings that match
    across both passes, ``"low"`` for ones unique to one pass.

    Match is by ``(path, line, normalised-comment)``. Comments that
    differ by phrasing (whitespace / punctuation / case) still match;
    comments with different content do not.
    """
    second_keys = {_key(f) for f in second_pass}
    out: list[InlineFinding] = []
    seen: set[_FindingKey] = set()

    for f in first_pass:
        k = _key(f)
        if k in second_keys:
            out.append(f.model_copy(update={"reproducibility": "stable"}))
        else:
            out.append(f.model_copy(update={"reproducibility": "low"}))
        seen.add(k)

    for f in second_pass:
        k = _key(f)
        if k in seen:
            continue
        # Unique to the second pass — surface it but mark low-repro.
        out.append(f.model_copy(update={"reproducibility": "low"}))
        seen.add(k)

    return out


__all__ = ["label_findings"]

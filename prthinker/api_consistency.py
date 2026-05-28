"""Cross-language API drift detection.

When a PR touches both backend (``.py``) and frontend (``.ts`` / ``.tsx``
/ ``.js``) files, the model usually reviews each file in isolation and
misses the case where the backend renames a field but the frontend
still uses the old name. This module detects mixed-language diffs and
prepares a whole-diff prompt that asks the model specifically for
*cross-language* consistency issues, then parses the JSON response.

Design:

* :func:`is_mixed_language` — quick scan over file paths.
* :func:`build_prompt` — render the cross-language-review prompt. The
  per-language file contents are listed in two sections so the model
  doesn't get confused which side it's looking at.
* :func:`parse_drift_findings` — safe-failure JSON parser. Malformed
  entries are dropped; never crashes the pipeline.

Per ``paper_rule.md`` no-fabrication: this module makes no claim about
detection precision / recall. The mechanism is what's shipped.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import PurePosixPath

from pydantic import ValidationError

from prthinker.diff import FileDiff
from prthinker.schemas import ApiDriftFinding

log = logging.getLogger(__name__)


_PY_EXT = {".py"}
_JS_EXT = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}

_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)
_ARRAY_RE = re.compile(r"\[[\s\S]*\]")


def _ext(path: str) -> str:
    return PurePosixPath(path).suffix.lower()


def classify_side(path: str) -> str | None:
    """Return ``"backend"`` / ``"frontend"`` / ``None`` for one path."""
    e = _ext(path)
    if e in _PY_EXT:
        return "backend"
    if e in _JS_EXT:
        return "frontend"
    return None


def is_mixed_language(file_diffs: list[FileDiff]) -> bool:
    """True when the diff touches at least one backend AND one frontend
    file. Pure-data — no I/O.
    """
    seen_backend = False
    seen_frontend = False
    for fd in file_diffs:
        if fd.is_binary or fd.is_deleted:
            continue
        side = classify_side(fd.path)
        if side == "backend":
            seen_backend = True
        elif side == "frontend":
            seen_frontend = True
        if seen_backend and seen_frontend:
            return True
    return False


PROMPT_TEMPLATE = """\
# Cross-Language API Consistency Check

This PR touches both backend (Python) and frontend (TypeScript /
JavaScript) files. Backend changes can rename, drop, or restructure
request / response fields while the frontend still uses the old shape;
the reverse also happens. Your job is to look at the diffs side by
side and report ONLY *cross-file* drift — places where one side's
contract has changed but the other side has not been updated.

You MUST output ONLY a JSON array, no surrounding prose, no markdown
fences. Each element must conform to:

  {{
    "backend_path":  "<file path on the backend side>",
    "frontend_path": "<file path on the frontend side>",
    "kind": "field_renamed" | "field_removed" | "type_changed"
          | "path_changed" | "method_changed" | "other",
    "summary":   "<one sentence: what the backend now expects>",
    "evidence":  "<short quote from each side that proves the drift>"
  }}

Rules:

- Only report drift that is visible *across* the two sides. A finding
  that only inspects backend OR only inspects frontend belongs in the
  per-file review, not here.
- If there is no cross-file drift, output exactly ``[]``.
- Do not invent fields or paths. Each ``backend_path`` / ``frontend_path``
  must come from the diff below.

## Backend (Python) files
{backend_block}

## Frontend (TypeScript / JavaScript) files
{frontend_block}
"""


def build_prompt(file_diffs: list[FileDiff]) -> str:
    """Render the cross-language-review prompt for the model.

    Returns ``""`` when the diff isn't mixed-language so the caller can
    avoid wasting a backend call.
    """
    if not is_mixed_language(file_diffs):
        return ""

    backend_parts: list[str] = []
    frontend_parts: list[str] = []
    for fd in file_diffs:
        if fd.is_binary or fd.is_deleted:
            continue
        side = classify_side(fd.path)
        section = (
            f"### `{fd.path}`\n\n```diff\n{fd.raw.rstrip()}\n```\n"
        )
        if side == "backend":
            backend_parts.append(section)
        elif side == "frontend":
            frontend_parts.append(section)

    return PROMPT_TEMPLATE.format(
        backend_block="\n".join(backend_parts) or "(none)",
        frontend_block="\n".join(frontend_parts) or "(none)",
    )


def parse_drift_findings(
    raw_output: str, *, allowed_paths: set[str],
) -> list[ApiDriftFinding]:
    """Best-effort parse of the model's JSON-array reply.

    Each entry's ``backend_path`` and ``frontend_path`` must be in
    ``allowed_paths`` (the set of paths that actually appear in the
    diff). Out-of-set paths are silently dropped — same safe-failure
    posture as :mod:`prthinker.findings`.
    """
    body = raw_output.strip()
    fence = _FENCE_RE.search(body)
    if fence:
        body = fence.group(1).strip()
    if not body or body == "[]":
        return []

    match = _ARRAY_RE.search(body)
    if match is None:
        log.warning("api_consistency parser: no JSON array found")
        return []

    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        log.warning("api_consistency parser: JSON decode failed (%s)", exc)
        return []
    if not isinstance(data, list):
        return []

    out: list[ApiDriftFinding] = []
    for entry in data:
        if not isinstance(entry, dict):
            continue
        try:
            df = ApiDriftFinding.model_validate(entry)
        except ValidationError as exc:
            log.debug("Dropped malformed drift finding %r: %s", entry, exc)
            continue
        if df.backend_path not in allowed_paths:
            log.debug("Drift finding cites unknown backend path %s", df.backend_path)
            continue
        if df.frontend_path not in allowed_paths:
            log.debug("Drift finding cites unknown frontend path %s", df.frontend_path)
            continue
        out.append(df)
    return out


__all__ = [
    "classify_side",
    "is_mixed_language",
    "build_prompt",
    "parse_drift_findings",
    "PROMPT_TEMPLATE",
]

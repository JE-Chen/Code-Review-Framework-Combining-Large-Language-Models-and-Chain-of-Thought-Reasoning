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

import logging
from pathlib import PurePosixPath

from pydantic import ValidationError

from prthinker.diff import FileDiff
from prthinker.lenient_json import extract_json_array
from prthinker.schemas import ApiDriftFinding

log = logging.getLogger(__name__)


_PY_EXT = {".py"}
_JS_EXT = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}

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


def _split_diffs_by_side(
    file_diffs: list[FileDiff],
) -> tuple[list[str], list[str]]:
    """Render each touched file as a prompt section and return
    ``(backend_sections, frontend_sections)``.
    """
    backend_parts: list[str] = []
    frontend_parts: list[str] = []
    for fd in file_diffs:
        if fd.is_binary or fd.is_deleted:
            continue
        side = classify_side(fd.path)
        if side is None:
            continue
        section = f"### `{fd.path}`\n\n```diff\n{fd.raw.rstrip()}\n```\n"
        if side == "backend":
            backend_parts.append(section)
        else:  # side == "frontend"
            frontend_parts.append(section)
    return backend_parts, frontend_parts


def build_prompt(file_diffs: list[FileDiff]) -> str:
    """Render the cross-language-review prompt for the model.

    Returns ``""`` when the diff isn't mixed-language so the caller can
    avoid wasting a backend call.
    """
    if not is_mixed_language(file_diffs):
        return ""
    backend_parts, frontend_parts = _split_diffs_by_side(file_diffs)
    return PROMPT_TEMPLATE.format(
        backend_block="\n".join(backend_parts) or "(none)",
        frontend_block="\n".join(frontend_parts) or "(none)",
    )


def _coerce_drift_entry(
    entry, allowed_paths: set[str],
) -> ApiDriftFinding | None:
    """Validate one raw entry; ``None`` if it must be dropped."""
    if not isinstance(entry, dict):
        return None
    try:
        df = ApiDriftFinding.model_validate(entry)
    except ValidationError as exc:
        log.debug("Dropped malformed drift finding %r: %s", entry, exc)
        return None
    if df.backend_path not in allowed_paths:
        log.debug("Drift cites unknown backend path %s", df.backend_path)
        return None
    if df.frontend_path not in allowed_paths:
        log.debug("Drift cites unknown frontend path %s", df.frontend_path)
        return None
    return df


def parse_drift_findings(
    raw_output: str, *, allowed_paths: set[str],
) -> list[ApiDriftFinding]:
    """Best-effort parse of the model's JSON-array reply.

    Each entry's ``backend_path`` and ``frontend_path`` must be in
    ``allowed_paths`` (the set of paths that actually appear in the
    diff). Out-of-set paths are silently dropped — same safe-failure
    posture as :mod:`prthinker.findings`.
    """
    data = extract_json_array(raw_output, parser_name="api_consistency parser")
    if not data:
        return []
    out: list[ApiDriftFinding] = []
    for entry in data:
        df = _coerce_drift_entry(entry, allowed_paths)
        if df is not None:
            out.append(df)
    return out


__all__ = [
    "classify_side",
    "is_mixed_language",
    "build_prompt",
    "parse_drift_findings",
    "PROMPT_TEMPLATE",
]

"""Multi-persona review with conflict surfacing.

Most LLM reviewers run *one* review pass. This module lets the pipeline
run N orthogonal personas (security, performance, readability,
API-stability, maintainability) in parallel over the same diff, then a
post-step asks the model where the N reviews disagree — surfacing the
*tensions* the human reviewer needs to resolve rather than averaging
them away.

Design constraints:

* Each persona has its own prompt fragment that frames the review
  through that single lens; the model is told NOT to comment on
  concerns outside that lens.
* The conflict step takes the N persona outputs and is asked to find
  cross-persona disagreements *only* — it is never used to add new
  findings, only to surface tensions between existing ones.
* Per ``paper_rule.md`` no-fabrication: no claim is made about whether
  multi-persona review is empirically better. The contribution is the
  conflict-visibility mechanism.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from enum import Enum

from pydantic import ValidationError

from prthinker.schemas import PersonaConflict

log = logging.getLogger(__name__)


class Persona(str, Enum):
    """Five orthogonal review angles."""

    SECURITY = "security"
    PERFORMANCE = "performance"
    READABILITY = "readability"
    API_STABILITY = "api_stability"
    MAINTAINABILITY = "maintainability"


_PERSONA_PROMPTS: dict[Persona, str] = {
    Persona.SECURITY: (
        "You are reviewing this diff EXCLUSIVELY for security concerns. "
        "Focus on: injection (SQL, command, log, prompt), authentication "
        "and authorization gaps, secret handling, deserialisation risk, "
        "TLS / cert checks, input validation, time-of-check / "
        "time-of-use, path traversal. Do NOT comment on performance, "
        "readability, style, or unrelated concerns."
    ),
    Persona.PERFORMANCE: (
        "You are reviewing this diff EXCLUSIVELY for performance "
        "concerns. Focus on: algorithmic complexity, unnecessary "
        "allocation, hot-path I/O, N+1 queries, blocking calls inside "
        "loops, memory growth, cache misses. Do NOT comment on style, "
        "naming, or security unless it is a direct cause of a "
        "performance regression."
    ),
    Persona.READABILITY: (
        "You are reviewing this diff EXCLUSIVELY for readability. Focus "
        "on: naming, function size, comment quality, nesting depth, "
        "variable lifetimes, dead code, magic numbers. Do NOT comment "
        "on performance, security, or behaviour."
    ),
    Persona.API_STABILITY: (
        "You are reviewing this diff EXCLUSIVELY for public-API "
        "stability. Focus on: renamed / removed exports, signature "
        "changes, behaviour changes on existing entry points, missing "
        "deprecation paths, missing version bumps. Do NOT comment on "
        "internal implementation details that don't escape the module."
    ),
    Persona.MAINTAINABILITY: (
        "You are reviewing this diff EXCLUSIVELY for maintainability. "
        "Focus on: test coverage of new code paths, error-message "
        "quality, logging adequacy, configuration discoverability, "
        "duplication with existing utilities, fragile coupling. Do NOT "
        "re-raise concerns the readability or performance personas "
        "would raise."
    ),
}


@dataclass(frozen=True)
class PersonaPromptParts:
    """Wraps the lens prompt + the diff for one persona run."""

    persona: Persona
    prompt: str


def build_persona_prompt(persona: Persona, *, diff_text: str) -> PersonaPromptParts:
    """Render a per-persona review prompt for ``diff_text``."""
    lens = _PERSONA_PROMPTS[persona]
    body = (
        f"# {persona.value.title()} review\n\n{lens}\n\n"
        "Reply with a short bullet list of findings, one per line. If "
        "this diff has nothing to say from your lens, reply with the "
        "single line ``(no concerns from this lens)``.\n\n"
        f"## Diff\n\n```diff\n{diff_text.rstrip()}\n```\n"
    )
    return PersonaPromptParts(persona=persona, prompt=body)


CONFLICT_PROMPT_TEMPLATE = """\
# Persona Conflict Surfacing

You are given the outputs of {n} orthogonal reviewers, each one
focused on a single lens. Your job is to surface places where the
reviewers *disagree* — for example, security says X but performance
says ¬X, or readability says inline but API-stability says extract.

You MUST output ONLY a JSON array, no surrounding prose, no markdown
fences. Each element conforms to:

  {{
    "personas":   ["<persona_a>", "<persona_b>", ...],
    "summary":    "<one sentence: the tension>",
    "resolution": "<one sentence: what a human reviewer should
                    consider when adjudicating; do NOT pick a winner>"
  }}

Rules:

- Only surface tensions between *different* personas. Cases where one
  persona says something and the others are silent are not conflicts.
- If there are no genuine conflicts, output exactly ``[]``.
- Do not invent persona names. ``personas`` must be drawn from the
  list ``{persona_names}``.

## Per-persona outputs

{persona_block}
"""


def build_conflict_prompt(
    persona_outputs: dict[Persona, str],
) -> str:
    """Render the conflict-surfacing prompt over N persona outputs."""
    names = [p.value for p in persona_outputs]
    body_parts: list[str] = []
    for p, out in persona_outputs.items():
        body_parts.append(
            f"### `{p.value}` reviewer\n\n{out.strip() or '(empty)'}\n"
        )
    return CONFLICT_PROMPT_TEMPLATE.format(
        n=len(persona_outputs),
        persona_names=", ".join(f"``{n}``" for n in names),
        persona_block="\n".join(body_parts),
    )


_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)
_ARRAY_RE = re.compile(r"\[[\s\S]*\]")


def _extract_json_array(raw_output: str) -> list | None:
    """Pull the JSON array out of a model reply; ``None`` on parse failure."""
    body = raw_output.strip()
    fence = _FENCE_RE.search(body)
    if fence:
        body = fence.group(1).strip()
    if not body or body == "[]":
        return []
    match = _ARRAY_RE.search(body)
    if match is None:
        log.warning("personas parser: no JSON array found")
        return None
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        log.warning("personas parser: JSON decode failed (%s)", exc)
        return None
    return data if isinstance(data, list) else None


def _coerce_conflict_entry(entry, valid_names: set[str]) -> PersonaConflict | None:
    """Validate one raw entry and return a :class:`PersonaConflict` or
    ``None`` if it must be dropped. Single-persona entries and entries
    citing unknown personas are filtered here so the caller stays flat.
    """
    if not isinstance(entry, dict):
        return None
    names = entry.get("personas")
    if not isinstance(names, list) or len(names) < 2:
        return None
    filtered = [n for n in names if isinstance(n, str) and n in valid_names]
    if len(filtered) < 2:
        return None
    payload = dict(entry)
    payload["personas"] = filtered
    try:
        return PersonaConflict.model_validate(payload)
    except ValidationError as exc:
        log.debug("Dropped malformed conflict %r: %s", entry, exc)
        return None


def parse_conflicts(
    raw_output: str,
    *,
    valid_personas: set[Persona],
) -> list[PersonaConflict]:
    """Best-effort parse of the conflict-finder reply.

    Out-of-set persona names and entries citing only one persona are
    dropped — same safe-failure posture as the rest of the parsers.
    """
    data = _extract_json_array(raw_output)
    if not data:
        return []
    valid_names = {p.value for p in valid_personas}
    out: list[PersonaConflict] = []
    for entry in data:
        conflict = _coerce_conflict_entry(entry, valid_names)
        if conflict is not None:
            out.append(conflict)
    return out


__all__ = [
    "CONFLICT_PROMPT_TEMPLATE",
    "Persona",
    "PersonaPromptParts",
    "build_conflict_prompt",
    "build_persona_prompt",
    "parse_conflicts",
]

"""Localized findings: prompt builder + defensive parser for translation.

Mirrors :mod:`prthinker.commit_review` in spirit. This module is *pure*: it
builds the prompt that asks the model to translate a list of review comments
into a target language (preserving order) and parses the model's JSON reply
into a list of translated strings. No backend call happens here.

The parser is best-effort — code fences are stripped, the outermost JSON
array is extracted, and any length mismatch or parse failure yields an empty
list so the caller can keep the original (untranslated) comments unchanged.

Per ``paper_rule.md``'s no-fabrication HARD rule, this module emits no
metrics and makes no quality claims; whether localization helps reviewers is
future work and is not measured here.
"""

from __future__ import annotations

import json
import logging
import re

log = logging.getLogger(__name__)

_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)
_ARRAY_RE = re.compile(r"\[[\s\S]*\]")

PROMPT_TEMPLATE = """\
# Localize Review Comments

You are translating {count} code-review comment(s) into {target_language}.

Rules:

- Translate each comment into {target_language}, preserving its technical
  meaning. Keep code identifiers, file paths, and inline ``code`` spans
  unchanged.
- Preserve the original order exactly: the N-th element of your output is the
  translation of the N-th comment below.
- Output ONLY a JSON array of strings, no surrounding prose, no markdown
  fences. The array MUST have exactly {count} element(s).

## Comments

{comment_block}
"""


def _format_comment_block(comments: list[str]) -> str:
    """Render the numbered, zero-based list of comments to translate."""
    lines = [
        f"### Comment {index}\n\n```\n{comment.strip()}\n```\n"
        for index, comment in enumerate(comments)
    ]
    return "\n".join(lines)


def build_localization_prompt(comments: list[str], target_language: str) -> str:
    """Build the prompt asking the model to translate each review comment."""
    return PROMPT_TEMPLATE.format(
        count=len(comments),
        target_language=target_language,
        comment_block=_format_comment_block(comments),
    )


def _extract_json_array(raw: str) -> list | None:
    """Pull the JSON array out of a model reply; ``None`` on parse failure."""
    body = raw.strip()
    fence = _FENCE_RE.search(body)
    if fence:
        body = fence.group(1).strip()
    if not body or body == "[]":
        return []
    match = _ARRAY_RE.search(body)
    if match is None:
        log.warning("localize parser: no JSON array found")
        return None
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        log.warning("localize parser: JSON decode failed (%s)", exc)
        return None
    return data if isinstance(data, list) else None


def parse_localized(raw: str, *, expected: int) -> list[str]:
    """Best-effort parse of the localization reply into translated strings.

    Tolerates fenced JSON. Returns ``[]`` on parse failure, on a non-string
    element, or on any length mismatch against ``expected`` so the caller
    keeps the original comments unchanged.
    """
    data = _extract_json_array(raw)
    if data is None:
        return []
    if len(data) != expected:
        log.warning(
            "localize parser: expected %d items, got %d", expected, len(data),
        )
        return []
    if not all(isinstance(item, str) for item in data):
        log.warning("localize parser: non-string element in array")
        return []
    return data


__all__ = [
    "PROMPT_TEMPLATE",
    "build_localization_prompt",
    "parse_localized",
]

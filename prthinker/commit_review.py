"""Commit-message quality review: prompt builder + defensive parser.

Mirrors :mod:`prthinker.counterfactual` and :mod:`prthinker.personas` in
spirit. This module is *pure*: it builds the prompt that asks the model to
assess each commit message (conventional-commits format, imperative mood,
clarity, subject length) and parses the model's JSON reply into a list of
:class:`CommitMessageNote`. No backend call happens here.

The parser is best-effort — code fences are stripped, the outermost JSON
array is extracted, and malformed entries are silently dropped so a bad
model reply never crashes the run.

Per ``paper_rule.md``'s no-fabrication HARD rule, this module emits no
metrics and makes no quality claims; whether the notes help reviewers is
future work and is not measured here.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass

log = logging.getLogger(__name__)

_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)
_ARRAY_RE = re.compile(r"\[[\s\S]*\]")

_KEY_MESSAGE_INDEX = "message_index"
_KEY_ISSUE = "issue"
_KEY_SUGGESTION = "suggestion"

PROMPT_TEMPLATE = """\
# Commit-Message Quality Review

You are reviewing the quality of {count} commit message(s). Assess each
message against these criteria:

- Conventional-commits format: ``<type>: <short description>`` where type
  is one of feat, fix, refactor, docs, test, chore, perf, security.
- Imperative mood in the subject ("add X", not "added X" / "adds X").
- Clarity: the subject describes what changed and is not vague.
- Subject length: the subject line should be 72 characters or fewer.

You MUST output ONLY a JSON array, no surrounding prose, no markdown
fences. Each element conforms to:

  {{
    "message_index": <int: zero-based index of the message below>,
    "issue":         "<one sentence: the problem with this message>",
    "suggestion":    "<one sentence: a concrete rewrite or fix>"
  }}

Rules:

- Only include messages that have a genuine issue. A message that meets
  all criteria gets no entry.
- ``message_index`` must refer to a message in the numbered list below.
- If every message is fine, output exactly ``[]``.

## Commit messages

{message_block}
"""


@dataclass(frozen=True)
class CommitMessageNote:
    """A single quality note about one commit message."""

    message_index: int
    issue: str
    suggestion: str


def _format_message_block(commit_messages: list[str]) -> str:
    """Render the numbered, zero-based list of commit messages."""
    lines = [
        f"### Message {index}\n\n```\n{message.strip()}\n```\n"
        for index, message in enumerate(commit_messages)
    ]
    return "\n".join(lines)


def build_prompt(commit_messages: list[str]) -> str:
    """Build the commit-message quality-review prompt."""
    return PROMPT_TEMPLATE.format(
        count=len(commit_messages),
        message_block=_format_message_block(commit_messages),
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
        log.warning("commit_review parser: no JSON array found")
        return None
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        log.warning("commit_review parser: JSON decode failed (%s)", exc)
        return None
    return data if isinstance(data, list) else None


def _note_from_entry(entry: object) -> CommitMessageNote | None:
    """Validate one raw entry into a note; ``None`` if malformed."""
    if not isinstance(entry, dict):
        return None
    index = entry.get(_KEY_MESSAGE_INDEX)
    issue = entry.get(_KEY_ISSUE)
    suggestion = entry.get(_KEY_SUGGESTION)
    if not isinstance(index, int) or isinstance(index, bool):
        log.debug("Dropped commit note with non-int message_index: %r", entry)
        return None
    if not isinstance(issue, str) or not isinstance(suggestion, str):
        log.debug("Dropped commit note with non-string fields: %r", entry)
        return None
    return CommitMessageNote(
        message_index=index, issue=issue, suggestion=suggestion,
    )


def parse_review(raw: str) -> list[CommitMessageNote]:
    """Best-effort parse of the commit-message review reply.

    Tolerates fenced JSON; returns ``[]`` for empty / no-JSON input and
    skips malformed entries rather than crashing the pipeline.
    """
    data = _extract_json_array(raw)
    if not data:
        return []
    notes: list[CommitMessageNote] = []
    for entry in data:
        note = _note_from_entry(entry)
        if note is not None:
            notes.append(note)
    return notes


__all__ = [
    "PROMPT_TEMPLATE",
    "CommitMessageNote",
    "build_prompt",
    "parse_review",
]

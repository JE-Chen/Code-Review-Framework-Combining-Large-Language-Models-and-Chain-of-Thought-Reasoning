"""Fence- and prose-tolerant JSON extraction shared by every model parser.

Models wrap the payload in code fences, precede it with chain-of-thought
prose, or trail off after it. The greedy ``\\[[\\s\\S]*\\]`` regex this
module replaces mis-parses all three: it spans from the first bracket to
the last across unrelated text, is fooled by a ``` ```python ``` code
fence, and raises ``Extra data`` on trailing prose — after which a
fail-open caller wrongly keeps the payload it meant to reject.

Instead we scan for bracket-balanced spans, tracking JSON-string state so
a bracket or quote *inside* a string never skews the nesting depth, and
return the **last** span that decodes to the requested container — the
model's final answer even behind reasoning, fences, or trailing text.

Runner-safe: standard library only.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Iterator

log = logging.getLogger(__name__)


def _advance_string(char: str, escape: bool) -> tuple[bool, bool]:
    """Fold one char of a JSON string literal → ``(still_in_string, escape)``."""
    if escape:
        return True, False
    if char == "\\":
        return True, True
    return char != '"', False


def _iter_balanced(text: str, open_char: str, close_char: str) -> Iterator[str]:
    """Yield each top-level balanced ``open_char..close_char`` span, in order.

    Only a depth-0 opener starts a span and its matching closer yields the
    whole substring; brackets or quotes inside a JSON string are ignored.
    """
    depth = 0
    start = -1
    in_string = escape = False
    for index, char in enumerate(text):
        if in_string:
            in_string, escape = _advance_string(char, escape)
            continue
        if char == '"':
            in_string = True
        elif char == open_char:
            if depth == 0:
                start = index
            depth += 1
        elif char == close_char and depth > 0:
            depth -= 1
            if depth == 0:
                yield text[start : index + 1]


def iter_json_arrays(text: str) -> Iterator[str]:
    """Yield each bracket-balanced ``[...]`` span in ``text``, in order."""
    return _iter_balanced(text, "[", "]")


def iter_json_objects(text: str) -> Iterator[str]:
    """Yield each brace-balanced ``{...}`` span in ``text``, in order."""
    return _iter_balanced(text, "{", "}")


def _last_valid(spans: Iterator[str], expected: type) -> object | None:
    """Parsed value of the LAST span that JSON-decodes to ``expected``."""
    result: object | None = None
    for span in spans:
        try:
            data = json.loads(span)
        except json.JSONDecodeError:
            continue
        if isinstance(data, expected):
            result = data
    return result


def extract_json_array(raw: str, *, parser_name: str = "parser") -> list | None:
    """Extract a JSON array from a model reply; ``None`` on failure.

    Returns ``[]`` for an empty / whitespace-only reply (an empty answer is
    "no items", not a parse failure). Otherwise returns the last balanced
    ``[...]`` span that decodes to a list.
    """
    if not raw.strip():
        return []
    data = _last_valid(iter_json_arrays(raw), list)
    if data is None:
        log.warning("%s: no JSON array found", parser_name)
        return None
    return data


def extract_json_object(raw: str, *, parser_name: str = "parser") -> dict | None:
    """Extract a JSON object from a model reply; ``None`` on failure."""
    data = _last_valid(iter_json_objects(raw), dict)
    if data is None:
        log.warning("%s: no JSON object found", parser_name)
        return None
    return data


__all__ = [
    "extract_json_array",
    "extract_json_object",
    "iter_json_arrays",
    "iter_json_objects",
]

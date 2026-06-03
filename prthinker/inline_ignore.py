"""Suppress findings on changed lines carrying an inline ignore directive.

A reviewer can annotate a changed line with ``# prthinker: ignore`` (any
comment syntax — only the token is matched) to drop findings on that
new-side line. This complements the file-level ``.prthinkerignore`` by
letting authors suppress at the exact source line.
"""

from __future__ import annotations

import re

from prthinker.schemas import InlineFinding

_DIRECTIVE = re.compile(r"prthinker:\s*ignore\b", re.IGNORECASE)
_HUNK = re.compile(r"@@ .*?\+(\d+)")


def _new_side_path(raw: str) -> str | None:
    """Return the new-side path from a ``+++`` header (None for /dev/null)."""
    path = raw[4:].split("\t", 1)[0].strip()
    if path == "/dev/null":
        return None
    return path[2:] if path.startswith("b/") else path


def ignored_lines(diff_text: str) -> dict[str, set[int]]:
    """Map each file to the new-side line numbers bearing the directive."""
    result: dict[str, set[int]] = {}
    path: str | None = None
    new_line = 0
    in_hunk = False
    for raw in diff_text.splitlines():
        if raw.startswith("+++ "):
            path, in_hunk = _new_side_path(raw), False
            continue
        hunk = _HUNK.match(raw)
        if hunk:
            new_line, in_hunk = int(hunk.group(1)) - 1, True
            continue
        if not in_hunk or path is None or raw[:1] not in ("+", " "):
            continue
        new_line += 1
        if _DIRECTIVE.search(raw):
            result.setdefault(path, set()).add(new_line)
    return result


def filter_inline_ignored(
    findings: list[InlineFinding], diff_text: str
) -> list[InlineFinding]:
    """Drop findings whose line carries an inline ignore directive."""
    if not diff_text:
        return findings
    ignored = ignored_lines(diff_text)
    return [f for f in findings if f.line not in ignored.get(f.path, set())]


__all__ = ["filter_inline_ignored", "ignored_lines"]

"""Unified-diff parser — splits a PR diff into per-file chunks.

Only the pieces we need:

* file path (new side; old side for deletions)
* raw diff text for the file (passed to the model verbatim)
* set of new-side line numbers that appear in the diff, so we can validate
  inline comment targets against what GitHub will accept.

We intentionally don't pull in ``unidiff`` — keeps runner deps thin and
the input format is simple enough.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field

_HUNK_RE = re.compile(
    r"^@@\s+-(?P<old_start>\d+)(?:,(?P<old_count>\d+))?\s+"
    r"\+(?P<new_start>\d+)(?:,(?P<new_count>\d+))?\s+@@"
)


@dataclass
class FileDiff:
    path: str
    raw: str
    new_lines: set[int] = field(default_factory=set)
    is_binary: bool = False
    is_deleted: bool = False

    def commentable_lines(self) -> set[int]:
        """Lines on the new side that GitHub will accept for inline review."""
        return set(self.new_lines)

    def content_sha256(self) -> str:
        """Stable hash of the post-change content of this file's diff.

        Used by the differential-review cache to decide whether the
        model needs to re-review this file on a force-push. We hash
        only the lines that survive on the *new* side (added or
        unchanged-context) — formatting whitespace, removed lines and
        diff metadata are excluded so a no-op force-push that only
        re-orders hunks still hits the cache.
        """
        h = hashlib.sha256()
        new_side: list[str] = []
        for line in self.raw.splitlines():
            if line.startswith("+") and not line.startswith("+++"):
                new_side.append(line[1:])
            elif line.startswith(" "):
                new_side.append(line[1:])
        h.update("\n".join(new_side).encode("utf-8"))
        return h.hexdigest()


def _starts_file(line: str) -> bool:
    return line.startswith("diff --git ")


def _git_header_b_path(line: str) -> str | None:
    """Pull the b-side path from a ``diff --git a/path b/path`` header."""
    parts = line.split(" ", 4)
    if len(parts) >= 4 and parts[3].startswith("b/"):
        return parts[3][2:].rstrip()
    return None


def _plus_path(line: str) -> str | None:
    """Resolve the new-file path from a ``+++`` header (None for /dev/null)."""
    target = line[4:].strip()
    if target == "/dev/null":
        return None
    return target[2:] if target.startswith("b/") else target


def _minus_a_path(line: str) -> str | None:
    """Resolve the new-file path from a ``--- a/path`` header, else None."""
    if "/dev/null" in line:
        return None
    target = line[4:].strip()
    return target[2:] if target.startswith("a/") else None


@dataclass
class _HeaderState:
    """Accumulator for path/flag extraction across per-file header lines."""

    new_path: str | None = None
    fallback: str | None = None
    is_binary: bool = False
    is_deleted: bool = False


def _apply_path_line(line: str, state: _HeaderState) -> None:
    """Fold a path-bearing header line (``diff``/``+++``/``---``) into `state`."""
    if line.startswith("diff --git "):
        state.fallback = _git_header_b_path(line) or state.fallback
    elif line.startswith("+++ "):
        state.new_path = _plus_path(line) or state.new_path
    elif line.startswith("--- ") and state.new_path is None:
        state.new_path = _minus_a_path(line)


def _apply_header_line(line: str, state: _HeaderState) -> None:
    """Fold one header line into `state` (prefix dispatch, in place)."""
    if line.startswith("deleted file mode"):
        state.is_deleted = True
    elif line.startswith("Binary files "):
        state.is_binary = True
    else:
        _apply_path_line(line, state)


def _extract_paths(diff_header_lines: list[str]) -> tuple[str | None, bool, bool]:
    """Return (new_path, is_binary, is_deleted) from the per-file header."""
    state = _HeaderState()
    for line in diff_header_lines:
        _apply_header_line(line, state)
    return (state.new_path or state.fallback), state.is_binary, state.is_deleted


def _advance_new_side(line: str, new_line_no: int, collected: set[int]) -> int:
    """Advance the new-side line counter for context and added lines."""
    if line.startswith(" ") or (line.startswith("+") and not line.startswith("+++")):
        new_line_no += 1
        collected.add(new_line_no)
    return new_line_no


def parse_unified_diff(diff_text: str) -> list[FileDiff]:
    """Split `diff_text` into one `FileDiff` per file.

    The raw text per file preserves the original `diff --git`/`@@` headers
    so the model still sees full context.
    """
    if not diff_text.strip():
        return []

    lines = diff_text.splitlines(keepends=True)
    files: list[FileDiff] = []

    current_buf: list[str] = []
    header_buf: list[str] = []
    in_hunks = False
    new_line_no = 0
    collected_new_lines: set[int] = set()

    def flush() -> None:
        if not current_buf:
            return
        new_path, is_binary, is_deleted = _extract_paths(header_buf)
        if new_path is None:
            return
        files.append(
            FileDiff(
                path=new_path,
                raw="".join(current_buf),
                new_lines=set(collected_new_lines),
                is_binary=is_binary,
                is_deleted=is_deleted,
            )
        )

    for line in lines:
        if _starts_file(line):
            flush()
            current_buf = [line]
            header_buf = [line]
            in_hunks = False
            new_line_no = 0
            collected_new_lines = set()
            continue

        if not current_buf:
            # Skip preamble before the first `diff --git`
            continue

        current_buf.append(line)

        if line.startswith("@@"):
            in_hunks = True
            header_buf.append(line)
            m = _HUNK_RE.match(line)
            if m:
                new_line_no = int(m.group("new_start")) - 1
            continue

        if not in_hunks:
            header_buf.append(line)
            continue

        # Track new-side line numbers for inline-comment validation.
        # '-' lines and metadata don't advance the new-side counter.
        new_line_no = _advance_new_side(line, new_line_no, collected_new_lines)

    flush()
    return files


def _content_from_raw(raw: str) -> dict[int, str]:
    """Map new-side line numbers to their content within one file's diff."""
    content: dict[int, str] = {}
    new_line = 0
    in_hunk = False
    for line in raw.splitlines():
        if line.startswith("@@"):
            match = _HUNK_RE.match(line)
            in_hunk = match is not None
            if match:
                new_line = int(match.group("new_start")) - 1
            continue
        if not in_hunk:
            continue
        if line.startswith("+") and not line.startswith("+++"):
            new_line += 1
            content[new_line] = line[1:]
        elif line.startswith(" "):
            new_line += 1
            content[new_line] = line[1:]
        # '-' lines are old-side deletions and do not advance the new side.
    return content


def new_side_content(diff_text: str) -> dict[str, dict[int, str]]:
    """Map ``{path: {new_line_no: source_text}}`` across a unified diff.

    Lets the summary quote the actual offending line next to a finding so
    a reviewer reads it without opening the Files-changed tab. Only new-side
    (added / context) lines are captured; removed lines have no new number.
    """
    return {
        fd.path: _content_from_raw(fd.raw) for fd in parse_unified_diff(diff_text)
    }


__all__ = ["FileDiff", "new_side_content", "parse_unified_diff"]

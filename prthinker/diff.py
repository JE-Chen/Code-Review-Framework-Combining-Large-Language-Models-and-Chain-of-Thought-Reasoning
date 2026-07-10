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
from collections.abc import Iterator
from dataclasses import dataclass, field

_HUNK_RE = re.compile(
    r"^@@\s+-(?P<old_start>\d+)(?:,(?P<old_count>\d+))?\s+"
    r"\+(?P<new_start>\d+)(?:,(?P<new_count>\d+))?\s+@@"
)


def _iter_new_side(
    raw: str, *, in_hunks_only: bool = True
) -> Iterator[tuple[int, str, bool]]:
    """Yield ``(new_line_no, content, is_added)`` per new-side diff line.

    Shared hunk walker behind :func:`iter_added_lines`,
    :func:`_content_from_raw` and :meth:`FileDiff.content_sha256`. The
    new-side counter resets at each ``@@`` header and advances on added
    (``+``) and context (space) lines; removed / metadata lines are
    skipped. With ``in_hunks_only`` (the default) lines before the first
    hunk header are ignored; ``content_sha256`` disables it to keep its
    historical treatment of raw text without hunk headers.
    """
    new_line = 0
    in_hunk = False
    for line in raw.splitlines():
        match = _HUNK_RE.match(line)
        if match:
            in_hunk = True
            new_line = int(match.group("new_start")) - 1
            continue
        if in_hunks_only and not in_hunk:
            continue
        if line.startswith("+") and not line.startswith("+++"):
            new_line += 1
            yield new_line, line[1:], True
        elif line.startswith(" "):
            new_line += 1
            yield new_line, line[1:], False


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
        new_side = [
            content
            for _, content, _ in _iter_new_side(self.raw, in_hunks_only=False)
        ]
        h = hashlib.sha256()
        h.update("\n".join(new_side).encode("utf-8"))
        return h.hexdigest()


def _starts_file(line: str) -> bool:
    return line.startswith("diff --git ")


def git_header_b_path(line: str) -> str | None:
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
        state.fallback = git_header_b_path(line) or state.fallback
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


def _hunk_start_line(line: str, current: int) -> int:
    """New-side line number just before a hunk, or `current` if unparsable."""
    match = _HUNK_RE.match(line)
    if match:
        return int(match.group("new_start")) - 1
    return current


@dataclass
class _ParseState:
    """Mutable accumulator threaded through the per-file diff scan."""

    files: list[FileDiff] = field(default_factory=list)
    current_buf: list[str] = field(default_factory=list)
    header_buf: list[str] = field(default_factory=list)
    in_hunks: bool = False
    new_line_no: int = 0
    collected_new_lines: set[int] = field(default_factory=set)

    def start_file(self, line: str) -> None:
        """Flush the pending file and begin a new one at a `diff --git` line."""
        self.flush()
        self.current_buf = [line]
        self.header_buf = [line]
        self.in_hunks = False
        self.new_line_no = 0
        self.collected_new_lines = set()

    def flush(self) -> None:
        """Append the buffered file to `files` when it has a resolvable path."""
        if not self.current_buf:
            return
        new_path, is_binary, is_deleted = _extract_paths(self.header_buf)
        if new_path is None:
            return
        self.files.append(
            FileDiff(
                path=new_path,
                raw="".join(self.current_buf),
                new_lines=set(self.collected_new_lines),
                is_binary=is_binary,
                is_deleted=is_deleted,
            )
        )

    def consume(self, line: str) -> None:
        """Fold one non-header diff line into the state machine."""
        self.current_buf.append(line)
        if line.startswith("@@"):
            self.in_hunks = True
            self.header_buf.append(line)
            self.new_line_no = _hunk_start_line(line, self.new_line_no)
        elif not self.in_hunks:
            self.header_buf.append(line)
        else:
            # '-' lines and metadata don't advance the new-side counter.
            self.new_line_no = _advance_new_side(
                line, self.new_line_no, self.collected_new_lines
            )


def parse_unified_diff(diff_text: str) -> list[FileDiff]:
    """Split `diff_text` into one `FileDiff` per file.

    The raw text per file preserves the original `diff --git`/`@@` headers
    so the model still sees full context.
    """
    if not diff_text.strip():
        return []
    state = _ParseState()
    for line in diff_text.splitlines(keepends=True):
        if _starts_file(line):
            state.start_file(line)
        elif state.current_buf:
            # Anything before the first `diff --git` is preamble; skip it.
            state.consume(line)
    state.flush()
    return state.files


def _content_from_raw(raw: str) -> dict[int, str]:
    """Map new-side line numbers to their content within one file's diff."""
    return {no: content for no, content, _ in _iter_new_side(raw)}


def iter_added_lines(raw: str) -> list[tuple[int, str]]:
    """Return ``(new_line_no, content)`` for added lines in one file's diff.

    Only lines added on the new side are returned; context lines advance
    the counter but are not emitted, and removed / metadata lines are
    skipped. Shared by the orientation scanners that care specifically
    about what a PR *introduces* (deferred-work markers, conflict markers).
    """
    return [
        (no, content)
        for no, content, is_added in _iter_new_side(raw)
        if is_added
    ]


def new_side_content(diff_text: str) -> dict[str, dict[int, str]]:
    """Map ``{path: {new_line_no: source_text}}`` across a unified diff.

    Lets the summary quote the actual offending line next to a finding so
    a reviewer reads it without opening the Files-changed tab. Only new-side
    (added / context) lines are captured; removed lines have no new number.
    """
    return {
        fd.path: _content_from_raw(fd.raw) for fd in parse_unified_diff(diff_text)
    }


__all__ = [
    "FileDiff",
    "git_header_b_path",
    "iter_added_lines",
    "new_side_content",
    "parse_unified_diff",
]

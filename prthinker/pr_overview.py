"""Deterministic, model-free preliminary PR overview.

Builds a short "what this PR does" digest from the commit messages and the
set of changed files — no inference, so it runs on the runner profile and
is cheap enough to render on every review. It complements (does not
replace) the model's per-file summaries: it answers "what changed" from
the commits and the file layout, while the pipeline answers "is it any
good".
"""

from __future__ import annotations

from collections import Counter

_CONVENTIONAL_TYPES: frozenset[str] = frozenset({
    "feat", "fix", "refactor", "docs", "test", "chore",
    "perf", "security", "build", "ci", "style", "revert",
})
_MAX_COMMITS_LISTED = 15
_MAX_GROUPS = 6
_ROOT_LABEL = "(root)"
_NO_EXT_LABEL = "(none)"


def _subject(message: str) -> str:
    """First non-empty line of a commit message."""
    stripped = message.strip()
    return stripped.splitlines()[0] if stripped else ""


def _commit_type(subject: str) -> str | None:
    """Conventional-commit type prefix (``feat``/``fix``/…), or None."""
    head = subject.split(":", 1)[0].strip().lower()
    head = head.split("(", 1)[0].strip()  # drop the optional (scope)
    return head if head in _CONVENTIONAL_TYPES else None


def summarize_commit_types(messages: list[str]) -> str:
    """A ``feat (3) · fix (1)`` tally of conventional-commit types."""
    types = Counter(
        t for m in messages if (t := _commit_type(_subject(m))) is not None
    )
    return " · ".join(f"{t} ({n})" for t, n in types.most_common())


def _top_level_dir(path: str) -> str:
    return path.split("/", 1)[0] if "/" in path else _ROOT_LABEL


def _extension(path: str) -> str:
    name = path.rsplit("/", 1)[-1]
    return name.rsplit(".", 1)[-1] if "." in name else _NO_EXT_LABEL


def _dir_summary(paths: list[str]) -> str:
    """Top ``_MAX_GROUPS`` directories as `` `a/`, `b/` ``."""
    dirs = Counter(_top_level_dir(p) for p in paths)
    return ", ".join(f"`{d}/`" for d, _ in dirs.most_common(_MAX_GROUPS))


def _ext_summary(paths: list[str]) -> str:
    """Top ``_MAX_GROUPS`` extensions as ``.py (8) · .rst (3)``."""
    exts = Counter(_extension(p) for p in paths)
    return " · ".join(
        f".{e} ({n})"
        for e, n in exts.most_common(_MAX_GROUPS)
        if e != _NO_EXT_LABEL
    )


def summarize_changes(paths: list[str]) -> str:
    """A ``12 file(s) across `a/`, `b/` — .py (8) · .rst (3)`` line."""
    if not paths:
        return ""
    line = f"{len(paths)} file(s)"
    dir_str = _dir_summary(paths)
    if dir_str:
        line += f" across {dir_str}"
    ext_str = _ext_summary(paths)
    if ext_str:
        line += f" — {ext_str}"
    return line


def _commit_lines(messages: list[str]) -> list[str]:
    """The bulleted, length-capped commit-subject list."""
    subjects = [s for m in messages if (s := _subject(m))]
    if not subjects:
        return []
    lines = [f"- **Commits ({len(subjects)}):**"]
    lines += [f"  - {s}" for s in subjects[:_MAX_COMMITS_LISTED]]
    extra = len(subjects) - _MAX_COMMITS_LISTED
    if extra > 0:
        lines.append(f"  - … and {extra} more")
    return lines


def build_overview_block(
    commit_messages: list[str], paths: list[str]
) -> list[str]:
    """Render the preliminary-overview markdown lines (empty list if no data)."""
    body: list[str] = []
    changes = summarize_changes(paths)
    if changes:
        body.append(f"- **Changes:** {changes}")
    types = summarize_commit_types(commit_messages)
    if types:
        body.append(f"- **Commit types:** {types}")
    body += _commit_lines(commit_messages)
    if not body:
        return []
    return ["### 📋 What this PR does (preliminary)", "", *body, "", "---", ""]


def build_overview_text(commit_messages: list[str], paths: list[str]) -> str:
    """Convenience: the overview block as a single string, or '' if empty."""
    block = build_overview_block(commit_messages, paths)
    return "\n".join(block) if block else ""


__all__ = [
    "build_overview_block",
    "build_overview_text",
    "summarize_changes",
    "summarize_commit_types",
]

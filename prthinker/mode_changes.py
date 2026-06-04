"""Surface file-mode (permission) changes a PR makes.

Git records a permission change as ``old mode 100644`` / ``new mode
100755`` in the diff header, with no textual hunk. The most security-
relevant case is a data file or script gaining the executable bit
(``...644`` → ``...755``): it is easy to miss in a large diff yet can
turn a checked-in file into something the CI or a deploy will run. This
module extracts those mode transitions and renders a self-omitting note,
flagging the newly-executable ones explicitly.

Runner-safe: pure string parsing over the diff already in hand.
"""

from __future__ import annotations

from dataclasses import dataclass

from prthinker.diff import git_header_b_path

_MODE_LIMIT = 12
_OLD_MODE_PREFIX = "old mode "
_NEW_MODE_PREFIX = "new mode "
_EXEC_BITS = ("7", "5", "1")


@dataclass(frozen=True)
class ModeChange:
    """One file's mode transition: path, old mode, new mode."""

    path: str
    old_mode: str
    new_mode: str

    @property
    def became_executable(self) -> bool:
        """True when the new mode adds an execute bit the old mode lacked."""
        return _is_executable(self.new_mode) and not _is_executable(
            self.old_mode
        )


def _is_executable(mode: str) -> bool:
    """True when a git mode string's owner digit carries an execute bit."""
    digits = mode.strip()
    return len(digits) >= 3 and digits[-3] in _EXEC_BITS


@dataclass
class _ModeState:
    """Accumulator threaded across the diff's header lines."""

    path: str | None = None
    old_mode: str | None = None
    changes: list[ModeChange] | None = None


def _fold_line(line: str, state: _ModeState) -> None:
    """Fold one diff line into the mode-change accumulator, in place."""
    if line.startswith("diff --git "):
        state.path = git_header_b_path(line)
        state.old_mode = None
    elif line.startswith(_OLD_MODE_PREFIX):
        state.old_mode = line[len(_OLD_MODE_PREFIX):].strip()
    elif line.startswith(_NEW_MODE_PREFIX) and state.old_mode is not None:
        new_mode = line[len(_NEW_MODE_PREFIX):].strip()
        if state.path is not None:
            state.changes.append(
                ModeChange(state.path, state.old_mode, new_mode)
            )
        state.old_mode = None


def detect_mode_changes(diff_text: str) -> list[ModeChange]:
    """Extract every ``old mode`` / ``new mode`` transition in the diff."""
    state = _ModeState(changes=[])
    for line in diff_text.splitlines():
        _fold_line(line, state)
    return state.changes


def _mode_line(change: ModeChange) -> str:
    """Render one ``path: old → new`` bullet, flagging new executables."""
    flag = " ⚠️ now executable" if change.became_executable else ""
    return f"- `{change.path}`: `{change.old_mode}` → `{change.new_mode}`{flag}"


def format_mode_note(changes: list[ModeChange]) -> str:
    """Collapsible 'file mode changes' block, or ``""`` when there are none."""
    if not changes:
        return ""
    shown = changes[:_MODE_LIMIT]
    lines = [
        f"<details><summary>🔑 {len(changes)} file mode change(s)"
        "</summary>",
        "",
    ]
    lines += [_mode_line(c) for c in shown]
    extra = len(changes) - len(shown)
    if extra > 0:
        lines.append(f"- … and {extra} more")
    lines += [
        "",
        "_A file gaining the execute bit can change what CI or a deploy "
        "runs — confirm it is intended._",
        "",
        "</details>",
    ]
    return "\n".join(lines)


__all__ = ["ModeChange", "detect_mode_changes", "format_mode_note"]

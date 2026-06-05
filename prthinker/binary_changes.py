"""List binary files a PR changes, which cannot be reviewed inline.

A changed image, font, compiled asset, or other binary shows up in the
diff only as ``Binary files a/x and b/y differ`` — there is no textual
hunk for the model or a human to read. Silently skipping it hides the
fact that the PR ships an opaque blob. This module collects those binary
paths and renders a self-omitting note so the reviewer knows to inspect
them out of band (download, diff the rendered asset, check provenance).

Runner-safe: reads the ``is_binary`` flag the diff parser already sets.
"""

from __future__ import annotations

from prthinker.diff import parse_unified_diff

_BINARY_LIMIT = 12


def binary_changed_files(diff_text: str) -> list[str]:
    """Return the paths of binary files in the diff, sorted."""
    paths = [fd.path for fd in parse_unified_diff(diff_text) if fd.is_binary]
    return sorted(paths)


def format_binary_note(paths: list[str]) -> str:
    """Collapsible 'binary changes' block, or ``""`` when there are none."""
    if not paths:
        return ""
    shown = paths[:_BINARY_LIMIT]
    lines = [
        f"<details><summary>📦 {len(paths)} binary file(s) changed — "
        "review out of band</summary>",
        "",
    ]
    lines += [f"- `{p}`" for p in shown]
    extra = len(paths) - len(shown)
    if extra > 0:
        lines.append(f"- … and {extra} more")
    lines += [
        "",
        "_No textual diff exists for these — inspect the rendered asset "
        "and its provenance directly._",
        "",
        "</details>",
    ]
    return "\n".join(lines)


__all__ = ["binary_changed_files", "format_binary_note"]

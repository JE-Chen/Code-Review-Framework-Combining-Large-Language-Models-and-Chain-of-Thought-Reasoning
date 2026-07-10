"""Shared added-line scan loop and note renderer for the diff detectors.

The orientation detectors (:mod:`prthinker.debug_left`,
:mod:`prthinker.new_markers`, :mod:`prthinker.merge_markers`,
:mod:`prthinker.bidi_guard`, :mod:`prthinker.empty_except`) all walk the
same added-lines-of-the-diff loop and render the same collapsible
``<details>`` note. This module holds that shared skeleton so each
detector only supplies its matcher and its wording.

Runner-safe: pure string handling over the diff already in hand.
"""

from __future__ import annotations

from typing import Callable, Iterator, TypeVar

from prthinker.diff import iter_added_lines, parse_unified_diff

HitT = TypeVar("HitT")


def iter_file_added_lines(
    diff_text: str,
) -> Iterator[tuple[str, list[tuple[int, str]]]]:
    """Yield ``(path, added_lines)`` per file in the diff.

    ``added_lines`` is the ``(new_line_no, content)`` list from
    :func:`prthinker.diff.iter_added_lines`, for detectors that need
    whole-file context (e.g. pairing an ``except:`` with its body line).
    """
    for file_diff in parse_unified_diff(diff_text):
        yield file_diff.path, iter_added_lines(file_diff.raw)


def scan_added_lines(
    diff_text: str, matcher: Callable[[str, int, str], HitT | None]
) -> list[HitT]:
    """Collect ``matcher(path, line_no, content)`` hits over every added line."""
    found: list[HitT] = []
    for path, added in iter_file_added_lines(diff_text):
        for line_no, content in added:
            hit = matcher(path, line_no, content)
            if hit is not None:
                found.append(hit)
    return found


def format_details_note(
    hits: list[HitT],
    *,
    summary: str,
    bullet: Callable[[HitT], str],
    footer: str,
    limit: int,
    open_details: bool = False,
) -> str:
    """Render the detectors' collapsible ``<details>`` block, or ``""``.

    ``summary`` is the one-line header, ``bullet`` renders one hit, and
    ``footer`` is the italic advisory line. At most ``limit`` hits are
    listed; the rest collapse into an "… and N more" bullet.
    ``open_details=True`` renders ``<details open>`` for warning-grade
    notes that should not start collapsed.
    """
    if not hits:
        return ""
    shown = hits[:limit]
    opening = "<details open>" if open_details else "<details>"
    lines = [f"{opening}<summary>{summary}</summary>", ""]
    lines += [bullet(h) for h in shown]
    extra = len(hits) - len(shown)
    if extra > 0:
        lines.append(f"- … and {extra} more")
    lines += ["", footer, "", "</details>"]
    return "\n".join(lines)


__all__ = ["format_details_note", "iter_file_added_lines", "scan_added_lines"]

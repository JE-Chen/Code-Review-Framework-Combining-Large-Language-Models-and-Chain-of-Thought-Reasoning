"""Compose the no-model reviewer-orientation signals into report blocks.

The per-signal modules (``bidi_guard``, ``merge_markers``, ``rename_map``,
``deleted_files``, ``mode_changes``, ``noise_files``, ``whitespace_only``,
``binary_changes``, ``large_hunk``, ``coverage_gap``, ``new_markers``,
``debug_left``, ``empty_except``) each answer one question about a diff
and render a self-omitting block. This module is the single place that
runs them in a sensible reading order — security warnings first, then
navigation, then skim guidance, then code-quality hints — and drops the
empty ones.

Keeping the composition here (rather than inline in the review command)
means the same signal set drives both the live PR comment and the
standalone ``triage`` command, with no duplication and one ordering to
maintain.

Runner-safe: every signal is a pure function over the diff text and the
changed-path list.
"""

from __future__ import annotations

from prthinker.bidi_guard import find_bidi_hits, format_bidi_note
from prthinker.binary_changes import binary_changed_files, format_binary_note
from prthinker.coverage_gap import coverage_gaps, format_coverage_gap_note
from prthinker.debug_left import find_debug_statements, format_debug_note
from prthinker.deleted_files import deleted_files, format_deleted_note
from prthinker.empty_except import (
    find_swallowed_excepts,
    format_swallowed_note,
)
from prthinker.large_hunk import format_large_block_note, large_blocks
from prthinker.merge_markers import find_conflict_markers, format_conflict_note
from prthinker.mode_changes import detect_mode_changes, format_mode_note
from prthinker.new_markers import format_new_markers_note, new_markers
from prthinker.noise_files import format_noise_note, noise_files
from prthinker.rename_map import detect_renames, format_rename_note
from prthinker.whitespace_only import (
    format_whitespace_note,
    whitespace_only_files,
)


def build_static_signal_sections(
    diff_text: str, changed_paths: list[str]
) -> tuple[str, ...]:
    """Return the non-empty no-model orientation blocks, in reading order.

    Ordering: security warnings (Trojan-Source, conflict markers) lead, so
    the most urgent issues are never buried; then navigation (moves,
    deletions, mode changes); then skim guidance (noise, formatting,
    binary, large blocks); then code-quality hints (coverage, markers,
    debug leftovers, swallowed exceptions).
    """
    sections = (
        format_bidi_note(find_bidi_hits(diff_text)),
        format_conflict_note(find_conflict_markers(diff_text)),
        format_rename_note(detect_renames(diff_text)),
        format_deleted_note(deleted_files(diff_text)),
        format_mode_note(detect_mode_changes(diff_text)),
        format_noise_note(noise_files(changed_paths)),
        format_whitespace_note(whitespace_only_files(diff_text)),
        format_binary_note(binary_changed_files(diff_text)),
        format_large_block_note(large_blocks(diff_text)),
        format_coverage_gap_note(coverage_gaps(changed_paths)),
        format_new_markers_note(new_markers(diff_text)),
        format_debug_note(find_debug_statements(diff_text)),
        format_swallowed_note(find_swallowed_excepts(diff_text)),
    )
    return tuple(section for section in sections if section)


__all__ = ["build_static_signal_sections"]

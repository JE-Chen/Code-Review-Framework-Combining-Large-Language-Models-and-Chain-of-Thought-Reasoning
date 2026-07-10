"""Structured reviewer-orientation signals for SARIF / HTML output.

The live PR comment renders the no-model signals as markdown via
:mod:`prthinker.orientation`. SARIF and the standalone HTML report need
them as *structured* records instead — a rule id, a level, a message, and
an optional location. This module reuses the very same detector functions
and flattens their results into a single :class:`SignalFinding` list that
both exporters consume, so detection logic is never duplicated; only the
presentation differs.

Runner-safe: every detector is a pure function over the diff text.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from prthinker.bidi_guard import find_bidi_hits
from prthinker.coverage_gap import coverage_gaps
from prthinker.debug_left import find_debug_statements
from prthinker.diff import FileDiff, parse_unified_diff
from prthinker.empty_except import find_swallowed_excepts
from prthinker.large_hunk import large_blocks
from prthinker.merge_markers import find_conflict_markers
from prthinker.mode_changes import detect_mode_changes
from prthinker.new_markers import new_markers
from prthinker.noise_files import noise_files
from prthinker.rename_map import detect_renames
from prthinker.whitespace_only import whitespace_only_files

_LEVEL_ERROR = "error"
_LEVEL_WARNING = "warning"
_LEVEL_NOTE = "note"

# Shared rule-id namespace for every exporter (SARIF, CodeClimate, CSV,
# GHA annotations) so a finding carries the same `prthinker/<rule>` id
# everywhere it surfaces.
RULE_PREFIX = "prthinker"


def report_fingerprint(rule_id: str, path: str, line: int, text: str) -> str:
    """Stable per-result SHA-256 dedup key shared by the report exporters.

    SARIF ``partialFingerprints`` and GitLab CodeClimate ``fingerprint``
    both hash the same four fields; keeping the single implementation here
    guarantees the two outputs never drift apart across runs.
    """
    raw = f"{rule_id}\0{path}\0{line}\0{text}".encode("utf-8")
    # Dedup key, not a security token.
    return hashlib.sha256(raw, usedforsecurity=False).hexdigest()


@dataclass(frozen=True)
class SignalFinding:
    """One structured orientation signal: rule, level, message, location."""

    rule_id: str
    name: str
    level: str
    message: str
    path: str | None = None
    line: int | None = None


def _bidi(diff: str) -> list[SignalFinding]:
    return [
        SignalFinding(
            "trojan-source", "Trojan-Source hidden character", _LEVEL_ERROR,
            f"Hidden bidi/invisible character(s): {', '.join(hit.markers)}",
            hit.path, hit.line,
        )
        for hit in find_bidi_hits(diff)
    ]


def _conflict(diff: str) -> list[SignalFinding]:
    return [
        SignalFinding(
            "merge-conflict", "Leftover merge-conflict marker", _LEVEL_ERROR,
            f"Leftover merge-conflict marker `{marker.marker}`",
            marker.path, marker.line,
        )
        for marker in find_conflict_markers(diff)
    ]


def _swallowed(diff: str) -> list[SignalFinding]:
    return [
        SignalFinding(
            "swallowed-exception", "Swallowed exception", _LEVEL_WARNING,
            "Swallowed exception (empty except body)", hit.path, hit.line,
        )
        for hit in find_swallowed_excepts(diff)
    ]


def _debug(diff: str) -> list[SignalFinding]:
    return [
        SignalFinding(
            "debug-statement", "Leftover debug statement", _LEVEL_WARNING,
            f"Leftover debug statement: {hit.text}", hit.path, hit.line,
        )
        for hit in find_debug_statements(diff)
    ]


def _markers(diff: str) -> list[SignalFinding]:
    return [
        SignalFinding(
            "deferred-marker", "Deferred-work marker", _LEVEL_NOTE,
            f"{marker.kind} marker: {marker.text}", marker.path, marker.line,
        )
        for marker in new_markers(diff)
    ]


def _renames(diff: str) -> list[SignalFinding]:
    out: list[SignalFinding] = []
    for rename in detect_renames(diff):
        sim = (
            f" ({rename.similarity}% similar)"
            if rename.similarity is not None
            else ""
        )
        out.append(
            SignalFinding(
                "rename", "Renamed or moved file", _LEVEL_NOTE,
                f"Renamed from `{rename.old_path}`{sim}", rename.new_path, None,
            )
        )
    return out


def _deleted(files: list[FileDiff]) -> list[SignalFinding]:
    # Attribute filter over the shared parse (mirrors
    # prthinker.deleted_files.deleted_files without re-parsing the diff).
    return [
        SignalFinding(
            "file-deleted", "Deleted file", _LEVEL_NOTE,
            "File deleted", file_diff.path, None,
        )
        for file_diff in files
        if file_diff.is_deleted
    ]


def _modes(diff: str) -> list[SignalFinding]:
    out: list[SignalFinding] = []
    for change in detect_mode_changes(diff):
        level = _LEVEL_WARNING if change.became_executable else _LEVEL_NOTE
        suffix = " (now executable)" if change.became_executable else ""
        out.append(
            SignalFinding(
                "file-mode-change", "File mode change", level,
                f"Mode {change.old_mode} → {change.new_mode}{suffix}",
                change.path, None,
            )
        )
    return out


def _noise(paths: list[str]) -> list[SignalFinding]:
    return [
        SignalFinding(
            "low-attention-file", "Low-attention file", _LEVEL_NOTE,
            f"Low-attention file ({reason})", path, None,
        )
        for path, reason in noise_files(paths)
    ]


def _whitespace(diff: str) -> list[SignalFinding]:
    return [
        SignalFinding(
            "formatting-only", "Formatting-only change", _LEVEL_NOTE,
            "Formatting-only change (whitespace)", path, None,
        )
        for path in whitespace_only_files(diff)
    ]


def _binary(files: list[FileDiff]) -> list[SignalFinding]:
    # Attribute filter over the shared parse (mirrors
    # prthinker.binary_changes.binary_changed_files without re-parsing).
    return [
        SignalFinding(
            "binary-change", "Binary change", _LEVEL_NOTE,
            "Binary change (no textual diff)", file_diff.path, None,
        )
        for file_diff in files
        if file_diff.is_binary
    ]


def _large_blocks(diff: str) -> list[SignalFinding]:
    return [
        SignalFinding(
            "large-block", "Large contiguous added block", _LEVEL_NOTE,
            f"Large contiguous added block ({block.lines} lines)",
            block.path, None,
        )
        for block in large_blocks(diff)
    ]


def _coverage(paths: list[str]) -> list[SignalFinding]:
    return [
        SignalFinding(
            "coverage-gap", "Test-coverage gap", _LEVEL_NOTE,
            "Changed without a matching test change", path, None,
        )
        for path in coverage_gaps(paths)
    ]


def _collect(diff_text: str) -> list[SignalFinding]:
    """Run every detector once over ``diff_text`` (single shared parse)."""
    files = parse_unified_diff(diff_text)
    paths = [file_diff.path for file_diff in files]
    return [
        *_bidi(diff_text),
        *_conflict(diff_text),
        *_renames(diff_text),
        *_deleted(files),
        *_modes(diff_text),
        *_noise(paths),
        *_whitespace(diff_text),
        *_binary(files),
        *_large_blocks(diff_text),
        *_coverage(paths),
        *_markers(diff_text),
        *_debug(diff_text),
        *_swallowed(diff_text),
    ]


# ``write_report_dir`` runs 6+ writers over the SAME diff and each one calls
# :func:`collect_signal_findings`; the memo makes those repeats free. Keyed
# by the diff's SHA-256 and size-capped (FIFO) so a long-lived process never
# grows without bound. Cached as a tuple of frozen dataclasses, so entries
# are safe to share; callers get a fresh list they may mutate.
_MEMO_MAX_ENTRIES = 4
_SIGNAL_MEMO: dict[str, tuple[SignalFinding, ...]] = {}


def collect_signal_findings(diff_text: str) -> list[SignalFinding]:
    """Flatten every no-model signal for ``diff_text`` into one list.

    Changed paths for the path-based signals (noise, coverage) are derived
    from the diff itself, so the caller only supplies the diff. Ordering
    matches the markdown report: security first, then navigation, skim
    guidance, and code-quality hints. Repeated calls with the same diff
    (the ``--report-dir`` writers) are served from a small in-process memo.
    """
    key = hashlib.sha256(
        diff_text.encode("utf-8"), usedforsecurity=False
    ).hexdigest()
    cached = _SIGNAL_MEMO.get(key)
    if cached is None:
        if len(_SIGNAL_MEMO) >= _MEMO_MAX_ENTRIES:
            _SIGNAL_MEMO.pop(next(iter(_SIGNAL_MEMO)))
        cached = tuple(_collect(diff_text))
        _SIGNAL_MEMO[key] = cached
    return list(cached)


__all__ = [
    "RULE_PREFIX",
    "SignalFinding",
    "collect_signal_findings",
    "report_fingerprint",
]

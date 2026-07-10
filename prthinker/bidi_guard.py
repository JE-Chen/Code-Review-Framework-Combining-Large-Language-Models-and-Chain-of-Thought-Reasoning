"""Detect Trojan-Source bidi / invisible characters a PR adds.

The Trojan-Source attack (CVE-2021-42574) hides logic from human readers
by embedding Unicode bidirectional-override control characters in source:
the compiler sees one token order, the reviewer's editor renders another,
so code that *reads* as a comment actually *executes*. Zero-width and
other invisible characters are abused the same way — to forge identifiers
or smuggle content past a skim. None of these belong in ordinary source.

This module scans the *added* diff lines for that curated set of control
characters and raises a warning note naming the offending code points and
their line, so a reviewer never silently merges a glyph they cannot see.
It complements the prompt-injection guard, which targets attacker text in
the diff rather than rendering-level deception in the code itself.

Runner-safe: pure character inspection over the diff already in hand.
"""

from __future__ import annotations

from dataclasses import dataclass

from prthinker.detector_util import format_details_note, scan_added_lines

_BIDI_LIMIT = 15

# Bidirectional formatting / override controls abused by Trojan Source.
_BIDI_CONTROLS = {
    0x202A: "LRE",
    0x202B: "RLE",
    0x202C: "PDF",
    0x202D: "LRO",
    0x202E: "RLO",
    0x2066: "LRI",
    0x2067: "RLI",
    0x2068: "FSI",
    0x2069: "PDI",
    0x200E: "LRM",
    0x200F: "RLM",
    0x061C: "ALM",
}
# Zero-width / invisible characters abused to forge or hide content.
_INVISIBLE = {
    0x200B: "ZWSP",
    0x200C: "ZWNJ",
    0x200D: "ZWJ",
    0x2060: "WJ",
    0xFEFF: "BOM",
}
_DANGEROUS = {**_BIDI_CONTROLS, **_INVISIBLE}


@dataclass(frozen=True)
class BidiHit:
    """One added line carrying dangerous characters: path, line, names."""

    path: str
    line: int
    markers: tuple[str, ...]


def _markers_in(content: str) -> tuple[str, ...]:
    """Return the sorted, de-duplicated names of dangerous chars in a line."""
    found = {
        _DANGEROUS[ord(ch)] for ch in content if ord(ch) in _DANGEROUS
    }
    return tuple(sorted(found))


def _hit_for_line(path: str, line_no: int, content: str) -> BidiHit | None:
    """Build a :class:`BidiHit` when the line carries dangerous chars."""
    markers = _markers_in(content)
    if not markers:
        return None
    return BidiHit(path, line_no, markers)


def find_bidi_hits(diff_text: str) -> list[BidiHit]:
    """Return every added line carrying bidi / invisible control chars."""
    return scan_added_lines(diff_text, _hit_for_line)


def _hit_line(hit: BidiHit) -> str:
    """Render one ``path:line — MARKERS`` bullet."""
    return f"- `{hit.path}:{hit.line}` — {', '.join(hit.markers)}"


def format_bidi_note(hits: list[BidiHit]) -> str:
    """Collapsible 'hidden-character' warning block, or ``""``."""
    return format_details_note(
        hits,
        summary=(
            f"🚨 {len(hits)} line(s) with hidden "
            "bidi / invisible characters"
        ),
        bullet=_hit_line,
        footer=(
            "_These render differently from what executes (Trojan Source) — "
            "treat as suspicious and verify the raw bytes._"
        ),
        limit=_BIDI_LIMIT,
        open_details=True,
    )


__all__ = ["BidiHit", "find_bidi_hits", "format_bidi_note"]

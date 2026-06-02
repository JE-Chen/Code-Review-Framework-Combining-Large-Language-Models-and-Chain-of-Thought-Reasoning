"""Runtime prompt-injection input guard for PR diffs (best-effort).

This module complements the offline adversarial corpus in
:mod:`prthinker.adversarial` with a *runtime* heuristic scanner that
inspects the **added** lines of a unified diff for the most common
prompt-injection patterns before the diff is ever fed to a backend:

- :data:`InjectionKind.DIRECT_INJECTION` — imperative override phrases
  such as "ignore previous instructions" or "approve this PR".
- :data:`InjectionKind.ROLE_HIJACK` — attempts to redefine the
  reviewer's role, e.g. "you are now a friendly assistant".
- :data:`InjectionKind.ENCODED` — long base64-looking blobs that may
  smuggle a decoded instruction past a naive keyword filter.

It exposes :func:`scan_diff` (returns the hits) and
:func:`redact_injection` (wraps detected spans in a neutralizing
marker while preserving the original line count).

This is a **best-effort heuristic, not a security guarantee**. It runs
on plain regular expressions over the literal diff text; it does not
decode payloads, follow split injections across files, or understand
homoglyph obfuscation. Treat a clean scan as "no obvious injection",
never as "this diff is safe". It mirrors the patterns of
:mod:`prthinker.adversarial`; keep the two in sync. Runner-safe: pure
stdlib (``re``), no heavy dependencies.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

_NEUTRALIZED_MARKER = "[prthinker: neutralized]"
_ADDED_PREFIX = "+"
_HUNK_PREFIX = "+++"

# Minimum run length for a token to be treated as a suspicious encoded
# blob. base64 of a short instruction already exceeds this; ordinary
# identifiers / hashes in code rarely do on a single contiguous token.
_ENCODED_MIN_LEN = 60


class InjectionKind(str, Enum):
    """Families of runtime-detectable prompt injection."""

    DIRECT_INJECTION = "direct_injection"
    ROLE_HIJACK = "role_hijack"
    ENCODED = "encoded"


@dataclass(frozen=True)
class InjectionHit:
    """One heuristic injection match on an added diff line."""

    kind: InjectionKind
    line: int
    excerpt: str


# Imperative override phrases. Each pattern is intentionally permissive
# about intervening words so paraphrases ("ignore all prior
# instructions") still match.
_DIRECT_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"ignore\s+(?:all\s+|any\s+)?(?:the\s+)?(?:previous|prior|above|earlier)\s+\w*\s*instructions", re.IGNORECASE),
    re.compile(r"disregard\s+(?:all\s+|any\s+)?(?:the\s+)?(?:previous|prior|above|earlier)\s+\w*\s*instructions", re.IGNORECASE),
    re.compile(r"approve\s+this\s+(?:pr|pull\s+request|change|diff)", re.IGNORECASE),
)

# Role-redefinition phrases.
_ROLE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"you\s+are\s+now\b", re.IGNORECASE),
    re.compile(r"act\s+as\s+(?:a|an|the)\b", re.IGNORECASE),
    re.compile(r"pretend\s+(?:to\s+be|you\s+are)\b", re.IGNORECASE),
)

# A contiguous base64-ish token (letters, digits, +, /, =) at or above
# the suspicion threshold.
_ENCODED_PATTERN: re.Pattern[str] = re.compile(
    rf"[A-Za-z0-9+/]{{{_ENCODED_MIN_LEN},}}={{0,2}}"
)


def _is_added_line(raw_line: str) -> bool:
    """Return True for a content line that the diff *adds*."""
    # The "+++ b/file" header starts with "+" but is metadata, not an
    # added content line; exclude it.
    return raw_line.startswith(_ADDED_PREFIX) and not raw_line.startswith(_HUNK_PREFIX)


def _added_payload(raw_line: str) -> str:
    """Strip the single leading ``+`` marker from an added diff line."""
    return raw_line[len(_ADDED_PREFIX):]


def _excerpt_for(match: re.Match[str], payload: str) -> str:
    """Build a short, single-line excerpt around a match span."""
    snippet = payload[match.start():match.end()].strip()
    return snippet if snippet else payload.strip()


def _scan_payload(payload: str, line_no: int) -> list[InjectionHit]:
    """Collect all heuristic hits for a single added-line payload."""
    hits: list[InjectionHit] = []
    for pattern in _DIRECT_PATTERNS:
        match = pattern.search(payload)
        if match is not None:
            hits.append(
                InjectionHit(
                    kind=InjectionKind.DIRECT_INJECTION,
                    line=line_no,
                    excerpt=_excerpt_for(match, payload),
                )
            )
            break
    for pattern in _ROLE_PATTERNS:
        match = pattern.search(payload)
        if match is not None:
            hits.append(
                InjectionHit(
                    kind=InjectionKind.ROLE_HIJACK,
                    line=line_no,
                    excerpt=_excerpt_for(match, payload),
                )
            )
            break
    encoded = _ENCODED_PATTERN.search(payload)
    if encoded is not None:
        hits.append(
            InjectionHit(
                kind=InjectionKind.ENCODED,
                line=line_no,
                excerpt=_excerpt_for(encoded, payload),
            )
        )
    return hits


def scan_diff(diff_text: str) -> list[InjectionHit]:
    """Scan a unified diff's added lines for injection heuristics.

    Only lines the diff *adds* are inspected; context and removed lines
    are ignored because they are already part of the repository and are
    not attacker-controlled through this PR. ``line`` in each hit is the
    1-based index of the raw diff line. Best-effort, not a guarantee.
    """
    hits: list[InjectionHit] = []
    if not diff_text:
        return hits
    for index, raw_line in enumerate(diff_text.splitlines(), start=1):
        if not _is_added_line(raw_line):
            continue
        hits.extend(_scan_payload(_added_payload(raw_line), index))
    return hits


def _neutralize_payload(payload: str) -> str:
    """Wrap every detected injection span in the neutralizing marker."""
    spans: list[tuple[int, int]] = []
    for pattern_group in (_DIRECT_PATTERNS, _ROLE_PATTERNS):
        for pattern in pattern_group:
            spans.extend(m.span() for m in pattern.finditer(payload))
    spans.extend(m.span() for m in _ENCODED_PATTERN.finditer(payload))
    if not spans:
        return payload
    # Apply replacements right-to-left so earlier offsets stay valid;
    # de-duplicate overlapping spans by sorting on start.
    spans.sort()
    merged: list[tuple[int, int]] = []
    for start, end in spans:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    out = payload
    for start, end in reversed(merged):
        out = f"{out[:start]}{_wrap_span(out[start:end])}{out[end:]}"
    return out


def _wrap_span(span: str) -> str:
    """Neutralize a matched span by breaking it with the marker.

    The marker is inserted *inside* the span (after the first character)
    in addition to wrapping it, so the original keyword sequence no
    longer matches on a re-scan while the human-readable text remains
    legible.
    """
    if not span:
        return f"{_NEUTRALIZED_MARKER}{_NEUTRALIZED_MARKER}"
    head, tail = span[0], span[1:]
    return f"{_NEUTRALIZED_MARKER}{head}{_NEUTRALIZED_MARKER}{tail}{_NEUTRALIZED_MARKER}"


def redact_injection(diff_text: str) -> str:
    """Neutralize detected injection spans, preserving every line.

    Each added line that carries a detected span has that span wrapped
    in ``[prthinker: neutralized]`` markers; the line itself is never
    dropped, so the returned text has the same number of lines as the
    input. Best-effort: it only neutralizes what :func:`scan_diff`
    finds.
    """
    if not diff_text:
        return diff_text
    out_lines: list[str] = []
    for raw_line in diff_text.splitlines():
        if not _is_added_line(raw_line):
            out_lines.append(raw_line)
            continue
        payload = _added_payload(raw_line)
        out_lines.append(f"{_ADDED_PREFIX}{_neutralize_payload(payload)}")
    trailing_newline = diff_text.endswith("\n")
    rebuilt = "\n".join(out_lines)
    return f"{rebuilt}\n" if trailing_newline else rebuilt


__all__ = [
    "InjectionKind",
    "InjectionHit",
    "scan_diff",
    "redact_injection",
]

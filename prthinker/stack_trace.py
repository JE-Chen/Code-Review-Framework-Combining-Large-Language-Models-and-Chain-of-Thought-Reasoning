"""Parse failure output into ranked fault-location candidates.

Turns the raw text of a failing run — a Python traceback, a Node / Go /
Rust stack, or any log that mentions ``path:line`` — into an ordered
list of :class:`TraceFrame` candidates, deepest user frame first.
Framework / runtime frames (site-packages, node internals, the Rust
toolchain) are filtered so the candidates point at the repository's own
code. This is the cheapest execution signal available to fault
localisation: it needs only the failure text, no re-run.

Runner-safe: pure stdlib (``re`` / ``dataclasses`` / ``pathlib``).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_PY_FRAME_RE = re.compile(
    r'^[ \t]*File "(?P<path>[^"]+)", line (?P<line>\d+)(?:, in (?P<symbol>\S+))?',
    re.MULTILINE,
)
# Node / JS style: ``at symbol (file:line:col)`` or ``at file:line:col``.
_NODE_FRAME_RE = re.compile(
    r"^[ \t]*at[ \t]+(?:(?P<symbol>[\w.<>$\[\]]+)[ \t]+\()?"
    r"(?P<path>(?:[A-Za-z]:)?[\w.\\/-]+):(?P<line>\d+)(?::\d+)?\)?",
    re.MULTILINE,
)
# Language-agnostic fallback: any ``path.ext:line`` mention (Go panics,
# Rust backtraces, compiler diagnostics, plain log lines).
_FILE_LINE_RE = re.compile(
    r"(?P<path>(?:[A-Za-z]:)?[\w.\\/-]+\.[A-Za-z]\w{0,4}):(?P<line>\d+)"
)
# Substrings marking frames outside the repository's own code.
_NOISE_MARKERS = (
    "site-packages",
    "dist-packages",
    "node_modules",
    "node:internal",
    "/lib/python",
    "importlib/_bootstrap",
    "/rustc/",
)


@dataclass(frozen=True)
class TraceFrame:
    """One ranked fault-location candidate mined from failure output.

    ``rank`` is the candidate's position in the suspicion order —
    0 is the most suspicious (the deepest user frame).
    """

    path: str
    line: int
    symbol: str = ""
    rank: int = 0


def _is_noise(path: str) -> bool:
    """True for frames in the runtime / dependencies, not the user's repo."""
    lowered = path.lower().replace("\\", "/")
    if lowered.startswith("<"):
        return True
    return any(marker in lowered for marker in _NOISE_MARKERS)


def _normalize_path(raw: str, workdir: Path | None) -> str:
    """Posix-style path, made repo-relative when it sits under ``workdir``."""
    path = raw.strip().replace("\\", "/")
    while path.startswith("./"):
        path = path[2:]
    if workdir is None:
        return path
    prefix = Path(workdir).as_posix().rstrip("/") + "/"
    if path.lower().startswith(prefix.lower()):
        return path[len(prefix):]
    return path


def _python_candidates(text: str) -> list[tuple[str, int, str]]:
    """Python traceback frames, deepest (most suspicious) first."""
    hits = [
        (match.group("path"), int(match.group("line")), match.group("symbol") or "")
        for match in _PY_FRAME_RE.finditer(text)
    ]
    # Python tracebacks list the outermost call first; the deepest frame
    # (where the exception was raised) is the best fault candidate.
    hits.reverse()
    return hits


def _generic_candidates(text: str) -> list[tuple[str, int, str]]:
    """Node / Go / Rust / generic ``path:line`` mentions in text order.

    Node and Go stacks print the innermost frame first, so appearance
    order already approximates suspicion order. Node-style matches are
    collected first so, at the same text position, the symbol-bearing
    frame wins the later dedupe.
    """
    hits: list[tuple[int, str, int, str]] = []
    for match in _NODE_FRAME_RE.finditer(text):
        symbol = match.group("symbol") or ""
        hits.append(
            (match.start("path"), match.group("path"), int(match.group("line")), symbol)
        )
    for match in _FILE_LINE_RE.finditer(text):
        hits.append(
            (match.start("path"), match.group("path"), int(match.group("line")), "")
        )
    hits.sort(key=lambda item: item[0])
    return [(path, line, symbol) for _, path, line, symbol in hits]


def _dedupe(candidates: list[tuple[str, int, str]]) -> list[TraceFrame]:
    """Drop repeated ``(path, line)`` keys, keeping the best (earliest) rank."""
    seen: set[tuple[str, int]] = set()
    frames: list[TraceFrame] = []
    for path, line, symbol in candidates:
        key = (path, line)
        if key in seen:
            continue
        seen.add(key)
        frames.append(TraceFrame(path=path, line=line, symbol=symbol, rank=len(frames)))
    return frames


def parse_traceback(
    text: str, workdir: Path | str | None = None
) -> list[TraceFrame]:
    """Extract ranked fault-location candidates from failure output.

    Python tracebacks are preferred when present (deepest user frame
    first, runtime / site-packages frames filtered); otherwise Node /
    Go / Rust stack shapes and a generic ``path:line`` fallback apply.
    With ``workdir`` given, absolute paths under it become repo-relative.
    Garbage input yields an empty list — never an exception.
    """
    wd = Path(workdir) if workdir is not None else None
    candidates = _python_candidates(text) or _generic_candidates(text)
    cleaned = [
        (_normalize_path(path, wd), line, symbol)
        for path, line, symbol in candidates
        if not _is_noise(path)
    ]
    return _dedupe(cleaned)


__all__ = ["TraceFrame", "parse_traceback"]

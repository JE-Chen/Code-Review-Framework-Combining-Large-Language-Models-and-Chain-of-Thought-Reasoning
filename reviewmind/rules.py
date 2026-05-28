"""Per-repo rule packs.

A `rules-dir` is a directory containing markdown (`.md`) files describing
team-specific coding standards. Each file becomes one "rule" appended to
the RAG-retrieved rules in the prompt — these rules are *always-on* (not
filtered by similarity threshold) because the team has explicitly opted
in by checking the directory into the repo.

The reader is intentionally simple: one markdown file = one rule string.
If a single rule grows beyond a screen, the team should split it across
files rather than chunking automatically — that keeps the inputs auditable.
"""

from __future__ import annotations

import logging
from pathlib import Path

log = logging.getLogger(__name__)


def load_rules_dir(path: Path | None) -> list[str]:
    """Read every `*.md` file under `path` (recursively).

    Returns the file contents as strings, sorted by relative path for
    determinism. Returns `[]` if `path` is None or missing.
    """
    if path is None:
        return []
    base = Path(path)
    if not base.exists():
        log.warning("rules-dir %s does not exist", base)
        return []
    if not base.is_dir():
        log.warning("rules-dir %s is not a directory", base)
        return []

    rules: list[tuple[str, str]] = []
    for md in sorted(base.rglob("*.md")):
        try:
            text = md.read_text(encoding="utf-8").strip()
        except OSError as exc:
            log.warning("skipping %s: %s", md, exc)
            continue
        if text:
            rules.append((str(md.relative_to(base)), text))

    log.info("Loaded %d rule(s) from %s", len(rules), base)
    return [text for _path, text in rules]


__all__ = ["load_rules_dir"]

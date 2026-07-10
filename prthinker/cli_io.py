"""Shared write-to-file-or-stdout helper for the reporting CLIs."""

from __future__ import annotations

import sys
from pathlib import Path


def emit_text(text: str, out: Path | None) -> None:
    """Write ``text`` to ``out`` (creating parent dirs) or to stdout when None."""
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)

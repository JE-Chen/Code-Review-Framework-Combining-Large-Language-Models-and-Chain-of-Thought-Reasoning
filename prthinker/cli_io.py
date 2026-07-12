"""Shared write-to-file-or-stdout helper for the reporting CLIs."""

from __future__ import annotations

import sys
from pathlib import Path


def write_stdout(text: str) -> None:
    """Write ``text`` to stdout, tolerating a console that cannot encode it.

    A Windows ``cp950`` terminal raises ``UnicodeEncodeError`` on the emoji
    in the summary comment, which otherwise crashes ``review-file`` at the
    very end after the whole review has run. The normal path is unchanged;
    only on that error do we fall back to writing UTF-8 bytes to the raw
    buffer so output degrades instead of aborting.
    """
    try:
        sys.stdout.write(text)
    except UnicodeEncodeError:
        buffer = getattr(sys.stdout, "buffer", None)
        if buffer is None:
            encoding = getattr(sys.stdout, "encoding", "ascii") or "ascii"
            sys.stdout.write(text.encode(encoding, "replace").decode(encoding))
        else:
            buffer.write(text.encode("utf-8", "replace"))
            buffer.flush()


def emit_text(text: str, out: Path | None) -> None:
    """Write ``text`` to ``out`` (creating parent dirs) or to stdout when None."""
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    else:
        write_stdout(text)

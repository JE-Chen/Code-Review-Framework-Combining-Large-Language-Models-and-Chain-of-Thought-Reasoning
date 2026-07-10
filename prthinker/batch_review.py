"""Batched single-call review of multiple trivial files.

A PR heavy in docs / config files used to pay one inline-findings model
call per file even at trivial depth. This module folds a group of
trivial-tier files into ONE prompt: the model reviews them together and
returns a flat findings array tagged by path, which is split back into
per-file findings through the same validating parser a single-file
review uses. Only the adaptive step planner opts files into this path.
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

from prthinker.findings import JSON_ARRAY_RE, extract_lenient_json, parse_inline_findings
from prthinker.prompts.batch_findings import BATCH_FINDINGS_TEMPLATE

if TYPE_CHECKING:
    from prthinker.diff import FileDiff
    from prthinker.schemas import InlineFinding

log = logging.getLogger("prthinker.pipeline")

# One batch call covers at most this many files / this much diff text.
# Both caps bound the prompt so a batch never crowds out the generation
# budget; overflowing files simply start the next chunk.
MAX_BATCH_FILES = 6
MAX_BATCH_CHARS = 24_000


def chunk_batchable(fds: list["FileDiff"]) -> list[list["FileDiff"]]:
    """Split batch candidates into prompt-sized chunks, preserving order.

    A single file larger than ``MAX_BATCH_CHARS`` still gets its own
    one-file chunk — one call for it remains cheaper than the full chain.
    """
    chunks: list[list["FileDiff"]] = []
    current: list["FileDiff"] = []
    current_chars = 0
    for fd in fds:
        size = len(fd.raw)
        if current and (
            len(current) >= MAX_BATCH_FILES or current_chars + size > MAX_BATCH_CHARS
        ):
            chunks.append(current)
            current = []
            current_chars = 0
        current.append(fd)
        current_chars += size
    if current:
        chunks.append(current)
    return chunks


def build_batch_prompt(fds: list["FileDiff"], max_findings: int) -> str:
    """Render the batched-findings prompt for one chunk of files."""
    sections: list[str] = []
    for fd in fds:
        sections.append(f"## File: {fd.path}\n```diff\n{fd.raw}\n```")
    return BATCH_FINDINGS_TEMPLATE.format(
        max_findings=max_findings,
        files_block="\n\n".join(sections),
    )


def _group_items_by_path(items: list, by_path: dict[str, list[dict]]) -> None:
    """Route raw findings into ``by_path`` buckets, logging unknown paths."""
    dropped = 0
    for item in items:
        if not isinstance(item, dict):
            continue
        path = item.get("path")
        if path not in by_path:
            dropped += 1
            continue
        by_path[path].append(item)
    if dropped:
        log.warning("Batched findings: dropped %d finding(s) with unknown path", dropped)


def parse_batch_findings(
    raw: str,
    fds: list["FileDiff"],
) -> dict[str, list["InlineFinding"]]:
    """Split a batched findings payload into validated per-file findings.

    Items are grouped by their ``path`` tag and re-parsed through
    :func:`~prthinker.findings.parse_inline_findings`, so every clamp
    (allowed lines, severity, suggestion sanity) applies exactly as in a
    single-file review. Unknown paths are dropped and logged; a malformed
    payload degrades to "no findings anywhere" rather than failing files.
    """
    by_path: dict[str, list[dict]] = {fd.path: [] for fd in fds}
    parsed = extract_lenient_json(raw, pattern=JSON_ARRAY_RE)
    items = parsed.data if isinstance(parsed.data, list) else []
    if not items and parsed.data is None:
        log.warning("Batched findings payload did not parse; treating as empty")
    _group_items_by_path(items, by_path)
    return {
        fd.path: parse_inline_findings(
            json.dumps(by_path[fd.path], ensure_ascii=False),
            path=fd.path,
            allowed_lines=fd.commentable_lines(),
        )
        for fd in fds
    }


__all__ = [
    "MAX_BATCH_CHARS",
    "MAX_BATCH_FILES",
    "build_batch_prompt",
    "chunk_batchable",
    "parse_batch_findings",
]

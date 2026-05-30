"""Incremental per-file review persistence.

Writes one JSON per file as the per-file loop finishes it, plus a
final ``review.json`` once the whole sweep completes. The goal is
crash-resilience: if the run is cancelled mid-PR (idle-poll sweep,
manual cancel, GPU OOM, runner timeout) every file already reviewed
is on disk and readable.

Files are written atomically (`.tmp` + ``os.replace``), so a partial
file is never observable. The slug for a file path swaps directory
separators and disallowed characters for ``_`` so the layout works
on every supported OS.
"""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from prthinker.schemas import InlineFinding

if TYPE_CHECKING:
    from prthinker.pipeline import FileReviewResult, ReviewResult

log = logging.getLogger(__name__)

_SLUG_REPLACE_RE = re.compile(r"[^A-Za-z0-9._-]+")


def _slug_for_path(path: str) -> str:
    """Map a repo-relative path to a filesystem-safe slug.

    ``prthinker/cli.py`` → ``prthinker__cli.py``
    ``src/components/X.tsx`` → ``src__components__X.tsx``
    """
    cleaned = _SLUG_REPLACE_RE.sub("_", path.replace("/", "__").replace("\\", "__"))
    return cleaned or "_unnamed"


def _atomic_write_json(target: Path, payload: Any) -> None:
    """Write JSON to ``target`` atomically via a sibling ``.tmp`` file."""
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".tmp")
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, target)


def serialize_file_result(fr: "FileReviewResult") -> dict:
    """Pack a FileReviewResult into a JSON-safe dict.

    Includes every field on FileReviewResult — unlike the matrix-shard
    serializer which is scoped to aggregate-mergeable fields only.
    """
    return {
        "path": fr.path,
        "rag_docs": list(fr.rag_docs),
        "step_outputs": dict(fr.step_outputs),
        "inline_findings": [f.model_dump() for f in fr.inline_findings],
        "verdict": fr.verdict.model_dump() if fr.verdict else None,
        "is_binary": fr.is_binary,
        "is_deleted": fr.is_deleted,
        "counterfactuals": [cf.model_dump() for cf in fr.counterfactuals],
    }


def serialize_review_result(result: "ReviewResult") -> dict:
    """Pack a complete ReviewResult — every pydantic-shaped field included."""
    return {
        "code_diff": result.code_diff,
        "rag_docs": list(result.rag_docs),
        "step_outputs": dict(result.step_outputs),
        "inline_findings": [f.model_dump() for f in result.inline_findings],
        "per_file": [serialize_file_result(fr) for fr in result.per_file],
        "counterfactuals": [cf.model_dump() for cf in result.counterfactuals],
        "api_drift": [d.model_dump() for d in result.api_drift],
        "pr_classification": (
            result.pr_classification.model_dump()
            if result.pr_classification else None
        ),
        "dep_upgrades": [u.model_dump() for u in result.dep_upgrades],
        "persona_reviews": [p.model_dump() for p in result.persona_reviews],
        "persona_conflicts": [c.model_dump() for c in result.persona_conflicts],
        "diff_entropy": (
            result.diff_entropy.model_dump() if result.diff_entropy else None
        ),
    }


@dataclass(frozen=True)
class ReviewMeta:
    repo: str = ""
    pr_number: int = 0
    head_sha: str = ""
    started_at: str = ""

    def to_dict(self) -> dict:
        return {
            "repo": self.repo,
            "pr_number": self.pr_number,
            "head_sha": self.head_sha,
            "started_at": self.started_at,
        }


class IncrementalReviewWriter:
    """Persists per-file results as they complete plus a final aggregate.

    Layout::

        <out_dir>/
          meta.json             # repo / pr / sha / started_at
          files/
            <slug>.json         # one per file, written as the file finishes
          review.json           # final aggregate, written once the run ends

    All writes are atomic. If a run is cancelled before ``write_final``,
    the directory still contains every ``files/*.json`` written so far.
    """

    def __init__(self, out_dir: Path, meta: ReviewMeta | None = None) -> None:
        self._out_dir = Path(out_dir)
        self._files_dir = self._out_dir / "files"
        self._files_dir.mkdir(parents=True, exist_ok=True)
        if meta is not None:
            _atomic_write_json(self._out_dir / "meta.json", meta.to_dict())

    @property
    def out_dir(self) -> Path:
        return self._out_dir

    @property
    def files_dir(self) -> Path:
        return self._files_dir

    def write_file_result(self, file_result: "FileReviewResult") -> Path:
        """Atomically persist one file's review payload. Returns the target path."""
        target = self._files_dir / f"{_slug_for_path(file_result.path)}.json"
        try:
            _atomic_write_json(target, serialize_file_result(file_result))
        except OSError as exc:
            log.warning(
                "Incremental save for %s failed (ignored): %s",
                file_result.path, exc,
            )
            return target
        log.debug("Incremental save: wrote %s", target)
        return target

    def write_final(self, result: "ReviewResult") -> Path:
        """Atomically persist the final aggregate ReviewResult."""
        target = self._out_dir / "review.json"
        try:
            _atomic_write_json(target, serialize_review_result(result))
        except OSError as exc:
            log.warning("Incremental save for final review failed: %s", exc)
            return target
        log.info(
            "Incremental save: wrote final review.json (files=%d, findings=%d)",
            len(result.per_file), len(result.inline_findings),
        )
        return target


def load_file_result(path: Path) -> dict:
    """Read one ``files/*.json`` back into a plain dict.

    Returned dict mirrors :func:`serialize_file_result`; callers wanting
    a :class:`FileReviewResult` can hand it to
    :func:`prthinker.cli._deserialize_partial_review`-style code.
    """
    return json.loads(Path(path).read_text(encoding="utf-8"))


def list_completed_files(out_dir: Path) -> list[Path]:
    """List every ``files/*.json`` written so far, sorted by name."""
    files_dir = Path(out_dir) / "files"
    if not files_dir.is_dir():
        return []
    return sorted(p for p in files_dir.glob("*.json") if p.is_file())


__all__ = [
    "IncrementalReviewWriter",
    "InlineFinding",
    "ReviewMeta",
    "list_completed_files",
    "load_file_result",
    "serialize_file_result",
    "serialize_review_result",
]

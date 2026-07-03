"""Evaluation harness skeleton — runs cases through a backend, records raw output.

This is the *framework* for benchmarking a review backend: it drives a
list of prompts through the injected :class:`InferenceBackend` and
records the verbatim model output for each case. Per ``paper_rule.md``'s
no-fabrication rule, it deliberately emits **no scores, no metrics, and
no aggregate numbers** — scoring belongs to a separate evaluation paper
that has actually run the experiments. :class:`BenchmarkOutcome`
therefore carries the raw output only; there is no numeric score field.

Runner-safe: depends on stdlib + the injected backend only (no torch /
numpy / faiss / httpx / transformers).
"""

from __future__ import annotations

import json
import hashlib
import platform
import subprocess
import sys
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from prthinker.backends.base import InferenceBackend

_CASE_ID_KEY = "case_id"
_RAW_OUTPUT_KEY = "raw_output"

DEFAULT_MAX_NEW_TOKENS = 1024


@dataclass(frozen=True)
class BenchmarkCase:
    """A single benchmark case: an identifier and the prompt to run."""

    case_id: str
    prompt: str


@dataclass(frozen=True)
class BenchmarkOutcome:
    """Raw result for one case — verbatim backend output, never a score.

    There is intentionally no numeric / score / metric field here: per
    ``paper_rule.md`` this harness records what the model said and stops.
    """

    case_id: str
    raw_output: str

    def to_dict(self) -> dict[str, str]:
        """Return the JSONL-serialisable mapping for this outcome."""
        return {_CASE_ID_KEY: self.case_id, _RAW_OUTPUT_KEY: self.raw_output}

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "BenchmarkOutcome":
        """Reconstruct an outcome from a parsed JSONL row."""
        return cls(
            case_id=data[_CASE_ID_KEY],
            raw_output=data[_RAW_OUTPUT_KEY],
        )


def run_cases(
    backend: InferenceBackend,
    cases: Sequence[BenchmarkCase],
    *,
    max_new_tokens: int = DEFAULT_MAX_NEW_TOKENS,
) -> list[BenchmarkOutcome]:
    """Run each case's prompt through ``backend``, recording raw output in order.

    No scoring or aggregation is performed: the harness records what the
    backend returned for every case, preserving input order.
    """
    outcomes: list[BenchmarkOutcome] = []
    for case in cases:
        raw_output = backend.generate(case.prompt, max_new_tokens)
        outcomes.append(
            BenchmarkOutcome(case_id=case.case_id, raw_output=raw_output)
        )
    return outcomes


def write_outcomes(
    outcomes: Sequence[BenchmarkOutcome], path: str | Path
) -> None:
    """Write ``outcomes`` to ``path`` as one JSON object per line (JSONL)."""
    target = Path(path)
    with target.open("w", encoding="utf-8") as handle:
        for outcome in outcomes:
            handle.write(json.dumps(outcome.to_dict(), ensure_ascii=False))
            handle.write("\n")


def load_cases(path: str | Path) -> list[BenchmarkCase]:
    """Load canonical ``case_id``/``prompt`` JSONL produced by adapters."""
    cases: list[BenchmarkCase] = []
    with Path(path).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            try:
                cases.append(BenchmarkCase(row["case_id"], row["prompt"]))
            except (KeyError, TypeError) as exc:
                raise ValueError(
                    f"invalid benchmark row at line {line_number}"
                ) from exc
    return cases


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _git_commit() -> str | None:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


def write_run_bundle(
    cases_path: str | Path,
    outcomes: Sequence[BenchmarkOutcome],
    output_dir: str | Path,
    *,
    backend: str,
    model: str,
    seed: int | None = None,
    parameters: dict[str, object] | None = None,
) -> Path:
    """Write outcomes plus an immutable-input manifest for reproducibility."""
    source = Path(cases_path)
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    outcomes_path = target / "outcomes.jsonl"
    write_outcomes(outcomes, outcomes_path)
    manifest = {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "dataset": {"path": str(source), "sha256": _sha256(source)},
        "outcomes": {
            "path": outcomes_path.name,
            "sha256": _sha256(outcomes_path),
            "count": len(outcomes),
        },
        "backend": backend,
        "model": model,
        "seed": seed,
        "parameters": parameters or {},
        "git_commit": _git_commit(),
        "runtime": {
            "python": sys.version,
            "platform": platform.platform(),
        },
    }
    manifest_path = target / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest_path

"""Aggregate-command helpers for ``cli_commands`` (imported only by it).

Split out of ``prthinker.cli_commands`` to keep that module under the
per-file line cap. The partial-merge logic and the GitHub-side posting
helpers for ``review-pr --aggregate-from`` live here.
"""

from __future__ import annotations

import argparse
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

from prthinker.checks import evaluate_gate
from prthinker.cli_review import _deserialize_partial_review
from prthinker.pipeline import FileReviewResult, ReviewResult
from prthinker.schemas import InlineFinding

log = logging.getLogger("prthinker")


@dataclass
class _MergeAccumulator:
    """Mutable buckets the per-partial merge loop appends into."""

    per_file: list[FileReviewResult] = field(default_factory=list)
    step_outputs: dict[str, str] = field(default_factory=dict)
    rag_docs: list[str] = field(default_factory=list)
    rag_docs_seen: set[str] = field(default_factory=set)
    paths_seen: set[str] = field(default_factory=set)


def _load_partial_payload(jp: Path) -> dict | None:
    try:
        return json.loads(Path(jp).read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 — surface the offending file
        log.warning("Skipping %s — not valid JSON (%s)", jp, exc)
        return None


def _absorb_partial(partial: ReviewResult, acc: _MergeAccumulator) -> None:
    """Merge one deserialized partial into the running aggregate.

    Mutates ``acc`` in place. Dedupes per_file by path with last-
    write-wins, relying on the caller sorting prior-state partials
    BEFORE this run's shard partials so matrix output overrides prior.
    """
    acc.step_outputs.update(partial.step_outputs)
    for d in partial.rag_docs:
        if d not in acc.rag_docs_seen:
            acc.rag_docs_seen.add(d)
            acc.rag_docs.append(d)
    for fr in partial.per_file:
        if fr.path in acc.paths_seen:
            acc.per_file = [x for x in acc.per_file if x.path != fr.path]
        acc.paths_seen.add(fr.path)
        acc.per_file.append(fr)


def merge_partial_reviews(json_paths: list[Path]) -> ReviewResult:
    """Merge partial review JSONs into a single ReviewResult.

    per_file results are the single source of truth: the flat
    inline_findings list is derived from them AFTER merging, so a
    prior-run partial carried forward through the per-PR state cache
    (whose top-level inline_findings has been intentionally zeroed
    out, with the real data on per_file[i].inline_findings) still
    reaches submit_inline_review() and evaluate_gate(). This honours
    the project rule that a file's prior review result is never lost
    just because this run could not refresh it.
    """
    acc = _MergeAccumulator()
    for jp in sorted(json_paths):
        payload = _load_partial_payload(jp)
        if payload is None:
            continue
        _absorb_partial(_deserialize_partial_review(payload), acc)

    merged_findings: list[InlineFinding] = [
        f for fr in acc.per_file for f in fr.inline_findings
    ]
    return ReviewResult(
        code_diff="",  # the aggregate doesn't need the raw diff
        rag_docs=acc.rag_docs,
        step_outputs=acc.step_outputs,
        inline_findings=merged_findings,
        per_file=acc.per_file,
    )


def _validate_aggregate_args(args: argparse.Namespace) -> Path:
    """Validate aggregate CLI args and return the resolved input directory."""
    if not args.repo:
        raise SystemExit("--repo or $GITHUB_REPOSITORY / $CI_PROJECT_PATH is required")
    if not args.pr_number:
        raise SystemExit("--pr-number is required")
    if not args.github_token:
        raise SystemExit("--github-token / $GITHUB_TOKEN / $GITLAB_TOKEN is required")
    input_dir_raw = (getattr(args, "aggregate_from", "") or "").strip()
    if not input_dir_raw:
        raise SystemExit(
            "--aggregate-from or $PRTHINKER_AGGREGATE_FROM is required"
        )
    input_dir = Path(input_dir_raw)
    if not input_dir.is_dir():
        raise SystemExit(f"{input_dir} is not a directory")
    return input_dir


def _open_aggregate_gate(args: argparse.Namespace, adapter: object) -> object | None:
    """Fetch head SHA and open the check-run gate, or None when not gating."""
    if args.gate_on == "none" or args.dry_run:
        return None
    head_sha: str | None = None
    try:
        head_sha = adapter.fetch_head_sha()
    except Exception as exc:  # noqa: BLE001
        log.warning("Could not fetch head SHA (%s); skipping gate", exc)
    if head_sha is None:
        return None
    return adapter.open_gate(head_sha)


def _resolve_review_event(args: argparse.Namespace, merged: ReviewResult) -> str:
    """Aggregate per-file judge verdicts into a GitHub review event."""
    if not (args.judge and merged.per_file):
        return "COMMENT"
    from prthinker.judge import aggregate as judge_aggregate
    from prthinker.judge import to_github_event
    verdicts = [fr.verdict for fr in merged.per_file if fr.verdict is not None]
    if not verdicts:
        return "COMMENT"
    review_event = to_github_event(judge_aggregate(verdicts))
    log.info("Judge verdict aggregated → %s", review_event)
    return review_event


def _submit_aggregate_inline_review(
    args: argparse.Namespace,
    adapter: object,
    merged: ReviewResult,
    review_event: str,
) -> None:
    """Submit inline findings, swallowing 422-class errors so the gate still runs."""
    if not (args.inline_review and merged.inline_findings):
        return
    # Inline submission can still 422 on edge cases the diff-hunk
    # pre-filter misses (e.g. renamed files where the new path's
    # blob SHA differs from what `+++ b/<path>` records). Log and
    # continue — the summary comment is already posted above, and
    # the check-run gate below still needs to run to unblock merge.
    try:
        review_id = adapter.submit_inline_review(
            merged.inline_findings,
            summary_body="prthinker — inline findings",
            event=review_event,
        )
        log.info(
            "Posted inline review id=%s (event=%s)",
            review_id, review_event,
        )
    except Exception as exc:  # noqa: BLE001 — must not skip the gate below
        log.error(
            "Inline review submission failed (%s); summary comment "
            "and check run will still be posted",
            exc,
        )


def _close_aggregate_gate(
    args: argparse.Namespace,
    adapter: object,
    merged: ReviewResult,
    gate_handle: object | None,
) -> None:
    """Evaluate and close the check-run gate when one was opened."""
    if gate_handle is None:
        return
    gate_result = evaluate_gate(merged.inline_findings, gate_on=args.gate_on)
    adapter.close_gate(gate_handle, gate_result)
    log.info(
        "Gate conclusion=%s (errors=%d warnings=%d info=%d, floor=%s)",
        gate_result.conclusion,
        gate_result.error_count, gate_result.warning_count,
        gate_result.info_count, args.gate_on,
    )

"""Comment-assembly, artifact-emission, and review-publish helpers.

Split out of :mod:`prthinker.cli_review` to keep that module under the
file-length bar. These helpers build the summary-comment overview sections,
write optional report artifacts (SARIF / HTML / JUnit / ...), assemble the
report-link footer, and submit the inline review / close the merge gate.

Every helper here is best-effort and self-omitting where it produces an
orientation block, so a missing data source degrades the comment rather than
breaking the review. The module imports only leaf helpers (formatters, report
writers, KG access); it never imports :mod:`prthinker.cli_review`, so the
dependency edge runs one way (``cli_review`` -> ``cli_review_emit``).
"""

from __future__ import annotations

import argparse
import importlib.metadata
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

from prthinker.api_surface import compute_api_surface
from prthinker.calibration import CalibrationStore
from prthinker.change_map import change_map_edges, format_change_map_mermaid
from prthinker.checks import evaluate_gate
from prthinker.codequality import write_codequality
from prthinker.config import env_str
from prthinker.confidence import filter_by_confidence
from prthinker.csv_report import write_csv
from prthinker.diff import parse_unified_diff
from prthinker.finding_dedup import dedupe_findings
from prthinker.formatters import (
    first_finding_ref,
    format_digest,
    format_review_footer,
    format_reviewer_checklist,
)
from prthinker.gha_annotations import print_gha_annotations
from prthinker.github_api import findings_off_diff
from prthinker.html_report import write_report
from prthinker.ignore import filter_findings, load_ignore
from prthinker.impact_map import format_impact_note, impacted_files
from prthinker.inline_ignore import filter_inline_ignored
from prthinker.judge import aggregate, to_github_event
from prthinker.junit_report import write_junit
from prthinker.markdown_report import write_markdown
from prthinker.metrics import write_metrics
from prthinker.orientation import build_static_signal_sections
from prthinker.pipeline import ReviewResult
from prthinker.pr_labels import compute_labels
from prthinker.pr_overview import build_overview_text
from prthinker.repo_kg import KnowledgeGraphStore
from prthinker.report_formats import write_report_dir
from prthinker.review_delta import (
    compute_delta,
    format_delta,
    format_new_block,
    format_resolved_block,
    load_fingerprints,
    load_records,
    new_records,
    resolved_records,
    save_fingerprints,
)
from prthinker.review_order import format_review_order_note, suggested_order
from prthinker.risk_score import compute_risk_scores, format_risk_note
from prthinker.sarif import write_sarif
from prthinker.schemas import InlineFinding
from prthinker.sonar_report import write_sonar

log = logging.getLogger("prthinker")


def _resolve_review_event(args: argparse.Namespace, result: ReviewResult) -> str:
    """Map aggregated judge verdicts to a platform review event."""
    if not (args.judge and result.per_file):
        return "COMMENT"
    verdicts = [fr.verdict for fr in result.per_file if fr.verdict is not None]
    if not verdicts:
        return "COMMENT"
    event = to_github_event(aggregate(verdicts))
    log.info("Judge verdict aggregated → %s", event)
    return event


def _apply_inline_ignore(result: ReviewResult) -> None:
    """Drop inline-suppressed findings across the aggregate and per-file lists."""
    if not result.code_diff:
        return
    result.inline_findings = filter_inline_ignored(result.inline_findings, result.code_diff)
    for file_result in result.per_file:
        file_result.inline_findings = filter_inline_ignored(
            file_result.inline_findings, result.code_diff
        )


def _apply_ignore_spec(args: argparse.Namespace, result: ReviewResult) -> None:
    """Apply the ``.prthinkerignore`` spec across aggregate and per-file lists."""
    spec = load_ignore(getattr(args, "ignore_file", "") or ".prthinkerignore")
    if spec.is_empty:
        return
    result.inline_findings = filter_findings(result.inline_findings, spec)
    for file_result in result.per_file:
        file_result.inline_findings = filter_findings(file_result.inline_findings, spec)


_CALIBRATION_EPSILON = 1e-6
_DEFAULT_HALF_LIFE_DAYS = 90
_DEFAULT_MIN_SAMPLES = 10
_DEFAULT_BASE_THRESHOLD = 0.5


def _calibrated_min_confidence(args: argparse.Namespace) -> float:
    """Confidence floor from the calibration store, or 0.0 when unavailable."""
    calibration_path = (getattr(args, "calibration_store", "") or "").strip()
    if not calibration_path:
        return 0.0
    calibration = CalibrationStore(calibration_path).hierarchical(
        getattr(args, "repo", "") or "",
        getattr(args, "calibration_author", "") or "",
        getattr(args, "calibration_category", "") or "",
        half_life_days=float(
            getattr(args, "calibration_half_life_days", _DEFAULT_HALF_LIFE_DAYS)
        ),
    )
    samples = calibration.accepted + calibration.dismissed + _CALIBRATION_EPSILON
    if samples >= int(getattr(args, "calibration_min_samples", _DEFAULT_MIN_SAMPLES)):
        return calibration.threshold(_DEFAULT_BASE_THRESHOLD)
    return 0.0


def _resolve_min_confidence(args: argparse.Namespace) -> float:
    """Explicit ``--min-confidence``, else the calibrated confidence floor."""
    min_conf = float(getattr(args, "min_confidence", 0.0) or 0.0)
    if min_conf <= 0:
        return _calibrated_min_confidence(args)
    return min_conf


def _postprocess_findings(args: argparse.Namespace, result: ReviewResult) -> None:
    """Apply inline / file ignore suppression and de-duplication in place."""
    _apply_inline_ignore(result)
    _apply_ignore_spec(args, result)
    if getattr(args, "dedupe_findings", False):
        result.inline_findings = dedupe_findings(result.inline_findings)
    min_conf = _resolve_min_confidence(args)
    if min_conf > 0:
        result.inline_findings = filter_by_confidence(result.inline_findings, min_conf)


# Single-file artifact writers keyed by their CLI destination attribute.
# Each entry is (args-attribute, writer, human label) and every writer here
# accepts ``(result, out_path)`` where ``out_path`` may be a plain string.
_ARTIFACT_WRITERS = (
    ("sarif_out", write_sarif, "SARIF"),
    ("html_report", write_report, "HTML report"),
    ("codequality_out", write_codequality, "Code Quality report"),
    ("junit_out", write_junit, "JUnit report"),
    ("csv_out", write_csv, "CSV"),
    ("metrics_out", write_metrics, "metrics"),
    ("markdown_out", write_markdown, "Markdown report"),
    ("sonar_out", write_sonar, "Sonar report"),
)


def _emit_review_artifacts(args: argparse.Namespace, result: ReviewResult) -> None:
    """Write optional SARIF / HTML / Code Quality / JUnit artifacts."""
    for attr, writer, label in _ARTIFACT_WRITERS:
        out_path = getattr(args, attr, "") or ""
        if out_path:
            writer(result, Path(out_path))
            log.info("Wrote %s to %s", label, out_path)
    report_dir = getattr(args, "report_dir", "") or ""
    if report_dir:
        written = write_report_dir(result, report_dir)
        log.info("Wrote %d reports to %s", len(written), report_dir)
    if getattr(args, "gha_annotations", False):
        print_gha_annotations(result)


def _append_api_impact(body: str, result: ReviewResult) -> str:
    """Append a public-API semver-impact line to the summary comment."""
    report = compute_api_surface(parse_unified_diff(result.code_diff))
    log.info("api-surface impact=%s (+%d/-%d/~%d)", report.impact,
             len(report.added), len(report.removed), len(report.changed))
    return f"{body}\n\nPublic API impact: **{report.impact}**"


def _author_reply_note(adapter: object) -> str:
    """`💬 N author reply(ies)` since the last review, or empty (best-effort)."""
    try:
        replies = adapter.fetch_author_replies()
    except Exception as exc:  # noqa: BLE001 — dialogue note is best-effort
        log.warning("Could not fetch author replies (%s)", exc)
        return ""
    return f"💬 {len(replies)} author reply(ies)" if replies else ""


def _progress_blocks(
    previous: set[str], path: Path, result: ReviewResult
) -> str | None:
    """Render the 'new since last' + 'resolved since last' detail blocks."""
    findings = result.inline_findings
    new_block = format_new_block(new_records(previous, findings))
    resolved = resolved_records(load_records(path), findings)
    resolved_block = format_resolved_block(resolved)
    joined = "\n\n".join(b for b in (new_block, resolved_block) if b)
    return joined or None


def _review_progress(
    args: argparse.Namespace, adapter: object, result: ReviewResult
) -> tuple[str | None, str | None]:
    """Return (since-last-review line, progress-block) and persist the run.

    Both are None on the first run (no baseline) or when disabled; the
    finding set is still written so the next run has a baseline. The
    progress block bundles the new-since-last and resolved-since-last
    detail lists.
    """
    if not getattr(args, "review_delta", False) or args.dry_run:
        return None, None
    path = Path(
        getattr(args, "delta_state", "") or ".prthinker/pr-state/findings-fp.json"
    )
    previous = load_fingerprints(path)
    line: str | None = None
    progress_block: str | None = None
    if previous is not None:
        bits = [format_delta(compute_delta(previous, result.inline_findings))]
        note = _author_reply_note(adapter)
        if note:
            bits.append(note)
        line = " · ".join(bits)
        progress_block = _progress_blocks(previous, path, result)
    try:
        save_fingerprints(path, result.inline_findings)
    except OSError as exc:
        log.warning("Could not persist finding fingerprints (%s)", exc)
    return line, progress_block


def _join_overview(*sections: str | None) -> str | None:
    """Combine the top-of-comment context sections, dropping empties."""
    parts = [s for s in sections if s]
    return "\n\n".join(parts) if parts else None


def _artifact_link(args: argparse.Namespace, server: str, repo: str, run_id: str) -> str | None:
    """Workflow-artifacts link, or None when nothing was produced in CI."""
    artifacts = [
        name for name, flag in (("report.html", "html_report"), ("prthinker.sarif", "sarif_out"))
        if getattr(args, flag, "")
    ]
    if not (repo and run_id and artifacts):
        return None
    joined = ", ".join(artifacts)
    return f"[Workflow artifacts: {joined}]({server}/{repo}/actions/runs/{run_id})"


def _code_scanning_link(args: argparse.Namespace, server: str, repo: str) -> str | None:
    """Code-scanning link for the PR, or None when SARIF / context is absent."""
    pr_number = getattr(args, "pr_number", 0)
    if not (getattr(args, "sarif_out", "") and repo and pr_number):
        return None
    return f"[Code scanning]({server}/{repo}/security/code-scanning?query=pr%3A{pr_number})"


def _report_links_footer(args: argparse.Namespace) -> str | None:
    """A '**Reports**' footer linking to the run artifacts / code scanning.

    The HTML report and SARIF are uploaded as workflow artifacts (no stable
    per-file URL), so the artifact link points at the run page; SARIF also
    surfaces under code scanning. Returns None outside CI / when nothing
    was produced.
    """
    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com").rstrip("/")
    repo = os.environ.get("GITHUB_REPOSITORY") or getattr(args, "repo", "") or ""
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    candidates = (
        _artifact_link(args, server, repo, run_id),
        _code_scanning_link(args, server, repo),
    )
    links = [link for link in candidates if link]
    if not links:
        return None
    return "---\n\n**Reports:** " + " · ".join(links)


def _append_report_links(args: argparse.Namespace, pages: list[str]) -> None:
    """Append the reports footer to the last summary page, when applicable."""
    footer = _report_links_footer(args)
    if footer:
        pages[-1] = pages[-1].rstrip() + "\n\n" + footer + "\n"


_GATE_CONCLUSION_ICON: dict[str, str] = {
    "success": "✅", "failure": "❌", "neutral": "⚪",
}


# Severities (most-severe first) that trip each gate floor — used to point
# the gate line at the first finding that actually caused a failure.
_GATE_FLOOR_SEVERITIES: dict[str, tuple[str, ...]] = {
    "warning": ("error", "warning"),
    "error": ("error",),
}


def _gate_line(
    args: argparse.Namespace,
    result: ReviewResult,
    files_url: str | None = None,
) -> str | None:
    """A pass/fail gate line for the digest, or None when not gating."""
    gate_on = getattr(args, "gate_on", "none")
    if gate_on == "none":
        return None
    gate = evaluate_gate(result.inline_findings, gate_on=gate_on)
    icon = _GATE_CONCLUSION_ICON.get(gate.conclusion, "")
    line = (
        f"{icon} {gate.conclusion} (gate-on: {gate_on}; "
        f"{gate.error_count} error, {gate.warning_count} warning, "
        f"{gate.info_count} info)"
    )
    if gate.conclusion == "failure":
        blocker = first_finding_ref(
            result.inline_findings,
            _GATE_FLOOR_SEVERITIES.get(gate_on, ()),
            files_url,
        )
        if blocker:
            line += f" — first blocker: {blocker}"
    return line


def _prthinker_version() -> str:
    try:
        return importlib.metadata.version("prthinker")
    except importlib.metadata.PackageNotFoundError:
        return ""


def _append_review_footer(
    args: argparse.Namespace, result: ReviewResult, pages: list[str]
) -> None:
    """Append the metadata + legend footer to the last summary page."""
    generated = datetime.now(timezone.utc).isoformat(timespec="minutes")
    footer = format_review_footer(
        result,
        head_sha=os.environ.get("GITHUB_SHA", ""),
        backend=getattr(args, "backend", "") or "",
        model=getattr(args, "model_name", "") or "",
        version=_prthinker_version(),
        generated_at=generated,
    )
    pages[-1] = pages[-1].rstrip() + "\n\n" + footer


def _maybe_write_job_summary(body: str) -> None:
    """Append the summary to the Actions run page when ``$GITHUB_STEP_SUMMARY``
    is set, so it is visible from the Checks tab without opening the PR."""
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not path:
        return
    try:
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(body.rstrip() + "\n")
    except OSError as exc:  # noqa: BLE001 — job summary is best-effort
        log.warning("Could not write job summary (%s)", exc)


def _impact_note(args: argparse.Namespace, result: ReviewResult) -> str | None:
    """'Impacted areas' note from the repo KG, or None (best-effort)."""
    if not getattr(args, "impact_map", False):
        return None
    kg_path = Path(getattr(args, "kg_store", "") or ".prthinker/repo-kg.sqlite")
    if not kg_path.exists():
        return None
    try:
        imports = KnowledgeGraphStore(kg_path).all_imports(
            Path(getattr(args, "kg_workdir", "") or ".")
        )
        changed = [fr.path for fr in result.per_file]
        return format_impact_note(impacted_files(imports, changed)) or None
    except Exception as exc:  # noqa: BLE001 — impact map is best-effort
        log.warning("Could not build impact map (%s)", exc)
        return None


def _kg_imports(args: argparse.Namespace) -> list | None:
    """Import edges from the repo KG, or None when unavailable (best-effort)."""
    kg_path = Path(getattr(args, "kg_store", "") or ".prthinker/repo-kg.sqlite")
    if not kg_path.exists():
        return None
    try:
        return KnowledgeGraphStore(kg_path).all_imports(
            Path(getattr(args, "kg_workdir", "") or ".")
        )
    except Exception as exc:  # noqa: BLE001 — KG-derived sections are best-effort
        log.warning("Could not read repo KG (%s)", exc)
        return None


def _review_order_note(args: argparse.Namespace, result: ReviewResult) -> str:
    """'Suggested review order' note from the KG, or '' (best-effort)."""
    if not getattr(args, "review_order", False):
        return ""
    imports = _kg_imports(args)
    if imports is None:
        return ""
    changed = [fr.path for fr in result.per_file]
    return format_review_order_note(suggested_order(imports, changed))


def _change_map_note(args: argparse.Namespace, result: ReviewResult) -> str:
    """Inline Mermaid change-map from the KG, or '' (best-effort)."""
    if not getattr(args, "change_map", False):
        return ""
    imports = _kg_imports(args)
    if imports is None:
        return ""
    changed = [fr.path for fr in result.per_file]
    return format_change_map_mermaid(change_map_edges(imports, changed))


def _risk_note(args: argparse.Namespace, result: ReviewResult) -> str:
    """'High-risk files' note when --risk-weighted is on, or '' (best-effort)."""
    if not getattr(args, "risk_weighted", False):
        return ""
    workdir = Path(getattr(args, "risk_workdir", "") or ".")
    changed = [fr.path for fr in result.per_file]
    try:
        scores = compute_risk_scores(changed, workdir=workdir)
    except Exception as exc:  # noqa: BLE001 — risk note is best-effort
        log.warning("Could not compute risk scores (%s)", exc)
        return ""
    return format_risk_note(scores)


def _extra_sections(
    args: argparse.Namespace, result: ReviewResult, files_url: str | None
) -> tuple[str, ...]:
    """Pre-rendered orientation blocks placed below the digest.

    Each is best-effort and self-omitting (empty string when it has
    nothing to say); only the non-empty ones survive into the comment.
    """
    changed = [fr.path for fr in result.per_file]
    diff = result.code_diff or ""
    sections = (
        *build_static_signal_sections(diff, changed),
        _review_order_note(args, result),
        _risk_note(args, result),
        _change_map_note(args, result),
        format_reviewer_checklist(result, files_url),
    )
    return tuple(s for s in sections if s)


def _maybe_set_labels(
    args: argparse.Namespace, adapter: object, result: ReviewResult
) -> None:
    """Apply prthinker-managed PR labels when enabled (best-effort)."""
    if not getattr(args, "pr_labels", False) or args.dry_run:
        return
    try:
        adapter.set_labels(compute_labels(result))
    except Exception as exc:  # noqa: BLE001 — labels must not break the review
        log.warning("Could not set PR labels (%s)", exc)


def _maybe_update_pr_body(
    args: argparse.Namespace, adapter: object, result: ReviewResult
) -> None:
    """Upsert the at-a-glance digest into the PR description (best-effort)."""
    if not getattr(args, "pr_body_summary", False) or args.dry_run:
        return
    digest = format_digest(result, _pr_files_url(args))
    if not digest:
        return
    try:
        adapter.update_body_section(digest)
    except Exception as exc:  # noqa: BLE001 — body edit must not break review
        log.warning("Could not update PR body summary (%s)", exc)


def _pr_files_url(args: argparse.Namespace) -> str | None:
    """Base URL of the PR's Files-changed tab, for diff deep links.

    Honours ``PRTHINKER_PR_FILES_URL`` (set this for GitHub Enterprise);
    otherwise defaults to github.com for the GitHub platform and returns
    None elsewhere (so links are simply omitted).
    """
    override = (env_str("PRTHINKER_PR_FILES_URL", "") or "").strip()
    if override:
        return override
    if getattr(args, "platform", "github") != "github":
        return None
    repo = getattr(args, "repo", "")
    pr_number = getattr(args, "pr_number", 0)
    if not repo or not pr_number:
        return None
    return f"https://github.com/{repo}/pull/{pr_number}/files"


def _build_preliminary_overview(
    args: argparse.Namespace, adapter: object, result: ReviewResult
) -> str | None:
    """Build the model-free PR overview from commits + changed files, or None.

    Best-effort: a commit-fetch failure degrades to a files-only overview
    rather than breaking the review.
    """
    if not getattr(args, "pr_overview", False):
        return None
    try:
        messages = adapter.fetch_commit_messages()
    except Exception as exc:  # noqa: BLE001 — overview is best-effort
        log.warning("Could not fetch commit messages for overview (%s)", exc)
        messages = []
    paths = [fr.path for fr in result.per_file]
    return build_overview_text(messages, paths) or None


def _inline_post_breakdown(
    args: argparse.Namespace, result: ReviewResult
) -> "tuple[int | None, tuple[InlineFinding, ...]]":
    """Compute (posted-on-diff count, off-diff findings) for the summary.

    The summary reports how many findings actually land on a diff hunk
    (= will be posted as inline comments) versus the raw total, so it never
    claims findings outside the diff were posted. Computed only when inline
    review is enabled; otherwise nothing is posted inline and the breakdown
    would be misleading.
    """
    if not getattr(args, "inline_review", False):
        return None, ()
    # On-diff and off-diff findings partition the set exactly, so derive the
    # posted count from the off-diff list instead of re-parsing the diff a
    # second time through count_findings_on_diff.
    off_diff = tuple(findings_off_diff(result.inline_findings, result.code_diff))
    posted_count = len(result.inline_findings) - len(off_diff)
    return posted_count, off_diff


def _submit_inline_review(
    args: argparse.Namespace, adapter: object, result: ReviewResult
) -> None:
    """Submit the per-line inline review when enabled and findings exist."""
    if not (args.inline_review and result.inline_findings):
        return
    review_event = _resolve_review_event(args, result)
    review_id = adapter.submit_inline_review(
        result.inline_findings,
        summary_body="prthinker — inline findings",
        event=review_event,
    )
    log.info("Posted inline review id=%s (event=%s)", review_id, review_event)


def _close_review_gate(
    args: argparse.Namespace, adapter: object, result: ReviewResult, gate_handle: object | None
) -> None:
    """Evaluate and close the merge gate when one was opened."""
    if gate_handle is None:
        return
    gate_result = evaluate_gate(
        result.inline_findings, gate_on=args.gate_on,
        with_annotations=getattr(args, "check_annotations", False),
    )
    adapter.close_gate(gate_handle, gate_result)
    log.info(
        "Gate conclusion=%s (errors=%d warnings=%d info=%d, floor=%s)",
        gate_result.conclusion, gate_result.error_count,
        gate_result.warning_count, gate_result.info_count, args.gate_on,
    )

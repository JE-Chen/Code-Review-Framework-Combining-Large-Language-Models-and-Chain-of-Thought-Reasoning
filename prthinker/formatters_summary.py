"""At-a-glance summary, digest, footer, and checklist renderers.

This module holds the top-of-comment *digest* pieces — the reviewed /
skipped file tallies, the clean-comment confirmation, the severity roll-up
and "review at a glance" overview block, the review-effort heuristic, the
metadata footer + legend, the standalone digest, and the reviewer
checklist.

It is split out of :mod:`prthinker.formatters` to keep each module under
the project's file-length bar. The orchestration layer in
:mod:`prthinker.formatters` imports the names it needs from here and
re-exports the public-facing helpers so existing call sites and tests
continue to reach them through ``prthinker.formatters``.
"""

from __future__ import annotations

from prthinker.formatters_blocks import (
    _file_ref,
    _first_finding_line,
    _first_line,
    _format_legend,
    _loc_ref,
    _sort_files_by_severity,
)
from prthinker.pipeline import ReviewResult
from prthinker.review_rollups import (
    ReviewRollup,
    rollup_review,
    rollup_rows,
    severity_counts,
)
from prthinker.schemas import InlineFinding


def _total_inline_findings(result: ReviewResult) -> int:
    """Total inline findings, counted from per_file when present."""
    if result.per_file:
        return sum(len(fr.inline_findings) for fr in result.per_file)
    return len(result.inline_findings)


def _reviewed_file_count(result: ReviewResult) -> int:
    """Number of non-binary, non-deleted files actually reviewed."""
    return sum(
        1 for fr in result.per_file if not (fr.is_binary or fr.is_deleted)
    )


def _skipped_file_count(result: ReviewResult) -> int:
    """Number of binary / deleted files that were skipped, not reviewed."""
    return sum(1 for fr in result.per_file if fr.is_binary or fr.is_deleted)


def _format_clean_comment(
    result: ReviewResult, marker: str, preliminary: str | None = None
) -> str:
    """One-line confirmation for a PR that produced zero findings."""
    reviewed = _reviewed_file_count(result)
    scope = f" across {reviewed} reviewed file(s)" if reviewed else ""
    head = f"{marker}\n## CoT Code Review\n\n"
    overview = f"{preliminary}\n\n" if preliminary else ""
    return f"{head}{overview}✅ No findings{scope}.\n"


_STATUS_BY_SEVERITY: tuple[tuple[str, str], ...] = (
    ("error", "🔴 Changes requested"),
    ("warning", "🟡 Review suggested"),
    ("info", "🔵 Minor notes"),
)
_OVERVIEW_HOTSPOT_LIMIT = 5


def _severity_counts(result: ReviewResult) -> dict[str, int]:
    """Tally inline findings by severity across every reviewed file."""
    return severity_counts(
        [f for fr in result.per_file for f in fr.inline_findings]
    )


def _overall_status(counts: dict[str, int]) -> str:
    """Plain-language verdict derived from the worst severity present."""
    for severity, label in _STATUS_BY_SEVERITY:
        if counts.get(severity):
            return label
    return "✅ Looks good — no findings"


def _hotspots_line(result: ReviewResult, files_url: str | None = None) -> str:
    """Top files by severity then finding count — look here first."""
    ranked = _sort_files_by_severity(
        [fr for fr in result.per_file if fr.inline_findings]
    )[:_OVERVIEW_HOTSPOT_LIMIT]
    return " · ".join(
        f"{_file_ref(fr.path, files_url, _first_finding_line(fr))} "
        f"({len(fr.inline_findings)})"
        for fr in ranked
    )


# Review-effort heuristic: a flat base, a minute per reviewed file, and a
# severity-weighted minute budget per finding. Deliberately rough — the "~"
# in the rendered line signals it is an estimate, not a measurement.
_EFFORT_BASE_MIN = 2
_EFFORT_PER_FILE_MIN = 1
_EFFORT_SEVERITY_MIN: dict[str, int] = {"error": 5, "warning": 3, "info": 1}


def _effort_estimate_minutes(result: ReviewResult) -> int:
    """Rough review-time estimate from file count and finding severity."""
    minutes = _EFFORT_BASE_MIN + _reviewed_file_count(result) * _EFFORT_PER_FILE_MIN
    for fr in result.per_file:
        for finding in fr.inline_findings:
            minutes += _EFFORT_SEVERITY_MIN.get(finding.severity, 1)
    return minutes


def _suggestions_line(rollup: ReviewRollup) -> str | None:
    """The suggestion-aggregate digest line, or ``None`` when empty."""
    if not rollup.suggestions:
        return None
    extra = f" · {rollup.verified_pass} sandbox-verified" if rollup.verified_pass else ""
    return f"- **Suggestions:** {rollup.suggestions} one-click fix(es){extra}"


def _audit_signals_line(rollup: ReviewRollup) -> str | None:
    """The audit-signals digest line, or ``None`` when there are none."""
    if not (rollup.evidence_backed or rollup.provenance_backed or rollup.rag_cited):
        return None
    return (
        "- **Audit signals:** "
        f"{rollup.evidence_backed} evidence-confirmed · "
        f"{rollup.provenance_backed} provenance-backed · "
        f"{rollup.rag_cited} RAG-cited"
    )


def _overview_extra_lines(
    result: ReviewResult,
    with_findings: int,
    rollup: ReviewRollup | None = None,
) -> list[str]:
    """Suggestion-aggregate and review-effort digest lines."""
    rollup = rollup if rollup is not None else rollup_review(result)
    lines = [
        line
        for line in (_suggestions_line(rollup), _audit_signals_line(rollup))
        if line is not None
    ]
    if rollup.verification and any(rollup.verification.values()):
        # Same wording as every other renderer — formatted from the shared
        # rollup rows so the digest can never drift from the reports.
        lines.append(f"- **Verification:** {dict(rollup_rows(rollup))['Verification']}")
    attention = f" · {with_findings} file(s) need attention" if with_findings else ""
    lines.append(
        f"- **Review effort:** ~{_effort_estimate_minutes(result)} min{attention}"
    )
    return lines


def _format_overview_block(
    result: ReviewResult,
    files_url: str | None = None,
    delta: str | None = None,
    gate: str | None = None,
    filtered: str | None = None,
    rollup: ReviewRollup | None = None,
) -> list[str]:
    """A compact, scannable digest pinned to the top of the summary.

    Lives in the upserted part-1 comment, so it is rewritten in place on
    every re-review and always reflects the latest run.
    """
    counts = _severity_counts(result)
    total = sum(counts.values())
    reviewed = _reviewed_file_count(result)
    with_findings = sum(1 for fr in result.per_file if fr.inline_findings)
    lines = [
        "### 🔎 Review at a glance",
        "",
        f"- **Status:** {_overall_status(counts)}",
    ]
    if gate:
        lines.append(f"- **Gate:** {gate}")
    lines += [
        f"- **Findings:** 🔴 {counts['error']} error · "
        f"🟡 {counts['warning']} warning · 🔵 {counts['info']} info "
        f"({total} total)",
        f"- **Files:** {reviewed} reviewed · {with_findings} with findings · "
        f"{reviewed - with_findings} clean",
    ]
    if filtered:
        lines.append(f"- **Filtered from view:** {filtered}")
    lines += _overview_extra_lines(result, with_findings, rollup)
    if delta:
        lines.append(f"- **Since last review:** {delta}")
    hotspots = _hotspots_line(result, files_url)
    if hotspots:
        lines.append(f"- **Hotspots:** {hotspots}")
    lines += ["", "---", ""]
    return lines


def format_review_footer(
    result: ReviewResult,
    *,
    head_sha: str = "",
    backend: str = "",
    model: str = "",
    version: str = "",
    generated_at: str = "",
) -> str:
    """Render the metadata footer + legend appended to the last page.

    Surfaces the review's context — commit, backend/model, time, file
    coverage, tool version — so a reader knows exactly what produced it.
    """
    skipped = _skipped_file_count(result)
    reviewed = _reviewed_file_count(result)
    bits: list[str] = []
    if head_sha:
        bits.append(f"commit `{head_sha[:8]}`")
    if backend or model:
        bits.append(f"via {backend or 'backend'} `{model}`".rstrip(" `"))
    bits.append(f"{reviewed} reviewed / {skipped} skipped")
    if version:
        bits.append(f"prthinker {version}")
    if generated_at:
        bits.append(generated_at)
    meta = "_Review metadata: " + " · ".join(bits) + "._"
    return "\n".join(["---", "", meta, "", *_format_legend()]).rstrip() + "\n"


def format_digest(
    result: ReviewResult,
    files_url: str | None = None,
    rollup: ReviewRollup | None = None,
) -> str:
    """The standalone at-a-glance digest (status / counts / hotspots).

    Reused for the compact PR-description section so the verdict shows at
    the top of the PR, not only in the comments. ``rollup`` lets a caller
    that already computed the audit rollup pass it in.
    """
    return "\n".join(
        _format_overview_block(result, files_url, rollup=rollup)
    ).strip()


_CHECKLIST_LIMIT = 12
_CHECKLIST_COMMENT_CAP = 80


def _checklist_item_for_finding(
    finding: InlineFinding, files_url: str | None
) -> str | None:
    """A manual-verification item for a finding that needs human follow-up.

    An error whose suggestion is not sandbox-verified still needs a human
    to confirm the fix; a low-reproducibility finding needs a second look.
    Everything else is left off the checklist to keep it short.
    """
    loc = _loc_ref(finding.path, finding.line, files_url)
    head = _first_line(finding.comment, _CHECKLIST_COMMENT_CAP)
    verified = (
        finding.verification is not None
        and finding.verification.status == "pass"
    )
    if finding.severity == "error" and not verified:
        return f"Verify the fix for {loc} — {head}"
    if finding.reproducibility == "low":
        return f"Re-confirm (low reproducibility) {loc} — {head}"
    return None


def format_reviewer_checklist(
    result: ReviewResult, files_url: str | None = None
) -> str:
    """A collapsible 'things to verify by hand' checklist, or ``""``.

    Built from the findings that a one-click suggestion cannot close on
    its own — unverified error fixes, low-reproducibility findings, and
    cross-language API drift — so the reviewer has an explicit gate list
    instead of re-deriving it from the full report.
    """
    items: list[str] = []
    for fr in result.per_file:
        for finding in fr.inline_findings:
            item = _checklist_item_for_finding(finding, files_url)
            if item:
                items.append(item)
    for drift in result.api_drift:
        items.append(
            f"Confirm cross-language contract `{drift.backend_path}` ↔ "
            f"`{drift.frontend_path}`"
        )
    if not items:
        return ""
    shown = items[:_CHECKLIST_LIMIT]
    rows = [f"- [ ] {item}" for item in shown]
    extra = len(items) - len(shown)
    if extra > 0:
        rows.append(f"- [ ] … and {extra} more item(s)")
    return "\n".join([
        f"<details><summary>✅ Reviewer checklist ({len(items)} item(s))"
        "</summary>",
        "", *rows, "", "</details>",
    ])

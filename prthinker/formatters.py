"""Markdown formatting for the consolidated PR comment.

Two layouts:

* single-pass result: top-level total summary + collapsible per-step blocks.
* per-file result: one collapsible block per file, each containing that
  file's total summary and a count of inline findings.

A sentinel marker is prepended so the comment can be upserted in place
across repeated workflow runs.

The leaf block renderers and shared presentation primitives live in
:mod:`prthinker.formatters_blocks`; the public-facing private helpers are
re-exported here so existing call sites and tests keep reaching them
through ``prthinker.formatters``.
"""

from __future__ import annotations

import dataclasses

from prthinker.change_stats import compute_change_stats
from prthinker.diff import new_side_content
from prthinker.formatters_blocks import (
    _SEVERITY_ICON,
    _SEVERITY_ICON_BY_NAME,
    _SEVERITY_RANK,
    _file_ref,
    _file_status_icon,
    _first_finding_line,
    _first_line,
    _format_api_drift_block,
    _format_dep_upgrade_block,
    _format_diff_entropy_block,
    _format_file_block,
    _format_legend,
    _format_persona_conflicts_block,
    _format_step_detail,
    _loc_ref,
    _sort_files_by_severity,
    _step_title,
)
# Not called in this module — re-exported on its own statement (so the
# suppressions sit on the reported line) because the test-suite reaches it
# via ``prthinker.formatters._format_provenance_block``.
from prthinker.formatters_blocks import _format_provenance_block  # noqa: F401  # pylint: disable=unused-import
from prthinker.pipeline import FileReviewResult, ReviewResult
from prthinker.schemas import InlineFinding

# Re-export the public-facing private block helpers so existing call sites
# and tests keep reaching them through ``prthinker.formatters``.
__all__ = [
    "CommentOptions",
    "first_finding_ref",
    "format_digest",
    "format_pr_comment",
    "format_pr_comment_pages",
    "format_review_footer",
    "format_reviewer_checklist",
]

# Category presentation for the optional "By category" index. Order here is
# the display order (most reviewer-critical buckets first).
_CATEGORY_ICON: tuple[tuple[str, str], ...] = (
    ("security", "🛡️"),
    ("correctness", "🎯"),
    ("performance", "⚡"),
    ("design", "📐"),
    ("test", "🧪"),
    ("docs", "📝"),
    ("style", "🎨"),
    ("other", "🔖"),
)


@dataclasses.dataclass(frozen=True)
class CommentOptions:
    """Optional rendering / display knobs for the consolidated PR comment.

    Grouping the optional parameters keeps :func:`format_pr_comment` and
    :func:`format_pr_comment_pages` within the project's parameter-count
    bar. ``result`` and ``marker`` remain explicit positionals; everything
    that tunes *how* the comment is rendered (or filtered) lives here.
    """

    #: Inline findings that land on a diff hunk, or ``None`` when no inline
    #: submission happens (local CLI / MCP / dry-run).
    posted_count: int | None = None
    #: List only files with findings; collapse clean ones into a count.
    findings_only: bool = False
    #: Drop ``info``-severity findings from the rendered summary (display
    #: only — the inline review and gate still see them).
    hide_info: bool = False
    #: Pre-rendered, model-free "what this PR does" overview.
    preliminary: str | None = None
    #: Base Files-changed URL for diff deep links.
    files_url: str | None = None
    #: "Since last review" summary line, when available.
    delta: str | None = None
    #: Drop findings whose confidence is below this floor (display only).
    min_confidence: float = 0.0
    #: Render findings as a compact flat table instead of blocks.
    table: bool = False
    #: Gate verdict line, when a gate ran.
    gate: str | None = None
    #: Findings outside the diff hunks (not posted inline).
    off_diff_findings: tuple[InlineFinding, ...] = ()
    #: Caller-supplied pre-rendered markdown blocks.
    extra_sections: tuple[str, ...] = ()
    #: Pre-computed "filtered from view" note; derived when ``None``.
    filtered: str | None = None


@dataclasses.dataclass(frozen=True)
class _RenderOpts:
    """Bundled per-file render options (keeps helper signatures small)."""

    posted_count: int | None = None
    findings_only: bool = False
    preliminary: str | None = None
    files_url: str | None = None
    delta: str | None = None
    table: bool = False
    gate: str | None = None
    off_diff: tuple[InlineFinding, ...] = ()
    extra_sections: tuple[str, ...] = ()
    filtered: str | None = None


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
    counts = {"error": 0, "warning": 0, "info": 0}
    for fr in result.per_file:
        for finding in fr.inline_findings:
            key = finding.severity if finding.severity in counts else "info"
            counts[key] += 1
    return counts


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


_MUST_FIX_LIMIT = 5
_SNIPPET_CAP = 100


def _html_escape(text: str) -> str:
    """Minimal HTML escape so a quoted source line renders verbatim."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _finding_snippet(
    content_map: dict[str, dict[int, str]], path: str, line: int
) -> str:
    """An inline ``↳ <code>…</code>`` quote of the offending source line.

    Returns ``""`` when the line content is unknown (the finding is off
    the diff hunks) or blank. HTML ``<code>`` is used rather than a
    markdown fence so any source character renders without escaping the
    list markup.
    """
    raw = (content_map.get(path) or {}).get(line)
    if not raw or not raw.strip():
        return ""
    snippet = raw.strip()
    if len(snippet) > _SNIPPET_CAP:
        snippet = snippet[: _SNIPPET_CAP - 1] + "…"
    return f"<br>↳ <code>{_html_escape(snippet)}</code>"


def _format_must_fix_block(
    result: ReviewResult, files_url: str | None = None
) -> list[str]:
    """Un-collapsed list of error-severity findings, pinned above all else."""
    errors = [
        f for fr in result.per_file for f in fr.inline_findings
        if f.severity == "error"
    ]
    if not errors:
        return []
    content_map = new_side_content(result.code_diff)
    lines = ["### 🚨 Must fix", ""]
    for finding in errors[:_MUST_FIX_LIMIT]:
        ref = _loc_ref(finding.path, finding.line, files_url)
        snippet = _finding_snippet(content_map, finding.path, finding.line)
        lines.append(f"- 🔴 {ref} — {_first_line(finding.comment)}{snippet}")
    extra = len(errors) - _MUST_FIX_LIMIT
    if extra > 0:
        lines.append(f"- … and {extra} more error(s)")
    lines += ["", "---", ""]
    return lines


# Review-effort heuristic: a flat base, a minute per reviewed file, and a
# severity-weighted minute budget per finding. Deliberately rough — the "~"
# in the rendered line signals it is an estimate, not a measurement.
_EFFORT_BASE_MIN = 2
_EFFORT_PER_FILE_MIN = 1
_EFFORT_SEVERITY_MIN: dict[str, int] = {"error": 5, "warning": 3, "info": 1}


def _suggestion_counts(result: ReviewResult) -> tuple[int, int]:
    """(one-click suggestions, sandbox-verified) across every finding."""
    suggestions = 0
    verified = 0
    for fr in result.per_file:
        for finding in fr.inline_findings:
            if finding.suggestion:
                suggestions += 1
            verification = finding.verification
            if verification is not None and verification.status == "pass":
                verified += 1
    return suggestions, verified


def _effort_estimate_minutes(result: ReviewResult) -> int:
    """Rough review-time estimate from file count and finding severity."""
    minutes = _EFFORT_BASE_MIN + _reviewed_file_count(result) * _EFFORT_PER_FILE_MIN
    for fr in result.per_file:
        for finding in fr.inline_findings:
            minutes += _EFFORT_SEVERITY_MIN.get(finding.severity, 1)
    return minutes


def _overview_extra_lines(result: ReviewResult, with_findings: int) -> list[str]:
    """Suggestion-aggregate and review-effort digest lines."""
    lines: list[str] = []
    suggestions, verified = _suggestion_counts(result)
    if suggestions:
        extra = f" · {verified} sandbox-verified" if verified else ""
        lines.append(f"- **Suggestions:** {suggestions} one-click fix(es){extra}")
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
    lines += _overview_extra_lines(result, with_findings)
    if delta:
        lines.append(f"- **Since last review:** {delta}")
    hotspots = _hotspots_line(result, files_url)
    if hotspots:
        lines.append(f"- **Hotspots:** {hotspots}")
    lines += ["", "---", ""]
    return lines


def _without_info_findings(result: ReviewResult) -> ReviewResult:
    """A display copy with every ``info``-severity finding stripped.

    Display-only: the original result (and the flat ``inline_findings``
    the CLI submits to the diff and feeds to the gate) is untouched.
    """
    per_file = [
        dataclasses.replace(
            fr,
            inline_findings=[f for f in fr.inline_findings if f.severity != "info"],
        )
        for fr in result.per_file
    ]
    inline = [f for f in result.inline_findings if f.severity != "info"]
    return dataclasses.replace(result, per_file=per_file, inline_findings=inline)


def _confident_enough(finding: InlineFinding, min_confidence: float) -> bool:
    """Keep a finding unless its model confidence is known and below floor."""
    conf = finding.provenance.confidence if finding.provenance else None
    return conf is None or conf >= min_confidence


def _without_low_confidence(
    result: ReviewResult, min_confidence: float
) -> ReviewResult:
    """Display copy dropping findings whose confidence is below the floor.

    Findings without a confidence score are kept (drop nothing on unknown).
    Display-only: the submitted/gated findings are untouched.
    """
    per_file = [
        dataclasses.replace(
            fr,
            inline_findings=[
                f for f in fr.inline_findings
                if _confident_enough(f, min_confidence)
            ],
        )
        for fr in result.per_file
    ]
    inline = [
        f for f in result.inline_findings
        if _confident_enough(f, min_confidence)
    ]
    return dataclasses.replace(result, per_file=per_file, inline_findings=inline)


def _count_hidden(
    result: ReviewResult, hide_info: bool, min_confidence: float
) -> tuple[int, int]:
    """Tally (info_hidden, low_confidence_hidden) across all per-file findings."""
    info_hidden = 0
    low_conf_hidden = 0
    for fr in result.per_file:
        for finding in fr.inline_findings:
            if hide_info and finding.severity == "info":
                info_hidden += 1
            elif min_confidence > 0 and not _confident_enough(finding, min_confidence):
                low_conf_hidden += 1
    return info_hidden, low_conf_hidden


def _filtered_note(
    result: ReviewResult, hide_info: bool, min_confidence: float
) -> str | None:
    """How many findings the display filters drop, counted on the original.

    ``hide_info`` and ``min_confidence`` mutate the *display* copy
    (including the digest counts), so without this note a reader sees
    e.g. ``🔵 0 info`` and wrongly concludes there were none. Surfacing the
    hidden tallies keeps the summary honest (the project's no-silent-caps
    rule). A finding hidden as ``info`` is not also counted as low-confidence.
    """
    info_hidden, low_conf_hidden = _count_hidden(result, hide_info, min_confidence)
    bits: list[str] = []
    if info_hidden:
        bits.append(f"{info_hidden} info")
    if low_conf_hidden:
        bits.append(f"{low_conf_hidden} low-confidence")
    return " · ".join(bits) + " hidden" if bits else None


def _apply_display_filters(
    result: ReviewResult, options: CommentOptions
) -> tuple[ReviewResult, str | None]:
    """Apply the info / confidence display filters and compute the note.

    Returns the (possibly filtered) display copy and the "filtered from
    view" note, defaulting the note to the derived tally when the caller
    did not pre-supply one.
    """
    filtered = options.filtered
    if filtered is None:
        filtered = _filtered_note(result, options.hide_info, options.min_confidence)
    if options.hide_info:
        result = _without_info_findings(result)
    if options.min_confidence > 0:
        result = _without_low_confidence(result, options.min_confidence)
    return result, filtered


def _render_opts_from(options: CommentOptions, filtered: str | None) -> _RenderOpts:
    """Build the per-file ``_RenderOpts`` from public ``CommentOptions``."""
    return _RenderOpts(
        posted_count=options.posted_count, findings_only=options.findings_only,
        preliminary=options.preliminary, files_url=options.files_url,
        delta=options.delta, table=options.table, gate=options.gate,
        off_diff=options.off_diff_findings, extra_sections=options.extra_sections,
        filtered=filtered,
    )


def format_pr_comment(
    result: ReviewResult,
    marker: str,
    options: CommentOptions | None = None,
) -> str:
    """Render the consolidated PR comment.

    Args:
        result: The completed review to render.
        marker: Sentinel marker prepended for in-place upsert.
        options: Optional rendering / display knobs; see
            :class:`CommentOptions`. Defaults to a no-op options object.

    Returns:
        The rendered markdown comment body.
    """
    options = options or CommentOptions()
    result, filtered = _apply_display_filters(result, options)
    if options.findings_only and _total_inline_findings(result) == 0:
        return _format_clean_comment(result, marker, options.preliminary)
    if result.per_file:
        return _format_per_file(result, marker, _render_opts_from(options, filtered))
    return _format_single(result, marker)


_SINGLE_RESERVED_STEPS: frozenset[str] = frozenset({"total_summary", "inline_findings"})


def _format_single_total(result: ReviewResult) -> list[str]:
    """Render the top-level total-summary lead for a single-pass review."""
    total = result.total_summary
    if total:
        return ["### Total Summary", "", total.strip(), ""]
    return ["_No total summary produced._", ""]


def _format_single_steps(result: ReviewResult) -> list[str]:
    """Render the collapsible per-step detail blocks for a single-pass review."""
    detail_steps = [
        name for name in result.step_outputs
        if name not in _SINGLE_RESERVED_STEPS
    ]
    if not detail_steps:
        return []
    parts: list[str] = ["---", "", "### Per-step Details", ""]
    for name in detail_steps:
        parts += _format_step_detail(
            _step_title(name), result.step_outputs[name].strip()
        )
    return parts


def _format_single_footer(result: ReviewResult) -> list[str]:
    """Render the RAG / inline-finding footer line for a single-pass review."""
    footer_bits: list[str] = []
    if result.rag_docs:
        footer_bits.append(f"RAG rules applied: {len(result.rag_docs)}")
    if result.inline_findings:
        footer_bits.append(f"Inline findings: {len(result.inline_findings)}")
    if not footer_bits:
        return []
    return ["---", "", "_" + " · ".join(footer_bits) + "_"]


def _format_single(result: ReviewResult, marker: str) -> str:
    parts: list[str] = [marker, "## CoT Code Review", ""]
    parts += _format_single_total(result)
    parts += _format_single_steps(result)
    parts += _format_single_footer(result)
    return "\n".join(parts).rstrip() + "\n"


def _per_file_header(result: ReviewResult) -> str:
    """Build the reviewed / skipped file-count header line."""
    skipped = [f for f in result.per_file if f.is_binary or f.is_deleted]
    reviewed_n = len(result.per_file) - len(skipped)
    header = f"Reviewed **{reviewed_n}** file(s)."
    if skipped:
        header += f" Skipped **{len(skipped)}** (binary / deleted)."
    return header


def _format_findings_summary(total: int, posted: int | None) -> list[str]:
    """Render the inline-findings counts as one unified bullet list.

    ``posted`` is how many findings fall on a diff hunk (and are therefore
    actually posted as inline comments). When it is ``None`` the count is
    unknown (no inline submission in this context) and only the total is
    listed.
    """
    if total <= 0:
        return []
    bullets = [f"- Found **{total}** inline finding(s)"]
    if posted is not None:
        bullets.append(f"- **{posted}** posted to the diff")
        outside = total - posted
        if outside > 0:
            bullets.append(f"- **{outside}** outside the diff hunks (not posted)")
    return ["**Inline findings**", "", *bullets, ""]


def _format_per_file_intro(
    result: ReviewResult, posted_count: int | None = None
) -> list[str]:
    """Render the classification, finding count, and overall summary lead."""
    parts: list[str] = []
    if result.pr_classification is not None:
        cls = result.pr_classification
        parts.append(
            f"PR classified as **{cls.pr_type}** — {cls.reason or '(no reason given)'}"
        )
        parts.append("")

    total_findings = sum(len(f.inline_findings) for f in result.per_file)
    parts += _format_findings_summary(total_findings, posted_count)

    overall = result.total_summary
    if overall:
        parts += ["### Overall Summary", "", overall.strip(), "", "---", ""]
    return parts


def _format_per_file_sections(result: ReviewResult) -> list[str]:
    """Render the optional cross-file analysis sections, in order."""
    parts: list[str] = []
    if result.diff_entropy is not None:
        parts += _format_diff_entropy_block(result.diff_entropy)
    if result.persona_conflicts:
        parts += _format_persona_conflicts_block(result.persona_conflicts)
    if result.dep_upgrades:
        parts += _format_dep_upgrade_block(result.dep_upgrades)
    if result.api_drift:
        parts += _format_api_drift_block(result.api_drift)
    return parts


def _files_to_render(
    per_file: list[FileReviewResult], findings_only: bool
) -> list[FileReviewResult]:
    """File blocks to render — filtered (findings-only) then severity-sorted."""
    files = per_file
    if findings_only:
        files = [fr for fr in per_file if fr.inline_findings]
    return _sort_files_by_severity(files)


def _hidden_clean_note(result: ReviewResult, findings_only: bool) -> list[str]:
    """A one-line note accounting for clean files omitted under findings-only."""
    if not findings_only:
        return []
    hidden = sum(1 for fr in result.per_file if not fr.inline_findings)
    if not hidden:
        return []
    return [f"_{hidden} file(s) reviewed with no findings — hidden._", ""]


def _files_with_severity(result: ReviewResult, severity: str) -> list[FileReviewResult]:
    """Files whose worst displayed severity equals ``severity``."""
    out = []
    for fr in result.per_file:
        if not fr.inline_findings:
            continue
        if _file_status_icon(fr.inline_findings) == _SEVERITY_ICON_BY_NAME[severity]:
            out.append(fr)
    return out


def _format_severity_groups(
    result: ReviewResult, files_url: str | None = None
) -> list[str]:
    """Collapsible 'By severity' index grouping files by worst severity."""
    rows: list[str] = []
    for severity, icon in _SEVERITY_ICON:
        files = _files_with_severity(result, severity)
        if not files:
            continue
        refs = " · ".join(
            _file_ref(fr.path, files_url, _first_finding_line(fr)) for fr in files
        )
        rows.append(f"- {icon} **{severity}** ({len(files)} file(s)): {refs}")
    if not rows:
        return []
    return [
        f"<details><summary>By severity ({len(rows)} group(s))</summary>",
        "", *rows, "", "</details>", "",
    ]


_CATEGORY_REF_LIMIT = 8


def _findings_by_category(
    result: ReviewResult,
) -> dict[str, list[InlineFinding]]:
    """Group every categorised finding by its category bucket."""
    groups: dict[str, list[InlineFinding]] = {}
    for fr in result.per_file:
        for finding in fr.inline_findings:
            if finding.category:
                groups.setdefault(finding.category, []).append(finding)
    return groups


def _category_row(
    icon: str, category: str, items: list[InlineFinding], files_url: str | None
) -> str:
    """One '- icon **category** (n): refs' line for the category index."""
    shown = items[:_CATEGORY_REF_LIMIT]
    refs = " · ".join(_loc_ref(f.path, f.line, files_url) for f in shown)
    more = len(items) - len(shown)
    suffix = f" · +{more} more" if more > 0 else ""
    return f"- {icon} **{category}** ({len(items)}): {refs}{suffix}"


def _format_category_groups(
    result: ReviewResult, files_url: str | None = None
) -> list[str]:
    """Collapsible 'By category' index, omitted when nothing is categorised."""
    groups = _findings_by_category(result)
    rows = [
        _category_row(icon, category, groups[category], files_url)
        for category, icon in _CATEGORY_ICON
        if groups.get(category)
    ]
    if not rows:
        return []
    return [
        f"<details><summary>By category ({len(rows)} group(s))</summary>",
        "", *rows, "", "</details>", "",
    ]


_TOP_FINDINGS_LIMIT = 10
_TOP_FINDINGS_MIN = 4


def _finding_confidence(finding: InlineFinding) -> float:
    """Self-rated confidence in ``[0, 1]``, or ``-1`` when not provided."""
    prov = finding.provenance
    if prov is not None and prov.confidence is not None:
        return prov.confidence
    return -1.0


def _format_top_findings(
    result: ReviewResult, files_url: str | None = None
) -> list[str]:
    """A single cross-file queue of findings ranked by severity then confidence.

    Complements the errors-only **Must fix** list and the file-level
    hotspots with one flat, prioritised "look at these first" list across
    every file. Collapsed, and skipped on small reviews where the per-file
    blocks already make the priority obvious.
    """
    flat = [f for fr in result.per_file for f in fr.inline_findings]
    if len(flat) < _TOP_FINDINGS_MIN:
        return []
    ranked = sorted(
        flat,
        key=lambda f: (_SEVERITY_RANK.get(f.severity, 0), _finding_confidence(f)),
        reverse=True,
    )
    shown = ranked[:_TOP_FINDINGS_LIMIT]
    rows = [
        f"{idx}. {_SEVERITY_ICON_BY_NAME.get(f.severity, '')} "
        f"{_loc_ref(f.path, f.line, files_url)} — {_first_line(f.comment)}"
        for idx, f in enumerate(shown, start=1)
    ]
    return [
        f"<details><summary>🔝 Top {len(shown)} of {len(flat)} findings"
        "</summary>",
        "", *rows, "", "</details>", "",
    ]


def _format_off_diff_block(
    off_diff: tuple[InlineFinding, ...], files_url: str | None = None
) -> list[str]:
    """List findings that fall outside the diff hunks and so are not posted.

    Surfacing these keeps the summary honest: the inline-findings counts
    say *how many* were dropped, and this block says *which ones*, so a
    reviewer can still act on them by hand instead of them vanishing.
    """
    if not off_diff:
        return []
    rows = [
        f"- {_loc_ref(f.path, f.line, files_url)} — {_first_line(f.comment)}"
        for f in off_diff
    ]
    return [
        f"<details><summary>⚠️ {len(off_diff)} finding(s) outside the diff "
        "(not posted inline)</summary>",
        "", *rows, "", "</details>", "",
    ]


def first_finding_ref(
    findings: list[InlineFinding],
    severities: tuple[str, ...],
    files_url: str | None = None,
) -> str | None:
    """Diff deep-link to the first finding matching ``severities`` (in order).

    ``severities`` is a priority list (e.g. ``("error", "warning")``); the
    first finding of the first severity present wins. Returns ``None`` when
    no finding matches — used by the gate line to point at its first blocker.
    """
    for severity in severities:
        for finding in findings:
            if finding.severity == severity:
                return _loc_ref(finding.path, finding.line, files_url)
    return None


def _format_extra_sections(sections: tuple[str, ...]) -> list[str]:
    """Render caller-supplied markdown blocks (risk, review order, …).

    Each non-empty section is a pre-rendered markdown string from the
    publish path; they sit between the index blocks and the per-file
    detail so the digest stays at the very top.
    """
    parts: list[str] = []
    for section in sections:
        if section and section.strip():
            parts += [section.rstrip(), ""]
    return parts


def _per_file_head_parts(
    result: ReviewResult, marker: str, opts: _RenderOpts
) -> list[str]:
    """Everything in the per-file comment that precedes the file blocks."""
    parts: list[str] = [
        marker,
        "## CoT Code Review (per-file)",
        "",
    ]
    parts += _format_must_fix_block(result, opts.files_url)
    if opts.preliminary:
        parts.append(opts.preliminary)
    parts += _format_overview_block(
        result, opts.files_url, opts.delta, opts.gate, opts.filtered
    )
    parts += _format_severity_groups(result, opts.files_url)
    parts += _format_category_groups(result, opts.files_url)
    parts += _format_top_findings(result, opts.files_url)
    parts += _format_off_diff_block(opts.off_diff, opts.files_url)
    parts += _format_extra_sections(opts.extra_sections)
    parts.append(_per_file_header(result))
    parts.append("")
    parts += _format_per_file_intro(result, opts.posted_count)
    parts += _hidden_clean_note(result, opts.findings_only)
    parts += _format_per_file_sections(result)
    return parts


def _format_findings_table(
    result: ReviewResult, files_url: str | None, findings_only: bool
) -> list[str]:
    """Flat, compact table of every finding — faster to scan than blocks."""
    rows: list[str] = []
    for fr in _files_to_render(result.per_file, findings_only):
        ordered = sorted(
            fr.inline_findings,
            key=lambda f: _SEVERITY_RANK.get(f.severity, 0),
            reverse=True,
        )
        for finding in ordered:
            icon = _SEVERITY_ICON_BY_NAME.get(finding.severity, "")
            loc = _loc_ref(finding.path, finding.line, files_url)
            text = _first_line(finding.comment).replace("|", "\\|")
            rows.append(f"| {icon} | {loc} | {text} |")
    if not rows:
        return []
    return ["| | Location | Finding |", "| --- | --- | --- |", *rows, ""]


def _format_per_file(
    result: ReviewResult, marker: str, opts: _RenderOpts
) -> str:
    parts = _per_file_head_parts(result, marker, opts)
    if opts.table:
        parts += _format_findings_table(result, opts.files_url, opts.findings_only)
    else:
        change_stats = compute_change_stats(result.code_diff)
        for fr in _files_to_render(result.per_file, opts.findings_only):
            parts += _format_file_block(fr, opts.files_url, change_stats)

    return "\n".join(parts).rstrip() + "\n"


# GitHub rejects an issue / PR comment body longer than 65 536 chars with a
# 422. Pages stay under this with headroom for the part label and the
# truncation safety net in github_api._cap_comment_body.
_PAGE_MAX_CHARS = 60000
_PART_LABEL_OVERHEAD = 200


def _continuation_head(marker: str) -> str:
    """Header that opens every page after the first."""
    return f"{marker}\n## CoT Code Review (per-file, continued)\n"


def _continued_header(header: str) -> str:
    """A file block's ``<summary>`` line tagged ``(continued)``."""
    return header.replace("</summary>", " (continued)</summary>", 1)


def _adjust_depth(depth: int, line: str) -> int:
    """Track ``<details>`` nesting so splits never cut inside a sub-block."""
    if line.startswith("<details"):
        return depth + 1
    if line.strip() == "</details>":
        return max(depth - 1, 0)
    return depth


def _pack_inner(
    first_header: str, cont_header: str, body: list[str], budget: int
) -> list[str]:
    """Pack a file block's inner lines into self-contained ``<details>`` pages.

    A page break is only taken at depth 0 (between whole nested sub-blocks),
    so the outer file block and every nested ``<details>`` stay balanced on
    each page. A single nested sub-block larger than the budget rides on its
    own page oversized rather than being cut mid-tag.
    """
    closer_overhead = len("\n</details>\n")
    pages: list[str] = []
    header = first_header
    chunk: list[str] = []
    size = len(header) + closer_overhead
    depth = 0
    for line in body:
        if chunk and depth == 0 and size + len(line) + 1 > budget:
            pages.append("\n".join([header, *chunk, "</details>", ""]))
            header, chunk, size = cont_header, [], len(cont_header) + closer_overhead
        chunk.append(line)
        size += len(line) + 1
        depth = _adjust_depth(depth, line)
    pages.append("\n".join([header, *chunk, "</details>", ""]))
    return pages


def _split_file_block(block: str, budget: int) -> list[str]:
    """Split one oversized file ``<details>`` block into per-page pieces.

    Each piece is an independently-opened-and-closed ``<details>`` block so
    the HTML never spans a comment boundary (which GitHub would render as
    broken markup). Blocks within budget — the common case — pass through
    unchanged. An unrecognised (non-details) block is left intact for the
    comment cap to truncate as a last resort.
    """
    if len(block) <= budget:
        return [block]
    lines = block.split("\n")
    if not lines or not lines[0].startswith("<details"):
        return [block]
    header = lines[0]
    body = lines[1:]
    while body and body[-1] == "":
        body = body[:-1]
    if body and body[-1] == "</details>":
        body = body[:-1]
    return _pack_inner(header, _continued_header(header), body, budget)


def _paginate_blocks(
    head: str, blocks: list[str], marker: str, max_chars: int
) -> list[str]:
    """Pack file blocks into pages, splitting only between whole blocks.

    A block larger than a single page is first split into self-contained
    ``<details>`` pieces (see :func:`_split_file_block`) so an oversized
    file is preserved across pages rather than truncated by the comment cap.
    """
    budget = max_chars - _PART_LABEL_OVERHEAD
    block_budget = budget - len(_continuation_head(marker)) - 1
    pages: list[str] = []
    current = head
    has_block = False
    for raw in blocks:
        for block in _split_file_block(raw, block_budget):
            candidate = f"{current}\n{block}"
            if has_block and len(candidate) > budget:
                pages.append(current)
                current = f"{_continuation_head(marker)}\n{block}"
            else:
                current = candidate
            has_block = True
    pages.append(current)
    return pages


def _label_pages(pages: list[str], marker: str) -> list[str]:
    """Insert a hidden part marker + visible ``Part k/N`` line on each page."""
    if len(pages) <= 1:
        return pages
    total = len(pages)
    labelled: list[str] = []
    for idx, page in enumerate(pages, start=1):
        label = f"<!-- prthinker:part={idx}/{total} -->\n_Part {idx} of {total}_\n"
        rest = page[len(marker):].lstrip("\n") if page.startswith(marker) else page
        labelled.append(f"{marker}\n{label}\n{rest}")
    return labelled


def format_pr_comment_pages(
    result: ReviewResult,
    marker: str,
    options: CommentOptions | None = None,
    *,
    max_chars: int = _PAGE_MAX_CHARS,
) -> list[str]:
    """Render the PR comment, paginated so no page exceeds ``max_chars``.

    Returns one body per comment. A short review is a single page,
    identical to :func:`format_pr_comment`. A long per-file review is
    split between file blocks (never inside one); each page after the
    first carries a continuation header and a ``Part k/N`` label so a
    1 MB review is preserved across several comments instead of being
    truncated to the GitHub limit.

    Args:
        result: The completed review to render.
        marker: Sentinel marker prepended for in-place upsert.
        options: Optional rendering / display knobs; see
            :class:`CommentOptions`.
        max_chars: Per-page character budget.

    Returns:
        One markdown body per comment page.
    """
    options = options or CommentOptions()
    result, filtered = _apply_display_filters(result, options)
    page_options = dataclasses.replace(
        options, hide_info=False, min_confidence=0.0, filtered=filtered
    )
    single = format_pr_comment(result, marker, page_options)
    # The table layout is compact; never block-paginate it.
    if len(single) <= max_chars or not result.per_file or options.table:
        return [single]
    opts = _render_opts_from(options, filtered)
    head = "\n".join(_per_file_head_parts(result, marker, opts))
    change_stats = compute_change_stats(result.code_diff)
    blocks = [
        "\n".join(_format_file_block(fr, options.files_url, change_stats))
        for fr in _files_to_render(result.per_file, options.findings_only)
    ]
    pages = _paginate_blocks(head, blocks, marker, max_chars)
    return _label_pages(pages, marker)


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


def format_digest(result: ReviewResult, files_url: str | None = None) -> str:
    """The standalone at-a-glance digest (status / counts / hotspots).

    Reused for the compact PR-description section so the verdict shows at
    the top of the PR, not only in the comments.
    """
    return "\n".join(_format_overview_block(result, files_url)).strip()


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

"""Markdown formatting for the consolidated PR comment.

Two layouts:

* single-pass result: top-level total summary + collapsible per-step blocks.
* per-file result: one collapsible block per file, each containing that
  file's total summary and a count of inline findings.

A sentinel marker is prepended so the comment can be upserted in place
across repeated workflow runs.
"""

from __future__ import annotations

import dataclasses
import hashlib
from collections import Counter
from collections.abc import Callable

from prthinker.change_stats import ChangeStat, change_badge, compute_change_stats
from prthinker.diff import new_side_content
from prthinker.pipeline import FileReviewResult, ReviewResult
from prthinker.schemas import InlineFinding

# Severity presentation, shared by the at-a-glance digest and per-file badges.
_SEVERITY_ICON: tuple[tuple[str, str], ...] = (
    ("error", "🔴"),
    ("warning", "🟡"),
    ("info", "🔵"),
)
_SEVERITY_RANK: dict[str, int] = {"error": 3, "warning": 2, "info": 1}
_SEVERITY_ICON_BY_NAME: dict[str, str] = dict(_SEVERITY_ICON)

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


def _diff_anchor(path: str, line: int) -> str:
    """GitHub's Files-changed anchor for ``path`` at new-side ``line``."""
    digest = hashlib.sha256(path.encode("utf-8")).hexdigest()
    return f"diff-{digest}R{line}"


def _file_ref(path: str, files_url: str | None, line: int = 1) -> str:
    """Markdown: a deep link into the diff, or a plain code span."""
    if not files_url:
        return f"`{path}`"
    return f"[`{path}`]({files_url}#{_diff_anchor(path, line)})"


def _file_summary_ref(path: str, files_url: str | None, line: int = 1) -> str:
    """HTML (for ``<summary>``): a linked code span, or a plain one."""
    if not files_url:
        return f"<code>{path}</code>"
    return (
        f'<a href="{files_url}#{_diff_anchor(path, line)}">'
        f"<code>{path}</code></a>"
    )


def _first_finding_line(fr: FileReviewResult) -> int:
    """New-side line to anchor a file link at (first finding, else 1)."""
    return fr.inline_findings[0].line if fr.inline_findings else 1


def _loc_ref(path: str, line: int, files_url: str | None) -> str:
    """Markdown ``path:line`` as a diff deep link, or a plain code span."""
    if not files_url:
        return f"`{path}:{line}`"
    return f"[`{path}:{line}`]({files_url}#{_diff_anchor(path, line)})"

_SECTION_TITLES: dict[str, str] = {
    "first_summary": "PR Summary",
    "first_code_review": "First Code Review",
    "linter": "Lint Findings",
    "code_smell": "Code Smell Detection",
}


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


def _first_line(text: str, cap: int = 120) -> str:
    """First line of a finding comment, length-capped for a one-liner."""
    head = (text or "").strip().splitlines()[0] if (text or "").strip() else ""
    return head if len(head) <= cap else head[: cap - 1] + "…"


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


def format_pr_comment(
    result: ReviewResult,
    marker: str,
    *,
    posted_count: int | None = None,
    findings_only: bool = False,
    hide_info: bool = False,
    preliminary: str | None = None,
    files_url: str | None = None,
    delta: str | None = None,
    min_confidence: float = 0.0,
    table: bool = False,
    gate: str | None = None,
    off_diff_findings: tuple[InlineFinding, ...] = (),
    extra_sections: tuple[str, ...] = (),
) -> str:
    """Render the consolidated PR comment.

    ``posted_count`` is the number of inline findings that actually land
    on a diff hunk (i.e. that GitHub will accept). When supplied, the
    findings summary distinguishes "found" from "posted to the diff"
    instead of overstating that every finding was posted. When ``None``
    (local CLI, MCP, dry-run — no inline submission happens) only the
    total is shown.

    ``findings_only`` lists only files that have findings (clean files are
    collapsed into a count) and reduces a zero-finding PR to a one-line
    confirmation instead of a full empty result.

    ``hide_info`` omits ``info``-severity findings from the rendered
    summary (display only — the inline review and gate still see them).

    ``preliminary`` is a pre-rendered, model-free "what this PR does"
    overview (from commit messages + changed files) pinned to the top.
    """
    if hide_info:
        result = _without_info_findings(result)
    if min_confidence > 0:
        result = _without_low_confidence(result, min_confidence)
    if findings_only and _total_inline_findings(result) == 0:
        return _format_clean_comment(result, marker, preliminary)
    if result.per_file:
        opts = _RenderOpts(
            posted_count=posted_count, findings_only=findings_only,
            preliminary=preliminary, files_url=files_url, delta=delta,
            table=table, gate=gate, off_diff=off_diff_findings,
            extra_sections=extra_sections,
        )
        return _format_per_file(result, marker, opts)
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
    parts += _format_overview_block(result, opts.files_url, opts.delta, opts.gate)
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
    *,
    posted_count: int | None = None,
    max_chars: int = _PAGE_MAX_CHARS,
    findings_only: bool = False,
    hide_info: bool = False,
    preliminary: str | None = None,
    files_url: str | None = None,
    delta: str | None = None,
    min_confidence: float = 0.0,
    table: bool = False,
    gate: str | None = None,
    off_diff_findings: tuple[InlineFinding, ...] = (),
    extra_sections: tuple[str, ...] = (),
) -> list[str]:
    """Render the PR comment, paginated so no page exceeds ``max_chars``.

    Returns one body per comment. A short review is a single page,
    identical to :func:`format_pr_comment`. A long per-file review is
    split between file blocks (never inside one); each page after the
    first carries a continuation header and a ``Part k/N`` label so a
    1 MB review is preserved across several comments instead of being
    truncated to the GitHub limit.

    ``findings_only`` renders only files with findings (clean ones become a
    count), which on a large but mostly-clean PR can collapse a multi-page
    summary back to one comment. ``hide_info`` drops ``info``-severity
    findings from the rendered summary. ``preliminary`` is the model-free
    PR overview pinned to the top of page 1.
    """
    if hide_info:
        result = _without_info_findings(result)
    if min_confidence > 0:
        result = _without_low_confidence(result, min_confidence)
    single = format_pr_comment(
        result, marker, posted_count=posted_count,
        findings_only=findings_only, preliminary=preliminary,
        files_url=files_url, delta=delta, table=table, gate=gate,
        off_diff_findings=off_diff_findings, extra_sections=extra_sections,
    )
    # The table layout is compact; never block-paginate it.
    if len(single) <= max_chars or not result.per_file or table:
        return [single]
    opts = _RenderOpts(
        posted_count=posted_count, findings_only=findings_only,
        preliminary=preliminary, files_url=files_url, delta=delta, gate=gate,
        off_diff=off_diff_findings, extra_sections=extra_sections,
    )
    head = "\n".join(_per_file_head_parts(result, marker, opts))
    change_stats = compute_change_stats(result.code_diff)
    blocks = [
        "\n".join(_format_file_block(fr, files_url, change_stats))
        for fr in _files_to_render(result.per_file, findings_only)
    ]
    pages = _paginate_blocks(head, blocks, marker, max_chars)
    return _label_pages(pages, marker)


_LEGEND_LINES: tuple[str, ...] = (
    "- **🔴 error · 🟡 warning · 🔵 info** — finding severity",
    "- **✅** no findings · **🚨** must-fix (errors) · "
    "**📋** PR overview · **🔎** review digest",
    "- **💬** author reply · **✓** sandbox-verified suggestion · "
    "**⚠️** low-reproducibility finding",
    "- file badge `🔴2 🟡1` = per-severity finding counts; "
    "filenames link into the diff",
)


def _format_legend() -> list[str]:
    """A collapsed key explaining every glyph used in the report."""
    return [
        "<details><summary>Legend</summary>",
        "", *_LEGEND_LINES, "", "</details>", "",
    ]


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
    skipped = sum(1 for fr in result.per_file if fr.is_binary or fr.is_deleted)
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


_ENTROPY_NOTE: dict[str, str] = {
    "focused": "PR is focused; no concerns from the diff-shape side.",
    "wide":    "PR is wide — touches many directories. Consider whether "
               "it could be split for easier review.",
    "bomb":    "**Consider splitting this PR.** It is large *and* spread "
               "across many areas; reviews of diffs this shape tend to "
               "miss issues regardless of the model used.",
}


def _format_diff_entropy_block(summary) -> list[str]:
    """Render the diff-shape header."""
    block: list[str] = [
        "### Diff shape",
        "",
        "| Files | +Lines | -Lines | Score | Verdict |",
        "| ---: | ---: | ---: | ---: | --- |",
        f"| {summary.file_count} | {summary.added_lines} | "
        f"{summary.removed_lines} | {summary.score:.2f} | "
        f"`{summary.verdict}` |",
        "",
        _ENTROPY_NOTE.get(summary.verdict, ""),
        "",
    ]
    return block


def _format_persona_conflicts_block(conflicts: list) -> list[str]:
    """Render the cross-persona tension table at the top of the PR
    comment. Resolutions intentionally do NOT pick a winner.
    """
    block: list[str] = [
        "### Persona conflicts (tensions to resolve)",
        "",
        "| Personas | Tension | Resolution framing |",
        "| --- | --- | --- |",
    ]
    for c in conflicts:
        personas = ", ".join(f"`{p}`" for p in c.personas)
        summary = c.summary.replace("|", "\\|").strip()
        resolution = (c.resolution or "").replace("|", "\\|").strip()
        block.append(f"| {personas} | {summary} | {resolution} |")
    block += ["", ""]
    return block


def _format_dep_upgrade_block(upgrades: list) -> list[str]:
    """Render the dependency-upgrade impact section.

    Keeps the table tight: severity / package / version delta / what
    to do. Full evidence stays in the raw ``dep_upgrade::*`` step
    outputs for traceability.
    """
    block: list[str] = [
        "### Dependency upgrade impact",
        "",
        "| Severity | Package | Bump | Summary |",
        "| --- | --- | --- | --- |",
    ]
    for u in upgrades:
        sev = u.severity
        bump = f"{u.old_version} -> {u.new_version}"
        summary = u.summary.replace("|", "\\|").strip()
        block.append(
            f"| {sev} | `{u.package}` ({u.ecosystem}) | {bump} | {summary} |"
        )
    block += ["", ""]
    return block


_API_DRIFT_KIND_LABEL: dict[str, str] = {
    "field_renamed":  "field renamed",
    "field_removed":  "field removed",
    "type_changed":   "type changed",
    "path_changed":   "path / route changed",
    "method_changed": "HTTP method changed",
    "other":          "other",
}


def _format_api_drift_block(drift: "list") -> list[str]:
    """Render the cross-language API-drift section near the top of the
    consolidated PR comment.
    """
    block: list[str] = [
        "### Cross-language API drift",
        "",
        "| Kind | Backend | Frontend | Summary |",
        "| --- | --- | --- | --- |",
    ]
    for df in drift:
        kind = _API_DRIFT_KIND_LABEL.get(df.kind, df.kind)
        summary = df.summary.replace("|", "\\|").strip()
        block.append(
            f"| {kind} | `{df.backend_path}` | `{df.frontend_path}` | {summary} |"
        )
    block += [
        "",
        "Evidence is preserved in the raw ``api_consistency`` step output "
        "for traceability.",
        "",
    ]
    return block


_FILE_RESERVED_STEPS: frozenset[str] = frozenset(
    {"total_summary", "inline_findings", "counterfactual", "walkthrough"}
)


def _format_step_detail(title: str, body: str) -> list[str]:
    """Render one collapsible per-step ``<details>`` block."""
    return [
        f"<details><summary>{title}</summary>",
        "",
        body,
        "",
        "</details>",
        "",
    ]


def _step_title(name: str) -> str:
    """Return the display title for a step output name."""
    return _SECTION_TITLES.get(name, name.replace("_", " ").title())


def _annotation_subblock(
    findings: list[InlineFinding],
    predicate: Callable[[InlineFinding], bool],
    renderer: Callable[[list[InlineFinding]], list[str]],
) -> list[str]:
    """Render one annotation sub-block for the findings matching ``predicate``."""
    matched = [f for f in findings if predicate(f)]
    return renderer(matched) if matched else []


def _format_finding_annotations(findings: list[InlineFinding]) -> list[str]:
    """Render provenance, reproducibility, and verification sub-blocks."""
    block: list[str] = []
    block += _annotation_subblock(
        findings, lambda f: f.provenance is not None, _format_provenance_block
    )
    block += _annotation_subblock(
        findings, lambda f: f.reproducibility is not None, _format_reproducibility_block
    )
    block += _annotation_subblock(
        findings, lambda f: f.verification is not None, _format_verification_block
    )
    return block


def _file_findings_badge(findings: list[InlineFinding]) -> str:
    """Per-file badge as severity icons (🔴2 🟡1), or a no-findings note."""
    if not findings:
        return " — no findings"
    counts = Counter(f.severity for f in findings)
    parts = [f"{icon}{counts[sev]}" for sev, icon in _SEVERITY_ICON if counts.get(sev)]
    return " — " + " ".join(parts)


def _file_status_icon(findings: list[InlineFinding]) -> str:
    """Leading status glyph for a file's ``<summary>`` (worst severity)."""
    for sev, icon in _SEVERITY_ICON:  # error, warning, info — worst first
        if any(f.severity == sev for f in findings):
            return icon
    return "✅"


def _file_sort_key(fr: FileReviewResult) -> tuple[int, int]:
    """Rank a file by (worst severity, finding count) for summary ordering."""
    ranks = [_SEVERITY_RANK.get(f.severity, 0) for f in fr.inline_findings]
    return (max(ranks, default=0), len(fr.inline_findings))


def _sort_files_by_severity(
    files: list[FileReviewResult],
) -> list[FileReviewResult]:
    """Most-severe / most-findings files first so they read at the top."""
    return sorted(files, key=_file_sort_key, reverse=True)


def _format_file_step_details(fr: FileReviewResult) -> list[str]:
    """Render the per-file step-output detail blocks, skipping reserved ones."""
    block: list[str] = []
    for name in fr.step_outputs:
        if name in _FILE_RESERVED_STEPS:
            continue
        block += _format_step_detail(_step_title(name), fr.step_outputs[name].strip())
    return block


def _signal_note(findings: list[InlineFinding]) -> str:
    """Surface already-computed trust signal: verified / low-repro counts."""
    verified = sum(
        1 for f in findings
        if f.verification is not None and f.verification.status == "pass"
    )
    low_repro = sum(1 for f in findings if f.reproducibility == "low")
    bits = []
    if verified:
        bits.append(f"✓ {verified} verified")
    if low_repro:
        bits.append(f"⚠️ {low_repro} low-repro")
    return f"_Signal: {' · '.join(bits)}_" if bits else ""


def _change_badge_suffix(
    path: str, change_stats: dict[str, ChangeStat] | None
) -> str:
    """Per-file ``(+12 −3 · 2 hunks)`` summary suffix, or ``""``."""
    if not change_stats:
        return ""
    badge = change_badge(change_stats.get(path))
    return f" ({badge})" if badge else ""


def _format_walkthrough_block(fr: FileReviewResult) -> list[str]:
    """Render the model-written 'what this change does' lead, when present.

    Pinned above the review **Summary** because it is orientation (what
    the change *is*) that the reviewer reads before the assessment (what
    is *wrong* with it). Rendered only when the ``--walkthrough`` step ran.
    """
    text = (fr.step_outputs.get("walkthrough") or "").strip()
    if not text:
        return []
    return ["**📝 Walkthrough**", "", text, ""]


def _format_file_block(
    fr: FileReviewResult,
    files_url: str | None = None,
    change_stats: dict[str, ChangeStat] | None = None,
) -> list[str]:
    # Skipped files (binary / deleted) are still listed so every touched
    # file is accounted for — just with the skip reason instead of a review.
    if fr.is_binary or fr.is_deleted:
        reason = "binary" if fr.is_binary else "deleted"
        return [f"- <code>{fr.path}</code> — _skipped ({reason})_", ""]

    summary = fr.total_summary or "_no summary_"
    badge = _file_findings_badge(fr.inline_findings)
    change = _change_badge_suffix(fr.path, change_stats)
    ref = _file_summary_ref(fr.path, files_url, _first_finding_line(fr))
    icon = _file_status_icon(fr.inline_findings)
    # Files with errors open expanded so the reviewer sees them with no click.
    has_error = any(f.severity == "error" for f in fr.inline_findings)
    tag = "<details open>" if has_error else "<details>"

    block: list[str] = [f"{tag}<summary>{icon} {ref}{badge}{change}</summary>", ""]
    signal = _signal_note(fr.inline_findings)
    if signal:
        block += [signal, ""]
    block += _format_walkthrough_block(fr)
    block += ["**Summary**", "", summary.strip(), ""]
    block += _format_finding_annotations(fr.inline_findings)
    block += _format_file_step_details(fr)
    if fr.counterfactuals:
        block += _format_counterfactuals_block(fr)
    block += ["</details>", ""]
    return block


def _citation_label(cite) -> str:
    """Map a provenance citation to its human-readable list label."""
    if cite.kind == "rag_rule" and cite.index is not None:
        return f"RAG rule #{cite.index}"
    if cite.kind == "accepted_example" and cite.index is not None:
        return f"Accepted example #{cite.index}"
    if cite.kind == "diff_evidence":
        lines = ", ".join(str(ln) for ln in cite.lines)
        return f"Diff line(s) {lines}" if lines else "Diff"
    return cite.kind


def _format_provenance_entry(finding: InlineFinding) -> list[str]:
    """Render one finding's provenance header and citation bullets."""
    prov = finding.provenance
    header = f"**line {finding.line}**"
    if prov.confidence is not None:
        header += f" — model confidence {prov.confidence:.2f}"
    lines: list[str] = [header, ""]
    if prov.citations:
        for cite in prov.citations:
            note = (" — " + cite.note.strip()) if cite.note.strip() else ""
            lines.append(f"- {_citation_label(cite)}{note}")
    else:
        # The provenance step ran for this finding but produced no
        # citation. Saying so is more honest than hiding it: the reviewer
        # learns the call rests on model judgement alone.
        lines.append("- _model judgement — no external citation_")
    lines.append("")
    return lines


def _format_provenance_block(findings: list[InlineFinding]) -> list[str]:
    """Render an audit-trail summary for every finding that carries a
    :class:`Provenance` object.

    Every finding that carries provenance is accounted for: those with
    citations list them, those without are flagged as resting on model
    judgement rather than being silently dropped. Findings with no
    provenance object at all (the feature never ran for them) are skipped,
    and an all-skipped list renders nothing.
    """
    relevant = [f for f in findings if f.provenance is not None]
    if not relevant:
        return []
    block: list[str] = [
        "<details><summary>Audit trail (provenance)</summary>",
        "",
    ]
    for finding in relevant:
        block += _format_provenance_entry(finding)
    block += ["</details>", ""]
    return block


_VERIFICATION_BADGE: dict[str, str] = {  # nosec B105 — display labels keyed on VerificationStatus literal, not credentials
    "pass":  "**[verified]**",
    "fail":  "**[FAILED]**",
    "skip":  "_[skipped]_",
    "error": "**[error]**",
}

_REPRO_BADGE: dict[str, str] = {
    "stable": "**[stable]**",
    "low":    "_[low-reproducibility]_",
}


def _format_reproducibility_block(findings: list[InlineFinding]) -> list[str]:
    """Render the per-finding stable / low-repro labels."""
    block: list[str] = [
        "<details><summary>Finding reproducibility (two-pass)</summary>",
        "",
        "| Line | Label | Comment |",
        "| ---: | --- | --- |",
    ]
    for f in findings:
        badge = _REPRO_BADGE.get(f.reproducibility or "", f.reproducibility or "")
        comment = f.comment.replace("|", "\\|").strip()
        if len(comment) > 80:
            comment = comment[:79].rstrip() + "..."
        block.append(f"| {f.line} | {badge} | {comment} |")
    block += ["", "</details>", ""]
    return block


def _format_verification_block(findings: list[InlineFinding]) -> list[str]:
    """Render the sandbox-verification badges for any finding whose
    ``suggestion`` block went through ``--verify-suggestions``."""
    block: list[str] = [
        "<details><summary>Suggestion verification (sandbox)</summary>",
        "",
        "| Line | Verdict | Verify cmd | Reason |",
        "| ---: | --- | --- | --- |",
    ]
    for f in findings:
        v = f.verification
        if v is None:
            continue
        badge = _VERIFICATION_BADGE.get(v.status, v.status)
        reason = (v.reason or "").replace("|", "\\|").strip()
        cmd = v.verify_cmd.replace("|", "\\|")
        block.append(f"| {f.line} | {badge} | `{cmd}` | {reason} |")
    block += ["", "</details>", ""]
    return block


def _format_counterfactuals_block(fr: FileReviewResult) -> list[str]:
    """Render counterfactual alternatives as a collapsible per-file block.

    Each block points at the inline-finding it elaborates by 1-based
    index (so the comment matches what reviewers see in the inline
    review). Trade-off axes become a small markdown table.
    """
    block: list[str] = [
        "<details><summary>Alternative implementations</summary>",
        "",
    ]
    for cf in fr.counterfactuals:
        idx = cf.finding_index
        if 0 <= idx < len(fr.inline_findings):
            anchor = fr.inline_findings[idx]
            block.append(f"**Finding {idx + 1} (line {anchor.line})**")
        else:
            block.append(f"**Finding {idx + 1}**")
        block.append("")
        for opt in cf.options:
            block.append(f"- **{opt.label}** — {opt.rationale.strip()}")
            if opt.tradeoffs:
                block.append("")
                block.append("  | Axis | Impact |")
                block.append("  | --- | --- |")
                for axis, impact in opt.tradeoffs.items():
                    block.append(f"  | {axis} | {impact} |")
                block.append("")
        block.append("")
    block += ["</details>", ""]
    return block


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


__all__ = [
    "first_finding_ref",
    "format_digest",
    "format_pr_comment",
    "format_pr_comment_pages",
    "format_review_footer",
    "format_reviewer_checklist",
]

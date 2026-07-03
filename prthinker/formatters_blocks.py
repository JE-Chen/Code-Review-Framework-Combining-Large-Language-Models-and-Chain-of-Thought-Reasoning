"""Leaf rendering helpers for the consolidated PR comment.

This module holds the low-level markdown / HTML primitives, the shared
severity / category presentation constants, and the per-file and
cross-file *block* renderers (the diff-shape, persona-conflict,
dependency-upgrade, API-drift, provenance, reproducibility, verification,
counterfactual, walkthrough, and per-file ``<details>`` blocks).

It is split out of :mod:`prthinker.formatters` to keep each module under
the project's file-length bar. The orchestration layer in
:mod:`prthinker.formatters` imports the names it needs from here and
re-exports the public-facing private helpers so existing call sites and
tests continue to reach them through ``prthinker.formatters``.
"""

from __future__ import annotations

import hashlib
from collections import Counter
from collections.abc import Callable

from prthinker.change_stats import ChangeStat, change_badge
from prthinker.pipeline import FileReviewResult
from prthinker.schemas import InlineFinding

# Severity presentation, shared by the at-a-glance digest and per-file badges.
_SEVERITY_ICON: tuple[tuple[str, str], ...] = (
    ("error", "🔴"),
    ("warning", "🟡"),
    ("info", "🔵"),
)
_SEVERITY_RANK: dict[str, int] = {"error": 3, "warning": 2, "info": 1}
_SEVERITY_ICON_BY_NAME: dict[str, str] = dict(_SEVERITY_ICON)

_SECTION_TITLES: dict[str, str] = {
    "first_summary": "PR Summary",
    "first_code_review": "First Code Review",
    "linter": "Lint Findings",
    "code_smell": "Code Smell Detection",
}

_FILE_RESERVED_STEPS: frozenset[str] = frozenset(
    {"total_summary", "inline_findings", "counterfactual", "walkthrough"}
)


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


def _first_line(text: str, cap: int = 120) -> str:
    """First line of a finding comment, length-capped for a one-liner."""
    head = (text or "").strip().splitlines()[0] if (text or "").strip() else ""
    return head if len(head) <= cap else head[: cap - 1] + "…"


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
    block += _annotation_subblock(
        findings, lambda f: bool(f.evidence), _format_evidence_block
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


def _is_verified(finding: InlineFinding) -> bool:
    """True when the finding carries a passing verification result."""
    return finding.verification is not None and finding.verification.status == "pass"


def _signal_note(findings: list[InlineFinding]) -> str:
    """Surface already-computed trust signal: verified / low-repro counts."""
    verified = sum(1 for f in findings if _is_verified(f))
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


def _format_skipped_file_block(fr: FileReviewResult) -> list[str]:
    """Render the one-line skip entry for a binary or deleted file."""
    reason = "binary" if fr.is_binary else "deleted"
    return [f"- <code>{fr.path}</code> — _skipped ({reason})_", ""]


def _format_file_block(
    fr: FileReviewResult,
    files_url: str | None = None,
    change_stats: dict[str, ChangeStat] | None = None,
) -> list[str]:
    # Skipped files (binary / deleted) are still listed so every touched
    # file is accounted for — just with the skip reason instead of a review.
    if fr.is_binary or fr.is_deleted:
        return _format_skipped_file_block(fr)

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


def _format_evidence_block(findings: list[InlineFinding]) -> list[str]:
    """Render reproducible verification evidence bound to stable findings."""
    block = [
        "<details><summary>Finding evidence</summary>", "",
        "| Finding | Kind | Tool | Status | Summary |",
        "| --- | --- | --- | --- | --- |",
    ]
    for finding in findings:
        for evidence in finding.evidence:
            summary = evidence.summary.replace("|", "\\|").replace("\n", " ")
            block.append(
                f"| `{finding.finding_id}` | {evidence.kind} | `{evidence.tool}` | "
                f"{evidence.status} | {summary} |"
            )
    return block + ["", "</details>", ""]


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

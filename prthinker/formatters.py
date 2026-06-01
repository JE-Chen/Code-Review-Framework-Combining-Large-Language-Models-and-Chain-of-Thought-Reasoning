"""Markdown formatting for the consolidated PR comment.

Two layouts:

* single-pass result: top-level total summary + collapsible per-step blocks.
* per-file result: one collapsible block per file, each containing that
  file's total summary and a count of inline findings.

A sentinel marker is prepended so the comment can be upserted in place
across repeated workflow runs.
"""

from __future__ import annotations

from prthinker.pipeline import FileReviewResult, ReviewResult
from prthinker.schemas import InlineFinding

_SECTION_TITLES: dict[str, str] = {
    "first_summary": "PR Summary",
    "first_code_review": "First Code Review",
    "linter": "Lint Findings",
    "code_smell": "Code Smell Detection",
}


def format_pr_comment(result: ReviewResult, marker: str) -> str:
    if result.per_file:
        return _format_per_file(result, marker)
    return _format_single(result, marker)


def _format_single(result: ReviewResult, marker: str) -> str:
    parts: list[str] = [marker, "## CoT Code Review", ""]

    total = result.total_summary
    if total:
        parts += ["### Total Summary", "", total.strip(), ""]
    else:
        parts += ["_No total summary produced._", ""]

    detail_steps = [
        name for name in result.step_outputs
        if name not in {"total_summary", "inline_findings"}
    ]
    if detail_steps:
        parts += ["---", "", "### Per-step Details", ""]
        for name in detail_steps:
            title = _SECTION_TITLES.get(name, name.replace("_", " ").title())
            body = result.step_outputs[name].strip()
            parts += [
                f"<details><summary>{title}</summary>",
                "",
                body,
                "",
                "</details>",
                "",
            ]

    footer_bits: list[str] = []
    if result.rag_docs:
        footer_bits.append(f"RAG rules applied: {len(result.rag_docs)}")
    if result.inline_findings:
        footer_bits.append(f"Inline findings: {len(result.inline_findings)}")
    if footer_bits:
        parts += ["---", "", "_" + " · ".join(footer_bits) + "_"]

    return "\n".join(parts).rstrip() + "\n"


def _format_per_file(result: ReviewResult, marker: str) -> str:
    parts: list[str] = [
        marker,
        "## CoT Code Review (per-file)",
        "",
        f"Reviewed **{len(result.per_file)}** file(s).",
        "",
    ]

    if result.pr_classification is not None:
        cls = result.pr_classification
        parts.append(
            f"PR classified as **{cls.pr_type}** — {cls.reason or '(no reason given)'}"
        )
        parts.append("")

    total_findings = sum(len(f.inline_findings) for f in result.per_file)
    if total_findings:
        parts.append(f"Posted **{total_findings}** inline finding(s).")
        parts.append("")

    overall = result.total_summary
    if overall:
        parts += [
            "### Overall Summary",
            "",
            overall.strip(),
            "",
            "---",
            "",
        ]

    if result.diff_entropy is not None:
        parts += _format_diff_entropy_block(result.diff_entropy)

    if result.persona_conflicts:
        parts += _format_persona_conflicts_block(result.persona_conflicts)

    if result.dep_upgrades:
        parts += _format_dep_upgrade_block(result.dep_upgrades)

    if result.api_drift:
        parts += _format_api_drift_block(result.api_drift)

    for fr in result.per_file:
        parts += _format_file_block(fr)

    return "\n".join(parts).rstrip() + "\n"


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


def _format_file_block(fr: FileReviewResult) -> list[str]:
    summary = fr.total_summary or "_no summary_"
    findings_n = len(fr.inline_findings)
    badge = f" — {findings_n} finding(s)" if findings_n else ""

    block: list[str] = [
        f"<details><summary><code>{fr.path}</code>{badge}</summary>",
        "",
        "**Summary**",
        "",
        summary.strip(),
        "",
    ]

    cited = [f for f in fr.inline_findings if f.provenance is not None]
    if cited:
        block += _format_provenance_block(cited)

    labelled = [f for f in fr.inline_findings if f.reproducibility is not None]
    if labelled:
        block += _format_reproducibility_block(labelled)

    verified = [f for f in fr.inline_findings if f.verification is not None]
    if verified:
        block += _format_verification_block(verified)

    detail_steps = [
        name for name in fr.step_outputs
        if name not in {"total_summary", "inline_findings", "counterfactual"}
    ]
    for name in detail_steps:
        title = _SECTION_TITLES.get(name, name.replace("_", " ").title())
        body = fr.step_outputs[name].strip()
        block += [
            f"<details><summary>{title}</summary>",
            "",
            body,
            "",
            "</details>",
            "",
        ]

    if fr.counterfactuals:
        block += _format_counterfactuals_block(fr)

    block += ["</details>", ""]
    return block


def _format_provenance_block(findings: list[InlineFinding]) -> list[str]:
    """Render an audit-trail summary listing the citations behind each
    finding that carries a non-empty :class:`Provenance` payload.

    Findings without provenance never show up here — the caller filters
    them in. Findings whose provenance has no citations and no
    confidence are not rendered (they would be empty noise).
    """
    block: list[str] = [
        "<details><summary>Audit trail (provenance)</summary>",
        "",
    ]
    rendered_any = False
    for f in findings:
        prov = f.provenance
        if prov is None:
            continue
        has_payload = bool(prov.citations) or prov.confidence is not None
        if not has_payload:
            continue
        rendered_any = True
        header = f"**line {f.line}**"
        if prov.confidence is not None:
            header += f" — model confidence {prov.confidence:.2f}"
        block.append(header)
        block.append("")
        for cite in prov.citations:
            if cite.kind == "rag_rule" and cite.index is not None:
                label = f"RAG rule #{cite.index}"
            elif cite.kind == "accepted_example" and cite.index is not None:
                label = f"Accepted example #{cite.index}"
            elif cite.kind == "diff_evidence":
                lines = ", ".join(str(ln) for ln in cite.lines)
                label = f"Diff line(s) {lines}" if lines else "Diff"
            else:
                label = cite.kind
            note = (" — " + cite.note.strip()) if cite.note.strip() else ""
            block.append(f"- {label}{note}")
        block.append("")
    block += ["</details>", ""]
    if not rendered_any:
        return []  # caller appended the opener; signal nothing to render
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


__all__ = ["format_pr_comment"]

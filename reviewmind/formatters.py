"""Markdown formatting for the consolidated PR comment.

Two layouts:

* single-pass result: top-level total summary + collapsible per-step blocks.
* per-file result: one collapsible block per file, each containing that
  file's total summary and a count of inline findings.

A sentinel marker is prepended so the comment can be upserted in place
across repeated workflow runs.
"""

from __future__ import annotations

from reviewmind.pipeline import FileReviewResult, ReviewResult
from reviewmind.schemas import InlineFinding

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

    total_findings = sum(len(f.inline_findings) for f in result.per_file)
    if total_findings:
        parts.append(f"Posted **{total_findings}** inline finding(s).")
        parts.append("")

    for fr in result.per_file:
        parts += _format_file_block(fr)

    return "\n".join(parts).rstrip() + "\n"


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

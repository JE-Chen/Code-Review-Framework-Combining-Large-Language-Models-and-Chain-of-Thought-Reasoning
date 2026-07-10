"""Standalone Markdown report for a review result.

The PR-comment formatter needs platform context (file URLs, comment
markers, paging). This exporter instead renders a single self-contained
Markdown document — summary, orientation signals, and per-file findings —
suitable for a downloadable CI artifact, a wiki paste, or any tool that
renders Markdown. It mirrors the HTML report's content without the
platform plumbing.

Runner-safe: pure string building plus the change-stat and signal helpers.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from prthinker.change_stats import compute_change_stats, total_changes
from prthinker.review_rollups import (
    ReviewRollup,
    all_findings,
    format_markdown_rollup,
    severity_counts,
)
from prthinker.schemas import SEVERITY_ORDER
from prthinker.signals import collect_signal_findings

if TYPE_CHECKING:
    from prthinker.pipeline import FileReviewResult, ReviewResult
    from prthinker.schemas import InlineFinding

_NO_FINDINGS = "_No findings._"


def _one_line(text: str) -> str:
    """Collapse a comment to a single line so it stays inside one bullet."""
    return " ".join(text.split())


def _summary_lines(result: "ReviewResult", findings: list["InlineFinding"]) -> list[str]:
    """The '## Summary' block: diff totals + finding counts."""
    counts = severity_counts(findings)
    lines = ["## Summary", ""]
    stats = compute_change_stats(result.code_diff or "")
    if stats:
        files, added, removed = total_changes(stats)
        lines.append(f"- {files} file(s) changed · +{added} −{removed}")
    lines.append(f"- Total findings: {len(findings)}")
    lines.append(
        "- " + " · ".join(f"{sev}: {counts[sev]}" for sev in SEVERITY_ORDER)
    )
    return lines


def _signal_lines(result: "ReviewResult") -> list[str]:
    """The '## Orientation signals' block, or [] when none fire."""
    signals = collect_signal_findings(result.code_diff or "")
    if not signals:
        return []
    lines = ["", "## Orientation signals", ""]
    for signal in signals:
        loc = ""
        if signal.path is not None:
            loc = f" `{signal.path}`" + (f":{signal.line}" if signal.line else "")
        lines.append(
            f"- [{signal.level}] {signal.name}{loc} — {_one_line(signal.message)}"
        )
    return lines


def _finding_line(finding: "InlineFinding") -> str:
    """One per-file finding bullet."""
    return (
        f"- `{finding.path}:{finding.line}` **[{finding.severity}]** "
        f"{_one_line(finding.comment)}"
    )


def _file_heading(file_result: "FileReviewResult") -> str:
    """Per-file section heading, flagging binary / deleted files."""
    suffix = ""
    if file_result.is_deleted:
        suffix = " (deleted)"
    elif file_result.is_binary:
        suffix = " (binary)"
    return f"### {file_result.path}{suffix}"


def _file_lines(result: "ReviewResult") -> list[str]:
    """The '## Findings' block: one subsection per file, or a flat list."""
    lines = ["", "## Findings", ""]
    if not result.per_file:
        if not result.inline_findings:
            return lines + [_NO_FINDINGS]
        return lines + [_finding_line(f) for f in result.inline_findings]
    for file_result in result.per_file:
        lines.append(_file_heading(file_result))
        if file_result.inline_findings:
            lines += [_finding_line(f) for f in file_result.inline_findings]
        else:
            lines.append(_NO_FINDINGS)
        lines.append("")
    return lines


def render_markdown(
    result: "ReviewResult",
    *,
    title: str = "prthinker review",
    rollup: ReviewRollup | None = None,
) -> str:
    """Render a self-contained Markdown review document as a string.

    ``rollup`` lets a caller that already computed the audit rollup pass it
    in; it is derived from ``result`` when omitted.
    """
    findings = all_findings(result)
    parts = [f"# {title}", ""]
    parts += _summary_lines(result, findings)
    parts += [""] + format_markdown_rollup(result, rollup)
    parts += _signal_lines(result)
    parts += _file_lines(result)
    return "\n".join(parts).rstrip() + "\n"


def write_markdown(result: "ReviewResult", out_path: "str | Path") -> None:
    """Render ``result`` and write the Markdown document to ``out_path``."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as handle:
        handle.write(render_markdown(result))


__all__ = ["render_markdown", "write_markdown"]

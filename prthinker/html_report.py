"""Standalone, XSS-safe HTML report for a CoT ``ReviewResult``.

Pure stdlib (``html`` only) so it stays runner-safe: no ``torch`` /
``transformers`` / ``faiss`` / ``numpy`` ever reach this module. Every
piece of model- or diff-derived text is funnelled through
:func:`html.escape` before it lands in the document, so a finding whose
comment contains ``<script>`` cannot break out of its text node.
"""

from __future__ import annotations

import html
from pathlib import Path

from prthinker.pipeline import FileReviewResult, ReviewResult
from prthinker.schemas import InlineFinding
from prthinker.signals import SignalFinding, collect_signal_findings

# Map a signal level onto the existing severity CSS classes so signals
# pick up the same colour ladder as findings.
_LEVEL_TO_SEV_CLASS = {"error": "error", "warning": "warning", "note": "info"}

# Severity ladder, ordered most→least serious so summary counts and the
# per-file listing render in a stable, meaningful order. Mirrors the
# ``Severity`` literal in :mod:`prthinker.schemas`.
_SEVERITIES: tuple[str, ...] = ("error", "warning", "info")

# Declared >=3 times across the markup, so hoisted to module constants
# (SonarQube python:S1192).
_DOCTYPE = "<!DOCTYPE html>"
_NO_FINDINGS = "No findings."
_CHARSET = '<meta charset="utf-8">'


def _esc(text: object) -> str:
    """Escape arbitrary (possibly model-derived) text for HTML body use."""
    return html.escape(str(text), quote=True)


def severity_counts(findings: list[InlineFinding]) -> dict[str, int]:
    """Count findings per severity, always returning all known buckets."""
    counts = {sev: 0 for sev in _SEVERITIES}
    for finding in findings:
        # Unknown severities (should not happen given the schema) are
        # bucketed under "info" rather than dropped, so the total stays
        # honest.
        counts[finding.severity if finding.severity in counts else "info"] += 1
    return counts


def _all_findings(result: ReviewResult) -> list[InlineFinding]:
    """Gather top-level and per-file findings into one flat list."""
    findings: list[InlineFinding] = list(result.inline_findings)
    for file_result in result.per_file:
        findings.extend(file_result.inline_findings)
    return findings


def _render_summary(counts: dict[str, int], total: int) -> str:
    """Render the severity-count summary block."""
    items = [
        f'<li class="sev-{sev}">{_esc(sev)}: {counts[sev]}</li>'
        for sev in _SEVERITIES
    ]
    return (
        '<section class="summary">'
        "<h2>Summary</h2>"
        f"<p>Total findings: {total}</p>"
        f'<ul>{"".join(items)}</ul>'
        "</section>"
    )


def _render_finding(finding: InlineFinding) -> str:
    """Render one finding as a list item with path:line and severity."""
    location = f"{_esc(finding.path)}:{finding.line}"
    return (
        f'<li class="finding sev-{_esc(finding.severity)}">'
        f'<span class="loc">{location}</span> '
        f'<span class="sev">[{_esc(finding.severity)}]</span> '
        f'<span class="msg">{_esc(finding.comment)}</span>'
        "</li>"
    )


def _file_label(file_result: FileReviewResult) -> str:
    """Header label for a per-file section, flagging binary/deleted files."""
    label = _esc(file_result.path)
    if file_result.is_deleted:
        return f"{label} (deleted)"
    if file_result.is_binary:
        return f"{label} (binary)"
    return label


def _render_file_section(file_result: FileReviewResult) -> str:
    """Render one per-file section with its findings."""
    if file_result.inline_findings:
        body = "<ul>" + "".join(
            _render_finding(f) for f in file_result.inline_findings
        ) + "</ul>"
    else:
        body = f"<p>{_NO_FINDINGS}</p>"
    return (
        '<section class="file">'
        f"<h3>{_file_label(file_result)}</h3>"
        f"{body}"
        "</section>"
    )


def _render_top_level(findings: list[InlineFinding]) -> str:
    """Render top-level (not per-file) findings, if any exist."""
    if not findings:
        return ""
    body = "<ul>" + "".join(_render_finding(f) for f in findings) + "</ul>"
    return (
        '<section class="top-findings">'
        "<h3>Findings</h3>"
        f"{body}"
        "</section>"
    )


def _render_files(result: ReviewResult) -> str:
    """Render top-level findings plus every per-file section."""
    top = _render_top_level(result.inline_findings)
    if not result.per_file:
        sections = top or f"<p>{_NO_FINDINGS}</p>"
        return f'<section class="files">{sections}</section>'
    file_sections = "".join(_render_file_section(fr) for fr in result.per_file)
    return f'<section class="files">{top}{file_sections}</section>'


def _render_signal(signal: SignalFinding) -> str:
    """Render one orientation signal as a list item."""
    sev_class = _LEVEL_TO_SEV_CLASS.get(signal.level, "info")
    if signal.path is not None:
        loc = _esc(signal.path)
        if signal.line is not None:
            loc = f"{loc}:{signal.line}"
        location = f'<span class="loc">{loc}</span> '
    else:
        location = ""
    return (
        f'<li class="signal sev-{sev_class}">'
        f'<span class="sev">[{_esc(signal.level)}]</span> '
        f'<span class="rule">{_esc(signal.name)}</span> '
        f"{location}"
        f'<span class="msg">{_esc(signal.message)}</span>'
        "</li>"
    )


def _render_signals(result: ReviewResult) -> str:
    """Render the no-model orientation-signal section, or '' when empty."""
    signals = collect_signal_findings(result.code_diff or "")
    if not signals:
        return ""
    items = "".join(_render_signal(s) for s in signals)
    return (
        '<section class="signals">'
        "<h2>Orientation signals</h2>"
        f"<ul>{items}</ul>"
        "</section>"
    )


def render_report(result: ReviewResult, *, title: str = "prthinker review") -> str:
    """Render a self-contained, XSS-safe HTML review document as a string."""
    findings = _all_findings(result)
    counts = severity_counts(findings)
    safe_title = _esc(title)
    return (
        f"{_DOCTYPE}\n"
        '<html lang="en"><head>'
        f"{_CHARSET}"
        f"<title>{safe_title}</title>"
        "</head><body>"
        f"<h1>{safe_title}</h1>"
        f"{_render_summary(counts, len(findings))}"
        f"{_render_signals(result)}"
        f"{_render_files(result)}"
        "</body></html>\n"
    )


def write_report(result: ReviewResult, out_path: Path) -> None:
    """Render ``result`` and write the HTML document to ``out_path``."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as handle:
        handle.write(render_report(result))


__all__ = ["render_report", "write_report", "severity_counts"]

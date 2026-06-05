"""Registry of file-based report formats and the ``--report-dir`` writer.

Every file-based exporter (SARIF, HTML, CodeClimate, JUnit, CSV, metrics,
Markdown, SonarQube) is registered here once with its canonical filename
and writer. ``write_report_dir`` then emits *all* of them into one
directory with standard names, so a CI job can publish the full set with a
single ``--report-dir`` flag instead of eight separate path flags. The
GitHub Actions annotations output is intentionally absent — it writes
workflow commands to stdout, not a file.

Runner-safe: every registered writer is itself runner-safe.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from prthinker.codequality import write_codequality
from prthinker.csv_report import write_csv
from prthinker.html_report import write_report
from prthinker.junit_report import write_junit
from prthinker.markdown_report import write_markdown
from prthinker.metrics import write_metrics
from prthinker.sarif import write_sarif
from prthinker.sonar_report import write_sonar

if TYPE_CHECKING:
    from prthinker.pipeline import ReviewResult


@dataclass(frozen=True)
class ReportFormat:
    """One file-based report format: name, default filename, writer."""

    name: str
    filename: str
    write: Callable[["ReviewResult", "str | Path"], None]


REPORT_FORMATS: tuple[ReportFormat, ...] = (
    ReportFormat("sarif", "prthinker.sarif", write_sarif),
    ReportFormat("html", "report.html", write_report),
    ReportFormat("markdown", "report.md", write_markdown),
    ReportFormat("codequality", "gl-code-quality.json", write_codequality),
    ReportFormat("sonar", "sonar-issues.json", write_sonar),
    ReportFormat("junit", "junit.xml", write_junit),
    ReportFormat("csv", "findings.csv", write_csv),
    ReportFormat("metrics", "metrics.json", write_metrics),
)


def write_report_dir(result: "ReviewResult", out_dir: "str | Path") -> list[Path]:
    """Write every registered report format into ``out_dir``.

    Creates the directory if needed and returns the list of paths written
    (in registry order) so the caller can log them.
    """
    directory = Path(out_dir)
    directory.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for fmt in REPORT_FORMATS:
        path = directory / fmt.filename
        fmt.write(result, path)
        written.append(path)
    return written


__all__ = ["REPORT_FORMATS", "ReportFormat", "write_report_dir"]

"""Unit tests for :mod:`prthinker.ignore` suppression of inline findings."""

from __future__ import annotations

from pathlib import Path

from prthinker.ignore import IgnoreSpec, filter_findings, load_ignore
from prthinker.schemas import (
    InlineFinding,
    Provenance,
    ProvenanceCitation,
)


def _finding(
    path: str,
    *,
    severity: str = "info",
    comment: str = "some remark",
    provenance: Provenance | None = None,
) -> InlineFinding:
    """Build an :class:`InlineFinding` with sane defaults for the tests."""
    return InlineFinding(
        path=path,
        line=1,
        severity=severity,  # type: ignore[arg-type]
        comment=comment,
        provenance=provenance,
    )


def test_glob_path_match_drops(tmp_path: Path) -> None:
    """A finding whose path matches a glob is dropped."""
    ignore_file = tmp_path / ".prthinkerignore"
    ignore_file.write_text("tests/*\n", encoding="utf-8")
    spec = load_ignore(ignore_file)

    findings = [_finding("tests/test_a.py"), _finding("src/app.py")]
    kept = filter_findings(findings, spec)

    assert [f.path for f in kept] == ["src/app.py"]


def test_rule_suppression(tmp_path: Path) -> None:
    """A finding mentioning a suppressed rule id is dropped."""
    ignore_file = tmp_path / ".prthinkerignore"
    ignore_file.write_text("rule:E501\n", encoding="utf-8")
    spec = load_ignore(ignore_file)

    findings = [
        _finding("a.py", comment="Line violates E501 length limit"),
        _finding("b.py", comment="Unrelated remark"),
    ]
    kept = filter_findings(findings, spec)

    assert [f.path for f in kept] == ["b.py"]


def test_rule_suppression_via_provenance(tmp_path: Path) -> None:
    """A rule id surfaced only in a provenance note still suppresses."""
    ignore_file = tmp_path / ".prthinkerignore"
    ignore_file.write_text("rule:no-mutable-default\n", encoding="utf-8")
    spec = load_ignore(ignore_file)

    prov = Provenance(
        citations=[
            ProvenanceCitation(kind="rag_rule", note="matches no-mutable-default")
        ]
    )
    findings = [_finding("a.py", comment="plain", provenance=prov)]
    kept = filter_findings(findings, spec)

    assert kept == []


def test_severity_suppression(tmp_path: Path) -> None:
    """Findings at a suppressed severity are dropped, others kept."""
    ignore_file = tmp_path / ".prthinkerignore"
    ignore_file.write_text("severity:info\n", encoding="utf-8")
    spec = load_ignore(ignore_file)

    findings = [
        _finding("a.py", severity="info"),
        _finding("b.py", severity="warning"),
        _finding("c.py", severity="error"),
    ]
    kept = filter_findings(findings, spec)

    assert [f.path for f in kept] == ["b.py", "c.py"]


def test_comments_and_blank_lines_ignored(tmp_path: Path) -> None:
    """Comment lines and blank lines contribute no patterns."""
    ignore_file = tmp_path / ".prthinkerignore"
    ignore_file.write_text(
        "# a comment\n\n   \n# another\n", encoding="utf-8"
    )
    spec = load_ignore(ignore_file)

    assert spec.is_empty
    findings = [_finding("a.py"), _finding("b.py")]
    assert filter_findings(findings, spec) == findings


def test_missing_file_is_noop_keep_all(tmp_path: Path) -> None:
    """A missing ignore file yields an empty spec that keeps every finding."""
    spec = load_ignore(tmp_path / "does_not_exist")

    assert spec == IgnoreSpec()
    assert spec.is_empty
    findings = [_finding("a.py"), _finding("b.py")]
    assert filter_findings(findings, spec) == findings


def test_multiple_patterns(tmp_path: Path) -> None:
    """A spec mixing globs, a rule, and a severity drops each matching kind."""
    ignore_file = tmp_path / ".prthinkerignore"
    ignore_file.write_text(
        "# mixed spec\n"
        "vendor/**\n"
        "*.lock\n"
        "rule:B101\n"
        "severity:info\n",
        encoding="utf-8",
    )
    spec = load_ignore(ignore_file)

    findings = [
        _finding("vendor/dep/x.py", severity="warning"),  # glob
        _finding("poetry.lock", severity="warning"),  # glob
        _finding("a.py", severity="warning", comment="uses B101 assert"),  # rule
        _finding("b.py", severity="info"),  # severity
        _finding("src/keep.py", severity="warning", comment="real bug"),  # kept
    ]
    kept = filter_findings(findings, spec)

    assert [f.path for f in kept] == ["src/keep.py"]


def test_non_matching_paths_are_kept(tmp_path: Path) -> None:
    """Findings whose path matches no glob are retained."""
    ignore_file = tmp_path / ".prthinkerignore"
    ignore_file.write_text("docs/*\n*.md\n", encoding="utf-8")
    spec = load_ignore(ignore_file)

    findings = [
        _finding("src/app.py"),
        _finding("lib/util.py"),
    ]
    kept = filter_findings(findings, spec)

    assert kept == findings


def test_empty_findings_list(tmp_path: Path) -> None:
    """Filtering an empty finding list returns an empty list."""
    ignore_file = tmp_path / ".prthinkerignore"
    ignore_file.write_text("*.py\n", encoding="utf-8")
    spec = load_ignore(ignore_file)

    assert filter_findings([], spec) == []


def test_filter_returns_new_list_when_empty_spec() -> None:
    """An empty spec returns a copy, not the original list object."""
    findings = [_finding("a.py")]
    result = filter_findings(findings, IgnoreSpec())

    assert result == findings
    assert result is not findings

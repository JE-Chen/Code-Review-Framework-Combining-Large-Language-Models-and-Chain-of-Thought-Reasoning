"""Tests for the deterministic PR-label computation."""

from __future__ import annotations

from prthinker import pr_labels
from prthinker.pipeline import FileReviewResult, ReviewResult
from prthinker.schemas import InlineFinding


def _fr(path: str, sev: str | None = None, **kw) -> FileReviewResult:
    findings = [InlineFinding(path=path, line=1, comment="x", severity=sev)] if sev else []
    return FileReviewResult(
        path=path, rag_docs=[], step_outputs={}, inline_findings=findings, **kw
    )


def _review(per_file: list[FileReviewResult]) -> ReviewResult:
    return ReviewResult(code_diff="", rag_docs=[], per_file=per_file)


def test_size_buckets():
    assert pr_labels.compute_labels(_review([_fr("a.py")]))[0] == "prthinker/size-xs"
    files = [_fr(f"f{i}.py") for i in range(30)]
    assert pr_labels.compute_labels(_review(files))[0] == "prthinker/size-m"
    big = [_fr(f"f{i}.py") for i in range(200)]
    assert pr_labels.compute_labels(_review(big))[0] == "prthinker/size-xl"


def test_status_label_picks_worst_severity():
    err = _review([_fr("a.py", "error"), _fr("b.py", "warning")])
    assert "prthinker/changes-requested" in pr_labels.compute_labels(err)
    warn = _review([_fr("a.py", "warning"), _fr("b.py", "info")])
    assert "prthinker/review-suggested" in pr_labels.compute_labels(warn)
    clean = _review([_fr("a.py")])
    assert "prthinker/clean" in pr_labels.compute_labels(clean)


def test_size_ignores_binary_and_deleted():
    files = [_fr("a.py"), _fr("x.bin", is_binary=True), _fr("d.py", is_deleted=True)]
    # Only a.py counts → size-xs.
    assert pr_labels.compute_labels(_review(files))[0] == "prthinker/size-xs"

"""Behaviour tests for :mod:`prthinker.formatters`.

Covers the three high-complexity targets (``_format_provenance_block``,
``_format_file_block``, ``_format_per_file``) on happy paths, edge cases,
and the empty / skip branches so the extract-method refactor stays
behaviour-preserving.
"""

from __future__ import annotations

from prthinker import formatters
from prthinker.pipeline import FileReviewResult, ReviewResult
from prthinker.schemas import (
    InlineFinding,
    Provenance,
    ProvenanceCitation,
)

_MARKER = "<!-- prthinker -->"


def _finding(**kw) -> InlineFinding:
    base = {"path": "a.py", "line": 10, "comment": "do thing"}
    base.update(kw)
    return InlineFinding(**base)


def _file_result(**kw) -> FileReviewResult:
    base = {
        "path": "a.py",
        "rag_docs": [],
        "step_outputs": {},
        "inline_findings": [],
    }
    base.update(kw)
    return FileReviewResult(**base)


# --------------------------------------------------------------------------
# _format_provenance_block
# --------------------------------------------------------------------------

def test_provenance_block_renders_citations_and_confidence():
    cite = ProvenanceCitation(kind="rag_rule", index=3, note="why")
    finding = _finding(
        line=12,
        provenance=Provenance(citations=[cite], confidence=0.42),
    )
    block = formatters._format_provenance_block([finding])
    text = "\n".join(block)
    assert "<details><summary>Audit trail (provenance)</summary>" in text
    assert "**line 12**" in text
    assert "model confidence 0.42" in text
    assert "- RAG rule #3 — why" in text
    assert block[-2] == "</details>"


def test_provenance_block_all_citation_kinds():
    cites = [
        ProvenanceCitation(kind="rag_rule", index=1),
        ProvenanceCitation(kind="accepted_example", index=2),
        ProvenanceCitation(kind="diff_evidence", lines=[5, 6]),
        ProvenanceCitation(kind="diff_evidence", lines=[]),
        # index None falls through the elif chain to the kind fallback label.
        ProvenanceCitation(kind="rag_rule", index=None),
    ]
    finding = _finding(provenance=Provenance(citations=cites, confidence=None))
    lines = formatters._format_provenance_block([finding])
    text = "\n".join(lines)
    assert "- RAG rule #1" in text
    assert "- Accepted example #2" in text
    assert "- Diff line(s) 5, 6" in text
    assert "- Diff" in lines
    assert "- rag_rule" in lines
    # No confidence line when confidence is None.
    assert "model confidence" not in text


def test_provenance_block_empty_when_no_payload():
    finding = _finding(provenance=Provenance(citations=[], confidence=None))
    assert formatters._format_provenance_block([finding]) == []


def test_provenance_block_empty_when_provenance_none():
    finding = _finding(provenance=None)
    assert formatters._format_provenance_block([finding]) == []


def test_provenance_block_confidence_only_no_citations():
    finding = _finding(provenance=Provenance(citations=[], confidence=0.9))
    text = "\n".join(formatters._format_provenance_block([finding]))
    assert "model confidence 0.90" in text


# --------------------------------------------------------------------------
# _format_file_block
# --------------------------------------------------------------------------

def test_file_block_skipped_binary():
    fr = _file_result(is_binary=True)
    block = formatters._format_file_block(fr)
    assert block == ["- <code>a.py</code> — _skipped (binary)_", ""]


def test_file_block_skipped_deleted():
    fr = _file_result(is_deleted=True)
    block = formatters._format_file_block(fr)
    assert block == ["- <code>a.py</code> — _skipped (deleted)_", ""]


def test_file_block_no_findings_badge():
    fr = _file_result(step_outputs={"first_summary": "hi"})
    text = "\n".join(formatters._format_file_block(fr))
    assert "<code>a.py</code> — no findings" in text
    assert "_no summary_" in text
    assert "<details><summary>PR Summary</summary>" in text
    assert text.strip().endswith("</details>")


def test_file_block_with_findings_and_provenance():
    cite = ProvenanceCitation(kind="rag_rule", index=1)
    f = _finding(provenance=Provenance(citations=[cite], confidence=0.5))
    fr = _file_result(inline_findings=[f], step_outputs={"total_summary": "x"})
    text = "\n".join(formatters._format_file_block(fr))
    assert "— 1 finding(s)" in text
    assert "Audit trail (provenance)" in text
    # total_summary is excluded from per-step detail blocks.
    assert "<details><summary>Total Summary</summary>" not in text


def test_file_block_excludes_reserved_step_names():
    fr = _file_result(
        step_outputs={
            "total_summary": "a",
            "inline_findings": "b",
            "counterfactual": "c",
            "linter": "real",
        }
    )
    text = "\n".join(formatters._format_file_block(fr))
    assert "<details><summary>Lint Findings</summary>" in text
    assert "real" in text
    assert "<details><summary>Counterfactual</summary>" not in text


# --------------------------------------------------------------------------
# _format_per_file / format_pr_comment
# --------------------------------------------------------------------------

def _review(**kw) -> ReviewResult:
    base = {"code_diff": "", "rag_docs": []}
    base.update(kw)
    return ReviewResult(**base)


def test_per_file_header_counts():
    fr_ok = _file_result(path="a.py")
    fr_bin = _file_result(path="b.bin", is_binary=True)
    result = _review(per_file=[fr_ok, fr_bin])
    out = formatters.format_pr_comment(result, _MARKER)
    assert out.startswith(_MARKER)
    assert "Reviewed **1** file(s)." in out
    assert "Skipped **1** (binary / deleted)." in out
    assert "## CoT Code Review (per-file)" in out


def test_per_file_no_skips_header():
    result = _review(per_file=[_file_result(path="a.py")])
    out = formatters.format_pr_comment(result, _MARKER)
    assert "Reviewed **1** file(s)." in out
    assert "Skipped" not in out


def test_per_file_total_findings_and_overall_summary():
    f = _finding()
    fr = _file_result(inline_findings=[f])
    result = _review(per_file=[fr], step_outputs={"total_summary": "the overall"})
    out = formatters.format_pr_comment(result, _MARKER)
    assert "Found **1** inline finding(s)" in out
    assert "Posted **1** inline finding(s)." not in out
    assert "### Overall Summary" in out
    assert "the overall" in out


def test_per_file_findings_summary_with_posted_count():
    fr = _file_result(inline_findings=[_finding(line=10), _finding(line=20)])
    result = _review(per_file=[fr])
    out = formatters.format_pr_comment(result, _MARKER, posted_count=1)
    assert "**Inline findings**" in out
    assert "- Found **2** inline finding(s)" in out
    assert "- **1** posted to the diff" in out
    assert "- **1** outside the diff hunks (not posted)" in out


def test_per_file_findings_summary_all_posted_hides_outside_line():
    fr = _file_result(inline_findings=[_finding(line=10), _finding(line=20)])
    result = _review(per_file=[fr])
    out = formatters.format_pr_comment(result, _MARKER, posted_count=2)
    assert "- Found **2** inline finding(s)" in out
    assert "- **2** posted to the diff" in out
    assert "outside the diff hunks" not in out


def test_per_file_findings_summary_without_posted_count():
    fr = _file_result(inline_findings=[_finding()])
    result = _review(per_file=[fr])
    out = formatters.format_pr_comment(result, _MARKER)
    assert "- Found **1** inline finding(s)" in out
    assert "posted to the diff" not in out


def test_format_findings_summary_zero_total_renders_nothing():
    assert formatters._format_findings_summary(0, None) == []
    assert formatters._format_findings_summary(0, 0) == []


def test_format_findings_summary_posted_zero_shows_outside():
    out = formatters._format_findings_summary(3, 0)
    assert "- Found **3** inline finding(s)" in out
    assert "- **0** posted to the diff" in out
    assert "- **3** outside the diff hunks (not posted)" in out


# --------------------------------------------------------------------------
# format_pr_comment_pages (multi-comment pagination)
# --------------------------------------------------------------------------

def _padded_file(path: str, pad: int) -> FileReviewResult:
    return _file_result(
        path=path,
        step_outputs={"total_summary": "x" * pad, "first_code_review": "y" * pad},
    )


def test_pages_single_when_under_cap():
    result = _review(per_file=[_file_result(path="a.py")])
    pages = formatters.format_pr_comment_pages(result, _MARKER)
    assert len(pages) == 1
    # Single page is byte-identical to the non-paginated render.
    assert pages[0] == formatters.format_pr_comment(result, _MARKER)


def test_pages_split_between_file_blocks_preserves_all():
    files = [_padded_file(f"f{i}.py", 120) for i in range(6)]
    result = _review(per_file=files, step_outputs={"total_summary": "overall"})
    pages = formatters.format_pr_comment_pages(result, _MARKER, max_chars=700)
    assert len(pages) > 1
    # Every page stays under the cap and carries the marker for upsert.
    assert all(len(p) <= 700 for p in pages)
    assert all(_MARKER in p for p in pages)
    # No file block is lost across the split.
    joined = "\n".join(pages)
    for i in range(6):
        assert f"f{i}.py" in joined


def test_pages_label_and_continuation_header():
    files = [_padded_file(f"f{i}.py", 120) for i in range(6)]
    result = _review(per_file=files)
    pages = formatters.format_pr_comment_pages(result, _MARKER, max_chars=700)
    total = len(pages)
    assert f"_Part 1 of {total}_" in pages[0]
    assert f"_Part {total} of {total}_" in pages[-1]
    assert "<!-- prthinker:part=1/" in pages[0]
    # Intro / header only on the first page; later pages are continuations.
    assert "## CoT Code Review (per-file)" in pages[0]
    assert "Reviewed **6** file(s)." in pages[0]
    assert "(per-file, continued)" in pages[1]
    assert "Reviewed **6**" not in pages[1]


def test_pages_oversized_single_block_still_emitted():
    # One block alone exceeds the budget — it must still appear (it is
    # capped later by the comment-body limit, never dropped).
    result = _review(per_file=[_padded_file("huge.py", 2000)])
    pages = formatters.format_pr_comment_pages(result, _MARKER, max_chars=500)
    assert "huge.py" in "\n".join(pages)


# --------------------------------------------------------------------------
# findings_only mode
# --------------------------------------------------------------------------

def test_findings_only_hides_clean_files():
    dirty = _file_result(path="bug.py", inline_findings=[_finding(path="bug.py")])
    clean = _file_result(path="ok.py")
    result = _review(per_file=[dirty, clean])
    out = formatters.format_pr_comment(result, _MARKER, findings_only=True)
    assert "bug.py" in out
    assert "ok.py" not in out
    assert "1 file(s) reviewed with no findings — hidden." in out


def test_findings_only_off_shows_clean_files():
    dirty = _file_result(path="bug.py", inline_findings=[_finding(path="bug.py")])
    clean = _file_result(path="ok.py")
    result = _review(per_file=[dirty, clean])
    out = formatters.format_pr_comment(result, _MARKER, findings_only=False)
    assert "ok.py" in out
    assert "hidden." not in out


def test_findings_only_zero_findings_collapses_to_one_liner():
    result = _review(per_file=[_file_result(path="a.py"), _file_result(path="b.py")])
    out = formatters.format_pr_comment(result, _MARKER, findings_only=True)
    assert out.startswith(_MARKER)
    assert "✅ No findings across 2 reviewed file(s)." in out
    assert "<details>" not in out


def test_findings_only_zero_findings_excludes_binary_from_count():
    result = _review(per_file=[
        _file_result(path="a.py"),
        _file_result(path="x.bin", is_binary=True),
    ])
    out = formatters.format_pr_comment(result, _MARKER, findings_only=True)
    # Only the one real reviewed file counts; the binary is not reviewed.
    assert "✅ No findings across 1 reviewed file(s)." in out


def test_findings_only_pages_collapse_when_mostly_clean():
    files = [_padded_file(f"clean{i}.py", 120) for i in range(8)]
    files.append(_file_result(path="bug.py", inline_findings=[_finding(path="bug.py")]))
    result = _review(per_file=files)
    # Without findings_only this paginates; with it, only bug.py remains.
    pages = formatters.format_pr_comment_pages(
        result, _MARKER, max_chars=700, findings_only=True
    )
    assert len(pages) == 1
    assert "bug.py" in pages[0]
    assert "clean0.py" not in pages[0]


def test_per_file_ends_with_newline_and_no_trailing_blank():
    result = _review(per_file=[_file_result(path="a.py")])
    out = formatters.format_pr_comment(result, _MARKER)
    assert out.endswith("\n")
    assert not out.endswith("\n\n")

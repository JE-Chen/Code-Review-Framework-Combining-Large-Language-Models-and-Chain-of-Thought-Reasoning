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


def test_provenance_block_flags_empty_payload_as_model_judgement():
    # A finding whose provenance ran but produced no citation is surfaced
    # as model judgement rather than dropped (so nothing is hidden).
    finding = _finding(provenance=Provenance(citations=[], confidence=None))
    text = "\n".join(formatters._format_provenance_block([finding]))
    assert "Audit trail (provenance)" in text
    assert "model judgement — no external citation" in text


def test_provenance_block_empty_when_provenance_none():
    finding = _finding(provenance=None)
    assert formatters._format_provenance_block([finding]) == []


def test_provenance_block_empty_when_all_provenance_none():
    findings = [_finding(provenance=None), _finding(provenance=None)]
    assert formatters._format_provenance_block(findings) == []


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
    assert "— 🔵1" in text
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
    pages = formatters.format_pr_comment_pages(result, _MARKER, max_chars=1500)
    assert len(pages) > 1
    # Every page stays under the cap and carries the marker for upsert.
    assert all(len(p) <= 1500 for p in pages)
    assert all(_MARKER in p for p in pages)
    # No file block is lost across the split.
    joined = "\n".join(pages)
    for i in range(6):
        assert f"f{i}.py" in joined


def test_pages_label_and_continuation_header():
    files = [_padded_file(f"f{i}.py", 120) for i in range(6)]
    result = _review(per_file=files)
    pages = formatters.format_pr_comment_pages(result, _MARKER, max_chars=1500)
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


def test_overview_block_at_top_with_severity_and_status():
    findings = [
        _finding(path="a.py", severity="error"),
        _finding(path="a.py", severity="warning"),
        _finding(path="b.py", severity="info"),
    ]
    a = _file_result(path="a.py", inline_findings=findings[:2])
    b = _file_result(path="b.py", inline_findings=findings[2:])
    out = formatters.format_pr_comment(_review(per_file=[a, b]), _MARKER)
    glance = out.index("### 🔎 Review at a glance")
    # The digest sits above the detailed per-file blocks.
    assert glance < out.index("<details>")
    assert "🔴 Changes requested" in out
    assert "🔴 1 error · 🟡 1 warning · 🔵 1 info (3 total)" in out
    assert "2 reviewed · 2 with findings · 0 clean" in out
    assert "**Hotspots:**" in out and "`a.py` (2)" in out


def test_overview_status_warning_when_no_errors():
    fr = _file_result(path="a.py", inline_findings=[_finding(severity="warning")])
    out = formatters.format_pr_comment(_review(per_file=[fr]), _MARKER)
    assert "🟡 Review suggested" in out
    assert "Changes requested" not in out


def test_overview_status_clean_has_no_hotspots():
    out = formatters.format_pr_comment(
        _review(per_file=[_file_result(path="a.py")]), _MARKER
    )
    assert "✅ Looks good — no findings" in out
    assert "**Hotspots:**" not in out


def test_hide_info_drops_info_findings_from_summary():
    fr = _file_result(path="a.py", inline_findings=[
        _finding(path="a.py", line=1, severity="warning"),
        _finding(path="a.py", line=2, severity="info"),
    ])
    out = formatters.format_pr_comment(_review(per_file=[fr]), _MARKER, hide_info=True)
    # info is excluded from the count badge and the at-a-glance tally.
    assert "🔴 0 error · 🟡 1 warning · 🔵 0 info (1 total)" in out
    assert "<code>a.py</code> — 🟡1" in out


def test_hide_info_off_keeps_info():
    fr = _file_result(path="a.py", inline_findings=[
        _finding(path="a.py", line=2, severity="info"),
    ])
    out = formatters.format_pr_comment(_review(per_file=[fr]), _MARKER, hide_info=False)
    assert "🔵 1" in out
    assert "<code>a.py</code> — 🔵1" in out


def test_hide_info_with_findings_only_collapses_info_only_pr():
    # A file whose only finding is info becomes "clean" once info is hidden.
    fr = _file_result(path="a.py", inline_findings=[
        _finding(path="a.py", severity="info"),
    ])
    out = formatters.format_pr_comment(
        _review(per_file=[fr]), _MARKER, findings_only=True, hide_info=True
    )
    assert "✅ No findings across 1 reviewed file(s)." in out


def test_hide_info_does_not_mutate_original_result():
    fr = _file_result(path="a.py", inline_findings=[
        _finding(path="a.py", severity="info", comment="fyi"),
    ])
    result = _review(per_file=[fr])
    formatters.format_pr_comment(result, _MARKER, hide_info=True)
    # Display filter must not strip findings from the caller's result.
    assert len(result.per_file[0].inline_findings) == 1


def test_file_summary_has_status_icon_prefix():
    err = _file_result(path="e.py", inline_findings=[_finding(path="e.py", severity="error")])
    warn = _file_result(path="w.py", inline_findings=[_finding(path="w.py", severity="warning")])
    clean = _file_result(path="c.py")
    out = formatters.format_pr_comment(_review(per_file=[err, warn, clean]), _MARKER)
    # Each file's <summary> opens with a worst-severity status glyph.
    assert "<summary>🔴 " in out
    assert "<summary>🟡 " in out
    assert "<summary>✅ " in out


def test_file_status_icon_helper():
    f = lambda sev: _finding(severity=sev)  # noqa: E731
    assert formatters._file_status_icon([f("info"), f("error")]) == "🔴"
    assert formatters._file_status_icon([f("info"), f("warning")]) == "🟡"
    assert formatters._file_status_icon([f("info")]) == "🔵"
    assert formatters._file_status_icon([]) == "✅"


def test_severity_badge_shows_icons():
    fr = _file_result(path="a.py", inline_findings=[
        _finding(path="a.py", severity="error"),
        _finding(path="a.py", severity="error"),
        _finding(path="a.py", severity="warning"),
    ])
    text = "\n".join(formatters._format_file_block(fr))
    assert "— 🔴2 🟡1" in text


def test_files_sorted_by_severity_then_count():
    err = _file_result(path="err.py", inline_findings=[_finding(path="err.py", severity="error")])
    warn = _file_result(path="warn.py", inline_findings=[_finding(path="warn.py", severity="warning")])
    clean = _file_result(path="clean.py")
    # Input order is clean, warn, err; output must be err, warn, clean.
    out = formatters.format_pr_comment(_review(per_file=[clean, warn, err]), _MARKER)
    assert out.index("err.py") < out.index("warn.py") < out.index("clean.py")


def test_deep_links_when_files_url_given():
    import hashlib
    fr = _file_result(path="a.py", inline_findings=[_finding(path="a.py", line=7)])
    out = formatters.format_pr_comment(
        _review(per_file=[fr]), _MARKER, files_url="https://github.com/o/r/pull/1/files"
    )
    anchor = hashlib.sha256(b"a.py").hexdigest()
    assert f"https://github.com/o/r/pull/1/files#diff-{anchor}R7" in out
    # Hotspot in the digest is a markdown link; the file header is an <a>.
    assert "](https://github.com/o/r/pull/1/files#diff-" in out
    assert '<a href="https://github.com/o/r/pull/1/files#diff-' in out


def test_no_links_when_files_url_absent():
    fr = _file_result(path="a.py", inline_findings=[_finding(path="a.py", line=7)])
    out = formatters.format_pr_comment(_review(per_file=[fr]), _MARKER)
    assert "<code>a.py</code>" in out
    assert "diff-" not in out


def test_must_fix_block_lists_errors_at_top():
    fr = _file_result(path="a.py", inline_findings=[
        _finding(path="a.py", line=4, severity="error", comment="boom\nmore"),
        _finding(path="a.py", line=9, severity="warning", comment="meh"),
    ])
    out = formatters.format_pr_comment(_review(per_file=[fr]), _MARKER)
    assert "### 🚨 Must fix" in out
    # Pinned above the at-a-glance digest.
    assert out.index("🚨 Must fix") < out.index("Review at a glance")
    # One-liner only (no second comment line), with the error location.
    assert "🔴 `a.py:4` — boom" in out
    assert "more" not in out.split("Review at a glance")[0].split("Must fix")[1]


def test_must_fix_absent_when_no_errors():
    fr = _file_result(path="a.py", inline_findings=[_finding(severity="warning")])
    out = formatters.format_pr_comment(_review(per_file=[fr]), _MARKER)
    assert "Must fix" not in out


def test_must_fix_caps_and_counts_overflow():
    findings = [_finding(path="a.py", line=i, severity="error") for i in range(1, 8)]
    fr = _file_result(path="a.py", inline_findings=findings)
    out = formatters.format_pr_comment(_review(per_file=[fr]), _MARKER)
    assert "… and 2 more error(s)" in out


def test_error_file_auto_expands():
    err = _file_result(path="e.py", inline_findings=[_finding(path="e.py", severity="error")])
    warn = _file_result(path="w.py", inline_findings=[_finding(path="w.py", severity="warning")])
    out = formatters.format_pr_comment(_review(per_file=[err, warn]), _MARKER)
    assert "<details open><summary>" in out          # error file expanded
    assert "<details><summary>" in out               # warning file collapsed


def test_signal_note_shows_verified_and_low_repro():
    from prthinker.schemas import SuggestionVerification
    verified = _finding(
        path="a.py", line=1, severity="warning",
        suggestion="x", verification=SuggestionVerification(status="pass", verify_cmd="pytest"),
    )
    shaky = _finding(path="a.py", line=2, severity="warning", reproducibility="low")
    out = "\n".join(formatters._format_file_block(
        _file_result(path="a.py", inline_findings=[verified, shaky])
    ))
    assert "_Signal: ✓ 1 verified · ⚠️ 1 low-repro_" in out


def test_min_confidence_drops_low_and_keeps_unknown():
    from prthinker.schemas import Provenance
    low = _finding(path="a.py", line=1, severity="warning",
                   provenance=Provenance(citations=[], confidence=0.2))
    high = _finding(path="a.py", line=2, severity="warning",
                    provenance=Provenance(citations=[], confidence=0.9))
    unknown = _finding(path="a.py", line=3, severity="warning")  # no provenance
    fr = _file_result(path="a.py", inline_findings=[low, high, unknown])
    out = formatters.format_pr_comment(
        _review(per_file=[fr]), _MARKER, min_confidence=0.5
    )
    # low (0.2) dropped → 2 of 3 remain in the badge / tally.
    assert "🟡2" in out
    assert "🟡 2 warning" in out  # at-a-glance warning tally


def test_min_confidence_zero_keeps_all():
    from prthinker.schemas import Provenance
    low = _finding(path="a.py", severity="warning",
                   provenance=Provenance(citations=[], confidence=0.1))
    out = formatters.format_pr_comment(
        _review(per_file=[_file_result(path="a.py", inline_findings=[low])]),
        _MARKER, min_confidence=0.0,
    )
    assert "🟡1" in out


def test_summary_table_renders_rows_not_blocks():
    findings = [
        _finding(path="a.py", line=4, severity="error", comment="boom"),
        _finding(path="b.py", line=9, severity="warning", comment="meh|pipe"),
    ]
    a = _file_result(path="a.py", inline_findings=[findings[0]])
    b = _file_result(path="b.py", inline_findings=[findings[1]])
    out = formatters.format_pr_comment(_review(per_file=[a, b]), _MARKER, table=True)
    assert "| | Location | Finding |" in out
    assert "| 🔴 | `a.py:4` | boom |" in out
    assert "| 🟡 | `b.py:9` | meh\\|pipe |"  # pipe escaped
    # Table mode replaces the collapsible per-file blocks (no per-file
    # "**Summary**" sections, no auto-expanded error file blocks).
    assert "**Summary**" not in out
    assert "<details open>" not in out


def test_summary_table_pages_single():
    files = [_padded_file(f"f{i}.py", 120) for i in range(6)]
    for fr in files:
        fr.inline_findings = [_finding(path=fr.path, severity="warning")]
    pages = formatters.format_pr_comment_pages(
        _review(per_file=files), _MARKER, max_chars=300, table=True
    )
    # Compact table is never block-paginated.
    assert len(pages) == 1
    assert "| | Location | Finding |" in pages[0]


def test_format_digest_standalone():
    fr = _file_result(path="a.py", inline_findings=[_finding(severity="error")])
    digest = formatters.format_digest(_review(per_file=[fr]))
    assert digest.startswith("### 🔎 Review at a glance")
    assert "🔴 Changes requested" in digest
    # Standalone digest carries no file blocks.
    assert "<details>" not in digest


def test_gate_line_in_digest():
    fr = _file_result(path="a.py", inline_findings=[_finding(severity="error")])
    out = formatters.format_pr_comment(
        _review(per_file=[fr]), _MARKER, gate="❌ failure (gate-on: error; 1 error, 0 warning)"
    )
    assert "- **Gate:** ❌ failure (gate-on: error; 1 error, 0 warning)" in out


def test_no_gate_line_when_absent():
    fr = _file_result(path="a.py", inline_findings=[_finding(severity="warning")])
    out = formatters.format_pr_comment(_review(per_file=[fr]), _MARKER)
    assert "**Gate:**" not in out


def test_severity_groups_block():
    err = _file_result(path="e.py", inline_findings=[_finding(path="e.py", severity="error")])
    warn = _file_result(path="w.py", inline_findings=[_finding(path="w.py", severity="warning")])
    out = formatters.format_pr_comment(_review(per_file=[err, warn]), _MARKER)
    assert "<details><summary>By severity (2 group(s))</summary>" in out
    assert "🔴 **error** (1 file(s)):" in out
    assert "🟡 **warning** (1 file(s)):" in out


def test_review_footer_and_legend():
    fr = _file_result(path="a.py", inline_findings=[_finding()])
    footer = formatters.format_review_footer(
        _review(per_file=[fr]),
        head_sha="abcdef1234", backend="anthropic", model="claude",
        version="0.1.0", generated_at="2026-06-03 04:00 UTC",
    )
    assert "Review metadata:" in footer
    assert "commit `abcdef12`" in footer
    assert "anthropic" in footer and "claude" in footer
    assert "prthinker 0.1.0" in footer
    assert "2026-06-03 04:00 UTC" in footer
    assert "1 reviewed / 0 skipped" in footer
    # Legend explains the glyphs.
    assert "<details><summary>Legend</summary>" in footer
    assert "🔴 error · 🟡 warning · 🔵 info" in footer


def test_review_footer_minimal_omits_empty_fields():
    footer = formatters.format_review_footer(_review(per_file=[_file_result(path="a.py")]))
    assert "Review metadata:" in footer
    assert "commit" not in footer  # no head_sha given
    assert "prthinker" not in footer.split("Legend")[0]  # no version given


def test_delta_line_in_digest():
    fr = _file_result(path="a.py", inline_findings=[_finding(path="a.py")])
    out = formatters.format_pr_comment(
        _review(per_file=[fr]), _MARKER, delta="+2 new · 1 resolved · 3 carried"
    )
    assert "- **Since last review:** +2 new · 1 resolved · 3 carried" in out


def test_no_delta_line_when_absent():
    fr = _file_result(path="a.py", inline_findings=[_finding(path="a.py")])
    out = formatters.format_pr_comment(_review(per_file=[fr]), _MARKER)
    assert "Since last review" not in out


def test_preliminary_pinned_above_glance_and_files():
    fr = _file_result(path="a.py", inline_findings=[_finding(path="a.py")])
    out = formatters.format_pr_comment(
        _review(per_file=[fr]), _MARKER,
        preliminary="### 📋 What this PR does (preliminary)\n\n- **Changes:** 1 file",
    )
    assert "What this PR does (preliminary)" in out
    assert out.index("What this PR does") < out.index("Review at a glance")
    assert out.index("Review at a glance") < out.index("<details>")


def test_preliminary_shown_on_clean_pr_comment():
    result = _review(per_file=[_file_result(path="a.py")])
    out = formatters.format_pr_comment(
        result, _MARKER, findings_only=True,
        preliminary="### 📋 What this PR does (preliminary)\n\n- **Changes:** 1 file",
    )
    assert "What this PR does (preliminary)" in out
    assert "✅ No findings across 1 reviewed file(s)." in out


def test_preliminary_only_on_first_page():
    files = [_padded_file(f"f{i}.py", 120) for i in range(6)]
    pages = formatters.format_pr_comment_pages(
        _review(per_file=files), _MARKER, max_chars=1500,
        preliminary="### 📋 What this PR does (preliminary)\n\n- **Changes:** 6 files",
    )
    assert len(pages) > 1
    assert "What this PR does" in pages[0]
    assert all("What this PR does" not in p for p in pages[1:])


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


# --------------------------------------------------------------------------
# Suggestions aggregate (digest)
# --------------------------------------------------------------------------

def test_suggestions_line_counts_one_click_and_verified():
    from prthinker.schemas import SuggestionVerification

    verified = _finding(
        path="a.py", suggestion="x = 1",
        verification=SuggestionVerification(status="pass", verify_cmd="pytest"),
    )
    plain = _finding(path="a.py", line=20, suggestion="y = 2")
    fr = _file_result(path="a.py", inline_findings=[verified, plain])
    out = formatters.format_pr_comment(_review(per_file=[fr]), _MARKER)
    assert "- **Suggestions:** 2 one-click fix(es) · 1 sandbox-verified" in out


def test_suggestions_line_absent_when_no_suggestions():
    fr = _file_result(path="a.py", inline_findings=[_finding(path="a.py")])
    out = formatters.format_pr_comment(_review(per_file=[fr]), _MARKER)
    assert "**Suggestions:**" not in out


def test_suggestions_line_omits_verified_when_none():
    fr = _file_result(
        path="a.py", inline_findings=[_finding(path="a.py", suggestion="z = 3")]
    )
    out = formatters.format_pr_comment(_review(per_file=[fr]), _MARKER)
    assert "- **Suggestions:** 1 one-click fix(es)" in out
    assert "sandbox-verified" not in out


# --------------------------------------------------------------------------
# Review-effort estimate (digest)
# --------------------------------------------------------------------------

def test_effort_estimate_present_and_scales_with_severity():
    clean = _review(per_file=[_file_result(path="a.py")])
    out_clean = formatters.format_pr_comment(clean, _MARKER)
    assert "- **Review effort:** ~" in out_clean
    # error weight (5) > info weight (1): an error PR estimates more time.
    err = _review(per_file=[
        _file_result(path="a.py", inline_findings=[_finding(severity="error")])
    ])
    assert (
        formatters._effort_estimate_minutes(err)
        > formatters._effort_estimate_minutes(clean)
    )


def test_effort_line_reports_files_needing_attention():
    fr = _file_result(path="a.py", inline_findings=[_finding(path="a.py")])
    out = formatters.format_pr_comment(_review(per_file=[fr]), _MARKER)
    assert "file(s) need attention" in out


# --------------------------------------------------------------------------
# By-category index (#3)
# --------------------------------------------------------------------------

def test_category_index_groups_by_bucket():
    sec = _finding(path="a.py", line=5, category="security")
    perf = _finding(path="b.py", line=7, category="performance")
    fr = _file_result(path="a.py", inline_findings=[sec])
    fr2 = _file_result(path="b.py", inline_findings=[perf])
    out = formatters.format_pr_comment(_review(per_file=[fr, fr2]), _MARKER)
    assert "<details><summary>By category (2 group(s))</summary>" in out
    assert "🛡️ **security** (1):" in out
    assert "⚡ **performance** (1):" in out


def test_category_index_absent_when_uncategorised():
    fr = _file_result(path="a.py", inline_findings=[_finding(path="a.py")])
    out = formatters.format_pr_comment(_review(per_file=[fr]), _MARKER)
    assert "By category" not in out


def test_category_index_caps_refs():
    findings = [
        _finding(path="a.py", line=i, category="style") for i in range(1, 12)
    ]
    fr = _file_result(path="a.py", inline_findings=findings)
    out = formatters.format_pr_comment(_review(per_file=[fr]), _MARKER)
    assert "🎨 **style** (11):" in out
    assert "+3 more" in out  # 11 findings, 8 shown


# --------------------------------------------------------------------------
# Off-diff findings block (#1)
# --------------------------------------------------------------------------

def test_off_diff_block_lists_unposted_findings():
    fr = _file_result(path="a.py", inline_findings=[_finding(path="a.py")])
    off = (_finding(path="z.py", line=99, comment="ghost line"),)
    out = formatters.format_pr_comment(
        _review(per_file=[fr]), _MARKER, off_diff_findings=off
    )
    assert "1 finding(s) outside the diff (not posted inline)" in out
    assert "ghost line" in out


def test_off_diff_block_absent_when_empty():
    fr = _file_result(path="a.py", inline_findings=[_finding(path="a.py")])
    out = formatters.format_pr_comment(_review(per_file=[fr]), _MARKER)
    assert "outside the diff (not posted inline)" not in out


# --------------------------------------------------------------------------
# first_finding_ref (#2 helper)
# --------------------------------------------------------------------------

def test_first_finding_ref_picks_priority_severity():
    findings = [
        _finding(path="a.py", line=3, severity="warning"),
        _finding(path="b.py", line=8, severity="error"),
    ]
    ref = formatters.first_finding_ref(findings, ("error", "warning"))
    assert ref == "`b.py:8`"


def test_first_finding_ref_none_when_no_match():
    findings = [_finding(severity="info")]
    assert formatters.first_finding_ref(findings, ("error",)) is None


# --------------------------------------------------------------------------
# Oversized-block pagination split (#7)
# --------------------------------------------------------------------------

def test_oversized_single_block_split_across_pages():
    # One file whose block alone dwarfs the page budget must be split into
    # several self-contained <details> blocks rather than truncated.
    big = _file_result(
        path="huge.py",
        inline_findings=[_finding(path="huge.py")],
        step_outputs={"total_summary": "s", "first_code_review": "q" * 4000},
    )
    pages = formatters.format_pr_comment_pages(
        _review(per_file=[big]), _MARKER, max_chars=1200
    )
    assert len(pages) > 1
    # Every page that opens a details block also closes one (valid markup).
    for page in pages:
        assert page.count("<details") <= page.count("</details>")
    assert any("(continued)" in page for page in pages)


def test_split_file_block_passthrough_when_small():
    block = "<details><summary>x</summary>\n\nbody\n</details>\n"
    assert formatters._split_file_block(block, 10_000) == [block]


# --------------------------------------------------------------------------
# Per-file change badge (#3)
# --------------------------------------------------------------------------

_BADGE_DIFF = (
    "diff --git a/a.py b/a.py\n"
    "--- a/a.py\n"
    "+++ b/a.py\n"
    "@@ -1,1 +1,2 @@\n"
    " ctx\n"
    "+added one\n"
    "+added two\n"
)


def test_file_block_shows_change_badge():
    fr = _file_result(path="a.py", inline_findings=[_finding(path="a.py")])
    out = formatters.format_pr_comment(
        _review(per_file=[fr], code_diff=_BADGE_DIFF), _MARKER
    )
    assert "(+2 −0)" in out


def test_file_block_no_badge_without_diff():
    fr = _file_result(path="a.py", inline_findings=[_finding(path="a.py")])
    out = formatters.format_pr_comment(_review(per_file=[fr]), _MARKER)
    # No diff text → no change badge in the summary line.
    assert "−0)" not in out and "−1)" not in out


# --------------------------------------------------------------------------
# extra_sections carrier
# --------------------------------------------------------------------------

def test_extra_sections_render_after_indexes_before_files():
    fr = _file_result(path="a.py", inline_findings=[_finding(path="a.py")])
    out = formatters.format_pr_comment(
        _review(per_file=[fr]), _MARKER,
        extra_sections=("**Injected section** here",),
    )
    assert "**Injected section** here" in out
    # Sits below the digest and above the per-file detail block.
    assert out.index("Review at a glance") < out.index("Injected section")
    assert out.index("Injected section") < out.index("**Summary**")


def test_extra_sections_skip_empty_strings():
    fr = _file_result(path="a.py", inline_findings=[_finding(path="a.py")])
    out = formatters.format_pr_comment(
        _review(per_file=[fr]), _MARKER, extra_sections=("", "  ", "real"),
    )
    assert "real" in out


# --------------------------------------------------------------------------
# Reviewer checklist (#5)
# --------------------------------------------------------------------------

def test_checklist_includes_unverified_error_and_low_repro():
    err = _finding(path="a.py", line=3, severity="error", comment="null deref")
    low = _finding(path="a.py", line=7, reproducibility="low", comment="maybe racy")
    fr = _file_result(path="a.py", inline_findings=[err, low])
    out = formatters.format_reviewer_checklist(_review(per_file=[fr]))
    assert "Reviewer checklist (2 item(s))" in out
    assert "- [ ] Verify the fix for `a.py:3`" in out
    assert "- [ ] Re-confirm (low reproducibility) `a.py:7`" in out


def test_checklist_skips_verified_error():
    from prthinker.schemas import SuggestionVerification

    err = _finding(
        path="a.py", severity="error", suggestion="x",
        verification=SuggestionVerification(status="pass", verify_cmd="pytest"),
    )
    fr = _file_result(path="a.py", inline_findings=[err])
    assert formatters.format_reviewer_checklist(_review(per_file=[fr])) == ""


def test_checklist_includes_api_drift():
    from prthinker.schemas import ApiDriftFinding

    drift = ApiDriftFinding(
        backend_path="api.py", frontend_path="api.ts", summary="diverged",
    )
    out = formatters.format_reviewer_checklist(_review(api_drift=[drift]))
    assert "Confirm cross-language contract `api.py` ↔ `api.ts`" in out


def test_checklist_empty_when_nothing_to_verify():
    fr = _file_result(path="a.py", inline_findings=[_finding(severity="info")])
    assert formatters.format_reviewer_checklist(_review(per_file=[fr])) == ""


# --------------------------------------------------------------------------
# Must-fix code snippet (#2)
# --------------------------------------------------------------------------

_SNIPPET_DIFF = (
    "diff --git a/a.py b/a.py\n"
    "--- a/a.py\n"
    "+++ b/a.py\n"
    "@@ -1,1 +1,2 @@\n"
    " ctx\n"
    "+    return user_input  # unsanitised\n"
)


def test_must_fix_quotes_offending_line():
    err = _finding(path="a.py", line=2, severity="error", comment="injection")
    fr = _file_result(path="a.py", inline_findings=[err])
    out = formatters.format_pr_comment(
        _review(per_file=[fr], code_diff=_SNIPPET_DIFF), _MARKER
    )
    assert "🚨 Must fix" in out
    assert "↳ <code>return user_input  # unsanitised</code>" in out


def test_must_fix_no_snippet_when_line_off_diff():
    err = _finding(path="a.py", line=99, severity="error", comment="ghost")
    fr = _file_result(path="a.py", inline_findings=[err])
    out = formatters.format_pr_comment(
        _review(per_file=[fr], code_diff=_SNIPPET_DIFF), _MARKER
    )
    assert "ghost" in out
    assert "↳ <code>" not in out


def test_must_fix_snippet_html_escaped():
    diff = (
        "diff --git a/a.py b/a.py\n--- a/a.py\n+++ b/a.py\n"
        "@@ -1,0 +1,1 @@\n+x = a < b & c\n"
    )
    err = _finding(path="a.py", line=1, severity="error", comment="cmp")
    fr = _file_result(path="a.py", inline_findings=[err])
    out = formatters.format_pr_comment(_review(per_file=[fr], code_diff=diff), _MARKER)
    assert "x = a &lt; b &amp; c" in out


# --------------------------------------------------------------------------
# Top findings queue (#3)
# --------------------------------------------------------------------------

def test_top_findings_ranks_across_files_by_severity():
    fr1 = _file_result(path="a.py", inline_findings=[
        _finding(path="a.py", line=1, severity="info", comment="nit"),
        _finding(path="a.py", line=2, severity="warning", comment="warn"),
    ])
    fr2 = _file_result(path="b.py", inline_findings=[
        _finding(path="b.py", line=3, severity="error", comment="boom"),
        _finding(path="b.py", line=4, severity="info", comment="nit2"),
    ])
    out = formatters.format_pr_comment(_review(per_file=[fr1, fr2]), _MARKER)
    assert "🔝 Top 4 of 4 findings" in out
    # Error ranks first in the queue.
    assert out.index("boom") < out.index("warn") < out.index("nit")


def test_top_findings_skipped_when_few():
    fr = _file_result(path="a.py", inline_findings=[
        _finding(path="a.py", line=1, severity="error", comment="one"),
        _finding(path="a.py", line=2, severity="warning", comment="two"),
    ])
    out = formatters.format_pr_comment(_review(per_file=[fr]), _MARKER)
    assert "Top" not in out.split("Must fix")[0]  # no top-findings header
    assert "🔝" not in out


def test_top_findings_confidence_breaks_severity_ties():
    from prthinker.schemas import Provenance

    findings = [
        _finding(path="a.py", line=1, severity="warning", comment="low-conf",
                 provenance=Provenance(confidence=0.2)),
        _finding(path="a.py", line=2, severity="warning", comment="high-conf",
                 provenance=Provenance(confidence=0.9)),
        _finding(path="a.py", line=3, severity="info", comment="i1"),
        _finding(path="a.py", line=4, severity="info", comment="i2"),
    ]
    fr = _file_result(path="a.py", inline_findings=findings)
    out = formatters.format_pr_comment(_review(per_file=[fr]), _MARKER)
    assert out.index("high-conf") < out.index("low-conf")


# --------------------------------------------------------------------------
# Walkthrough block (#4)
# --------------------------------------------------------------------------

def test_walkthrough_rendered_above_summary():
    fr = _file_result(
        path="a.py",
        inline_findings=[_finding(path="a.py")],
        step_outputs={"walkthrough": "Adds a guard clause.", "total_summary": "ok"},
    )
    out = formatters.format_pr_comment(_review(per_file=[fr]), _MARKER)
    assert "**📝 Walkthrough**" in out
    assert "Adds a guard clause." in out
    # Orientation precedes the review summary inside the file block.
    assert out.index("Walkthrough") < out.index("**Summary**")


def test_walkthrough_not_rendered_as_generic_step_detail():
    fr = _file_result(
        path="a.py",
        inline_findings=[_finding(path="a.py")],
        step_outputs={"walkthrough": "narrative"},
    )
    out = formatters.format_pr_comment(_review(per_file=[fr]), _MARKER)
    # Reserved: must not show up as a "Walkthrough" collapsible step block.
    assert "<details><summary>Walkthrough</summary>" not in out


def test_walkthrough_absent_when_step_did_not_run():
    fr = _file_result(path="a.py", inline_findings=[_finding(path="a.py")])
    out = formatters.format_pr_comment(_review(per_file=[fr]), _MARKER)
    assert "📝 Walkthrough" not in out

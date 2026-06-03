"""PR-comment markdown + JSONL store round-trips."""

from __future__ import annotations

from prthinker.accepted import AcceptedExample, AcceptedExamplesStore
from prthinker.dismissed import DismissedExample, DismissedExamplesStore
from prthinker.formatters import format_pr_comment
from prthinker.pipeline import FileReviewResult, ReviewResult
from prthinker.rules import load_rules_dir
from prthinker.schemas import InlineFinding


_MARKER = "<!-- prthinker:summary -->"


def test_single_pass_comment_contains_total_and_marker() -> None:
    result = ReviewResult(
        code_diff="", rag_docs=[],
        step_outputs={
            "first_summary": "S",
            "first_code_review": "R",
            "linter": "L",
            "code_smell": "C",
            "total_summary": "TOTAL",
        },
    )
    body = format_pr_comment(result, marker=_MARKER)
    assert body.startswith(_MARKER)
    assert "TOTAL" in body
    # Per-step blocks render as <details>.
    assert "<details>" in body


def test_per_file_layout_renders_one_block_per_file() -> None:
    fr_a = FileReviewResult(
        path="a.py", rag_docs=[],
        step_outputs={"total_summary": "A summary"},
        inline_findings=[],
    )
    fr_b = FileReviewResult(
        path="b.py", rag_docs=[],
        step_outputs={"total_summary": "B summary"},
        inline_findings=[InlineFinding(
            path="b.py", line=1, severity="warning", comment="x",
        )],
    )
    result = ReviewResult(
        code_diff="", rag_docs=[],
        step_outputs={},
        inline_findings=fr_b.inline_findings,
        per_file=[fr_a, fr_b],
    )
    body = format_pr_comment(result, marker=_MARKER)
    assert "<code>a.py</code>" in body
    assert "<code>b.py</code>" in body
    # Top-level header reports inline findings, per-file row reports findings.
    assert "Found **1** inline finding(s)" in body
    assert "1 finding(s)" in body


def test_empty_result_renders_no_summary_text() -> None:
    body = format_pr_comment(
        ReviewResult(code_diff="", rag_docs=[]),
        marker=_MARKER,
    )
    assert "No total summary" in body


# ----- DismissedExamplesStore + AcceptedExamplesStore ---------------------

def test_dismissed_store_append_and_reload(tmp_jsonl) -> None:
    store = DismissedExamplesStore(tmp_jsonl)
    store.append(DismissedExample(
        path="a.py", comment="false positive — already handled",
        reason="thumbs-down",
    ))
    store.append(DismissedExample(
        path="b.py", comment="not relevant", reason="reply match",
    ))
    reloaded = DismissedExamplesStore(tmp_jsonl)
    assert len(reloaded) == 2
    paths = [e.path for e in reloaded]
    assert paths == ["a.py", "b.py"]


def test_accepted_store_round_trip(tmp_jsonl) -> None:
    store = AcceptedExamplesStore(tmp_jsonl)
    store.append(AcceptedExample(
        path="a.py", comment="use Path.resolve",
        suggestion="path = Path(p).resolve()", pr_number=42,
    ))
    reloaded = AcceptedExamplesStore(tmp_jsonl)
    assert len(reloaded) == 1
    ex = list(reloaded)[0]
    assert ex.path == "a.py"
    assert ex.suggestion == "path = Path(p).resolve()"
    assert ex.pr_number == 42


# ----- rules-dir loader ---------------------------------------------------

def test_rules_dir_returns_sorted_markdown_files(tmp_rules_dir) -> None:
    rules = load_rules_dir(tmp_rules_dir)
    assert len(rules) == 2
    assert any("pathlib" in r for r in rules)
    assert any("logging" in r for r in rules)


def test_rules_dir_handles_missing_directory(tmp_path) -> None:
    rules = load_rules_dir(tmp_path / "does-not-exist")
    assert rules == []


def test_rules_dir_handles_none() -> None:
    assert load_rules_dir(None) == []

"""Tests for the incremental per-file review writer."""

from __future__ import annotations

import json
from pathlib import Path

from prthinker.incremental_save import (
    IncrementalReviewWriter,
    ReviewMeta,
    _slug_for_path,
    list_completed_files,
    load_file_result,
    serialize_file_result,
    serialize_review_result,
)
from prthinker.pipeline import FileReviewResult, ReviewResult
from prthinker.schemas import InlineFinding


def _finding(path: str, line: int, comment: str = "x") -> InlineFinding:
    return InlineFinding(
        path=path, line=line, severity="warning", comment=comment, suggestion=""
    )


def _file_result(path: str, *, findings: list[InlineFinding] | None = None) -> FileReviewResult:
    return FileReviewResult(
        path=path,
        rag_docs=["rule-1"],
        step_outputs={"summary": f"summary of {path}"},
        inline_findings=findings or [],
    )


def test_slug_replaces_separators_and_unsafe_chars():
    assert _slug_for_path("a/b.py") == "a__b.py"
    assert _slug_for_path("a\\b.py") == "a__b.py"
    assert _slug_for_path("a/b/c d.py") == "a__b__c_d.py"
    assert _slug_for_path("") == "_unnamed"


def test_writer_creates_files_dir_and_meta(tmp_path: Path):
    meta = ReviewMeta(repo="o/r", pr_number=1, head_sha="abc", started_at="t")
    writer = IncrementalReviewWriter(tmp_path / "out", meta=meta)
    assert (tmp_path / "out" / "files").is_dir()
    meta_payload = json.loads((tmp_path / "out" / "meta.json").read_text("utf-8"))
    assert meta_payload == {
        "repo": "o/r", "pr_number": 1, "head_sha": "abc", "started_at": "t"
    }
    assert writer.files_dir == tmp_path / "out" / "files"


def test_write_file_result_is_atomic_and_visible(tmp_path: Path):
    writer = IncrementalReviewWriter(tmp_path / "out")
    fr = _file_result("src/a.py", findings=[_finding("src/a.py", 7, "bad name")])
    target = writer.write_file_result(fr)

    assert target.exists()
    payload = json.loads(target.read_text("utf-8"))
    assert payload["path"] == "src/a.py"
    assert payload["inline_findings"][0]["line"] == 7
    # No leftover .tmp files
    assert list((tmp_path / "out" / "files").glob("*.tmp")) == []


def test_multiple_files_each_get_their_own_json(tmp_path: Path):
    writer = IncrementalReviewWriter(tmp_path / "out")
    for path in ["src/a.py", "src/b.py", "docs/c.md"]:
        writer.write_file_result(_file_result(path))
    completed = list_completed_files(tmp_path / "out")
    assert {p.name for p in completed} == {
        "src__a.py.json", "src__b.py.json", "docs__c.md.json"
    }


def test_write_file_result_overwrites_same_path(tmp_path: Path):
    writer = IncrementalReviewWriter(tmp_path / "out")
    writer.write_file_result(_file_result("a.py"))
    fr2 = _file_result("a.py")
    fr2.step_outputs = {"summary": "v2"}
    writer.write_file_result(fr2)
    completed = list_completed_files(tmp_path / "out")
    assert len(completed) == 1
    payload = load_file_result(completed[0])
    assert payload["step_outputs"]["summary"] == "v2"


def test_write_final_emits_review_json(tmp_path: Path):
    writer = IncrementalReviewWriter(tmp_path / "out")
    result = ReviewResult(
        code_diff="--- a\n+++ b\n",
        rag_docs=["rule-1"],
        per_file=[_file_result("a.py"), _file_result("b.py")],
    )
    writer.write_final(result)
    payload = json.loads((tmp_path / "out" / "review.json").read_text("utf-8"))
    assert [fr["path"] for fr in payload["per_file"]] == ["a.py", "b.py"]
    assert payload["rag_docs"] == ["rule-1"]


def test_serialize_round_trip_keeps_fields(tmp_path: Path):
    fr = _file_result(
        "x.py", findings=[_finding("x.py", 1, "c1"), _finding("x.py", 2, "c2")]
    )
    data = serialize_file_result(fr)
    assert data["path"] == "x.py"
    assert [f["comment"] for f in data["inline_findings"]] == ["c1", "c2"]
    assert data["verdict"] is None
    assert data["counterfactuals"] == []


def test_partial_files_present_even_without_final(tmp_path: Path):
    """The whole point: a crash mid-run still leaves per-file JSONs readable."""
    writer = IncrementalReviewWriter(tmp_path / "out")
    writer.write_file_result(_file_result("a.py"))
    writer.write_file_result(_file_result("b.py"))
    # Simulate crash: no write_final call.
    assert not (tmp_path / "out" / "review.json").exists()
    completed = list_completed_files(tmp_path / "out")
    assert len(completed) == 2
    payloads = [load_file_result(p) for p in completed]
    assert sorted(p["path"] for p in payloads) == ["a.py", "b.py"]


def test_serialize_review_result_includes_top_level_fields(tmp_path: Path):
    result = ReviewResult(
        code_diff="diff", rag_docs=["r1", "r2"],
        step_outputs={"k": "v"},
        inline_findings=[_finding("a.py", 1)],
    )
    payload = serialize_review_result(result)
    assert payload["rag_docs"] == ["r1", "r2"]
    assert payload["step_outputs"] == {"k": "v"}
    assert payload["inline_findings"][0]["path"] == "a.py"
    assert payload["per_file"] == []

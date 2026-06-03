"""Tests for cross-run finding delta tracking."""

from __future__ import annotations

from pathlib import Path

from prthinker import review_delta
from prthinker.schemas import InlineFinding


def _f(path: str, comment: str, severity: str = "warning") -> InlineFinding:
    return InlineFinding(path=path, line=1, comment=comment, severity=severity)


def test_fingerprint_is_line_independent():
    a = InlineFinding(path="x.py", line=5, comment="Same issue", severity="warning")
    b = InlineFinding(path="x.py", line=99, comment="same   ISSUE", severity="warning")
    # Different lines + whitespace/case, same identity.
    assert review_delta.fingerprint(a) == review_delta.fingerprint(b)


def test_fingerprint_distinguishes_path_and_severity():
    base = _f("x.py", "msg", "warning")
    assert review_delta.fingerprint(base) != review_delta.fingerprint(_f("y.py", "msg"))
    assert review_delta.fingerprint(base) != review_delta.fingerprint(
        _f("x.py", "msg", "error")
    )


def test_compute_delta_counts_new_resolved_carried():
    prev = set(review_delta.fingerprints([_f("a.py", "old"), _f("b.py", "keep")]))
    current = [_f("b.py", "keep"), _f("c.py", "fresh")]
    delta = review_delta.compute_delta(prev, current)
    assert delta.new == 1       # c.py/fresh
    assert delta.resolved == 1  # a.py/old
    assert delta.carried == 1   # b.py/keep


def test_format_delta():
    delta = review_delta.ReviewDelta(new=2, resolved=3, carried=5)
    assert review_delta.format_delta(delta) == "+2 new · 3 resolved · 5 carried"


def test_load_returns_none_when_missing(tmp_path: Path):
    assert review_delta.load_fingerprints(tmp_path / "nope.json") is None


def test_save_then_load_roundtrip(tmp_path: Path):
    path = tmp_path / "state" / "fp.json"
    findings = [_f("a.py", "one"), _f("b.py", "two")]
    review_delta.save_fingerprints(path, findings)
    loaded = review_delta.load_fingerprints(path)
    assert loaded == set(review_delta.fingerprints(findings))


def test_load_corrupt_file_returns_none(tmp_path: Path):
    path = tmp_path / "fp.json"
    path.write_text("not json{", encoding="utf-8")
    assert review_delta.load_fingerprints(path) is None


def test_records_dedup_and_fields():
    recs = review_delta.records([_f("a.py", "msg"), _f("a.py", "msg")])
    assert len(recs) == 1
    assert recs[0]["path"] == "a.py" and recs[0]["severity"] == "warning"
    assert recs[0]["comment"] == "msg"


def test_resolved_records_finds_gone_findings():
    prev = review_delta.records([_f("a.py", "old"), _f("b.py", "keep")])
    resolved = review_delta.resolved_records(prev, [_f("b.py", "keep")])
    assert len(resolved) == 1 and resolved[0]["path"] == "a.py"


def test_save_persists_records_and_load(tmp_path: Path):
    path = tmp_path / "fp.json"
    review_delta.save_fingerprints(path, [_f("a.py", "one")])
    recs = review_delta.load_records(path)
    assert recs and recs[0]["path"] == "a.py"


def test_format_resolved_block_struck_through():
    block = review_delta.format_resolved_block(
        [{"path": "a.py", "comment": "fixed it", "fp": "x"}]
    )
    assert "✅ Resolved since last review (1)" in block
    assert "~~`a.py` — fixed it~~" in block


def test_format_resolved_block_empty():
    assert review_delta.format_resolved_block([]) == ""


# --- cli wiring: _review_progress (delta + dialogue + resolved) --------------

import argparse  # noqa: E402

from prthinker.cli_review import _review_progress  # noqa: E402
from prthinker.dialogue import AuthorReply  # noqa: E402
from prthinker.pipeline import FileReviewResult, ReviewResult  # noqa: E402


class _ReplyAdapter:
    def __init__(self, replies):
        self._replies = replies

    def fetch_author_replies(self):
        return self._replies


def _result(comments: list[str]) -> ReviewResult:
    findings = [_f("a.py", c) for c in comments]
    fr = FileReviewResult(
        path="a.py", rag_docs=[], step_outputs={}, inline_findings=findings,
    )
    return ReviewResult(
        code_diff="", rag_docs=[], inline_findings=findings, per_file=[fr],
    )


def _args(tmp_path: Path, **kw):
    base = {
        "review_delta": True, "dry_run": False,
        "delta_state": str(tmp_path / "fp.json"),
    }
    base.update(kw)
    return argparse.Namespace(**base)


def test_review_progress_first_run_returns_none_but_saves(tmp_path: Path):
    adapter = _ReplyAdapter([])
    line, resolved = _review_progress(_args(tmp_path), adapter, _result(["a"]))
    assert line is None and resolved is None
    assert (tmp_path / "fp.json").exists()


def test_review_progress_second_run_reports_delta_and_resolved(tmp_path: Path):
    adapter = _ReplyAdapter([AuthorReply(author="u", body="thanks")])
    a = _args(tmp_path)
    _review_progress(a, adapter, _result(["old", "keep"]))      # baseline
    line, resolved = _review_progress(a, adapter, _result(["keep", "new"]))
    assert "+1 new" in line and "1 resolved" in line
    assert "💬 1 author reply(ies)" in line
    assert resolved is not None and "old" in resolved


def test_review_progress_disabled_returns_none(tmp_path: Path):
    adapter = _ReplyAdapter([])
    line, resolved = _review_progress(
        _args(tmp_path, review_delta=False), adapter, _result(["a"])
    )
    assert line is None and resolved is None

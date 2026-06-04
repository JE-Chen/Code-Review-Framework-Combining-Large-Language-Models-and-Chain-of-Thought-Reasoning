"""Tests for prthinker.golden: golden-set regression snapshots."""

from __future__ import annotations

import json

from prthinker.golden import SnapshotDiff, diff_snapshot, write_snapshot
from prthinker.pipeline import ReviewResult
from prthinker.schemas import InlineFinding


def _result(*findings: InlineFinding) -> ReviewResult:
    return ReviewResult(
        code_diff="",
        rag_docs=[],
        inline_findings=list(findings),
    )


def _finding(path: str, line: int, comment: str, severity: str = "info") -> InlineFinding:
    return InlineFinding(path=path, line=line, comment=comment, severity=severity)


def test_write_then_diff_identical_is_empty(tmp_path):
    snapshot = str(tmp_path / "golden.json")
    result = _result(_finding("a.py", 3, "fix this"))
    write_snapshot(result, snapshot)

    diff = diff_snapshot(result, snapshot)

    assert diff == SnapshotDiff(added=[], removed=[])


def test_new_finding_shows_in_added(tmp_path):
    snapshot = str(tmp_path / "golden.json")
    write_snapshot(_result(_finding("a.py", 3, "fix this")), snapshot)

    fresh = _result(
        _finding("a.py", 3, "fix this"),
        _finding("b.py", 9, "new finding"),
    )
    diff = diff_snapshot(fresh, snapshot)

    assert diff.added == ["b.py::9::new finding"]
    assert diff.removed == []


def test_removed_finding_shows_in_removed(tmp_path):
    snapshot = str(tmp_path / "golden.json")
    write_snapshot(
        _result(
            _finding("a.py", 3, "fix this"),
            _finding("b.py", 9, "stale finding"),
        ),
        snapshot,
    )

    fresh = _result(_finding("a.py", 3, "fix this"))
    diff = diff_snapshot(fresh, snapshot)

    assert diff.added == []
    assert diff.removed == ["b.py::9::stale finding"]


def test_missing_snapshot_file_marks_everything_added(tmp_path):
    snapshot = str(tmp_path / "does-not-exist.json")
    fresh = _result(
        _finding("a.py", 3, "one"),
        _finding("b.py", 9, "two"),
    )

    diff = diff_snapshot(fresh, snapshot)

    assert diff.added == ["a.py::3::one", "b.py::9::two"]
    assert diff.removed == []


def test_empty_result_against_missing_snapshot_is_empty(tmp_path):
    snapshot = str(tmp_path / "does-not-exist.json")
    diff = diff_snapshot(_result(), snapshot)
    assert diff == SnapshotDiff(added=[], removed=[])


def test_roundtrip_stable_ordering(tmp_path):
    snapshot = str(tmp_path / "golden.json")
    # Insertion order is deliberately unsorted; output must be deterministic.
    unsorted = _result(
        _finding("z.py", 2, "later"),
        _finding("a.py", 5, "first"),
        _finding("a.py", 1, "earliest"),
    )
    sorted_input = _result(
        _finding("a.py", 1, "earliest"),
        _finding("a.py", 5, "first"),
        _finding("z.py", 2, "later"),
    )

    write_snapshot(unsorted, snapshot)
    first_bytes = (tmp_path / "golden.json").read_bytes()
    write_snapshot(sorted_input, snapshot)
    second_bytes = (tmp_path / "golden.json").read_bytes()

    assert first_bytes == second_bytes

    paths = [record["path"] for record in json.loads(first_bytes.decode("utf-8"))]
    assert paths == ["a.py", "a.py", "z.py"]

    # A snapshot written from either ordering diffs clean against the other.
    assert diff_snapshot(unsorted, snapshot) == SnapshotDiff(added=[], removed=[])


def test_severity_change_keeps_identity_key(tmp_path):
    # Identity key is (path, line, comment); severity is not part of it, so a
    # severity-only change is neither added nor removed.
    snapshot = str(tmp_path / "golden.json")
    write_snapshot(_result(_finding("a.py", 3, "msg", severity="info")), snapshot)

    fresh = _result(_finding("a.py", 3, "msg", severity="error"))
    diff = diff_snapshot(fresh, snapshot)

    assert diff == SnapshotDiff(added=[], removed=[])

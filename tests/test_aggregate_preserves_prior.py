"""Tests for `prthinker.cli.merge_partial_reviews`.

Codifies the project rule:

  A file's prior review result is NEVER lost from the posted PR review
  just because this run failed to refresh it.

The aggregate path is the only place the rule is actually enforced
on the GitHub side — submit_inline_review and evaluate_gate both
read the flat inline_findings list, so a prior-carried partial whose
top-level inline_findings was zeroed (as the workflow's write-state
step deliberately does) must still surface its per-file findings
into that flat list.
"""

from __future__ import annotations

import json
from pathlib import Path

from prthinker.cli import merge_partial_reviews


def _matrix_shard_payload(path: str, line: int, severity: str = "warning") -> dict:
    """Payload that an in-runner matrix shard writes via --output-json.

    The shard reviews exactly one file; the top-level inline_findings
    list mirrors per_file[0].inline_findings (the matrix workflow's
    actual on-disk shape).
    """
    finding = {
        "path": path,
        "line": line,
        "severity": severity,
        "comment": f"matrix-shard finding on {path}:{line}",
        "suggestion": "",
    }
    return {
        "code_diff": "",
        "rag_docs": [],
        "step_outputs": {},
        "inline_findings": [finding],
        "per_file": [
            {
                "path": path,
                "rag_docs": [],
                "step_outputs": {},
                "inline_findings": [finding],
                "verdict": None,
                "is_binary": False,
                "is_deleted": False,
            }
        ],
    }


def _carried_forward_payload(path: str, line: int, severity: str = "error") -> dict:
    """Payload shape the workflow's write-state step writes per file.

    Top-level inline_findings is INTENTIONALLY [] (the rewriter zeroes
    it) — the only path findings reach the aggregate from is
    per_file[0].inline_findings. The pre-fix aggregate dropped these
    on the floor.
    """
    finding = {
        "path": path,
        "line": line,
        "severity": severity,
        "comment": f"carried-forward finding on {path}:{line}",
        "suggestion": "",
    }
    return {
        "code_diff": "",
        "rag_docs": [],
        "step_outputs": {},
        "inline_findings": [],
        "per_file": [
            {
                "path": path,
                "rag_docs": [],
                "step_outputs": {},
                "inline_findings": [finding],
                "verdict": None,
                "is_binary": False,
                "is_deleted": False,
            }
        ],
    }


def _write(tmp_path: Path, name: str, payload: dict) -> Path:
    p = tmp_path / name
    p.write_text(json.dumps(payload), encoding="utf-8")
    return p


def test_carried_forward_partial_findings_reach_merged_inline(tmp_path):
    """The rule. A prior partial whose top-level inline_findings is []
    still contributes its per_file findings to merged.inline_findings.
    """
    paths = [_write(tmp_path, "aaa-prior.json",
                    _carried_forward_payload("src/a.py", 12))]
    merged = merge_partial_reviews(paths)
    assert [f.path for f in merged.inline_findings] == ["src/a.py"]
    assert [f.line for f in merged.inline_findings] == [12]
    assert [fr.path for fr in merged.per_file] == ["src/a.py"]


def test_matrix_shard_overrides_prior_for_same_path(tmp_path):
    """When a file is refreshed by THIS run, the new partial wins.

    The workflow names prior-state partials with an 'aaa-' prefix so
    they sort before matrix-shard partials; last-write-wins on the
    dedupe loop then guarantees the matrix output overrides.
    """
    paths = [
        _write(tmp_path, "aaa-prior.json",
               _carried_forward_payload("src/a.py", 12, severity="error")),
        _write(tmp_path, "partial-0.json",
               _matrix_shard_payload("src/a.py", 99, severity="warning")),
    ]
    merged = merge_partial_reviews(paths)
    assert len(merged.inline_findings) == 1
    assert merged.inline_findings[0].line == 99
    assert merged.inline_findings[0].severity == "warning"


def test_prior_and_new_files_both_surface(tmp_path):
    """Prior + new for DIFFERENT files both make it into the output."""
    paths = [
        _write(tmp_path, "aaa-prior-a.json",
               _carried_forward_payload("src/a.py", 12)),
        _write(tmp_path, "aaa-prior-b.json",
               _carried_forward_payload("src/b.py", 34)),
        _write(tmp_path, "partial-0.json",
               _matrix_shard_payload("src/c.py", 7)),
    ]
    merged = merge_partial_reviews(paths)
    assert sorted(fr.path for fr in merged.per_file) == [
        "src/a.py", "src/b.py", "src/c.py"
    ]
    assert sorted(f.path for f in merged.inline_findings) == [
        "src/a.py", "src/b.py", "src/c.py"
    ]


def test_empty_input_returns_empty_review(tmp_path):
    merged = merge_partial_reviews([])
    assert merged.per_file == []
    assert merged.inline_findings == []
    assert merged.code_diff == ""


def test_invalid_json_is_skipped_not_fatal(tmp_path):
    bad = tmp_path / "broken.json"
    bad.write_text("{ not json", encoding="utf-8")
    good = _write(tmp_path, "partial-0.json",
                  _matrix_shard_payload("src/a.py", 1))
    merged = merge_partial_reviews([bad, good])
    assert [fr.path for fr in merged.per_file] == ["src/a.py"]

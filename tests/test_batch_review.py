"""Batched trivial-file review: chunking, prompt, parsing, pipeline wiring."""

from __future__ import annotations

import json

from prthinker.batch_review import (
    MAX_BATCH_FILES,
    build_batch_prompt,
    chunk_batchable,
    parse_batch_findings,
)
from prthinker.diff import FileDiff, parse_unified_diff
from prthinker.pipeline import CoTPipeline, PerFileReviewOptions
from tests.conftest import FakeBackend


class NoOpRetriever:
    def retrieve(self, query: str) -> list[str]:
        del query
        return []


def _fd(path: str, added: int = 2) -> FileDiff:
    raw = "\n".join(
        [f"--- a/{path}", f"+++ b/{path}", "@@ -1,9 +1,9 @@"]
        + [f"+line {i}" for i in range(added)]
    )
    return parse_unified_diff(f"diff --git a/{path} b/{path}\n{raw}")[0]


# ---------------------------------------------------------------------------
# chunk_batchable
# ---------------------------------------------------------------------------


def test_chunk_respects_file_cap():
    fds = [_fd(f"f{i}.md") for i in range(MAX_BATCH_FILES + 2)]
    chunks = chunk_batchable(fds)
    assert [len(c) for c in chunks] == [MAX_BATCH_FILES, 2]
    assert [fd.path for c in chunks for fd in c] == [fd.path for fd in fds]


def test_chunk_respects_char_cap():
    big = _fd("big.md")
    big.raw = "x" * 20_000
    other = _fd("other.md")
    other.raw = "y" * 20_000
    chunks = chunk_batchable([big, other])
    assert [len(c) for c in chunks] == [1, 1]


def test_single_oversize_file_still_gets_a_chunk():
    huge = _fd("huge.md")
    huge.raw = "x" * 50_000
    assert [len(c) for c in chunk_batchable([huge])] == [1]


def test_chunk_empty_input():
    assert chunk_batchable([]) == []


# ---------------------------------------------------------------------------
# build_batch_prompt / parse_batch_findings
# ---------------------------------------------------------------------------


def test_prompt_lists_every_file_and_budget():
    fds = [_fd("a.md"), _fd("b.yml")]
    prompt = build_batch_prompt(fds, max_findings=7)
    assert "## File: a.md" in prompt
    assert "## File: b.yml" in prompt
    assert "at most 7 findings per file" in prompt


def test_parse_groups_by_path_and_validates():
    fds = [_fd("a.md", added=5), _fd("b.md", added=5)]
    raw = json.dumps(
        [
            {"path": "a.md", "line": 2, "severity": "warning", "comment": "w"},
            {"path": "b.md", "line": 3, "severity": "info", "comment": "i"},
            {"path": "ghost.md", "line": 1, "severity": "error", "comment": "x"},
        ]
    )
    by_path = parse_batch_findings(raw, fds)
    assert [f.comment for f in by_path["a.md"]] == ["w"]
    assert [f.comment for f in by_path["b.md"]] == ["i"]
    assert set(by_path) == {"a.md", "b.md"}  # ghost path dropped


def test_parse_clamps_to_commentable_lines():
    fds = [_fd("a.md", added=2)]  # new-side lines 1..2 only
    raw = json.dumps(
        [{"path": "a.md", "line": 99, "severity": "info", "comment": "off-diff"}]
    )
    assert parse_batch_findings(raw, fds)["a.md"] == []


def test_parse_malformed_payload_degrades_to_empty():
    fds = [_fd("a.md")]
    assert parse_batch_findings("total garbage", fds) == {"a.md": []}


def test_parse_non_dict_items_ignored():
    fds = [_fd("a.md")]
    assert parse_batch_findings('["str", 42]', fds) == {"a.md": []}


# ---------------------------------------------------------------------------
# Pipeline integration
# ---------------------------------------------------------------------------


def _docs_diff(paths: list[str]) -> str:
    parts = []
    for path in paths:
        parts += [
            f"diff --git a/{path} b/{path}",
            f"--- a/{path}",
            f"+++ b/{path}",
            "@@ -1,2 +1,2 @@",
            f"+update {path}",
        ]
    return "\n".join(parts)


def test_three_trivial_files_share_one_model_call():
    backend = FakeBackend(
        [json.dumps([{"path": "b.md", "line": 1, "severity": "info", "comment": "n"}])]
    )
    pipeline = CoTPipeline(backend=backend, retriever=NoOpRetriever())
    result = pipeline.run_per_file(
        _docs_diff(["a.md", "b.md", "c.md"]),
        PerFileReviewOptions(inline_review=True, step_plan="adaptive"),
    )
    assert len(backend.calls) == 1
    assert [fr.path for fr in result.per_file] == ["a.md", "b.md", "c.md"]
    by_path = {fr.path: fr for fr in result.per_file}
    assert [f.comment for f in by_path["b.md"].inline_findings] == ["n"]
    assert by_path["a.md"].inline_findings == []
    assert all(
        fr.step_outputs.get("step_plan") == "trivial" for fr in result.per_file
    )


def test_mixed_diff_batches_docs_and_loops_code():
    code_lines = [f"+line {i}" for i in range(50)]
    diff = _docs_diff(["a.md", "b.md"]) + "\n" + "\n".join(
        ["diff --git a/mod.py b/mod.py", "--- a/mod.py", "+++ b/mod.py",
         "@@ -1,60 +1,60 @@"] + code_lines
    )
    backend = FakeBackend(["[]", '{"summary": "ok", "findings": []}'])
    pipeline = CoTPipeline(backend=backend, retriever=NoOpRetriever())
    result = pipeline.run_per_file(
        diff,
        PerFileReviewOptions(inline_review=True, step_plan="adaptive"),
    )
    # One batch call for the two docs files + one unified call for mod.py.
    assert len(backend.calls) == 2
    assert [fr.path for fr in result.per_file] == ["a.md", "b.md", "mod.py"]


def test_full_plan_never_batches():
    backend = FakeBackend()
    pipeline = CoTPipeline(backend=backend, retriever=NoOpRetriever())
    pipeline.run_per_file(
        _docs_diff(["a.md", "b.md"]),
        PerFileReviewOptions(inline_review=True),
    )
    # Full plan: every file runs the whole chain individually (6 calls each).
    assert len(backend.calls) == 12


def test_tier_budgets_cap_generation():
    backend = FakeBackend(["[]", '{"summary": "ok", "findings": []}'])
    pipeline = CoTPipeline(backend=backend, retriever=NoOpRetriever())
    code_lines = [f"+line {i}" for i in range(50)]
    diff = _docs_diff(["a.md"]) + "\n" + "\n".join(
        ["diff --git a/mod.py b/mod.py", "--- a/mod.py", "+++ b/mod.py",
         "@@ -1,60 +1,60 @@"] + code_lines
    )
    pipeline.run_per_file(
        diff,
        PerFileReviewOptions(inline_review=True, step_plan="adaptive"),
    )
    budgets = sorted(tokens for _, tokens in backend.calls)
    # Batch call capped at the standard budget; unified standard call too.
    assert budgets == [8192, 8192]

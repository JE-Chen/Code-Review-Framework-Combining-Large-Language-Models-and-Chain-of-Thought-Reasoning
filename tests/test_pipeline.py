"""``CoTPipeline`` — end-to-end with a ``FakeBackend``.

Covers single-pass and per-file modes, the dismissed-filter integration
path, and the ``extra_rules`` merge into RAG docs.
"""

from __future__ import annotations

from reviewmind.pipeline import CoTPipeline
from reviewmind.rag import NoOpRetriever

from tests.conftest import FakeBackend


def test_single_pass_runs_all_registered_steps() -> None:
    backend = FakeBackend([
        "first_summary out",
        "first_code_review out",
        "linter out",
        "code_smell out",
        "total_summary out",
    ])
    pipeline = CoTPipeline(backend=backend, retriever=NoOpRetriever())
    result = pipeline.run("diff --git a/x b/x\n@@ -1 +1 @@\n-x\n+y\n")

    assert set(result.step_outputs) == {
        "first_summary", "first_code_review",
        "linter", "code_smell", "total_summary",
    }
    assert result.total_summary == "total_summary out"
    assert len(backend.calls) == 5


def test_per_file_runs_steps_per_file() -> None:
    # Two files × 5 steps = 10 generate() calls (inline_review disabled).
    backend = FakeBackend(["x"] * 20)
    pipeline = CoTPipeline(backend=backend, retriever=NoOpRetriever())
    diff = (
        "diff --git a/a.py b/a.py\n"
        "--- a/a.py\n+++ b/a.py\n@@ -1 +1,2 @@\n x\n+y\n"
        "diff --git a/b.py b/b.py\n"
        "--- a/b.py\n+++ b/b.py\n@@ -1 +1,2 @@\n z\n+w\n"
    )
    result = pipeline.run_per_file(diff, inline_review=False)
    assert len(result.per_file) == 2
    assert [fr.path for fr in result.per_file] == ["a.py", "b.py"]
    assert len(backend.calls) == 10  # 5 steps × 2 files


def test_per_file_with_inline_review_adds_findings_step() -> None:
    # 2 files × (5 base steps + 1 inline_findings step) = 12 calls.
    # The 6th call per file is inline_findings; return a JSON array.
    inline_payload = '[{"line": 1, "severity": "warning", "comment": "use logging"}]'
    backend = FakeBackend([
        "s1", "s2", "s3", "s4", "s5", inline_payload,
        "s1", "s2", "s3", "s4", "s5", inline_payload,
    ])
    pipeline = CoTPipeline(backend=backend, retriever=NoOpRetriever())
    diff = (
        "diff --git a/a.py b/a.py\n"
        "--- a/a.py\n+++ b/a.py\n@@ -1 +1,2 @@\n x\n+y\n"
        "diff --git a/b.py b/b.py\n"
        "--- a/b.py\n+++ b/b.py\n@@ -1 +1,2 @@\n z\n+w\n"
    )
    result = pipeline.run_per_file(diff, inline_review=True)
    assert len(result.inline_findings) == 2
    assert {f.path for f in result.inline_findings} == {"a.py", "b.py"}
    assert all(f.severity == "warning" for f in result.inline_findings)


def test_extra_rules_get_merged_into_context() -> None:
    backend = FakeBackend(["fine"] * 5)
    pipeline = CoTPipeline(
        backend=backend,
        retriever=NoOpRetriever(),
        extra_rules=("Team rule A", "Team rule B"),
    )
    pipeline.run("diff --git a/x b/x\n@@ -1 +1 @@\n-x\n+y\n")
    # Both extra rules should appear inside the rendered prompt for at
    # least one step.
    prompts = [call[0] for call in backend.calls]
    assert any("Team rule A" in p for p in prompts)
    assert any("Team rule B" in p for p in prompts)


def test_binary_and_deleted_files_skip_pipeline() -> None:
    backend = FakeBackend(["x"] * 100)
    pipeline = CoTPipeline(backend=backend, retriever=NoOpRetriever())
    diff = (
        "diff --git a/keep.py b/keep.py\n"
        "--- a/keep.py\n+++ b/keep.py\n@@ -1 +1,2 @@\n x\n+y\n"
        "diff --git a/gone.py b/gone.py\n"
        "deleted file mode 100644\n"
        "--- a/gone.py\n+++ /dev/null\n@@ -1 +0,0 @@\n-x\n"
        "diff --git a/logo.png b/logo.png\n"
        "Binary files a/logo.png and b/logo.png differ\n"
    )
    result = pipeline.run_per_file(diff, inline_review=False)
    assert [fr.path for fr in result.per_file] == ["keep.py"]
    assert len(backend.calls) == 5  # only the kept file

"""CoTPipeline integration with the repository context retriever.

The retriever is opt-in: when injected, each file review prompt is prefixed
with the retrieved cross-file context; when absent, prompts are unchanged.
"""

from __future__ import annotations

from pathlib import Path

from prthinker.pipeline import CoTPipeline, PerFileReviewOptions
from prthinker.rag import NoOpRetriever
from prthinker.repo_retrieval import RepoContext, RepoContextRetriever

from tests.conftest import FakeBackend

_DIFF = "diff --git a/a.py b/a.py\n--- a/a.py\n+++ b/a.py\n@@ -1 +1,2 @@\n x\n+y\n"


class _StubRepoRetriever(RepoContextRetriever):
    """Returns a fixed related file + symbol regardless of query."""

    def __init__(self, context: RepoContext) -> None:
        self._context = context
        self.queries: list[str] = []

    def retrieve(self, query: str, workdir: Path) -> RepoContext:
        self.queries.append(query)
        return self._context


def test_repo_context_is_injected_into_prompts(tmp_path) -> None:
    backend = FakeBackend(["s1", "s2", "s3", "s4", "s5"])
    retriever = _StubRepoRetriever(
        RepoContext(files=("helpers/util.py",), symbols={"helpers/util.py": ["do_thing"]})
    )
    pipeline = CoTPipeline(
        backend=backend,
        retriever=NoOpRetriever(),
        repo_retriever=retriever,
        repo_workdir=tmp_path,
    )
    pipeline.run_per_file(_DIFF, PerFileReviewOptions(inline_review=False))
    assert retriever.queries, "the retriever should have been queried per file"
    prompts = [prompt for prompt, _ in backend.calls]
    assert all("Related repository context" in p for p in prompts)
    assert any("helpers/util.py" in p and "do_thing" in p for p in prompts)


def test_no_retriever_leaves_prompts_unchanged(tmp_path) -> None:
    backend = FakeBackend(["s1", "s2", "s3", "s4", "s5"])
    pipeline = CoTPipeline(backend=backend, retriever=NoOpRetriever())
    pipeline.run_per_file(_DIFF, PerFileReviewOptions(inline_review=False))
    assert backend.calls
    assert all("Related repository context" not in p for p, _ in backend.calls)


def test_workdir_only_adds_graph_impact_context(tmp_path) -> None:
    # No retriever, only a work-tree: the changed file's import-graph neighbours
    # (its importer + its dependency) are surfaced as deterministic impact.
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "a.py").write_text(
        "from app.dep import helper\n\ndef run():\n    return 1\n", encoding="utf-8"
    )
    (tmp_path / "app" / "dep.py").write_text("def helper():\n    return 2\n", encoding="utf-8")
    (tmp_path / "app" / "caller.py").write_text(
        "from app.a import run\n", encoding="utf-8"
    )
    backend = FakeBackend(["s1", "s2", "s3", "s4", "s5"])
    pipeline = CoTPipeline(
        backend=backend, retriever=NoOpRetriever(), repo_workdir=tmp_path,
    )
    diff = "diff --git a/app/a.py b/app/a.py\n--- a/app/a.py\n+++ b/app/a.py\n@@ -1 +1,2 @@\n x\n+y\n"
    pipeline.run_per_file(diff, PerFileReviewOptions(inline_review=False))
    prompts = [p for p, _ in backend.calls]
    assert all("Cross-file impact" in p for p in prompts)
    # both the dependency and the caller of app/a.py are listed
    assert any("app/dep.py" in p and "app/caller.py" in p for p in prompts)


def test_retrieved_self_file_is_not_listed(tmp_path) -> None:
    # If the retriever returns only the file under review, there is no
    # cross-file context to add, so prompts stay clean.
    backend = FakeBackend(["s1", "s2", "s3", "s4", "s5"])
    retriever = _StubRepoRetriever(RepoContext(files=("a.py",)))
    pipeline = CoTPipeline(
        backend=backend,
        retriever=NoOpRetriever(),
        repo_retriever=retriever,
        repo_workdir=tmp_path,
    )
    pipeline.run_per_file(_DIFF, PerFileReviewOptions(inline_review=False))
    assert all("Related repository context" not in p for p, _ in backend.calls)

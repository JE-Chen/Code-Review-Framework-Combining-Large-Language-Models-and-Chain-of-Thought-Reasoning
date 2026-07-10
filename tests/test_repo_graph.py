"""Tests for import-graph structural retrieval (prthinker.repo_graph)."""

from __future__ import annotations

from prthinker.repo_graph import (
    GraphExpandedRetriever,
    _resolve_import,
    bidirectional_neighbours,
    build_import_adjacency,
    build_python_import_graph,
)
from prthinker.repo_retrieval import LexicalRepoRetriever
from prthinker.repo_retrieval_factory import create_repo_retriever
from tests.test_repo_retrieval import _make_repo


# --------------------------------------------------------------------------
# graph-guided candidate expansion
# --------------------------------------------------------------------------

def test_build_python_import_graph_resolves_to_files():
    files = [
        ("pkg/a.py", "from pkg.b import thing\nimport pkg.c\n"),
        ("pkg/b.py", "x = 1\n"),
        ("pkg/c.py", "y = 2\n"),
    ]
    graph = build_python_import_graph(files)
    assert graph["pkg/a.py"] == {"pkg/b.py", "pkg/c.py"}
    assert graph["pkg/b.py"] == set()


def test_resolve_import_falls_back_to_shorter_prefix():
    index = {"pkg.sub": "pkg/sub/__init__.py"}
    assert _resolve_import("pkg.sub.deep.thing", index) == "pkg/sub/__init__.py"
    assert _resolve_import("unknown.mod", index) is None


def test_graph_expansion_adds_import_neighbours(tmp_path):
    # The query hits handler.py lexically; util.py is reachable only via the
    # import edge, so graph expansion must surface it as an extra candidate.
    repo = _make_repo(tmp_path, {
        "app/handler.py": "from app.util import helper\n\ndef handle():\n    return widget\n",
        "app/util.py": "def helper():\n    return 1\n",
        "app/unrelated.py": "def z():\n    return 0\n",
    })
    base = LexicalRepoRetriever(top_k=1)
    result = GraphExpandedRetriever(base, neighbour_budget=5).retrieve("widget handle", repo)
    assert "app/handler.py" in result.files
    assert "app/util.py" in result.files  # added purely via the import graph


def test_graph_expansion_zero_budget_returns_base(tmp_path):
    repo = _make_repo(tmp_path, {
        "a.py": "from b import x\n\ndef f():\n    return token\n",
        "b.py": "x = 1\n",
    })
    base = LexicalRepoRetriever(top_k=1)
    result = GraphExpandedRetriever(base, neighbour_budget=0).retrieve("token", repo)
    assert len(result.files) == 1


def test_factory_graph_wraps_lexical_base():
    assert isinstance(create_repo_retriever("graph"), GraphExpandedRetriever)


def test_bidirectional_neighbours_unions_imports_and_importers():
    graph = {"a.py": {"b.py"}, "c.py": {"b.py"}, "b.py": set()}
    adjacency = bidirectional_neighbours(graph)
    # b.py is imported by a and c; a/c each depend on b
    assert adjacency["b.py"] == {"a.py", "c.py"}
    assert adjacency["a.py"] == {"b.py"}


def test_build_import_adjacency_from_worktree(tmp_path):
    repo = _make_repo(tmp_path, {
        "a.py": "from b import x\n",
        "b.py": "y = 1\n",
    })
    adjacency = build_import_adjacency(repo)
    assert adjacency["b.py"] == {"a.py"}
    assert adjacency["a.py"] == {"b.py"}


def test_graph_multi_hop_reaches_further_neighbours(tmp_path):
    # a -> b -> c chain. Seeding from a, hops=1 reaches b only; hops=2 reaches c.
    repo = _make_repo(tmp_path, {
        "a.py": "from b import x\n\ndef f():\n    return token\n",
        "b.py": "from c import y\n",
        "c.py": "z = 1\n",
    })
    base = LexicalRepoRetriever(top_k=1)
    one = GraphExpandedRetriever(base, hops=1, neighbour_budget=10).retrieve("token", repo)
    two = GraphExpandedRetriever(base, hops=2, neighbour_budget=10).retrieve("token", repo)
    assert "b.py" in one.files and "c.py" not in one.files
    assert "b.py" in two.files and "c.py" in two.files


# --------------------------------------------------------------------------
# rerank refinements: snippet fallback, ranked order, multi-vote
# --------------------------------------------------------------------------


def test_graph_expansion_builds_graph_once_per_workdir(tmp_path, monkeypatch):
    import prthinker.repo_graph as rg

    repo = _make_repo(tmp_path, {
        "app/handler.py": "from app.util import helper\n\ndef handle():\n    return widget\n",
        "app/util.py": "def helper():\n    return 1\n",
    })
    builds = []
    real_build = rg.build_python_import_graph

    def _counting_build(files):
        builds.append(len(files))
        return real_build(files)

    monkeypatch.setattr(rg, "build_python_import_graph", _counting_build)
    base = LexicalRepoRetriever(top_k=1)
    retriever = GraphExpandedRetriever(base, neighbour_budget=5)
    first = retriever.retrieve("widget handle", repo)
    second = retriever.retrieve("widget handle", repo)
    assert first.files == second.files
    assert "app/util.py" in first.files
    assert len(builds) == 1  # graph + reverse graph memoized per workdir

"""Tests for the cross-file connectivity edges in the KG visualization.

Before imports were captured, the visualization rendered N disconnected
per-file stars — every file became its own island because the only
edges in the graph were file→symbol (`file-of`) and class→method
(`method-of`). These tests pin the rule that a workdir where one file
imports another emits a file→file `imports` edge that turns those
islands into a connected graph.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from prthinker.kg_visualize import build_graph_data
from prthinker.repo_kg import KnowledgeGraphStore, scan_workdir_full


def _write(workdir: Path, rel: str, body: str) -> None:
    target = workdir / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")


def _build(workdir: Path, kg_path: Path):
    symbols, imports = scan_workdir_full(workdir)
    store = KnowledgeGraphStore(kg_path)
    store.rebuild(workdir, symbols, imports)
    return store


def _file_to_file_edges(data: dict) -> set[tuple[str, str]]:
    edges: set[tuple[str, str]] = set()
    for link in data["links"]:
        if link["rel"] != "imports":
            continue
        src = link["source"][len("file::"):]
        tgt = link["target"][len("file::"):]
        edges.add((src, tgt))
    return edges


def test_python_absolute_import_links_two_files(tmp_path):
    _write(tmp_path, "pkg/__init__.py", "")
    _write(tmp_path, "pkg/a.py", "def foo():\n    return 1\n")
    _write(tmp_path, "pkg/b.py", "from pkg.a import foo\n\ndef bar():\n    return foo()\n")
    store = _build(tmp_path, tmp_path / ".kg.sqlite")
    data = build_graph_data(store, tmp_path)
    edges = _file_to_file_edges(data)
    assert ("pkg/b.py", "pkg/a.py") in edges


def test_python_relative_import_links_sibling_files(tmp_path):
    _write(tmp_path, "pkg/__init__.py", "")
    _write(tmp_path, "pkg/a.py", "X = 1\n")
    _write(tmp_path, "pkg/b.py", "from .a import X\n\nY = X + 1\n")
    store = _build(tmp_path, tmp_path / ".kg.sqlite")
    data = build_graph_data(store, tmp_path)
    edges = _file_to_file_edges(data)
    assert ("pkg/b.py", "pkg/a.py") in edges


def test_python_relative_import_walks_up_parents(tmp_path):
    _write(tmp_path, "pkg/__init__.py", "")
    _write(tmp_path, "pkg/sub/__init__.py", "")
    _write(tmp_path, "pkg/a.py", "Z = 9\n")
    _write(tmp_path, "pkg/sub/b.py", "from ..a import Z\n")
    store = _build(tmp_path, tmp_path / ".kg.sqlite")
    data = build_graph_data(store, tmp_path)
    edges = _file_to_file_edges(data)
    assert ("pkg/sub/b.py", "pkg/a.py") in edges


def test_external_imports_are_dropped(tmp_path):
    _write(tmp_path, "pkg/__init__.py", "")
    _write(tmp_path, "pkg/a.py", "import httpx\nimport json\n\ndef f():\n    return httpx.Client()\n")
    store = _build(tmp_path, tmp_path / ".kg.sqlite")
    data = build_graph_data(store, tmp_path)
    edges = _file_to_file_edges(data)
    assert edges == set()
    file_ids = [n["id"] for n in data["nodes"] if n["kind"] == "file"]
    assert "file::pkg/a.py" in file_ids
    assert not any(fid.endswith("httpx") for fid in file_ids)


def test_from_dotted_target_resolves_to_package_init(tmp_path):
    _write(tmp_path, "pkg/__init__.py", "")
    _write(tmp_path, "pkg/sub/__init__.py", "Q = 1\n")
    _write(tmp_path, "pkg/sub/inner.py", "")
    _write(tmp_path, "pkg/a.py", "from pkg.sub import Q\n")
    store = _build(tmp_path, tmp_path / ".kg.sqlite")
    data = build_graph_data(store, tmp_path)
    edges = _file_to_file_edges(data)
    assert ("pkg/a.py", "pkg/sub/__init__.py") in edges


def test_tsjs_relative_import_links_two_files(tmp_path):
    _write(tmp_path, "src/a.ts", "export const A = 1;\n")
    _write(tmp_path, "src/b.ts", 'import { A } from "./a";\nexport const B = A + 1;\n')
    store = _build(tmp_path, tmp_path / ".kg.sqlite")
    data = build_graph_data(store, tmp_path)
    edges = _file_to_file_edges(data)
    assert ("src/b.ts", "src/a.ts") in edges


def test_tsjs_index_resolution(tmp_path):
    _write(tmp_path, "src/lib/index.ts", "export const X = 1;\n")
    _write(tmp_path, "src/main.ts", 'import { X } from "./lib";\n')
    store = _build(tmp_path, tmp_path / ".kg.sqlite")
    data = build_graph_data(store, tmp_path)
    edges = _file_to_file_edges(data)
    assert ("src/main.ts", "src/lib/index.ts") in edges


def test_tsjs_bare_specifier_is_dropped(tmp_path):
    _write(tmp_path, "src/a.ts", "export const A = 1;\n")
    _write(tmp_path, "src/main.ts",
           'import { thing } from "lodash";\nimport { A } from "./a";\n')
    store = _build(tmp_path, tmp_path / ".kg.sqlite")
    data = build_graph_data(store, tmp_path)
    edges = _file_to_file_edges(data)
    assert ("src/main.ts", "src/a.ts") in edges
    assert all(tgt != "lodash" for _, tgt in edges)


def test_self_import_loops_are_dropped(tmp_path):
    _write(tmp_path, "pkg/__init__.py", "")
    _write(tmp_path, "pkg/a.py", "import pkg.a\n")
    store = _build(tmp_path, tmp_path / ".kg.sqlite")
    data = build_graph_data(store, tmp_path)
    edges = _file_to_file_edges(data)
    assert all(src != tgt for src, tgt in edges)


@pytest.mark.parametrize("rel", ["pkg/c.py", "pkg/d.py"])
def test_graph_becomes_connected_with_imports(tmp_path, rel):
    """The core property: with imports, what used to be N stars
    becomes a single connected component.

    Build a tiny pkg where a imports b imports c imports d. Each file
    has at most one symbol so per-file stars are trivial; the test
    checks that BFS from any file node touches every file node.
    """
    _write(tmp_path, "pkg/__init__.py", "")
    _write(tmp_path, "pkg/a.py", "from pkg.b import B\ndef A(): return B\n")
    _write(tmp_path, "pkg/b.py", "from pkg.c import C\nB = C\n")
    _write(tmp_path, "pkg/c.py", "from pkg.d import D\nC = D\n")
    _write(tmp_path, "pkg/d.py", "D = 0\n")
    store = _build(tmp_path, tmp_path / ".kg.sqlite")
    data = build_graph_data(store, tmp_path)

    adj: dict[str, set[str]] = {}
    for link in data["links"]:
        if link["rel"] != "imports":
            continue
        s = link["source"]
        t = link["target"]
        adj.setdefault(s, set()).add(t)
        adj.setdefault(t, set()).add(s)
    file_ids = {n["id"] for n in data["nodes"] if n["kind"] == "file"}

    start = "file::" + rel
    seen: set[str] = {start}
    frontier = [start]
    while frontier:
        nxt = []
        for v in frontier:
            for nb in adj.get(v, ()):
                if nb not in seen and nb in file_ids:
                    seen.add(nb)
                    nxt.append(nb)
        frontier = nxt
    assert file_ids.issubset(seen), f"unreachable files: {file_ids - seen}"

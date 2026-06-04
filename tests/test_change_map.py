"""Tests for the inline Mermaid change-map (change_map)."""

from __future__ import annotations

from prthinker.change_map import change_map_edges, format_change_map_mermaid
from prthinker.repo_kg import Import


def _imp(from_file: str, target: str) -> Import:
    return Import(from_file=from_file, target=target, kind="py_absolute")


def test_edges_only_between_changed_files():
    changed = ["pkg/app.py", "pkg/core.py"]
    imports = [
        _imp("pkg/app.py", "pkg.core"),     # both changed -> kept
        _imp("pkg/app.py", "external.lib"),  # target not changed -> dropped
        _imp("pkg/other.py", "pkg.core"),    # source not changed -> dropped
    ]
    assert change_map_edges(imports, changed) == [("pkg/app.py", "pkg/core.py")]


def test_edges_empty_when_no_internal_imports():
    changed = ["a.py", "b.py"]
    assert change_map_edges([], changed) == []


def test_format_mermaid_renders_graph_block():
    edges = [("pkg/app.py", "pkg/core.py")]
    block = format_change_map_mermaid(edges, ["pkg/app.py", "pkg/core.py"])
    assert "```mermaid" in block
    assert "graph LR" in block
    assert "pkg/app.py" in block and "pkg/core.py" in block
    assert "-->" in block
    assert "🗺️ Change map" in block


def test_format_mermaid_empty_for_no_edges():
    assert format_change_map_mermaid([], ["a.py"]) == ""

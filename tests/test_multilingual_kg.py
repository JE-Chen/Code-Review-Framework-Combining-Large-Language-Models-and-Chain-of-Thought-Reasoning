"""Language-aware persistence stays compatible with older graph databases."""

import sqlite3
import sys
from types import SimpleNamespace

from prthinker.context_graph import parse_tree_sitter, scan_import_edges
from prthinker.repo_kg import Import, KnowledgeGraphStore, Symbol, _coarse_symbol_kind


def test_language_roundtrip_and_migration(tmp_path):
    path = tmp_path / "kg.sqlite"
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE symbols (id INTEGER PRIMARY KEY, workdir TEXT, file_path TEXT, symbol TEXT, kind TEXT, line INTEGER, parent TEXT, ts REAL)")
    store = KnowledgeGraphStore(path)
    symbol = Symbol("hello", "function", "hello.rs", 2, language="rust")
    store.rebuild(tmp_path, [symbol])
    assert store.all_symbols(tmp_path) == [symbol]
    assert _coarse_symbol_kind("struct_item") == "class"
    assert _coarse_symbol_kind("function_item") == "function"


def test_import_scan_excludes_generated_trees(tmp_path):
    generated = tmp_path / "node_modules"
    generated.mkdir()
    (generated / "A.java").write_text("import dangerous.Secret;")
    (tmp_path / "A.java").write_text("import local.Helper;")
    assert scan_import_edges(tmp_path) == [("A.java", "local.Helper")]


def test_cross_language_include_links_are_grounded(tmp_path):
    store = KnowledgeGraphStore(tmp_path / "kg.sqlite")
    symbols = [Symbol("main", "function", "main.cpp", 1, language="cpp"),
               Symbol("util", "function", "util.h", 1, language="c")]
    store.rebuild(tmp_path, symbols, [Import("main.cpp", "util.h", "generic")])
    assert store.all_relations(tmp_path) == [{
        "source_file": "main.cpp", "target_file": "util.h", "kind": "imports",
        "source_language": "cpp", "target_language": "c",
    }]
    store.rebuild(tmp_path, [])
    assert store.all_relations(tmp_path) == []


def test_csharp_uses_the_language_pack_binding_name(tmp_path, monkeypatch):
    calls = []
    parser = SimpleNamespace(parse=lambda _source: SimpleNamespace(root_node=SimpleNamespace(type="root", children=[])))
    monkeypatch.setitem(sys.modules, "tree_sitter_language_pack",
                        SimpleNamespace(get_parser=lambda language: calls.append(language) or parser))
    source = tmp_path / "A.cs"
    source.write_text("class Alpha {}")
    assert parse_tree_sitter(source, "c_sharp") == []
    assert calls == ["csharp"]

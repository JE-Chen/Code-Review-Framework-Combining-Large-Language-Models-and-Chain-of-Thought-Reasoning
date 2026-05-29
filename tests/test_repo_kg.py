"""Tests for the repo knowledge-graph scanner + store.

We build a tiny throwaway workdir for each test so the scanner runs
against real Python / TS files without depending on the repo's own
contents.
"""

from __future__ import annotations

from pathlib import Path

from prthinker.repo_kg import (
    KnowledgeGraphStore,
    Symbol,
    format_kg_block,
    scan_workdir,
)


def _write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


# ----- Python scanner ---------------------------------------------------

def test_scan_python_picks_up_functions_classes_methods(tmp_path: Path) -> None:
    _write(tmp_path / "a.py", (
        "def top_level():\n"
        "    pass\n"
        "\n"
        "class Widget:\n"
        "    def method(self):\n"
        "        pass\n"
        "\n"
        "BAUD_RATE = 9600\n"
    ))
    syms = scan_workdir(tmp_path)
    names = {s.symbol for s in syms}
    assert "top_level" in names
    assert "Widget" in names
    assert "method" in names
    assert "BAUD_RATE" in names
    method = [s for s in syms if s.symbol == "method"][0]
    assert method.parent == "Widget"
    assert method.kind == "method"


def test_scan_python_handles_async_def(tmp_path: Path) -> None:
    _write(tmp_path / "a.py", "async def fetch():\n    pass\n")
    syms = scan_workdir(tmp_path)
    assert any(s.symbol == "fetch" and s.kind == "function" for s in syms)


def test_scan_python_ignores_broken_files(tmp_path: Path) -> None:
    _write(tmp_path / "good.py", "def ok():\n    pass\n")
    _write(tmp_path / "bad.py", "def !!! invalid syntax")
    syms = scan_workdir(tmp_path)
    assert any(s.symbol == "ok" for s in syms)
    assert not any(s.file_path == "bad.py" for s in syms)


def test_scan_python_skips_private_module_dirs(tmp_path: Path) -> None:
    _write(tmp_path / "src" / "real.py", "def real():\n    pass\n")
    _write(tmp_path / "node_modules" / "pkg" / "junk.py", "def junk():\n    pass\n")
    _write(tmp_path / "__pycache__" / "cache.py", "def cache():\n    pass\n")
    syms = scan_workdir(tmp_path)
    names = {s.symbol for s in syms}
    assert "real" in names
    assert "junk" not in names
    assert "cache" not in names


# ----- TypeScript / JavaScript scanner ----------------------------------

def test_scan_ts_export_forms(tmp_path: Path) -> None:
    _write(tmp_path / "api.ts", (
        "export function getUser(id: string) {}\n"
        "export class UserService {}\n"
        "export interface UserDTO {}\n"
        "export const MAX_RETRIES = 3;\n"
        "export default UserService;\n"
    ))
    syms = scan_workdir(tmp_path)
    names_kinds = {(s.symbol, s.kind) for s in syms}
    assert ("getUser", "function") in names_kinds
    assert ("UserService", "class") in names_kinds
    assert ("UserDTO", "ts_type") in names_kinds
    assert ("MAX_RETRIES", "const") in names_kinds


def test_scan_jsx_file(tmp_path: Path) -> None:
    _write(tmp_path / "App.jsx", "export function App() { return null }\n")
    syms = scan_workdir(tmp_path)
    assert any(s.symbol == "App" for s in syms)


# ----- Store ------------------------------------------------------------

def test_store_rebuild_then_read(tmp_path: Path) -> None:
    store_path = tmp_path / "kg.sqlite"
    store = KnowledgeGraphStore(store_path)
    n = store.rebuild(tmp_path, [
        Symbol(symbol="foo", kind="function", file_path="a.py", line=1),
        Symbol(symbol="Bar", kind="class", file_path="b.py", line=10),
    ])
    assert n == 2
    syms = store.all_symbols(tmp_path)
    names = {s.symbol for s in syms}
    assert names == {"foo", "Bar"}


def test_store_rebuild_wipes_prior_rows_for_same_workdir(tmp_path: Path) -> None:
    store = KnowledgeGraphStore(tmp_path / "kg.sqlite")
    store.rebuild(tmp_path, [
        Symbol(symbol="old", kind="function", file_path="x.py", line=1),
    ])
    store.rebuild(tmp_path, [
        Symbol(symbol="new", kind="function", file_path="y.py", line=1),
    ])
    names = {s.symbol for s in store.all_symbols(tmp_path)}
    assert names == {"new"}


def test_store_isolated_by_workdir(tmp_path: Path) -> None:
    wd_a = tmp_path / "a"
    wd_b = tmp_path / "b"
    wd_a.mkdir()
    wd_b.mkdir()
    store = KnowledgeGraphStore(tmp_path / "kg.sqlite")
    store.rebuild(wd_a, [Symbol(symbol="A", kind="function", file_path="a.py", line=1)])
    store.rebuild(wd_b, [Symbol(symbol="B", kind="function", file_path="b.py", line=1)])
    assert [s.symbol for s in store.all_symbols(wd_a)] == ["A"]
    assert [s.symbol for s in store.all_symbols(wd_b)] == ["B"]


# ----- Format block -----------------------------------------------------

def test_format_kg_block_empty_returns_empty_string() -> None:
    assert format_kg_block([]) == ""


def test_format_kg_block_lists_each_symbol() -> None:
    block = format_kg_block([
        Symbol(symbol="foo", kind="function", file_path="a.py", line=10),
        Symbol(symbol="Bar", kind="class", file_path="b.py", line=20),
    ])
    assert "foo" in block and "Bar" in block
    assert "a.py:10" in block and "b.py:20" in block


def test_format_kg_block_respects_max_symbols() -> None:
    syms = [Symbol(symbol=f"s{i}", kind="function", file_path="x.py", line=i+1)
            for i in range(50)]
    block = format_kg_block(syms, max_symbols=5)
    assert "s0" in block
    assert "s4" in block
    assert "s5" not in block

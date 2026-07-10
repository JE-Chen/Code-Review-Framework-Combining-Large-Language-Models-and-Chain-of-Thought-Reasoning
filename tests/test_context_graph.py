"""Tests for the polyglot import-edge scanner in :mod:`prthinker.context_graph`."""

from __future__ import annotations

from pathlib import Path

from prthinker.context_graph import _IMPORT_PATTERNS, scan_import_edges


def test_import_patterns_share_one_c_include_regex() -> None:
    # The C-family suffixes reuse a single compiled pattern object.
    assert _IMPORT_PATTERNS[".c"] is _IMPORT_PATTERNS[".h"]
    assert _IMPORT_PATTERNS[".c"] is _IMPORT_PATTERNS[".cpp"]


def test_scan_import_edges_empty_workdir(tmp_path: Path) -> None:
    assert scan_import_edges(tmp_path) == []


def test_scan_import_edges_java_import(tmp_path: Path) -> None:
    (tmp_path / "A.java").write_text(
        "import com.example.Util;\nclass A {}\n", encoding="utf-8"
    )
    assert scan_import_edges(tmp_path) == [("A.java", "com.example.Util")]


def test_scan_import_edges_c_family_includes(tmp_path: Path) -> None:
    (tmp_path / "m.c").write_text('#include "util.h"\n', encoding="utf-8")
    (tmp_path / "m.h").write_text("#include <stdio.h>\n", encoding="utf-8")
    (tmp_path / "m.cpp").write_text("#include <vector>\n", encoding="utf-8")
    edges = dict(scan_import_edges(tmp_path))
    assert edges == {"m.c": "util.h", "m.h": "stdio.h", "m.cpp": "vector"}


def test_scan_import_edges_skips_unknown_suffixes(tmp_path: Path) -> None:
    (tmp_path / "notes.txt").write_text("import nothing\n", encoding="utf-8")
    assert scan_import_edges(tmp_path) == []


def test_scan_import_edges_skips_undecodable_file(tmp_path: Path) -> None:
    (tmp_path / "bad.java").write_bytes(b"\xff\xfe\x00import broken")
    (tmp_path / "ok.java").write_text("import a.b.C;\n", encoding="utf-8")
    assert scan_import_edges(tmp_path) == [("ok.java", "a.b.C")]

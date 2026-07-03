"""Tests for the repo-KG blast-radius estimator."""

from __future__ import annotations

from prthinker import impact_map
from prthinker.repo_kg import Import


def _imp(from_file: str, target: str) -> Import:
    return Import(from_file=from_file, target=target, kind="py_absolute")


def test_impacted_files_finds_downstream_importers():
    imports = [
        _imp("app/main.py", "pkg.core"),  # imports changed module → impacted
        _imp("app/util.py", "pkg.core"),  # impacted
        _imp("app/other.py", "pkg.unrelated"),  # unrelated
    ]
    out = impact_map.impacted_files(imports, ["pkg/core.py"])
    assert out == ["app/main.py", "app/util.py"]


def test_impacted_excludes_changed_files_themselves():
    imports = [_imp("pkg/core.py", "pkg.helpers"), _imp("app/x.py", "pkg.core")]
    # pkg/core.py is itself changed → not listed even though it imports a changed file.
    out = impact_map.impacted_files(imports, ["pkg/core.py", "pkg/helpers.py"])
    assert "pkg/core.py" not in out
    assert "app/x.py" in out


def test_impacted_matches_bare_module_and_relative():
    imports = [_imp("a.py", "core"), _imp("b.py", ".core")]
    out = impact_map.impacted_files(imports, ["core.py"])
    assert out == ["a.py", "b.py"]


def test_impacted_empty_when_no_match():
    assert impact_map.impacted_files([_imp("a.py", "z")], ["pkg/core.py"]) == []


def test_generic_polyglot_import_target():
    imports = [Import("src/Api.java", "pkg.Core", "generic")]
    assert impact_map.impacted_files(imports, ["pkg/Core.java"]) == ["src/Api.java"]


def test_format_impact_note_caps_and_counts():
    files = [f"f{i}.py" for i in range(13)]
    note = impact_map.format_impact_note(files)
    assert "Impacted areas (downstream importers):" in note
    assert "`f0.py`" in note
    assert "(+3 more)" in note


def test_format_impact_note_empty():
    assert impact_map.format_impact_note([]) == ""

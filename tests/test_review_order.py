"""Tests for the suggested review order (review_order)."""

from __future__ import annotations

from prthinker.repo_kg import Import
from prthinker.review_order import format_review_order_note, suggested_order


def _imp(from_file: str, target: str) -> Import:
    return Import(from_file=from_file, target=target, kind="py_absolute")


def test_order_puts_most_depended_upon_first():
    changed = ["pkg/app.py", "pkg/core.py", "pkg/util.py"]
    # app imports core and util; core imports util. util is most depended-upon.
    imports = [
        _imp("pkg/app.py", "pkg.core"),
        _imp("pkg/app.py", "pkg.util"),
        _imp("pkg/core.py", "pkg.util"),
    ]
    order = suggested_order(imports, changed)
    assert order[0] == "pkg/util.py"   # in-degree 2
    assert order[1] == "pkg/core.py"   # in-degree 1
    assert order[2] == "pkg/app.py"    # in-degree 0


def test_order_is_stable_on_ties():
    changed = ["a.py", "b.py", "c.py"]
    # No edges → all in-degree 0 → original order preserved.
    assert suggested_order([], changed) == ["a.py", "b.py", "c.py"]


def test_order_ignores_imports_from_unchanged_files():
    changed = ["pkg/core.py", "pkg/app.py"]
    # An unchanged file importing core must not inflate its in-degree, and
    # an import targeting a non-changed module is ignored.
    imports = [
        _imp("pkg/other.py", "pkg.core"),     # other.py not in changed set
        _imp("pkg/app.py", "external.lib"),   # target not a changed file
    ]
    order = suggested_order(imports, changed)
    assert order == ["pkg/core.py", "pkg/app.py"]  # both in-degree 0, stable


def test_format_review_order_marks_start_here():
    note = format_review_order_note(["pkg/util.py", "pkg/app.py"])
    assert "Suggested review order" in note
    assert "start here: `pkg/util.py`" in note
    assert "`pkg/util.py` → `pkg/app.py`" in note


def test_format_review_order_empty_for_single_file():
    assert format_review_order_note(["only.py"]) == ""
    assert format_review_order_note([]) == ""

"""Unit tests for the heuristic public-API-surface / semver-impact detector."""

from __future__ import annotations

from prthinker.api_surface import ApiSurfaceReport, compute_api_surface
from prthinker.diff import FileDiff


def _file(raw: str, *, is_binary: bool = False, is_deleted: bool = False) -> FileDiff:
    """Build a minimal FileDiff carrying only the raw text under test."""
    return FileDiff(
        path="pkg/mod.py",
        raw=raw,
        is_binary=is_binary,
        is_deleted=is_deleted,
    )


def test_added_public_def_is_minor() -> None:
    raw = "@@ -0,0 +1 @@\n+def new_feature(x):\n"
    report = compute_api_surface([_file(raw)])
    assert report.added == ["new_feature"]
    assert report.removed == []
    assert report.changed == []
    assert report.impact == "minor"


def test_removed_public_def_is_major() -> None:
    raw = "@@ -1 +0,0 @@\n-def gone(x):\n"
    report = compute_api_surface([_file(raw)])
    assert report.removed == ["gone"]
    assert report.added == []
    assert report.impact == "major"


def test_signature_change_is_major() -> None:
    raw = "@@ -1 +1 @@\n-def f(a):\n+def f(a, b):\n"
    report = compute_api_surface([_file(raw)])
    assert report.changed == ["f"]
    assert report.added == []
    assert report.removed == []
    assert report.impact == "major"


def test_private_helper_is_ignored() -> None:
    raw = "@@ -0,0 +1 @@\n+def _helper(x):\n"
    report = compute_api_surface([_file(raw)])
    assert report.added == []
    assert report.removed == []
    assert report.changed == []
    assert report.impact == "patch"


def test_indented_method_is_ignored() -> None:
    raw = "@@ -0,0 +1 @@\n+    def inner(self):\n"
    report = compute_api_surface([_file(raw)])
    assert report.added == []
    assert report.impact == "patch"


def test_no_api_change_is_patch() -> None:
    raw = "@@ -1 +1 @@\n-    x = 1\n+    x = 2\n"
    report = compute_api_surface([_file(raw)])
    assert report.added == []
    assert report.removed == []
    assert report.changed == []
    assert report.impact == "patch"


def test_binary_and_deleted_files_are_skipped() -> None:
    binary = _file("@@ -0,0 +1 @@\n+def should_not_count():\n", is_binary=True)
    deleted = _file("@@ -1 +0,0 @@\n-def also_skipped():\n", is_deleted=True)
    report = compute_api_surface([binary, deleted])
    assert report.added == []
    assert report.removed == []
    assert report.changed == []
    assert report.impact == "patch"


def test_added_public_class_is_minor() -> None:
    raw = "@@ -0,0 +1 @@\n+class Widget:\n"
    report = compute_api_surface([_file(raw)])
    assert report.added == ["Widget"]
    assert report.impact == "minor"


def test_empty_input_is_patch() -> None:
    report = compute_api_surface([])
    assert isinstance(report, ApiSurfaceReport)
    assert report.impact == "patch"


def test_removal_dominates_addition_as_major() -> None:
    raw = "@@ -1 +1 @@\n-def old_api():\n+def brand_new():\n"
    report = compute_api_surface([_file(raw)])
    assert "brand_new" in report.added
    assert "old_api" in report.removed
    assert report.impact == "major"


def test_report_is_frozen() -> None:
    report = compute_api_surface([])
    try:
        report.impact = "major"  # type: ignore[misc]
    except AttributeError:
        return
    raise AssertionError("ApiSurfaceReport must be immutable")

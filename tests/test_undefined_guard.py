"""``prthinker.undefined_guard`` — phantom undefined-name suppression.

Pure-helper coverage (reconstruction, name binding, claim extraction,
the public filter) plus one ``CoTPipeline`` + ``FakeBackend`` integration
test proving a real review drops the hallucinated ``NameError`` while
keeping a genuinely missing import.
"""

from __future__ import annotations

from prthinker.pipeline import CoTPipeline, PerFileReviewOptions
from prthinker.rag import NoOpRetriever
from prthinker.schemas import InlineFinding
from prthinker.undefined_guard import (
    claimed_missing_name,
    collect_bound_names,
    reconstruct_source_from_diff,
    suppress_phantom_undefined,
)

from tests.conftest import FakeBackend


def _finding(comment: str, *, line: int = 5, severity: str = "error") -> InlineFinding:
    return InlineFinding(path="q.py", line=line, severity=severity, comment=comment)


# --------------------------------------------------------------------------
# reconstruct_source_from_diff
# --------------------------------------------------------------------------

def test_reconstruct_lifts_the_hunk_heading() -> None:
    # The import sits in the @@ section heading, not the hunk body — the
    # exact blind spot that produced the false NameError on PR #39.
    diff = (
        "diff --git a/q.py b/q.py\n"
        "--- a/q.py\n+++ b/q.py\n"
        "@@ -2,3 +2,3 @@ import gc\n"
        " import torch\n"
        "-x = old()\n"
        "+x = gc.collect()\n"
    )
    source = reconstruct_source_from_diff(diff)
    assert "import gc" in source
    assert "import torch" in source
    assert "x = gc.collect()" in source


def test_reconstruct_excludes_removed_and_header_lines() -> None:
    diff = (
        "diff --git a/q.py b/q.py\n"
        "--- a/q.py\n+++ b/q.py\n"
        "@@ -1 +1,2 @@\n"
        "-gone = 1\n"
        "+kept = 2\n"
    )
    source = reconstruct_source_from_diff(diff)
    assert "kept = 2" in source
    assert "gone = 1" not in source
    assert "+++ b/q.py" not in source
    assert "diff --git" not in source


def test_reconstruct_empty_diff_is_empty() -> None:
    assert reconstruct_source_from_diff("") == ""


# --------------------------------------------------------------------------
# collect_bound_names
# --------------------------------------------------------------------------

def test_collect_bound_names_ast_path() -> None:
    source = (
        "import gc\n"
        "import os.path\n"
        "from a.b import c, d as e\n"
        "def helper():\n"
        "    pass\n"
        "class Thing:\n"
        "    pass\n"
        "value = 1\n"
    )
    names = collect_bound_names(source)
    assert {"gc", "os", "c", "e", "helper", "Thing", "value"} <= names
    assert "d" not in names  # aliased away
    assert "len" in names  # builtins are always bound


def test_collect_bound_names_regex_fallback_on_partial_fragment() -> None:
    # A leading dedent makes this invalid Python, forcing the regex path.
    fragment = (
        "    import gc\n"
        "x = gc.collect()\n"
        "from pkg import helper as aliased\n"
    )
    names = collect_bound_names(fragment)
    assert "gc" in names
    assert "aliased" in names
    assert "helper" not in names  # aliased away


def test_collect_bound_names_empty_source_has_builtins_only() -> None:
    names = collect_bound_names("")
    assert "print" in names
    assert "gc" not in names


# --------------------------------------------------------------------------
# claimed_missing_name
# --------------------------------------------------------------------------

def test_claim_used_but_not_imported() -> None:
    comment = "gc is used but not imported. This will raise a NameError."
    assert claimed_missing_name(comment) == "gc"


def test_claim_name_is_not_defined() -> None:
    assert claimed_missing_name("name 'foo' is not defined") == "foo"


def test_claim_undefined_name_with_backticks() -> None:
    assert claimed_missing_name("undefined name `bar`") == "bar"


def test_claim_missing_import_phrasing() -> None:
    assert claimed_missing_name("Missing import for `requests`.") == "requests"


def test_claim_returns_none_for_unrelated_comment() -> None:
    assert claimed_missing_name("Prefer logging over print().") is None


def test_claim_returns_none_when_no_identifier_subject() -> None:
    # Keyword present but no "<name> is ..." subject to verify against —
    # without a concrete identifier the guard must not act.
    assert claimed_missing_name("Undefined symbol usage detected here.") is None


# --------------------------------------------------------------------------
# suppress_phantom_undefined
# --------------------------------------------------------------------------

_DIFF_WITH_GC_HEADING = (
    "diff --git a/q.py b/q.py\n"
    "--- a/q.py\n+++ b/q.py\n"
    "@@ -2,3 +2,3 @@ import gc\n"
    " import torch\n"
    "-x = old()\n"
    "+x = gc.collect()\n"
)


def test_suppress_drops_phantom_when_symbol_is_bound() -> None:
    findings = [_finding("gc is used but not imported. This raises a NameError.")]
    kept = suppress_phantom_undefined(
        findings, diff_text=_DIFF_WITH_GC_HEADING, path="q.py"
    )
    assert kept == []


def test_suppress_keeps_finding_for_genuinely_missing_symbol() -> None:
    findings = [_finding("missingdep is used but not imported.")]
    kept = suppress_phantom_undefined(
        findings, diff_text=_DIFF_WITH_GC_HEADING, path="q.py"
    )
    assert len(kept) == 1


def test_suppress_keeps_unrelated_findings_untouched() -> None:
    findings = [_finding("Prefer logging over print().", severity="warning")]
    kept = suppress_phantom_undefined(
        findings, diff_text=_DIFF_WITH_GC_HEADING, path="q.py"
    )
    assert kept == findings


def test_suppress_skips_non_python_files() -> None:
    findings = [_finding("gc is used but not imported.")]
    md = InlineFinding(
        path="README.md", line=5, severity="error",
        comment="gc is used but not imported.",
    )
    kept = suppress_phantom_undefined(
        [md], diff_text=_DIFF_WITH_GC_HEADING, path="README.md"
    )
    assert kept == [md]
    # The same comment on a .py file is suppressed.
    assert suppress_phantom_undefined(
        findings, diff_text=_DIFF_WITH_GC_HEADING, path="q.py"
    ) == []


def test_suppress_empty_findings() -> None:
    assert suppress_phantom_undefined(
        [], diff_text=_DIFF_WITH_GC_HEADING, path="q.py"
    ) == []


def test_suppress_mixed_drops_only_the_phantom() -> None:
    phantom = _finding("gc is used but not imported.")
    real = _finding("absentlib is used but not imported.", line=5, severity="warning")
    unrelated = _finding("Add a docstring.", line=5, severity="info")
    kept = suppress_phantom_undefined(
        [phantom, real, unrelated], diff_text=_DIFF_WITH_GC_HEADING, path="q.py"
    )
    assert phantom not in kept
    assert real in kept
    assert unrelated in kept


# --------------------------------------------------------------------------
# Pipeline integration (FakeBackend)
# --------------------------------------------------------------------------

def test_pipeline_drops_phantom_namerror_finding() -> None:
    inline_payload = (
        "["
        '{"line": 5, "severity": "error",'
        ' "comment": "gc is used but not imported. This raises a NameError."},'
        '{"line": 5, "severity": "warning",'
        ' "comment": "absentlib is used but not imported."}'
        "]"
    )
    backend = FakeBackend(["s1", "s2", "s3", "s4", "s5", inline_payload])
    pipeline = CoTPipeline(backend=backend, retriever=NoOpRetriever())
    diff = (
        "diff --git a/q.py b/q.py\n"
        "--- a/q.py\n+++ b/q.py\n"
        "@@ -2,3 +2,4 @@ import gc\n"
        " import torch\n"
        " \n"
        "+x = gc.collect()\n"
        " y = 1\n"
    )
    result = pipeline.run_per_file(diff, PerFileReviewOptions(inline_review=True))

    comments = [f.comment for f in result.inline_findings]
    assert not any("gc is used" in c for c in comments)  # phantom dropped
    assert any("absentlib" in c for c in comments)  # real finding kept

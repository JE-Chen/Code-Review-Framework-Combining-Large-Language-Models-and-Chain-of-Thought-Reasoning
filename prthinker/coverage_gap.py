"""Flag production code changed without a matching test change.

A change to behaviour that ships with no test change is the single most
common thing a reviewer has to notice by hand. This is a cheap,
deterministic heuristic — no model call — that compares the changed
production ``.py`` files against the changed test files and reports the
ones with no same-named test touched. It is a *hint*, surfaced as
informational context: a docs-only or pure-refactor PR legitimately
changes no tests, so the signal never gates the review.

Runner-safe: pure path inspection over the changed-file list. (Named
``coverage_gap`` rather than ``test_gap`` so pytest does not collect this
module as a test file.)
"""

from __future__ import annotations

import posixpath

_COVERAGE_GAP_LIMIT = 10


def _is_test_path(path: str) -> bool:
    """True for a pytest-style test file (``tests/`` dir or ``test_*`` name)."""
    base = posixpath.basename(path)
    parts = path.split("/")
    return (
        "tests" in parts
        or base.startswith("test_")
        or base.endswith("_test.py")
        or base == "conftest.py"
    )


def _is_prod_py(path: str) -> bool:
    """True for a production Python file (a ``.py`` that is not a test)."""
    base = posixpath.basename(path)
    return (
        path.endswith(".py")
        and not _is_test_path(path)
        and base != "__init__.py"
    )


def _stem(path: str) -> str:
    """Module stem of a path (``pkg/foo.py`` -> ``foo``)."""
    return posixpath.basename(path)[:-3]


def coverage_gaps(changed_paths: list[str]) -> list[str]:
    """Production files whose same-named test was not also changed.

    A production file ``pkg/foo.py`` is considered covered by this PR when
    a changed test path carries the ``foo`` stem (``tests/test_foo.py`` or
    ``foo_test.py``). Files without such a match are returned, sorted.
    """
    covered: set[str] = set()
    for path in changed_paths:
        if not _is_test_path(path):
            continue
        base = _stem(path)
        if base.startswith("test_"):
            covered.add(base[len("test_"):])
        elif base.endswith("_test"):
            covered.add(base[: -len("_test")])
    gaps = [
        p for p in changed_paths
        if _is_prod_py(p) and _stem(p) not in covered
    ]
    return sorted(gaps)


def format_coverage_gap_note(gaps: list[str]) -> str:
    """Collapsible 'changed without a test change' block, or ``""``."""
    if not gaps:
        return ""
    shown = gaps[:_COVERAGE_GAP_LIMIT]
    lines = [
        f"<details><summary>🧪 {len(gaps)} file(s) changed without a "
        "matching test change</summary>",
        "",
    ]
    lines += [f"- `{p}`" for p in shown]
    extra = len(gaps) - len(shown)
    if extra > 0:
        lines.append(f"- … and {extra} more")
    lines += [
        "",
        "_Heuristic hint — a docs-only or pure-refactor change may need "
        "no test._",
        "",
        "</details>",
    ]
    return "\n".join(lines)


__all__ = ["coverage_gaps", "format_coverage_gap_note"]

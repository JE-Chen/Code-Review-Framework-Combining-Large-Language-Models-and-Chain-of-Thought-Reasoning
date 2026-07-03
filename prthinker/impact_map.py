"""Estimate a PR's blast radius from the repo knowledge graph.

Given the import edges (``from_file`` imports ``target``) and the set of
changed files, find the *downstream importers* — files that import a
changed module but were not themselves changed. Surfacing these in the
overview flags review-worthy ripple effects the diff alone does not show.
Matching is heuristic (module names vs raw import targets), so the result
is a hint, not a guarantee.
"""

from __future__ import annotations

from collections.abc import Iterable

from prthinker.repo_kg import Import

_IMPACT_LIMIT = 10


def _module_candidates(path: str) -> set[str]:
    """Plausible import-target spellings for a source path."""
    stem = path.rsplit(".", 1)[0] if "." in path.rsplit("/", 1)[-1] else path
    parts = [p for p in stem.split("/") if p and p != "."]
    if not parts:
        return set()
    dotted = ".".join(parts)
    return {dotted, "/".join(parts), "::".join(parts), parts[-1]}


def impacted_files(
    imports: Iterable[Import], changed_paths: list[str]
) -> list[str]:
    """Files that import a changed module and were not themselves changed."""
    targets: set[str] = set()
    for path in changed_paths:
        targets |= _module_candidates(path)
    changed = set(changed_paths)
    impacted: set[str] = set()
    for imp in imports:
        cleaned = imp.target.lstrip(".")
        last = cleaned.replace("::", ".").replace("/", ".").split(".")[-1]
        normalized = cleaned.replace("::", ".").replace("/", ".")
        if (cleaned in targets or normalized in targets or last in targets) and imp.from_file not in changed:
            impacted.add(imp.from_file)
    return sorted(impacted)


def format_impact_note(impacted: list[str]) -> str:
    """One-line 'Impacted areas' note, capped with an overflow count."""
    if not impacted:
        return ""
    shown = impacted[:_IMPACT_LIMIT]
    note = "**Impacted areas (downstream importers):** " + ", ".join(
        f"`{p}`" for p in shown
    )
    extra = len(impacted) - len(shown)
    if extra > 0:
        note += f" (+{extra} more)"
    return note


__all__ = ["format_impact_note", "impacted_files"]

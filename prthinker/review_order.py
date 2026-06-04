"""Suggest the order to read a PR's changed files.

Severity ordering answers "where are the problems"; it does not answer
"what should I read first to understand the change". A reviewer grasps a
diff faster bottom-up: the *foundational* changed files — the ones the
other changed files import — before the call sites that depend on them.

Using the repo knowledge graph's import edges (the same source the impact
map reads), this ranks the changed files by how many *other changed
files* import them. The most-depended-upon file is the recommended
"start here"; the rest follow in dependency order, ties broken by the
original diff order so the result is deterministic.

Runner-safe: reads import tuples already materialised in the KG store.
"""

from __future__ import annotations

from collections.abc import Iterable

from prthinker.repo_kg import Import

_ORDER_LIMIT = 12


def _module_candidates(path: str) -> set[str]:
    """Plausible import-target spellings for a source path (dotted + leaf)."""
    stem = path[:-3] if path.endswith(".py") else path
    parts = [p for p in stem.split("/") if p and p != "."]
    if not parts:
        return set()
    return {".".join(parts), parts[-1]}


def _candidate_owner(changed_paths: list[str]) -> dict[str, str]:
    """Map every candidate module spelling back to its changed file."""
    owner: dict[str, str] = {}
    for path in changed_paths:
        for cand in _module_candidates(path):
            owner.setdefault(cand, path)
    return owner


def _in_degrees(
    imports: Iterable[Import], changed_paths: list[str]
) -> dict[str, int]:
    """Count distinct changed files importing each changed file."""
    changed = set(changed_paths)
    owner = _candidate_owner(changed_paths)
    importers: dict[str, set[str]] = {p: set() for p in changed_paths}
    for imp in imports:
        if imp.from_file not in changed:
            continue
        cleaned = imp.target.lstrip(".")
        target_file = owner.get(cleaned) or owner.get(cleaned.split(".")[-1])
        if target_file is not None and target_file != imp.from_file:
            importers[target_file].add(imp.from_file)
    return {path: len(importers[path]) for path in changed_paths}


def suggested_order(
    imports: Iterable[Import], changed_paths: list[str]
) -> list[str]:
    """Changed files ordered most-depended-upon first (stable on ties)."""
    degree = _in_degrees(imports, changed_paths)
    index = {path: i for i, path in enumerate(changed_paths)}
    return sorted(changed_paths, key=lambda p: (-degree[p], index[p]))


def format_review_order_note(order: list[str]) -> str:
    """A 'Suggested review order' note marking the first file 'start here'.

    Returns ``""`` when there is nothing useful to say (zero or one file).
    """
    if len(order) < 2:
        return ""
    shown = order[:_ORDER_LIMIT]
    chain = " → ".join(f"`{p}`" for p in shown)
    extra = len(order) - len(shown)
    if extra > 0:
        chain += f" → … (+{extra})"
    return (
        f"**Suggested review order** (👉 start here: `{order[0]}`): {chain}"
    )


__all__ = ["format_review_order_note", "suggested_order"]

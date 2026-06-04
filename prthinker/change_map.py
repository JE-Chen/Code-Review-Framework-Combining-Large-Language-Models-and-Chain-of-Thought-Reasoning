"""Render a PR's intra-change import structure as a Mermaid graph.

The knowledge-graph visualiser ships a full repo graph as a standalone
HTML artifact — too heavy to read inline. For a single PR a reviewer
only needs the structure *among the changed files*: which changed module
imports which other changed module. GitHub renders ```mermaid blocks
natively, so a small directed graph embedded in the summary lets a
reviewer see the shape of the change at a glance.

Runner-safe: reads import tuples from the KG store and emits text.
"""

from __future__ import annotations

from collections.abc import Iterable

from prthinker.repo_kg import Import

_NODE_LIMIT = 30


def _module_candidates(path: str) -> set[str]:
    """Plausible import-target spellings for a source path (dotted + leaf)."""
    stem = path[:-3] if path.endswith(".py") else path
    parts = [p for p in stem.split("/") if p and p != "."]
    if not parts:
        return set()
    return {".".join(parts), parts[-1]}


def change_map_edges(
    imports: Iterable[Import], changed_paths: list[str]
) -> list[tuple[str, str]]:
    """Directed ``(importer, imported)`` edges between changed files only."""
    changed = set(changed_paths)
    owner: dict[str, str] = {}
    for path in changed_paths:
        for cand in _module_candidates(path):
            owner.setdefault(cand, path)
    edges: set[tuple[str, str]] = set()
    for imp in imports:
        if imp.from_file not in changed:
            continue
        cleaned = imp.target.lstrip(".")
        target = owner.get(cleaned) or owner.get(cleaned.split(".")[-1])
        if target is not None and target != imp.from_file:
            edges.add((imp.from_file, target))
    return sorted(edges)


def _node_id(path: str, ids: dict[str, str]) -> str:
    """Stable short Mermaid node id for a path (``n0``, ``n1``, …)."""
    if path not in ids:
        ids[path] = f"n{len(ids)}"
    return ids[path]


def format_change_map_mermaid(
    edges: list[tuple[str, str]], changed_paths: list[str]
) -> str:
    """A collapsible ```mermaid graph of the change's import edges, or ``""``.

    Renders nothing when there are no intra-change edges (the diff has no
    internal structure worth drawing). Capped at ``_NODE_LIMIT`` nodes so
    a sprawling PR does not produce an unreadable hairball.
    """
    if not edges:
        return ""
    ids: dict[str, str] = {}
    lines = ["graph LR"]
    for importer, imported in edges:
        if len(ids) >= _NODE_LIMIT and (
            importer not in ids or imported not in ids
        ):
            continue
        left = _node_id(importer, ids)
        right = _node_id(imported, ids)
        lines.append(f'    {left}["{importer}"] --> {right}["{imported}"]')
    body = "\n".join(lines)
    return (
        "<details><summary>🗺️ Change map (imports between changed "
        "files)</summary>\n\n"
        f"```mermaid\n{body}\n```\n\n"
        "_Arrows point from importer to imported; only edges between files "
        "in this PR are shown._\n\n"
        "</details>"
    )


__all__ = ["change_map_edges", "format_change_map_mermaid"]

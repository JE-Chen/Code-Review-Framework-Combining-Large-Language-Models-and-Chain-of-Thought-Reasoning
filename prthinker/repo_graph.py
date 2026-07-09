"""Import-graph structural retrieval — build the graph, expand with neighbours.

LocAgent-style structural recall split from :mod:`prthinker.repo_retrieval`
(which keeps the lexical/semantic/rerank primitives) so each module stays
under the file-size bar: a lightweight Python import graph over the
work-tree, its bidirectional adjacency, and
:class:`GraphExpandedRetriever`, which widens a base retriever's hits with
their import neighbours. The dependency edge runs one way (this module
imports repo_retrieval, never the reverse).

Runner-safe: stdlib only.
"""

from __future__ import annotations

import re
from pathlib import Path

from prthinker.repo_retrieval import (
    RepoContext,
    RepoContextRetriever,
    _iter_code_files,
)


_PY_IMPORT_RE = re.compile(
    r"^[ \t]*(?:from[ \t]+([.\w]+)[ \t]+import|import[ \t]+([.\w]+))", re.MULTILINE
)
_DEFAULT_SEED_FILES = 5
_DEFAULT_NEIGHBOUR_BUDGET = 15


def _module_index(rels: list[str]) -> dict[str, str]:
    """Map python dotted module paths to their repo file (for import resolving)."""
    index: dict[str, str] = {}
    for rel in rels:
        if not rel.endswith(".py"):
            continue
        module = rel[:-3].replace("/", ".")
        index[module] = rel
        if module.endswith(".__init__"):
            index[module[: -len(".__init__")]] = rel
    return index


def _resolve_import(module: str, index: dict[str, str]) -> str | None:
    """Resolve a dotted import to a repo file, trying shorter prefixes."""
    candidate = module.lstrip(".")
    while candidate:
        if candidate in index:
            return index[candidate]
        if "." not in candidate:
            return None
        candidate = candidate.rsplit(".", 1)[0]
    return None


def build_python_import_graph(files: list[tuple[str, str]]) -> dict[str, set[str]]:
    """Map each .py file to the set of repo files it imports (best-effort)."""
    index = _module_index([rel for rel, _ in files])
    graph: dict[str, set[str]] = {}
    for rel, text in files:
        if not rel.endswith(".py"):
            continue
        targets = set()
        for from_mod, import_mod in _PY_IMPORT_RE.findall(text):
            resolved = _resolve_import(from_mod or import_mod, index)
            if resolved and resolved != rel:
                targets.add(resolved)
        graph[rel] = targets
    return graph


def _reverse_graph(graph: dict[str, set[str]]) -> dict[str, set[str]]:
    """Invert an import graph to map each file to the files that import it."""
    importers: dict[str, set[str]] = {}
    for source, targets in graph.items():
        for target in targets:
            importers.setdefault(target, set()).add(source)
    return importers


def bidirectional_neighbours(graph: dict[str, set[str]]) -> dict[str, set[str]]:
    """Map each file to its import-graph neighbours in both directions.

    Combines a file's imports (dependencies) with its importers (callers), so
    a single lookup gives the impact set of changing that file — the review
    pipeline uses this to surface cross-file impact context deterministically.
    """
    adjacency = {rel: set(targets) for rel, targets in graph.items()}
    for source, targets in graph.items():
        for target in targets:
            adjacency.setdefault(target, set()).add(source)
    return adjacency


def build_import_adjacency(workdir: Path) -> dict[str, set[str]]:
    """Read a work-tree and return its bidirectional import adjacency map."""
    graph = build_python_import_graph(list(_iter_code_files(Path(workdir))))
    return bidirectional_neighbours(graph)


class GraphExpandedRetriever(RepoContextRetriever):
    """Lexical recall widened with import-graph neighbours of the top hits.

    LocAgent-style structural recall: after lexical retrieval, the files the
    top hits import — and the files that import them — are added as candidates,
    so a gold file that is related but not lexically similar is still surfaced.
    Model-free and deterministic; intended as the candidate layer beneath the
    reranker.
    """

    def __init__(
        self,
        base: RepoContextRetriever,
        *,
        seed_files: int = _DEFAULT_SEED_FILES,
        neighbour_budget: int = _DEFAULT_NEIGHBOUR_BUDGET,
        hops: int = 1,
    ) -> None:
        self._base = base
        self._seed_files = max(1, seed_files)
        self._neighbour_budget = max(0, neighbour_budget)
        self._hops = max(1, hops)

    def retrieve(self, query: str, workdir: Path) -> RepoContext:
        """Retrieve lexically, then append import-graph neighbours of top hits."""
        workdir = Path(workdir)
        base = self._base.retrieve(query, workdir)
        if not base.files or not self._neighbour_budget:
            return base
        graph = build_python_import_graph(list(_iter_code_files(workdir)))
        neighbours = self._neighbours(base.files, graph)
        merged = list(base.files) + [n for n in neighbours if n not in base.files]
        return RepoContext(
            tuple(merged),
            {rel: base.spans.get(rel, []) for rel in merged},
            {rel: base.symbols.get(rel, []) for rel in merged},
        )

    def _neighbours(self, files: tuple[str, ...], graph: dict[str, set[str]]) -> list[str]:
        """Import-graph neighbours within ``hops`` of the seed files, up to budget."""
        importers = _reverse_graph(graph)
        seen = set(files)
        found: list[str] = []
        queue = [(seed, 0) for seed in files[: self._seed_files]]
        while queue:
            node, depth = queue.pop(0)
            if depth >= self._hops or len(found) >= self._neighbour_budget:
                continue
            for neighbour in sorted(graph.get(node, set()) | importers.get(node, set())):
                if neighbour not in seen:
                    seen.add(neighbour)
                    found.append(neighbour)
                    queue.append((neighbour, depth + 1))
        return found[: self._neighbour_budget]

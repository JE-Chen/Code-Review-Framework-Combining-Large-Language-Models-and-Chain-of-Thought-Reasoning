"""Model-in-the-loop retrieval stages and the retriever strategy factory.

The block-granular LLM stages — :class:`BlockRerankingRetriever` (one-shot
block selection over a file-level rerank) and :class:`IterativeRetriever`
(agentic multi-round explore-and-select, mirroring the ContextBench SOTA
mechanism) — plus :func:`create_repo_retriever`, the single factory entry
point for every repository-retrieval strategy. Split from
:mod:`prthinker.repo_retrieval` (which keeps the strategy primitives) so
each module stays under the file-size bar; the dependency edge runs one
way (this module imports repo_retrieval, never the reverse).

Runner-safe: stdlib + the injected backend.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from prthinker.repo_retrieval import (
    _DEFAULT_CANDIDATE_K,
    GraphExpandedRetriever,
    LexicalRepoRetriever,
    QueryRewritingRetriever,
    RepoContext,
    RepoContextRetriever,
    RerankingRepoRetriever,
    SemanticRepoRetriever,
    SentenceTransformerEmbedder,
    StructuralExpansionRetriever,
    _Backend,
    _rerank_snippet,
    enclosing_blocks,
    enrich_context_spans,
)


_BLOCK_RERANK_MAX_NEW_TOKENS = 512
_DEFAULT_BLOCK_CANDIDATES = 6
_DEFAULT_MAX_BLOCK_LINES = 120


def _block_rows(context: RepoContext, workdir: Path) -> list[tuple[str, int, int, str]]:
    """Flatten a context's per-file candidate spans into (path, start, end, name)."""
    rows: list[tuple[str, int, int, str]] = []
    for rel in context.files:
        spans = context.spans.get(rel, [])
        if not spans:
            continue
        try:
            lines = (workdir / rel).read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        names = {(start, end): name for start, end, name in enclosing_blocks(lines)}
        rows.extend((rel, start, end, names.get((start, end), "")) for start, end in spans)
    return rows


def _blocks_listing(rows: list[tuple[str, int, int, str]], workdir: Path) -> str:
    """A numbered listing of candidate blocks (path::name + snippet) for the prompt."""
    parts = []
    for index, (rel, start, end, name) in enumerate(rows):
        label = f"{rel}::{name}" if name else rel
        snippet = _rerank_snippet(workdir, rel, [(start, end)])
        parts.append(f"[{index}] {label} (lines {start}-{end})\n{snippet}")
    return "\n".join(parts)


def _build_block_rerank_prompt(query: str, listing: str) -> str:
    """Prompt asking the model to select the blocks that are the relevant context."""
    return (
        "You are selecting the code blocks that form the relevant CONTEXT for a "
        "software issue — the functions or classes a developer must read or change "
        "to resolve it. From the numbered candidate blocks below, return ONLY a "
        "JSON array of the numbers of the relevant blocks, most relevant first. Be "
        "selective: include a block only if its code is directly involved.\n\n"
        f"Issue:\n{query}\n\nCandidate blocks:\n{listing}\n"
    )


def _parse_block_selection(
    raw: str, rows: list[tuple[str, int, int, str]]
) -> set[tuple[str, int]]:
    """Parse the model's chosen block indices into (path, start) keys."""
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if not match:
        return set()
    try:
        picks = json.loads(match.group(0))
    except json.JSONDecodeError:
        return set()
    return {
        (rows[pick][0], rows[pick][1])
        for pick in picks
        if isinstance(pick, int) and 0 <= pick < len(rows)
    }


def _context_from_blocks(
    files: tuple[str, ...], rows: list[tuple[str, int, int, str]]
) -> RepoContext:
    """Rebuild a RepoContext from the selected block rows (files preserved)."""
    spans: dict[str, list[tuple[int, int]]] = {}
    symbols: dict[str, list[str]] = {}
    for rel, start, end, name in rows:
        spans.setdefault(rel, []).append((start, end))
        if name:
            symbols.setdefault(rel, []).append(name)
    return RepoContext(files, spans, symbols)


class BlockRerankingRetriever(RepoContextRetriever):
    """Two-stage RAG: file localisation, then a backend selects relevant blocks.

    The inner retriever localises files; this stage enriches each with candidate
    def/class blocks and asks the backend which blocks are the context relevant
    to the issue. Selecting blocks — rather than dumping every candidate the way
    a bare :func:`enrich_context_spans` pass does — keeps line and symbol
    *precision* high while retaining the recall of block-granular spans, the
    level ContextBench's gold context is defined at. ``votes > 1`` unions
    repeated selections (self-consistency).
    """

    def __init__(
        self,
        inner: RepoContextRetriever,
        backend: _Backend,
        *,
        block_candidates: int = _DEFAULT_BLOCK_CANDIDATES,
        max_block_lines: int | None = _DEFAULT_MAX_BLOCK_LINES,
        focus_lines: int | None = None,
        max_new_tokens: int = _BLOCK_RERANK_MAX_NEW_TOKENS,
        votes: int = 1,
    ) -> None:
        self._inner = inner
        self._backend = backend
        self._block_candidates = max(1, block_candidates)
        self._max_block_lines = max_block_lines
        self._focus_lines = focus_lines
        self._max_new_tokens = max_new_tokens
        self._votes = max(1, votes)

    def retrieve(self, query: str, workdir: Path) -> RepoContext:
        """Localise files, then keep the backend-selected candidate blocks."""
        workdir = Path(workdir)
        context = enrich_context_spans(
            self._inner.retrieve(query, workdir), query, workdir,
            max_blocks=self._block_candidates, max_block_lines=self._max_block_lines,
            focus_lines=self._focus_lines,
        )
        rows = _block_rows(context, workdir)
        if not rows:
            return context
        prompt = _build_block_rerank_prompt(query, _blocks_listing(rows, workdir))
        chosen = self._vote(prompt, rows) or rows
        return _context_from_blocks(context.files, chosen)

    def _vote(
        self, prompt: str, rows: list[tuple[str, int, int, str]]
    ) -> list[tuple[str, int, int, str]]:
        """Union the block selection across ``votes`` runs, preserving order."""
        picked: set[tuple[str, int]] = set()
        for _ in range(self._votes):
            raw = self._backend.generate(prompt, self._max_new_tokens)
            picked.update(_parse_block_selection(raw, rows))
        return [row for row in rows if (row[0], row[1]) in picked]


_ITER_ROUNDS = 3
_ITER_MAX_NEW_TOKENS = 512


@dataclass(frozen=True)
class _IterStep:
    """One round's outcome: selected block rows, the next query, and a stop flag."""

    rows: tuple[tuple[str, int, int, str], ...]
    next_query: str
    done: bool


def _build_iter_prompt(query: str, listing: str, selected_count: int) -> str:
    """Prompt for one retrieval round: select blocks and propose the next search."""
    return (
        "You are iteratively retrieving the code context needed to resolve an "
        f"issue. You have selected {selected_count} block(s) so far. From the "
        "candidate blocks below, return ONLY a JSON object: "
        '{"blocks": [indices of the directly relevant blocks], '
        '"next_query": "search terms for code you still need, empty if done", '
        '"done": true or false}. Select only blocks whose code is directly '
        "involved.\n\n"
        f"Issue:\n{query}\n\nCandidate blocks:\n{listing}\n"
    )


def _parse_iter_response(
    raw: str, rows: list[tuple[str, int, int, str]]
) -> _IterStep:
    """Parse one round's JSON object into selected rows, next query and stop flag."""
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return _IterStep((), "", True)
    try:
        obj = json.loads(match.group(0))
    except json.JSONDecodeError:
        return _IterStep((), "", True)
    picks = obj.get("blocks", []) if isinstance(obj, dict) else []
    chosen = tuple(
        rows[pick] for pick in picks
        if isinstance(pick, int) and 0 <= pick < len(rows)
    )
    return _IterStep(chosen, str(obj.get("next_query", "")), bool(obj.get("done", False)))


class IterativeRetriever(RepoContextRetriever):
    """Agentic multi-round retrieval: explore, select blocks, repeat.

    Mirrors the ContextBench SOTA mechanism — a coding agent gathers context over
    several rounds rather than in one shot. Each round the backend selects the
    relevant blocks from the current candidate pool *and* proposes the next search
    query, which widens the pool with newly relevant files; selections accumulate
    until the backend signals it has enough or the round budget runs out.
    ``focus_lines`` keeps each block at the balance-point granularity.
    """

    def __init__(
        self,
        base: RepoContextRetriever,
        backend: _Backend,
        *,
        rounds: int = _ITER_ROUNDS,
        block_candidates: int = _DEFAULT_BLOCK_CANDIDATES,
        max_block_lines: int | None = _DEFAULT_MAX_BLOCK_LINES,
        focus_lines: int | None = None,
        max_new_tokens: int = _ITER_MAX_NEW_TOKENS,
    ) -> None:
        self._base = base
        self._backend = backend
        self._rounds = max(1, rounds)
        self._block_candidates = max(1, block_candidates)
        self._max_block_lines = max_block_lines
        self._focus_lines = focus_lines
        self._max_new_tokens = max_new_tokens

    def retrieve(self, query: str, workdir: Path) -> RepoContext:
        """Gather context over up to ``rounds`` explore-and-select rounds.

        The answer is the blocks the backend *selected*, not every file it
        browsed while exploring — so the predicted file set stays the relevant
        subset and precision does not collapse under wide exploration.
        """
        workdir = Path(workdir)
        selected: dict[tuple[str, int], tuple[str, int, int, str]] = {}
        search = query
        for _ in range(self._rounds):
            rows = self._candidate_rows(search, query, workdir)
            if not rows:
                break
            step = self._select(query, rows, workdir, len(selected))
            for row in step.rows:
                selected[(row[0], row[1])] = row
            if step.done or not step.next_query.strip():
                break
            search = step.next_query
        final_rows = list(selected.values())
        files = tuple(dict.fromkeys(row[0] for row in final_rows))
        return _context_from_blocks(files, final_rows)

    def _candidate_rows(
        self, search: str, query: str, workdir: Path
    ) -> list[tuple[str, int, int, str]]:
        """Retrieve + enrich this round's candidate block pool.

        Block relevance is scored against the round's own ``search`` terms (plus
        the standing issue ``query``) so a file surfaced by an exploration query
        still gets its blocks predicted instead of scoring zero under the
        original issue text.
        """
        context = enrich_context_spans(
            self._base.retrieve(search, workdir), f"{query}\n{search}", workdir,
            max_blocks=self._block_candidates, max_block_lines=self._max_block_lines,
            focus_lines=self._focus_lines,
        )
        return _block_rows(context, workdir)

    def _select(
        self, query: str, rows: list[tuple[str, int, int, str]],
        workdir: Path, selected_count: int,
    ) -> _IterStep:
        """Run the backend for one round and parse its selection + next query."""
        prompt = _build_iter_prompt(query, _blocks_listing(rows, workdir), selected_count)
        return _parse_iter_response(self._backend.generate(prompt, self._max_new_tokens), rows)


def _build_structural(**options) -> RepoContextRetriever:
    """Factory helper: structural retriever wrapping a lexical base."""
    base = options.pop("base", None) or LexicalRepoRetriever(**options)
    return StructuralExpansionRetriever(base)


def _build_graph(**options) -> RepoContextRetriever:
    """Factory helper: graph-expanded retriever wrapping a lexical base."""
    base = options.pop("base", None) or LexicalRepoRetriever(**options)
    return GraphExpandedRetriever(base)


def _build_semantic(**options) -> RepoContextRetriever:
    """Factory helper: semantic retriever, defaulting to a lazy ST embedder."""
    embedder = options.pop("embedder", None) or SentenceTransformerEmbedder()
    return SemanticRepoRetriever(embedder, **options)


def _build_rerank(**options) -> RepoContextRetriever:
    """Factory helper: reranking retriever over a lexical candidate base."""
    backend = options.pop("backend")
    base = options.pop("base", None) or LexicalRepoRetriever(top_k=_DEFAULT_CANDIDATE_K)
    return RerankingRepoRetriever(base, backend, **options)


def _build_query_rewrite(**options) -> RepoContextRetriever:
    """Factory helper: query-rewriting retriever over a lexical base."""
    backend = options.pop("backend")
    base = options.pop("base", None) or LexicalRepoRetriever(**options)
    return QueryRewritingRetriever(base, backend)


def _build_block_rerank(**options) -> RepoContextRetriever:
    """Factory helper: block-reranking retriever over a file-level rerank base."""
    backend = options.pop("backend")
    base = options.pop("base", None) or _build_rerank(backend=backend)
    return BlockRerankingRetriever(base, backend, **options)


def _build_iterative(**options) -> RepoContextRetriever:
    """Factory helper: iterative multi-round retriever over a lexical base."""
    backend = options.pop("backend")
    base = options.pop("base", None) or LexicalRepoRetriever(top_k=_DEFAULT_CANDIDATE_K)
    return IterativeRetriever(base, backend, **options)


def create_repo_retriever(kind: str = "lexical", **options) -> RepoContextRetriever:
    """Factory: build a repository context retriever by strategy name."""
    builders = {
        "lexical": LexicalRepoRetriever,
        "semantic": _build_semantic,
        "structural": _build_structural,
        "graph": _build_graph,
        "rerank": _build_rerank,
        "block_rerank": _build_block_rerank,
        "iterative": _build_iterative,
        "query_rewrite": _build_query_rewrite,
    }
    if kind not in builders:
        raise ValueError(f"unknown repo retriever kind: {kind!r}")
    return builders[kind](**options)

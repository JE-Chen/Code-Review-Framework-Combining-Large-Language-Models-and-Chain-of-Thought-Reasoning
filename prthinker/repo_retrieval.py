"""Repository context retrieval — locate the files/spans relevant to a query.

A first-class framework capability (Strategy + Factory) that, given a natural
-language query (an issue, a task, or a diff summary) and a repository
work-tree, returns the most relevant source files together with candidate line
spans and defined symbols. It is the retrieval half of RAG-for-code: the CoT
review pipeline can use it to gather cross-file context, and the benchmark
harness uses it to answer repository-context-localisation datasets instead of
asking the model to guess file paths from the issue text alone.

Runner-safe: pure stdlib (``re`` / ``math`` / ``collections`` / ``pathlib``),
no torch / faiss / transformers. The lexical strategy needs no model, so it
runs anywhere the work-tree is checked out.
"""

from __future__ import annotations

import math
import re
from abc import ABC, abstractmethod
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, Protocol

_CODE_SUFFIXES = frozenset({
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".go", ".rs",
    ".c", ".cc", ".cpp", ".h", ".hpp", ".rb", ".php",
})
_MAX_FILE_BYTES = 1_000_000
_DEFAULT_TOP_K = 10
_DEFAULT_MAX_SPANS = 3
_DEFAULT_SPAN_CONTEXT = 3
_BM25_K1 = 1.5
_BM25_B = 0.75
_PATH_BOOST = 6.0
_IDENT_PATH_BOOST = 3.0
_MIN_TOKEN_LEN = 2

_WORD_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{2,}")
_CAMEL_RE = re.compile(r"\b[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]+)+\b")
_SNAKE_RE = re.compile(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b")
_DOTTED_RE = re.compile(r"\b[a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)+\b")
_PATH_RE = re.compile(r"[\w./-]+\.(?:py|js|ts|tsx|java|go|rs|c|cpp|h|rb|php)\b")
_TRACE_RE = re.compile(r'File "([^"]+\.\w+)"')
_DEF_RE = re.compile(r"\s*(?:def|class)\s+([A-Za-z_]\w*)")
_STOPWORDS = frozenset({
    "the", "and", "for", "that", "this", "with", "from", "have", "has",
    "are", "was", "were", "not", "but", "can", "should", "would", "when",
    "where", "which", "into", "return", "using", "use", "used", "code",
    "file", "issue", "test", "tests", "class", "function", "true", "false",
    "self", "none", "value", "object", "type", "error", "python",
})
# (CamelCase / snake_case / dotted-path) regex paired with its query weight.
_IDENTIFIER_WEIGHTS = ((_CAMEL_RE, 5), (_SNAKE_RE, 4), (_DOTTED_RE, 3))


def _split_identifier(token: str) -> list[str]:
    """Break a CamelCase / snake_case identifier into lowercase sub-words."""
    spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", token).replace("_", " ")
    return [part.lower() for part in spaced.split() if len(part) > _MIN_TOKEN_LEN]


def prose_tokens(text: str) -> list[str]:
    """Lowercase, stopword-filtered word tokens (the weak-signal fallback)."""
    return [w.lower() for w in _WORD_RE.findall(text) if w.lower() not in _STOPWORDS]


@dataclass
class QueryExpansion:
    """A weighted query plus the filename/identifier hints mined from a query."""

    terms: Counter = field(default_factory=Counter)
    path_hints: set[str] = field(default_factory=set)
    ident_hints: set[str] = field(default_factory=set)


def _mine_path_hints(text: str) -> set[str]:
    """File basenames mentioned as quoted paths or traceback frames."""
    hints = {Path(m).name.lower() for m in _PATH_RE.findall(text)}
    hints.update(Path(m).name.lower() for m in _TRACE_RE.findall(text))
    return hints


def expand_query(text: str) -> QueryExpansion:
    """Mine paths, identifiers and prose from a query into a weighted term set."""
    expansion = QueryExpansion(path_hints=_mine_path_hints(text))
    for regex, weight in _IDENTIFIER_WEIGHTS:
        for token in regex.findall(text):
            for sub in _split_identifier(token):
                expansion.terms[sub] += weight
                expansion.ident_hints.add(sub)
    for token in prose_tokens(text):
        expansion.terms[token] += 1
    return expansion


@dataclass(frozen=True)
class RepoContext:
    """Retrieved files with their candidate line spans and defined symbols."""

    files: tuple[str, ...] = ()
    spans: dict[str, list[tuple[int, int]]] = field(default_factory=dict)
    symbols: dict[str, list[str]] = field(default_factory=dict)


@dataclass
class _Document:
    """Per-file token statistics gathered once when indexing a work-tree."""

    rel: str
    lines: list[str]
    body: Counter
    path_tokens: set[str]
    length: int
    basename: str


def _iter_code_files(workdir: Path) -> Iterator[tuple[str, str]]:
    """Yield ``(relative_posix_path, text)`` for each in-scope code file."""
    for path in workdir.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in _CODE_SUFFIXES:
            continue
        try:
            if path.stat().st_size > _MAX_FILE_BYTES:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        yield path.relative_to(workdir).as_posix(), text


def _index_document(rel: str, text: str) -> _Document:
    """Build the token statistics for one file."""
    body = Counter(prose_tokens(text))
    path_tokens = set(prose_tokens(rel.replace("/", " ").replace(".", " ")))
    return _Document(
        rel=rel,
        lines=text.splitlines(),
        body=body,
        path_tokens=path_tokens,
        length=sum(body.values()),
        basename=Path(rel).name.lower(),
    )


def _compute_idf(docs: list[_Document]) -> dict[str, float]:
    """BM25 inverse-document-frequency for every term in the corpus."""
    doc_freq: Counter = Counter()
    for doc in docs:
        for term in doc.body:
            doc_freq[term] += 1
    n_docs = len(docs) or 1
    return {
        term: math.log(1 + (n_docs - df + 0.5) / (df + 0.5))
        for term, df in doc_freq.items()
    }


def _bm25_score(
    doc: _Document, terms: Counter, idf: dict[str, float], avg_len: float
) -> float:
    """BM25 relevance of one file against the weighted query terms."""
    score = 0.0
    for term, qweight in terms.items():
        freq = doc.body.get(term, 0)
        if not freq:
            continue
        denom = freq + _BM25_K1 * (1 - _BM25_B + _BM25_B * doc.length / avg_len)
        score += qweight * idf.get(term, 0.0) * (freq * (_BM25_K1 + 1)) / denom
    return score


def _filename_boost(doc: _Document, expansion: QueryExpansion) -> float:
    """Additive boost when a file's name matches a mined path/identifier."""
    bonus = 0.0
    if doc.basename in expansion.path_hints:
        bonus += _PATH_BOOST
    shared = doc.path_tokens & expansion.ident_hints
    return bonus + _IDENT_PATH_BOOST * len(shared)


class RepoContextRetriever(ABC):
    """Strategy: retrieve the repository context relevant to a query."""

    @abstractmethod
    def retrieve(self, query: str, workdir: Path) -> RepoContext:
        """Return the relevant files/spans/symbols for ``query`` under ``workdir``."""


class LexicalRepoRetriever(RepoContextRetriever):
    """BM25 lexical retriever with issue-aware query expansion (no model)."""

    def __init__(
        self,
        *,
        top_k: int = _DEFAULT_TOP_K,
        max_spans_per_file: int = _DEFAULT_MAX_SPANS,
        span_context: int = _DEFAULT_SPAN_CONTEXT,
        keep_ratio: float | None = None,
    ) -> None:
        self._top_k = max(1, top_k)
        self._max_spans = max(0, max_spans_per_file)
        self._span_context = max(0, span_context)
        # Dynamic cutoff: within the top_k, keep only files scoring at least
        # ``keep_ratio`` of the top score (drops the low-confidence tail so
        # precision is not capped by always emitting the full top_k). ``None``
        # keeps the fixed top_k behaviour.
        self._keep_ratio = keep_ratio
        # Corpus + IDF memo keyed by workdir: retriever instances are
        # per-review, so the work-tree is read and indexed once per
        # retriever lifetime instead of on every query (structural
        # expansion retrieves twice per query, iterative once per round).
        self._index_cache: dict[Path, tuple[list[_Document], dict[str, float]]] = {}

    def _corpus(self, workdir: Path) -> tuple[list[_Document], dict[str, float]]:
        """Indexed documents + IDF for ``workdir``, built once and memoized."""
        key = workdir.resolve()
        cached = self._index_cache.get(key)
        if cached is None:
            docs = [
                _index_document(rel, text)
                for rel, text in _iter_code_files(workdir)
            ]
            cached = (docs, _compute_idf(docs))
            self._index_cache[key] = cached
        return cached

    def retrieve(self, query: str, workdir: Path) -> RepoContext:
        """Rank the work-tree's code files against the expanded query."""
        workdir = Path(workdir)
        if not workdir.is_dir():
            raise FileNotFoundError(workdir)
        expansion = expand_query(query)
        docs, idf = self._corpus(workdir)
        if not docs:
            return RepoContext()
        scored = self._rank(docs, expansion, idf)
        top = self._select(scored)
        spans = {d.rel: self._spans(d, expansion.terms, idf) for d in top}
        symbols = {d.rel: self._symbols(d, spans[d.rel]) for d in top}
        return RepoContext(tuple(d.rel for d in top), spans, symbols)

    @staticmethod
    def _rank(
        docs: list[_Document], expansion: QueryExpansion, idf: dict[str, float]
    ) -> list[tuple[float, _Document]]:
        """Score docs by BM25 + filename boost, sorted high-to-low (ties by path)."""
        avg_len = sum(d.length for d in docs) / len(docs)
        scored = [
            (_bm25_score(d, expansion.terms, idf, avg_len) + _filename_boost(d, expansion), d)
            for d in docs
        ]
        scored.sort(key=lambda item: (-item[0], item[1].rel))
        return scored

    def _select(self, scored: list[tuple[float, _Document]]) -> list[_Document]:
        """Take the top_k, then drop the low-confidence tail below keep_ratio."""
        ranked = scored[: self._top_k]
        if not ranked or self._keep_ratio is None:
            return [doc for _, doc in ranked]
        threshold = self._keep_ratio * ranked[0][0]
        kept = [doc for score, doc in ranked if score >= threshold]
        return kept or [ranked[0][1]]

    def _spans(
        self, doc: _Document, terms: Counter, idf: dict[str, float]
    ) -> list[tuple[int, int]]:
        """Top IDF-weighted query-bearing lines, widened to context spans."""
        scored = []
        for lineno, line in enumerate(doc.lines, 1):
            weight = sum(
                terms[t] * idf.get(t, 0.0)
                for t in set(prose_tokens(line)) if t in terms
            )
            if weight:
                scored.append((weight, lineno))
        scored.sort(reverse=True)
        n_lines = len(doc.lines)
        spans = [
            (max(1, lineno - self._span_context), min(n_lines, lineno + self._span_context))
            for _, lineno in scored[: self._max_spans]
        ]
        return sorted(spans)

    @staticmethod
    def _symbols(doc: _Document, spans: list[tuple[int, int]]) -> list[str]:
        """def/class names defined on the predicted span lines."""
        covered = {ln for start, end in spans for ln in range(start, end + 1)}
        symbols: list[str] = []
        for lineno in sorted(covered):
            if lineno > len(doc.lines):
                continue
            match = _DEF_RE.match(doc.lines[lineno - 1])
            if match:
                symbols.append(match.group(1))
        return symbols


# --- structural (iterative) expansion ------------------------------------

_DEF_SCAN_RE = re.compile(r"^[ \t]*(?:def|class)\s+([A-Za-z_]\w*)", re.MULTILINE)
_IMPORT_SCAN_RE = re.compile(r"^[ \t]*(?:from|import)\s+([A-Za-z_][\w.]*)", re.MULTILINE)
_DEFAULT_EXPANSION_FILES = 3


def structural_terms(text: str) -> list[str]:
    """Defined symbol names and imported module leaves in a source file."""
    terms = _DEF_SCAN_RE.findall(text)
    terms += [module.split(".")[-1] for module in _IMPORT_SCAN_RE.findall(text)]
    return terms


class StructuralExpansionRetriever(RepoContextRetriever):
    """Two-round retriever that expands the query with round-one structure.

    Round one localises candidate files lexically; the symbols they define and
    the modules they import are fed back into the query for a second round, so
    the repository's own structure sharpens the retrieval. Model-free.
    """

    def __init__(
        self,
        base: LexicalRepoRetriever,
        *,
        expansion_files: int = _DEFAULT_EXPANSION_FILES,
    ) -> None:
        self._base = base
        self._expansion_files = max(1, expansion_files)

    def retrieve(self, query: str, workdir: Path) -> RepoContext:
        """Retrieve, expand the query with structural terms, retrieve again."""
        workdir = Path(workdir)
        first = self._base.retrieve(query, workdir)
        extra = self._structural_query(first, workdir)
        if not extra:
            return first
        return self._base.retrieve(f"{query} {extra}", workdir)

    def _structural_query(self, context: RepoContext, workdir: Path) -> str:
        """Collect structural terms from the top round-one files."""
        terms: list[str] = []
        for rel in context.files[: self._expansion_files]:
            try:
                text = (workdir / rel).read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            terms.extend(structural_terms(text))
        return " ".join(terms)


# --- semantic embedding retrieval ----------------------------------------

class Embedder(ABC):
    """Strategy: turn texts into dense vectors for semantic similarity."""

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one vector per input text, in order."""


def _cosine(vec_a: list[float], vec_b: list[float]) -> float:
    """Cosine similarity of two vectors (0.0 when either has zero norm)."""
    dot = sum(x * y for x, y in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(x * x for x in vec_a))
    norm_b = math.sqrt(sum(y * y for y in vec_b))
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0


class SentenceTransformerEmbedder(Embedder):
    """Embedder backed by sentence-transformers, loaded lazily on first use.

    The heavy model import is deferred to ``embed`` so importing this module
    stays runner-safe: constructing the embedder pulls in no ML dependency,
    only the first embedding call requires ``sentence-transformers`` installed.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self._model_name = model_name
        self._model = None

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Encode texts, loading the model on the first call."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer  # noqa: PLC0415

            self._model = SentenceTransformer(self._model_name)
        return [[float(x) for x in vector] for vector in self._model.encode(texts)]


class SemanticRepoRetriever(RepoContextRetriever):
    """Rank files by embedding similarity to the query (files only).

    The embedder is injected (Dependency Injection): tests supply a
    deterministic fake, production supplies a sentence-transformers model via
    the factory. Requires an embedding backend to run — no lexical fallback.
    """

    def __init__(self, embedder: Embedder, *, top_k: int = _DEFAULT_TOP_K) -> None:
        self._embedder = embedder
        self._top_k = max(1, top_k)

    def retrieve(self, query: str, workdir: Path) -> RepoContext:
        """Embed the query and every file, ranking files by cosine similarity."""
        workdir = Path(workdir)
        if not workdir.is_dir():
            raise FileNotFoundError(workdir)
        files = list(_iter_code_files(workdir))
        if not files:
            return RepoContext()
        vectors = self._embedder.embed([query] + [text for _, text in files])
        query_vec = vectors[0]
        scored = sorted(
            ((_cosine(query_vec, vec), rel) for vec, (rel, _) in zip(vectors[1:], files)),
            key=lambda item: (-item[0], item[1]),
        )
        return RepoContext(tuple(rel for _, rel in scored[: self._top_k]))


# --- LLM re-ranking (RAG retrieval + model localisation) -----------------

_DEFAULT_CANDIDATE_K = 20
_RERANK_SNIPPET_LINES = 4
_RERANK_MAX_NEW_TOKENS = 512


class _Backend(Protocol):
    """Minimal backend surface the reranker needs (any InferenceBackend fits)."""

    def generate(self, prompt: str, max_new_tokens: int) -> str:
        """Return the model's completion for ``prompt``."""


def _rerank_snippet(workdir: Path, rel: str, spans: list[tuple[int, int]]) -> str:
    """A few representative lines from a candidate file for the rerank prompt.

    Uses the predicted span when present, else falls back to the head of the
    file — so graph-expanded neighbour candidates (which carry no spans) are
    still shown as code, not a bare path, and the model can judge them.
    """
    try:
        lines = (workdir / rel).read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return ""
    start = spans[0][0] if spans else 1
    window = lines[start - 1: start - 1 + _RERANK_SNIPPET_LINES]
    return "\n".join(f"    {line}" for line in window)


def _build_rerank_prompt(query: str, candidates_block: str) -> str:
    """Prompt asking the model to rank the files that must change, most first.

    Deliberately selective (only files that likely need editing) so precision
    holds; the code snippet under each candidate lets the model judge on
    content, which keeps recall high without listing everything.
    """
    return (
        "You are localising the files relevant to a software issue. From the "
        "candidate files below, return only the files that most likely need to "
        "be edited to fix the issue, as a JSON array of their exact paths, MOST "
        "RELEVANT FIRST. Be selective: omit a file unless its code is directly "
        "involved.\n\n"
        f"Issue:\n{query}\n\nCandidate files:\n{candidates_block}\n"
    )


def _parse_selected(raw: str, candidates: tuple[str, ...]) -> list[str]:
    """Return mentioned candidate paths in the model's order (deduped)."""
    known = set(candidates)
    ordered: list[str] = []
    for path in _PATH_RE.findall(raw):
        if path in known and path not in ordered:
            ordered.append(path)
    return ordered


class RerankingRepoRetriever(RepoContextRetriever):
    """RAG localisation: retrieve candidates, then a backend selects the files.

    The candidate layer supplies recall (files + code snippets); the injected
    backend reads them and returns the relevant subset, ranked. This is the
    framework's retrieval-augmented, model-in-the-loop localisation. With
    ``votes > 1`` the selection is run several times and unioned
    (self-consistency), recovering recall lost to single-run model variance.
    """

    def __init__(
        self,
        base: RepoContextRetriever,
        backend: _Backend,
        *,
        max_new_tokens: int = _RERANK_MAX_NEW_TOKENS,
        votes: int = 1,
    ) -> None:
        self._base = base
        self._backend = backend
        self._max_new_tokens = max_new_tokens
        self._votes = max(1, votes)

    def retrieve(self, query: str, workdir: Path) -> RepoContext:
        """Retrieve candidates then keep the backend-selected (unioned) subset."""
        workdir = Path(workdir)
        candidates = self._base.retrieve(query, workdir)
        if not candidates.files:
            return candidates
        prompt = self._rerank_prompt(query, candidates, workdir)
        chosen = self._vote(prompt, candidates.files) or list(candidates.files)
        return RepoContext(
            tuple(chosen),
            {rel: candidates.spans.get(rel, []) for rel in chosen},
            {rel: candidates.symbols.get(rel, []) for rel in chosen},
        )

    def _vote(self, prompt: str, files: tuple[str, ...]) -> list[str]:
        """Union the selections across ``votes`` runs, preserving file order."""
        selected: set[str] = set()
        for _ in range(self._votes):
            raw = self._backend.generate(prompt, self._max_new_tokens)
            selected.update(_parse_selected(raw, files))
        return [rel for rel in files if rel in selected]

    def _rerank_prompt(self, query: str, candidates: RepoContext, workdir: Path) -> str:
        """Assemble the candidate list (paths + code snippets) into a prompt."""
        blocks = [
            f"- {rel}\n{_rerank_snippet(workdir, rel, candidates.spans.get(rel, []))}"
            for rel in candidates.files
        ]
        return _build_rerank_prompt(query, "\n".join(blocks))


# --- LLM query rewriting -------------------------------------------------

_QUERY_REWRITE_MAX_NEW_TOKENS = 256


def _build_query_rewrite_prompt(issue: str) -> str:
    """Prompt asking the model for the best code-search terms for an issue."""
    return (
        "Extract the most useful code-search terms for locating the files to "
        "fix this issue: key symbols (class/function names), the component or "
        "module involved, and any error identifier. Return a short "
        "space-separated list of terms only, no prose.\n\n"
        f"Issue:\n{issue}\n"
    )


class QueryRewritingRetriever(RepoContextRetriever):
    """Rewrite a verbose issue into focused search terms, then retrieve.

    A single cheap backend call distils the issue into the symbols / component
    / error terms most useful for retrieval; those terms are appended to the
    original query before delegating to the base retriever, sharpening recall.
    """

    def __init__(
        self,
        base: RepoContextRetriever,
        backend: _Backend,
        *,
        max_new_tokens: int = _QUERY_REWRITE_MAX_NEW_TOKENS,
    ) -> None:
        self._base = base
        self._backend = backend
        self._max_new_tokens = max_new_tokens

    def retrieve(self, query: str, workdir: Path) -> RepoContext:
        """Distil the query via the backend, then retrieve with it appended."""
        prompt = _build_query_rewrite_prompt(query)
        terms = self._backend.generate(prompt, self._max_new_tokens).strip()
        expanded = f"{query} {terms}" if terms else query
        return self._base.retrieve(expanded, Path(workdir))


# --- graph-guided candidate expansion (LocAgent-style structural recall) --


_DEF_HEAD_RE = re.compile(r"^([ \t]*)(?:def|class)\s+([A-Za-z_]\w*)")
_DEFAULT_MAX_BLOCKS = 3


def enclosing_blocks(lines: list[str]) -> list[tuple[int, int, str]]:
    """Return ``(start, end, name)`` for each def/class block, by indentation.

    A block runs from its ``def``/``class`` header to the line before the next
    non-blank line indented at or below the header — i.e. the whole function or
    class body. 1-based, inclusive; this matches ContextBench gold spans, which
    are whole blocks rather than isolated lines.
    """
    blocks = []
    for index, line in enumerate(lines):
        match = _DEF_HEAD_RE.match(line)
        if not match:
            continue
        indent = len(match.group(1))
        end = _block_end(lines, index, indent)
        blocks.append((index + 1, end, match.group(2)))
    return blocks


def _block_end(lines: list[str], header_index: int, indent: int) -> int:
    """1-based last non-blank line of the block opened at ``header_index``."""
    end = len(lines)
    for probe in range(header_index + 1, len(lines)):
        stripped = lines[probe].strip()
        if stripped and len(lines[probe]) - len(lines[probe].lstrip()) <= indent:
            end = probe
            break
    while end > header_index + 1 and not lines[end - 1].strip():
        end -= 1
    return end


def focus_window(
    lines: list[str], span: tuple[int, int],
    terms: Counter, idf: dict[str, float], window_lines: int,
) -> tuple[int, int]:
    """Narrow a block span to its densest ``window_lines``-line query window.

    Whole-block spans over-predict lines (high recall, low precision); the
    ContextBench finding is that the balance point is a granularity of a few
    dozen lines, so this slides a fixed window over the block and keeps the one
    carrying the most IDF-weighted query-term mass. Blocks already within the
    window are returned unchanged.
    """
    start, end = span
    if end - start + 1 <= window_lines:
        return span
    weights = [
        sum(terms[t] * idf.get(t, 0.0)
            for t in set(prose_tokens(lines[i])) if t in terms)
        for i in range(start - 1, end)
    ]
    running = sum(weights[:window_lines])
    best_sum, best_offset = running, 0
    for offset in range(1, len(weights) - window_lines + 1):
        running += weights[offset + window_lines - 1] - weights[offset - 1]
        if running > best_sum:
            best_sum, best_offset = running, offset
    win_start = start + best_offset
    return win_start, win_start + window_lines - 1


def predict_blocks(
    terms: Counter, idf: dict[str, float], lines: list[str], max_blocks: int,
    *, max_block_lines: int | None = None, focus_lines: int | None = None,
) -> tuple[list[tuple[int, int]], list[str]]:
    """Rank def/class blocks by query relevance; return top block spans + names.

    Scores each block by the IDF-weighted query-term mass in its body, so the
    prediction is function-granular (spans = whole blocks, symbols = their
    names) instead of scattered line windows. ``max_block_lines`` drops blocks
    longer than the cap — a whole-class block spanning hundreds of lines is too
    coarse to be precise context, so excluding it lets the enclosed method
    blocks (also enumerated here) stand in at function granularity.
    ``focus_lines`` narrows each kept block to its densest query window, trading
    a little recall for precision at the ContextBench balance-point granularity.
    """
    top = _scored_blocks(terms, idf, lines, max_block_lines)[:max_blocks]
    spans = [
        focus_window(lines, (start, end), terms, idf, focus_lines)
        if focus_lines is not None else (start, end)
        for _, start, end, _ in top
    ]
    symbols = [name for _, _, _, name in top]
    return sorted(spans), symbols


def _scored_blocks(
    terms: Counter, idf: dict[str, float], lines: list[str],
    max_block_lines: int | None,
) -> list[tuple[float, int, int, str]]:
    """Blocks under the line cap by IDF-weighted query-term mass, best first."""
    scored = []
    for start, end, name in enclosing_blocks(lines):
        if max_block_lines is not None and end - start + 1 > max_block_lines:
            continue
        body_tokens = set(prose_tokens(" ".join(lines[start - 1:end])))
        weight = sum(terms[t] * idf.get(t, 0.0) for t in body_tokens if t in terms)
        if weight:
            scored.append((weight, start, end, name))
    scored.sort(key=lambda item: (-item[0], item[1]))
    return scored


def enrich_context_spans(
    context: RepoContext, query: str, workdir: Path,
    *, max_blocks: int = _DEFAULT_MAX_BLOCKS, max_block_lines: int | None = None,
    focus_lines: int | None = None,
) -> RepoContext:
    """Predict function-block spans + symbols for every file in a context.

    Retrieval strategies that add files without spans (graph neighbours, LLM
    reranks) leave the line/symbol dimensions empty; this fills them by ranking
    each retrieved file's def/class blocks against the query and predicting the
    top blocks' whole spans and names — matching the block granularity of the
    gold context so line- and symbol-level scores reflect real predictions.
    ``max_block_lines`` caps block size so coarse whole-class spans give way to
    their enclosed methods (keeps line/symbol precision from collapsing).
    """
    workdir = Path(workdir)
    # Read only the files already in the context — walking the whole
    # work-tree to reach a handful of known paths is wasted I/O.
    texts: dict[str, str] = {}
    for rel in context.files:
        try:
            texts[rel] = (workdir / rel).read_text(
                encoding="utf-8", errors="ignore"
            )
        except OSError:
            continue
    idf = _compute_idf([_index_document(rel, text) for rel, text in texts.items()])
    terms = expand_query(query).terms
    spans, symbols = {}, {}
    for rel, text in texts.items():
        block_spans, block_symbols = predict_blocks(
            terms, idf, text.splitlines(), max_blocks,
            max_block_lines=max_block_lines, focus_lines=focus_lines,
        )
        spans[rel] = block_spans
        symbols[rel] = block_symbols
    return RepoContext(context.files, spans, symbols)

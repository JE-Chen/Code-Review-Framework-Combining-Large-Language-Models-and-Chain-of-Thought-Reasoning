"""Tests for the repository context retriever (prthinker.repo_retrieval)."""

from __future__ import annotations

import pytest

from prthinker.repo_retrieval import (
    BlockRerankingRetriever,
    Embedder,
    GraphExpandedRetriever,
    IterativeRetriever,
    LexicalRepoRetriever,
    QueryExpansion,
    RepoContext,
    QueryRewritingRetriever,
    RepoContextRetriever,
    RerankingRepoRetriever,
    SemanticRepoRetriever,
    StructuralExpansionRetriever,
    _context_from_blocks,
    _parse_block_selection,
    _parse_iter_response,
    _parse_selected,
    _split_identifier,
    _resolve_import,
    bidirectional_neighbours,
    build_import_adjacency,
    build_python_import_graph,
    create_repo_retriever,
    expand_query,
    prose_tokens,
    structural_terms,
)


def _make_repo(tmp_path, files: dict[str, str]):
    """Materialise a fake work-tree from a ``{relative_path: content}`` map."""
    for rel, content in files.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return tmp_path


# --------------------------------------------------------------------------
# pure helpers
# --------------------------------------------------------------------------

def test_split_identifier_camel_and_snake():
    assert _split_identifier("EarthLocationAttribute") == ["earth", "location", "attribute"]
    assert _split_identifier("itrs_to_observed") == ["itrs", "observed"]


def test_split_identifier_drops_short_parts():
    # single/short fragments (<= 2 chars) are not useful query terms
    assert _split_identifier("a_bc_def") == ["def"]


def test_prose_tokens_lowercases_and_drops_stopwords():
    tokens = prose_tokens("The FooBar Should return Baz")
    assert "foobar" in tokens and "baz" in tokens
    assert "should" not in tokens and "return" not in tokens


def test_expand_query_mines_paths_from_traceback_and_quotes():
    text = 'Traceback:\n  File "astropy/coordinates/itrs.py", line 5\nsee `admin/options.py`'
    expansion = expand_query(text)
    assert "itrs.py" in expansion.path_hints
    assert "options.py" in expansion.path_hints


def test_expand_query_weights_identifiers_above_prose():
    expansion = expand_query("The EarthLocationAttribute broke during widget rendering")
    # identifier sub-words are weighted (>=5 for CamelCase) above prose (==1)
    assert expansion.terms["earth"] >= 5
    assert expansion.terms["widget"] == 1
    assert "earth" in expansion.ident_hints


def test_expand_query_empty_text():
    expansion = expand_query("")
    assert expansion.terms == QueryExpansion().terms
    assert not expansion.path_hints and not expansion.ident_hints


# --------------------------------------------------------------------------
# retrieval
# --------------------------------------------------------------------------

def test_retrieve_ranks_relevant_file_first(tmp_path):
    repo = _make_repo(tmp_path, {
        "pkg/widgets.py": "class WidgetRenderer:\n    def render(self):\n        return 1\n",
        "pkg/unrelated.py": "def add(a, b):\n    return a + b\n",
        "README.md": "not a code file",
    })
    retriever = LexicalRepoRetriever()
    result = retriever.retrieve("WidgetRenderer fails to render", repo)
    assert result.files[0] == "pkg/widgets.py"
    assert "pkg/unrelated.py" in result.files  # still retrieved, ranked lower


def test_retrieve_filename_boost_beats_body_only_match(tmp_path):
    # Both files mention "options"; the one whose *path* matches the mined
    # traceback file name must win via the filename boost.
    repo = _make_repo(tmp_path, {
        "admin/options.py": "def configure():\n    options = 1\n    return options\n",
        "core/helpers.py": "def helper():\n    options = options = options = 1\n    return options\n",
    })
    retriever = LexicalRepoRetriever()
    result = retriever.retrieve('Traceback File "admin/options.py" options broken', repo)
    assert result.files[0] == "admin/options.py"


def test_retrieve_predicts_spans_and_symbols(tmp_path):
    repo = _make_repo(tmp_path, {
        "m.py": "import os\n\n\nclass Alpha:\n    def beta(self):\n        return widget\n",
    })
    retriever = LexicalRepoRetriever()
    result = retriever.retrieve("widget", repo)
    assert result.spans["m.py"], "expected at least one span on the matching line"
    start, end = result.spans["m.py"][0]
    assert start <= 6 <= end
    # a def/class inside the span line range is surfaced as a symbol
    assert "beta" in result.symbols["m.py"] or "Alpha" in result.symbols["m.py"]


def test_retrieve_respects_top_k(tmp_path):
    repo = _make_repo(tmp_path, {f"f{i}.py": f"def g{i}():\n    return token\n" for i in range(20)})
    result = LexicalRepoRetriever(top_k=3).retrieve("token", repo)
    assert len(result.files) == 3


def test_retrieve_max_spans_zero_predicts_no_spans(tmp_path):
    repo = _make_repo(tmp_path, {"a.py": "def f():\n    return token\n"})
    result = LexicalRepoRetriever(max_spans_per_file=0).retrieve("token", repo)
    assert result.spans["a.py"] == []


def test_keep_ratio_drops_low_confidence_tail(tmp_path):
    # One strongly-matching file (name + body) and several irrelevant ones; the
    # dynamic cutoff keeps the strong file and drops the zero-signal tail.
    files = {"target_widget.py": "class Widget:\n    widget = widget = widget\n"}
    files.update({f"noise{i}.py": "def alpha():\n    return beta\n" for i in range(8)})
    repo = _make_repo(tmp_path, files)
    strict = LexicalRepoRetriever(keep_ratio=0.6).retrieve("Widget widget", repo)
    loose = LexicalRepoRetriever(keep_ratio=None).retrieve("Widget widget", repo)
    assert "target_widget.py" in strict.files
    assert len(strict.files) < len(loose.files)


def test_keep_ratio_always_keeps_at_least_one(tmp_path):
    repo = _make_repo(tmp_path, {f"f{i}.py": "def g():\n    return token\n" for i in range(5)})
    result = LexicalRepoRetriever(keep_ratio=0.99).retrieve("token", repo)
    assert len(result.files) >= 1


def test_retrieve_empty_repo_returns_empty_context(tmp_path):
    result = LexicalRepoRetriever().retrieve("anything", tmp_path)
    assert result == RepoContext()
    assert result.files == ()


def test_retrieve_ignores_non_code_and_oversized_files(tmp_path):
    big = "x = 'token'\n" + "# pad\n" * 200_000  # > 1 MB
    repo = _make_repo(tmp_path, {
        "keep.py": "def f():\n    return token\n",
        "notes.txt": "token token token",
        "huge.py": big,
    })
    result = LexicalRepoRetriever().retrieve("token", repo)
    assert "keep.py" in result.files
    assert "notes.txt" not in result.files  # non-code suffix
    assert "huge.py" not in result.files    # oversized, skipped


def test_retrieve_missing_workdir_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        LexicalRepoRetriever().retrieve("q", tmp_path / "does_not_exist")


def test_retrieve_handles_undecodable_bytes(tmp_path):
    (tmp_path / "bin.py").write_bytes(b"\xff\xfe def token():\n    pass\n")
    # errors='ignore' means the file is read, not crashed on
    result = LexicalRepoRetriever().retrieve("token", tmp_path)
    assert "bin.py" in result.files


# --------------------------------------------------------------------------
# factory
# --------------------------------------------------------------------------

def test_factory_builds_lexical_strategy():
    retriever = create_repo_retriever("lexical", top_k=5)
    assert isinstance(retriever, LexicalRepoRetriever)
    assert isinstance(retriever, RepoContextRetriever)


def test_factory_unknown_kind_raises():
    with pytest.raises(ValueError, match="unknown repo retriever"):
        create_repo_retriever("magic")


# --------------------------------------------------------------------------
# structural (iterative) expansion
# --------------------------------------------------------------------------

def test_structural_terms_extracts_symbols_and_imports():
    text = "from pkg.helpers import thing\nimport os\nclass Widget:\n    def render(self):\n        pass\n"
    terms = structural_terms(text)
    assert "Widget" in terms and "render" in terms
    assert "helpers" in terms and "os" in terms  # imported module leaves


def test_structural_expansion_uses_round_one_structure(tmp_path):
    # The issue never names WidgetRenderer, but a lexical hit on "render" pulls
    # in renderer.py, whose class name then expands the query to reach caller.py.
    repo = _make_repo(tmp_path, {
        "renderer.py": "class WidgetRenderer:\n    def render(self):\n        return 1\n",
        "caller.py": "x = 'WidgetRenderer instance used here'\n" * 3,
        "noise.py": "def f():\n    return 0\n",
    })
    base = LexicalRepoRetriever(top_k=2)
    result = StructuralExpansionRetriever(base).retrieve("render pipeline", repo)
    assert "caller.py" in result.files


# --------------------------------------------------------------------------
# semantic embedding retrieval (injected embedder)
# --------------------------------------------------------------------------

class _KeywordEmbedder(Embedder):
    """Deterministic test embedder: vector = counts of a fixed vocabulary."""

    _VOCAB = ("widget", "parser", "network")

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [[float(t.lower().count(word)) for word in self._VOCAB] for t in texts]


def test_semantic_retriever_ranks_by_embedding_similarity(tmp_path):
    repo = _make_repo(tmp_path, {
        "widget.py": "widget widget widget\n",
        "parser.py": "parser parser parser\n",
    })
    result = SemanticRepoRetriever(_KeywordEmbedder(), top_k=1).retrieve("widget bug", repo)
    assert result.files == ("widget.py",)


def test_semantic_retriever_missing_workdir_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        SemanticRepoRetriever(_KeywordEmbedder()).retrieve("q", tmp_path / "nope")


def test_factory_semantic_accepts_injected_embedder():
    retriever = create_repo_retriever("semantic", embedder=_KeywordEmbedder())
    assert isinstance(retriever, SemanticRepoRetriever)


def test_factory_semantic_default_embedder_is_lazy():
    # Building the default semantic retriever must NOT import the heavy ML
    # stack (it loads only on the first embed call), keeping the module
    # runner-safe.
    import sys

    retriever = create_repo_retriever("semantic")
    assert isinstance(retriever, SemanticRepoRetriever)
    assert "sentence_transformers" not in sys.modules


# --------------------------------------------------------------------------
# LLM re-ranking (RAG retrieval + model selection)
# --------------------------------------------------------------------------

class _SelectingBackend:
    """Fake backend that echoes a fixed selection as a JSON array."""

    def __init__(self, selection: list[str]) -> None:
        self._selection = selection
        self.prompts: list[str] = []

    def generate(self, prompt: str, max_new_tokens: int) -> str:
        self.prompts.append(prompt)
        return json_dumps(self._selection)


def json_dumps(value) -> str:
    import json

    return json.dumps(value)


def test_parse_selected_keeps_only_known_candidates():
    candidates = ("a/x.py", "b/y.py", "c/z.py")
    raw = 'I pick `c/z.py` and "a/x.py" and unknown/other.py.'
    # model order preserved; unknown paths dropped
    assert _parse_selected(raw, candidates) == ["c/z.py", "a/x.py"]


def test_reranking_retriever_keeps_backend_selection(tmp_path):
    repo = _make_repo(tmp_path, {
        "keep.py": "def relevant():\n    return token\n",
        "drop.py": "def other():\n    return token\n",
    })
    backend = _SelectingBackend(["keep.py"])
    base = LexicalRepoRetriever(top_k=5)
    result = RerankingRepoRetriever(base, backend).retrieve("token", repo)
    assert result.files == ("keep.py",)
    assert backend.prompts and "Candidate files:" in backend.prompts[0]


def test_reranking_falls_back_when_selection_unparseable(tmp_path):
    repo = _make_repo(tmp_path, {"a.py": "def f():\n    return token\n"})
    backend = _SelectingBackend([])  # returns "[]" -> nothing parseable
    result = RerankingRepoRetriever(LexicalRepoRetriever(), backend).retrieve("token", repo)
    assert "a.py" in result.files  # falls back to the candidate set, never empty


def test_factory_rerank_needs_backend():
    retriever = create_repo_retriever("rerank", backend=_SelectingBackend(["x"]))
    assert isinstance(retriever, RerankingRepoRetriever)


# --------------------------------------------------------------------------
# block-level LLM re-ranking (precise line/symbol context selection)
# --------------------------------------------------------------------------

class _IndexBackend:
    """Fake backend that echoes a fixed list of block indices as a JSON array."""

    def __init__(self, indices: list[int]) -> None:
        self._indices = indices
        self.prompts: list[str] = []

    def generate(self, prompt: str, max_new_tokens: int) -> str:
        self.prompts.append(prompt)
        return json_dumps(self._indices)


_THREE_BLOCKS = (
    "def alpha():\n    return token\n"
    "def beta():\n    return token\n"
    "def gamma():\n    return token\n"
)


def test_parse_block_selection_maps_indices_and_drops_out_of_range():
    rows = [("a.py", 1, 2, "f"), ("b.py", 3, 4, "g")]
    assert _parse_block_selection("[0, 5, 1]", rows) == {("a.py", 1), ("b.py", 3)}
    assert _parse_block_selection("no json here", rows) == set()   # no array
    assert _parse_block_selection("[oops not json]", rows) == set()  # bad json
    assert _parse_block_selection("[1.5]", rows) == set()          # non-int dropped


def test_context_from_blocks_groups_spans_and_symbols_by_file():
    rows = [("a.py", 1, 2, "f"), ("a.py", 5, 6, "h"), ("b.py", 3, 4, "")]
    ctx = _context_from_blocks(("a.py", "b.py"), rows)
    assert ctx.spans == {"a.py": [(1, 2), (5, 6)], "b.py": [(3, 4)]}
    assert ctx.symbols == {"a.py": ["f", "h"]}  # blank name contributes no symbol
    assert ctx.files == ("a.py", "b.py")


def test_block_rerank_keeps_only_the_selected_block(tmp_path):
    repo = _make_repo(tmp_path, {"m.py": _THREE_BLOCKS})
    backend = _IndexBackend([1])  # the beta block (lines 3-4)
    result = BlockRerankingRetriever(LexicalRepoRetriever(top_k=5), backend).retrieve(
        "token", repo)
    assert result.spans["m.py"] == [(3, 4)]   # precise: only the chosen block
    assert result.symbols["m.py"] == ["beta"]
    assert result.files == ("m.py",)          # file localisation preserved
    assert "Candidate blocks:" in backend.prompts[0]


def test_block_rerank_unions_votes(tmp_path):
    repo = _make_repo(tmp_path, {"m.py": _THREE_BLOCKS})

    class _Alt:
        def __init__(self) -> None:
            self.n = 0

        def generate(self, prompt, max_new_tokens):
            self.n += 1
            return json_dumps([0] if self.n == 1 else [2])

    result = BlockRerankingRetriever(
        LexicalRepoRetriever(), _Alt(), votes=2).retrieve("token", repo)
    assert result.spans["m.py"] == [(1, 2), (5, 6)]  # alpha + gamma, order kept


def test_block_rerank_falls_back_when_nothing_selected(tmp_path):
    repo = _make_repo(tmp_path, {"m.py": _THREE_BLOCKS})
    backend = _IndexBackend([])  # empty selection
    result = BlockRerankingRetriever(LexicalRepoRetriever(), backend).retrieve(
        "token", repo)
    assert result.spans["m.py"]  # never empty — keeps all candidate blocks


def test_block_rerank_empty_repo_returns_empty(tmp_path):
    result = BlockRerankingRetriever(
        LexicalRepoRetriever(), _IndexBackend([0])).retrieve("q", tmp_path)
    assert result.files == ()


def test_factory_block_rerank_builds_retriever():
    retriever = create_repo_retriever("block_rerank", backend=_IndexBackend([0]))
    assert isinstance(retriever, BlockRerankingRetriever)


def test_predict_blocks_cap_drops_coarse_class_for_its_methods():
    # A class spanning the whole file vs its two short methods: without a cap the
    # class block dominates (coarse, over-predicts lines); with a cap it is
    # dropped and the focused method blocks stand in.
    from collections import Counter

    from prthinker.repo_retrieval import predict_blocks

    lines = ["class Big:"]
    for i in range(200):
        lines.append(f"    x{i} = token" if i in (10, 150) else f"    x{i} = 0")
    idf = {"token": 1.0}
    terms = Counter({"token": 3})
    uncapped, _ = predict_blocks(terms, idf, lines, max_blocks=5)
    capped, _ = predict_blocks(terms, idf, lines, max_blocks=5, max_block_lines=120)
    assert (1, len(lines)) in uncapped            # whole-class block selected
    assert (1, len(lines)) not in capped          # coarse block excluded by cap


def test_block_rerank_cap_excludes_oversized_blocks(tmp_path):
    body = "".join(f"        v{i} = token\n" for i in range(200))
    repo = _make_repo(tmp_path, {
        "m.py": f"class C:\n    def method(self):\n{body}\n"
    })
    backend = _IndexBackend([0])
    result = BlockRerankingRetriever(
        LexicalRepoRetriever(), backend, max_block_lines=50).retrieve("token", repo)
    for spans in result.spans.values():
        for start, end in spans:
            assert end - start + 1 <= 50  # no block longer than the cap survives


def test_focus_window_picks_densest_query_region():
    from collections import Counter

    from prthinker.repo_retrieval import focus_window

    lines = [f"filler line {i}" for i in range(100)]
    lines[70] = "the token appears right here"
    win = focus_window(lines, (1, 100), Counter({"token": 1}), {"token": 1.0}, 10)
    assert win[1] - win[0] + 1 == 10       # exactly the window size
    assert win[0] <= 71 <= win[1]          # covers the query line (1-based 71)


def test_focus_window_short_block_returned_unchanged():
    from collections import Counter

    from prthinker.repo_retrieval import focus_window

    assert focus_window(["a", "b", "c"], (1, 3),
                        Counter({"x": 1}), {"x": 1.0}, 10) == (1, 3)


def test_predict_blocks_focus_narrows_to_window():
    from collections import Counter

    from prthinker.repo_retrieval import predict_blocks

    lines = ["def big():"] + [f"    v{i} = 0" for i in range(100)]
    lines[80] = "    y = token"
    spans, _ = predict_blocks(
        Counter({"token": 1}), {"token": 1.0}, lines, 5, focus_lines=10)
    assert spans and all(end - start + 1 <= 10 for start, end in spans)


# --------------------------------------------------------------------------
# iterative (agentic) multi-round retrieval
# --------------------------------------------------------------------------

class _JsonBackend:
    """Fake backend replaying a scripted sequence of JSON round responses."""

    def __init__(self, responses: list[str]) -> None:
        self._responses = responses
        self.prompts: list[str] = []

    def generate(self, prompt: str, max_new_tokens: int) -> str:
        self.prompts.append(prompt)
        return self._responses.pop(0) if self._responses else '{"done": true}'


def test_parse_iter_response_reads_blocks_query_and_done():
    rows = [("a.py", 1, 2, "f"), ("b.py", 3, 4, "g")]
    step = _parse_iter_response(
        '{"blocks": [1, 9], "next_query": "more", "done": false}', rows)
    assert step.rows == (("b.py", 3, 4, "g"),)   # index 9 out of range dropped
    assert step.next_query == "more" and step.done is False


def test_parse_iter_response_stops_on_unparseable():
    rows = [("a.py", 1, 2, "f")]
    assert _parse_iter_response("no json", rows).done is True
    assert _parse_iter_response("{bad json", rows).done is True


def test_iterative_retriever_explores_new_files_across_rounds(tmp_path):
    repo = _make_repo(tmp_path, {
        "alpha.py": "def af():\n    return alphaword\n",
        "beta.py": "def bf():\n    return betaword\n",
    })
    backend = _JsonBackend([
        '{"blocks": [0], "next_query": "betaword", "done": false}',  # round 1
        '{"blocks": [0], "next_query": "", "done": true}',           # round 2
    ])
    result = IterativeRetriever(
        LexicalRepoRetriever(top_k=3), backend, rounds=3).retrieve("alphaword", repo)
    assert set(result.files) == {"alpha.py", "beta.py"}  # 2nd query surfaced beta
    assert result.spans.get("alpha.py") and result.spans.get("beta.py")
    assert len(backend.prompts) == 2  # stopped when done


def test_iterative_retriever_stops_on_first_round_done(tmp_path):
    repo = _make_repo(tmp_path, {"alpha.py": "def af():\n    return alphaword\n"})
    backend = _JsonBackend(['{"blocks": [0], "next_query": "x", "done": true}'])
    result = IterativeRetriever(
        LexicalRepoRetriever(), backend, rounds=3).retrieve("alphaword", repo)
    assert result.files == ("alpha.py",)
    assert len(backend.prompts) == 1  # done after one round


def test_iterative_retriever_stops_on_empty_next_query(tmp_path):
    repo = _make_repo(tmp_path, {"alpha.py": "def af():\n    return alphaword\n"})
    backend = _JsonBackend(['{"blocks": [0], "next_query": "  ", "done": false}'])
    IterativeRetriever(
        LexicalRepoRetriever(), backend, rounds=3).retrieve("alphaword", repo)
    assert len(backend.prompts) == 1  # blank next query ends the loop


def test_factory_iterative_builds_retriever():
    retriever = create_repo_retriever("iterative", backend=_JsonBackend([]))
    assert isinstance(retriever, IterativeRetriever)


def test_factory_structural_wraps_lexical_base():
    retriever = create_repo_retriever("structural", top_k=4)
    assert isinstance(retriever, StructuralExpansionRetriever)


# --------------------------------------------------------------------------
# graph-guided candidate expansion
# --------------------------------------------------------------------------

def test_build_python_import_graph_resolves_to_files():
    files = [
        ("pkg/a.py", "from pkg.b import thing\nimport pkg.c\n"),
        ("pkg/b.py", "x = 1\n"),
        ("pkg/c.py", "y = 2\n"),
    ]
    graph = build_python_import_graph(files)
    assert graph["pkg/a.py"] == {"pkg/b.py", "pkg/c.py"}
    assert graph["pkg/b.py"] == set()


def test_resolve_import_falls_back_to_shorter_prefix():
    index = {"pkg.sub": "pkg/sub/__init__.py"}
    assert _resolve_import("pkg.sub.deep.thing", index) == "pkg/sub/__init__.py"
    assert _resolve_import("unknown.mod", index) is None


def test_graph_expansion_adds_import_neighbours(tmp_path):
    # The query hits handler.py lexically; util.py is reachable only via the
    # import edge, so graph expansion must surface it as an extra candidate.
    repo = _make_repo(tmp_path, {
        "app/handler.py": "from app.util import helper\n\ndef handle():\n    return widget\n",
        "app/util.py": "def helper():\n    return 1\n",
        "app/unrelated.py": "def z():\n    return 0\n",
    })
    base = LexicalRepoRetriever(top_k=1)
    result = GraphExpandedRetriever(base, neighbour_budget=5).retrieve("widget handle", repo)
    assert "app/handler.py" in result.files
    assert "app/util.py" in result.files  # added purely via the import graph


def test_graph_expansion_zero_budget_returns_base(tmp_path):
    repo = _make_repo(tmp_path, {
        "a.py": "from b import x\n\ndef f():\n    return token\n",
        "b.py": "x = 1\n",
    })
    base = LexicalRepoRetriever(top_k=1)
    result = GraphExpandedRetriever(base, neighbour_budget=0).retrieve("token", repo)
    assert len(result.files) == 1


def test_factory_graph_wraps_lexical_base():
    assert isinstance(create_repo_retriever("graph"), GraphExpandedRetriever)


def test_bidirectional_neighbours_unions_imports_and_importers():
    graph = {"a.py": {"b.py"}, "c.py": {"b.py"}, "b.py": set()}
    adjacency = bidirectional_neighbours(graph)
    # b.py is imported by a and c; a/c each depend on b
    assert adjacency["b.py"] == {"a.py", "c.py"}
    assert adjacency["a.py"] == {"b.py"}


def test_build_import_adjacency_from_worktree(tmp_path):
    repo = _make_repo(tmp_path, {
        "a.py": "from b import x\n",
        "b.py": "y = 1\n",
    })
    adjacency = build_import_adjacency(repo)
    assert adjacency["b.py"] == {"a.py"}
    assert adjacency["a.py"] == {"b.py"}


def test_enclosing_blocks_spans_whole_functions():
    from prthinker.repo_retrieval import enclosing_blocks

    lines = "class A:\n    def foo(self):\n        return 1\n\ndef top():\n    pass\n".split("\n")
    blocks = enclosing_blocks(lines)
    assert (1, 3, "A") in blocks  # class A spans its whole body (blank trimmed)
    assert (2, 3, "foo") in blocks
    assert any(name == "top" and start == 5 for start, _, name in blocks)


def test_predict_blocks_ranks_and_returns_symbols():
    from collections import Counter

    from prthinker.repo_retrieval import predict_blocks

    lines = (
        "def relevant():\n    return widget\n\n"
        "def other():\n    return 1\n"
    ).split("\n")
    spans, symbols = predict_blocks(Counter({"widget": 5}), {"widget": 2.0}, lines, 3)
    assert (1, 2) in spans        # the whole relevant() block
    assert symbols[0] == "relevant"  # its name is the predicted symbol


def test_enrich_context_spans_predicts_block_and_symbol(tmp_path):
    from prthinker.repo_retrieval import enrich_context_spans

    repo = _make_repo(tmp_path, {
        "m.py": "import os\n\n\nclass Alpha:\n    def beta(self):\n        return widget\n",
    })
    bare = RepoContext(files=("m.py",))
    enriched = enrich_context_spans(bare, "widget", repo)
    assert enriched.spans["m.py"], "a block span should be predicted"
    start, end = enriched.spans["m.py"][0]
    assert start <= 6 <= end  # the block containing 'widget' covers line 6
    # the enclosing def/class name is surfaced as a symbol
    assert set(enriched.symbols["m.py"]) & {"Alpha", "beta"}


def test_graph_multi_hop_reaches_further_neighbours(tmp_path):
    # a -> b -> c chain. Seeding from a, hops=1 reaches b only; hops=2 reaches c.
    repo = _make_repo(tmp_path, {
        "a.py": "from b import x\n\ndef f():\n    return token\n",
        "b.py": "from c import y\n",
        "c.py": "z = 1\n",
    })
    base = LexicalRepoRetriever(top_k=1)
    one = GraphExpandedRetriever(base, hops=1, neighbour_budget=10).retrieve("token", repo)
    two = GraphExpandedRetriever(base, hops=2, neighbour_budget=10).retrieve("token", repo)
    assert "b.py" in one.files and "c.py" not in one.files
    assert "b.py" in two.files and "c.py" in two.files


# --------------------------------------------------------------------------
# rerank refinements: snippet fallback, ranked order, multi-vote
# --------------------------------------------------------------------------

def test_parse_selected_preserves_model_order():
    candidates = ("a/x.py", "b/y.py", "c/z.py")
    raw = '["c/z.py", "a/x.py"]'  # model ranks z first
    assert _parse_selected(raw, candidates) == ["c/z.py", "a/x.py"]


def test_rerank_snippet_falls_back_to_file_head(tmp_path):
    from prthinker.repo_retrieval import _rerank_snippet

    (tmp_path / "f.py").write_text("line1\nline2\nline3\n", encoding="utf-8")
    # No spans -> head of file is shown (not empty), so neighbours are judged.
    snippet = _rerank_snippet(tmp_path, "f.py", [])
    assert "line1" in snippet


def test_rerank_multi_vote_unions_selections(tmp_path):
    repo = _make_repo(tmp_path, {
        "a.py": "def f():\n    return token\n",
        "b.py": "def g():\n    return token\n",
    })

    class _AlternatingBackend:
        def __init__(self):
            self._n = 0

        def generate(self, prompt, max_new_tokens):
            self._n += 1
            return '["a.py"]' if self._n == 1 else '["b.py"]'

    backend = _AlternatingBackend()
    base = LexicalRepoRetriever(top_k=5)
    result = RerankingRepoRetriever(base, backend, votes=2).retrieve("token", repo)
    # Union of the two votes keeps both files.
    assert set(result.files) >= {"a.py", "b.py"}


# --------------------------------------------------------------------------
# query rewriting
# --------------------------------------------------------------------------

def test_query_rewriting_appends_backend_terms(tmp_path):
    repo = _make_repo(tmp_path, {
        "widget.py": "class WidgetRenderer:\n    pass\n",
        "misc.py": "def h():\n    return 0\n",
    })

    class _TermBackend:
        def generate(self, prompt, max_new_tokens):
            return "WidgetRenderer"

    result = QueryRewritingRetriever(
        LexicalRepoRetriever(top_k=1), _TermBackend()
    ).retrieve("something broke", repo)
    # The vague query alone would not surface widget.py; the rewritten term does.
    assert result.files[0] == "widget.py"


def test_factory_query_rewrite_needs_backend():
    retriever = create_repo_retriever("query_rewrite", backend=_SelectingBackend(["x"]))
    assert isinstance(retriever, QueryRewritingRetriever)


# --------------------------------------------------------------------------
# benchmark harness integration
# --------------------------------------------------------------------------

def test_run_retrieval_cases_uses_retriever_and_handles_missing_workdir(tmp_path):
    import json

    from prthinker.benchmark import BenchmarkCase, run_retrieval_cases

    repo = _make_repo(tmp_path, {
        "pkg/widgets.py": "class WidgetRenderer:\n    pass\n",
        "other.py": "def f():\n    return 1\n",
    })
    cases = [
        BenchmarkCase(case_id="c1", prompt="WidgetRenderer is broken"),
        BenchmarkCase(case_id="c2", prompt="no work-tree for this one"),
    ]

    def resolve(case):
        return repo if case.case_id == "c1" else None

    outcomes = run_retrieval_cases(create_repo_retriever("lexical"), cases, resolve)
    assert [o.case_id for o in outcomes] == ["c1", "c2"]
    assert "pkg/widgets.py" in json.loads(outcomes[0].raw_output)["retrieved"]
    # An unresolved work-tree yields an empty retrieval, not a crash.
    assert json.loads(outcomes[1].raw_output)["retrieved"] == []

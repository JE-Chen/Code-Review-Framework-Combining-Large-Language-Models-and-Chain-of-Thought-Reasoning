"""Tests for the LLM retrieval stages + factory (prthinker.repo_retrieval_factory)."""

from __future__ import annotations

from prthinker.repo_retrieval import LexicalRepoRetriever
from prthinker.repo_retrieval_factory import (
    BlockRerankingRetriever,
    IterativeRetriever,
    _context_from_blocks,
    _parse_block_selection,
    _parse_iter_response,
    create_repo_retriever,
)
from tests.test_repo_retrieval import _make_repo, json_dumps


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

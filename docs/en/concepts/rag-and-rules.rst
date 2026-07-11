RAG and rule packs
==================

The reviewer's prompts have a dedicated *rules* slot that combines two
sources: a globally-retrieved set of best-practice rules (RAG) and any
team-specific rules the repo wants always-on.

Global RAG
----------

``codes/util/faiss_util.py`` builds an ``IndexFlatIP`` over ``rule_docs``
from ``datas/RAG_data/rag_data.py``, using L2-normalised embeddings from
``Qwen/Qwen3-Embedding-4B``. The index is built once at module import
time — querying is cheap.

The retriever interface is in ``prthinker.rag.RAGRetriever``. Three
implementations are provided:

* ``FaissRAGRetriever`` — wraps the FAISS index in-process. Needs the
  embedding model loaded (≈ 8 GB VRAM). Used on the inference server.
* ``RemoteRAGRetriever`` — POSTs to the server's ``/rag`` endpoint.
  Lets a thin runner do RAG without bundling the embedding model. Used
  by the GitHub Action.
* ``NoOpRetriever`` — returns ``[]``. Useful when you want pure-LLM
  baseline behaviour for ablations.

Threshold
~~~~~~~~~

``--rag-threshold`` (default ``0.7``) drops any retrieved doc whose
cosine similarity to the query is below the floor. Tuning this is the
single most impactful knob — too low and the prompt fills with
unrelated rules; too high and you starve the model of context.

Per-repo rule packs
-------------------

The ``--rules-dir`` flag (env ``PRTHINKER_RULES_DIR``) reads every ``*.md``
file under the given directory (recursively, sorted) and appends each
file's content as a rule **after** RAG-retrieved rules in the prompt.

Two important differences from RAG rules:

* **Always on** — no threshold filtering. The team has opted in by
  checking the file into the repo, so it always applies.
* **One file = one rule** — keeps inputs auditable in git diff.

Example layout::

   ./team-rules/
   ├── 010-imports.md
   ├── 020-error-handling.md
   ├── 030-logging.md
   └── 040-database.md

Each file should be a short, scannable rule:

.. code-block:: markdown

   # Database queries

   - Always use parameterised queries; never f-string SQL.
   - Wrap multi-statement transactions in `with conn:` blocks.
   - Reject queries that touch the `users` table without an explicit
     `WHERE user_id = ?` predicate.

How rules get into the prompt
-----------------------------

The single source of truth for the rules slot is
``codes/run/CoT_Prompts/global_rule.py``. The pipeline calls
``build_global_rule_template(prompt=..., rag_rules=merged_list)`` and
``merged_list`` is the concatenation of *retrieved RAG rules* + *rules
from --rules-dir*.

Both kinds of rule are rendered into the prompt's
*"8. RAG Rules (Retrieval-Augmented Guidance)"* section.

Wire diagram
------------

::

           --rules-dir
                │
                ▼
        load_rules_dir(path)
                │
                │  list[str]
                ▼
           extra_rules ──┐
                         │
   retriever.retrieve()  │
        │                ▼
        │       CoTPipeline._merge_rules()
        │                │
        ▼                ▼
   rag_docs ─── rag_docs (merged) ──▶ build_global_rule_template(...)
                                            │
                                            ▼
                                       backend.generate()

Adding a new retriever
----------------------

Subclass ``RAGRetriever``:

.. code-block:: python

   from prthinker.rag import RAGRetriever

   class HybridRetriever(RAGRetriever):
       """Returns BM25 results plus FAISS results, deduplicated."""

       def __init__(self, bm25, faiss):
           self._bm25 = bm25
           self._faiss = faiss

       def retrieve(self, prompt: str) -> list[str]:
           seen: set[str] = set()
           out: list[str] = []
           for doc in self._bm25.search(prompt) + self._faiss.search(prompt):
               if doc not in seen:
                   seen.add(doc)
                   out.append(doc)
           return out

The pipeline's only contract is the one ``retrieve(str) -> list[str]``
method — no global side effects, no setup ordering required.

Repository-context retrieval strategies
---------------------------------------

Separate from the rules slot, per-file review prompts can be prefixed
with cross-file *repository context* retrieved from a local work-tree
(``--repo-context-workdir``). ``--repo-context-strategy`` (env
``PRTHINKER_REPO_CONTEXT_STRATEGY``, default ``none``) selects the
strategy; every strategy is built through the ``create_repo_retriever``
factory:

* ``lexical`` — BM25 over the work-tree's code files with issue-aware
  query expansion. Model-free.
* ``semantic`` — ranks files by embedding similarity to the query, via
  an injected sentence-transformers embedder.
* ``structural`` — two lexical rounds: the symbols defined and modules
  imported by the round-one hits are fed back into the query, so the
  repository's own structure sharpens the second round. Model-free.
* ``graph`` — widens lexical recall with import-graph neighbours of the
  top hits (the files they import, and the files that import them).
  Model-free and deterministic.
* ``rerank`` — retrieves lexical candidates, then the review backend
  reads their snippets and returns the relevant subset, ranked.
* ``block_rerank`` — on top of a file-level rerank, the backend selects
  the relevant ``def`` / ``class`` blocks from per-file candidates,
  keeping line and symbol precision high.
* ``iterative`` — agentic multi-round retrieval: each round the backend
  selects relevant blocks from the candidate pool *and* proposes the
  next search query; selections accumulate until it signals it has
  enough or the round budget runs out.
* ``query_rewrite`` — one cheap backend call distils a verbose issue
  into focused search terms, appended to the query before delegating to
  the lexical base.
* ``hypothesis`` — model-in-the-loop propose-verify localization: each
  round the model proposes suspect (path, symbol, line) hypotheses
  which are statically verified (path/symbol existence, AST line
  spans, import-graph callers); refuted hypotheses feed back as
  corrections and confirmed locations rank first.
  ``--repo-context-rounds`` bounds the loop.
* ``execution`` — execution-grounded re-ranking: stack-trace frames
  mined from the change/issue text are fused (reciprocal-rank fusion)
  with spectrum-based fault localization (Ochiai/Tarantula over
  per-test coverage, collected via subprocess when failing tests are
  supplied programmatically) and the lexical base ranking; with no
  signals it degrades to the base retriever.

The work-tree is read and indexed once per retriever instance (memoized
per work-tree), not once per query — multi-round strategies re-query
the built index instead of re-reading the repository.

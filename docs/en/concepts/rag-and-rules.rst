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

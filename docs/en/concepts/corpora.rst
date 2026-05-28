Learned corpora: dismissed and accepted
=======================================

The reviewer keeps two JSONL stores that capture how PR authors react to
its findings over time. Both are populated by ``harvest-*`` CLI commands
and consumed by the inference server at startup.

Asymmetric roles
----------------

.. list-table::
   :header-rows: 1
   :widths: 25 35 40

   * - Store
     - Used to
     - Source signal
   * - ``dismissed.jsonl``
     - *filter* candidate findings (drop if too similar)
     - 👎 reactions, "false positive" replies, ignored comments
   * - ``accepted.jsonl``
     - *augment* the prompt with top-K exemplars
     - PRs containing ``Apply suggestion`` commits

The asymmetry is intentional. Dismissals are negative training signal
(*do not produce something like this again*) and are applied as a
similarity-based output filter. Accepted suggestions are positive
training signal (*more of this kind of advice has worked here*) and are
applied as in-context exemplars at prompt-build time.

Store shapes
------------

``dismissed.jsonl`` — one JSON object per line:

.. code-block:: json

   {
     "path": "src/auth.py",
     "comment": "Don't store tokens in plaintext",
     "reason": "thumbs-down reaction",
     "diff_snippet": "@@ -3,1 +3,3 @@\n+token = req.json()['token']"
   }

``accepted.jsonl`` — one JSON object per line:

.. code-block:: json

   {
     "path": "src/auth.py",
     "comment": "Use Path.resolve to canonicalise the path",
     "suggestion": "    path = Path(path).resolve()",
     "pr_number": 137
   }

Both are append-only — the harvest commands never overwrite existing
lines, so re-running with ``--max-prs 200`` after ``--max-prs 100`` does
the right thing. Lines that fail to parse are skipped with a warning.

Harvesting
----------

.. code-block:: bash

   # Pulls 👎 reactions and dismissal-keyword replies
   prthinker harvest-dismissed \
       --repo owner/name \
       --max-prs 100 \
       --out .prthinker/dismissed.jsonl

   # Scans PRs containing "Apply suggestion" commits, keeps any
   # review comment that includes a ```suggestion``` block on those PRs
   prthinker harvest-accepted \
       --repo owner/name \
       --max-prs 100 \
       --out .prthinker/accepted.jsonl

The dismissal keyword list is hard-coded for now (mix of English and
Chinese): *false positive, wontfix, not relevant, ignore this,
intentional, by design*, plus their Traditional Chinese equivalents.

The accepted harvest is best-effort: GitHub does not link an "Apply
suggestion" commit back to the specific review comment that produced it,
so the harvester assumes that on any PR with such a commit, every
``suggestion``-bearing review comment was accepted. False positives wash
out at K=3.

Similarity filter (dismissed)
-----------------------------

On the server, ``DismissedFilter`` embeds each stored ``comment`` once
at boot using the same ``codes/util/faiss_util.get_embedding`` that
backs RAG. For each candidate finding the filter embeds the finding's
``comment`` text and compares it to every stored example with cosine
similarity. The finding is dropped when:

.. math::

   \max_{e \in \text{store}} \langle \mathrm{emb}(f.\text{comment}),
   \mathrm{emb}(e.\text{comment}) \rangle \geq \tau

Default ``τ = 0.85``. Override via ``PRTHINKER_DISMISSED_THRESHOLD``.

Top-K exemplars (accepted)
--------------------------

``AcceptedExamplesRetriever`` works the same way but returns the K best
matches above its own (lower) threshold instead of filtering. The
selected examples are rendered into the ``inline_findings`` prompt as a
``## Examples of past advice that was accepted in this repo`` block,
positioned before the diff itself.

Defaults: ``K = 3``, ``τ = 0.6``. Override via ``PRTHINKER_ACCEPTED_TOP_K``,
``PRTHINKER_ACCEPTED_THRESHOLD``.

Cold-start
----------

Both filters are no-ops when their store is empty or missing — startup
logs ``filter disabled`` / ``exemplars disabled``. You can run the
reviewer with neither store for as long as you like; the corpora are a
quality booster, not a dependency.

Research use
------------

These two files are a labelled negative + positive corpus, accumulated
organically from production review traffic. They let you measure:

* dismissal rate per category over time
* drop-rate of the similarity filter (precision/recall against held-out
  human-labelled examples)
* whether exemplar injection shifts the distribution of generated
  suggestions

See ``paper/`` for the reference numbers used in the original
manuscript.

Configuration
=============

Every CLI flag has an equivalent environment variable. CLI arguments win
over env vars, env vars win over package defaults. Configuration is
validated at startup — invalid combinations raise immediately, no silent
fallbacks.

Backend selection
-----------------

.. list-table::
   :header-rows: 1
   :widths: 35 30 35

   * - CLI flag
     - Env var
     - Default
   * - ``--backend {local,remote,openai,anthropic}``
     - ``PRTHINKER_BACKEND``
     - ``remote``
   * - ``--remote-url URL``
     - ``PRTHINKER_REMOTE_URL``
     - *(required for remote)*
   * - ``--remote-api-key TOKEN``
     - ``PRTHINKER_REMOTE_API_KEY``
     - *(unset)*
   * - ``--remote-timeout SECONDS``
     - ``PRTHINKER_REMOTE_TIMEOUT``
     - ``600``
   * - ``--use-remote-pipeline``
     - ``PRTHINKER_USE_REMOTE_PIPELINE``
     - ``false``
   * - ``--model-name NAME``
     - ``PRTHINKER_MODEL_NAME``
     - ``Qwen/Qwen3-Coder-30B-A3B-Instruct``
   * - ``--lora-path PATH``
     - ``PRTHINKER_LORA_PATH``
     - *(unset)*

``--use-remote-pipeline`` calls the ``/review`` endpoint once per file
instead of looping ``/ask`` per step on the runner. This is faster and
keeps prompt orchestration in one place (the server), but ties the
runner to a server that implements ``/review``.

OpenAI-compatible providers (``--backend openai``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This one backend talks to any service that implements the OpenAI
``POST /chat/completions`` shape — OpenAI itself, Azure OpenAI, vLLM,
Ollama (``/v1``), LM Studio, llama.cpp server, Together AI, Groq,
DeepInfra, OpenRouter, …

.. list-table::
   :header-rows: 1
   :widths: 35 30 35

   * - CLI flag
     - Env var
     - Default
   * - ``--openai-model NAME``
     - ``PRTHINKER_OPENAI_MODEL``
     - ``gpt-4o-mini``
   * - ``--openai-api-key TOKEN``
     - ``PRTHINKER_OPENAI_API_KEY`` / ``OPENAI_API_KEY``
     - *(required)*
   * - ``--openai-base-url URL``
     - ``PRTHINKER_OPENAI_BASE_URL``
     - ``https://api.openai.com/v1``
   * - ``--openai-organization ID``
     - ``PRTHINKER_OPENAI_ORGANIZATION`` / ``OPENAI_ORG_ID``
     - *(unset)*

Anthropic Claude (``--backend anthropic``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 35 30 35

   * - CLI flag
     - Env var
     - Default
   * - ``--anthropic-model NAME``
     - ``PRTHINKER_ANTHROPIC_MODEL``
     - ``claude-opus-4-7``
   * - ``--anthropic-api-key TOKEN``
     - ``PRTHINKER_ANTHROPIC_API_KEY`` / ``ANTHROPIC_API_KEY``
     - *(required)*
   * - ``--anthropic-base-url URL``
     - ``PRTHINKER_ANTHROPIC_BASE_URL``
     - ``https://api.anthropic.com``
   * - ``--anthropic-version VER``
     - ``PRTHINKER_ANTHROPIC_VERSION``
     - ``2023-06-01``

RAG and rules
-------------

.. list-table::
   :header-rows: 1
   :widths: 35 30 35

   * - CLI flag
     - Env var
     - Default
   * - ``--no-rag``
     - ``PRTHINKER_RAG_ENABLED=false``
     - RAG on
   * - ``--remote-rag``
     - ``PRTHINKER_REMOTE_RAG``
     - ``false``
   * - ``--rag-threshold FLOAT``
     - ``PRTHINKER_RAG_THRESHOLD``
     - ``0.7``
   * - ``--rules-dir PATH``
     - ``PRTHINKER_RULES_DIR``
     - *(unset)*

``--remote-rag`` makes the runner call the server's ``/rag`` endpoint
instead of loading the 4B embedding model in-process — required for the
default GitHub-hosted CI runner.

``--rules-dir`` ingests every ``*.md`` file under the given directory as
an always-on team rule, appended after RAG-retrieved rules in the prompt.

Per-file mode and inline review
-------------------------------

.. list-table::
   :header-rows: 1
   :widths: 35 35 30

   * - CLI flag
     - Env var
     - Default
   * - ``--per-file``
     - ``PRTHINKER_PER_FILE``
     - ``false``
   * - ``--inline-review``
     - ``PRTHINKER_INLINE_REVIEW``
     - ``false``
   * - ``--max-findings-per-file N``
     - ``PRTHINKER_MAX_FINDINGS_PER_FILE``
     - ``10``
   * - ``--exclude-globs PATTERNS``
     - ``PRTHINKER_EXCLUDE_GLOBS``
     - *(unset)*
   * - ``--target-file PATH``
     - ``PRTHINKER_TARGET_FILE``
     - *(unset)*

Inline review requires per-file mode (the inline-findings step needs to
know which file it's looking at). Enabling ``--inline-review`` without
``--per-file`` is harmless but a no-op.

``--exclude-globs`` takes a comma-separated list of fnmatch patterns
(for example ``.idea/*,datas/*,*.md,*.lock``). Paths in the parsed
diff that match any pattern are dropped before the per-file loop —
useful for IDE state, generated data files, and large documentation
edits that would otherwise spend GPU minutes for no value.

``--target-file`` restricts the per-file loop to a single exact path.
Combined with ``--output-json`` it lets a CI matrix shard own one
file's review (see :doc:`github-actions` for the matrix workflow).

Matrix sharding and aggregation
-------------------------------

For workflows that split per-file review across runners (CI matrix or
external job queue), each shard runs ``review-pr`` in *partial* mode
and a final aggregator merges every shard's findings into one
PR-level review.

.. list-table::
   :header-rows: 1
   :widths: 35 35 30

   * - CLI flag
     - Env var
     - Default
   * - ``--output-json PATH``
     - ``PRTHINKER_OUTPUT_JSON``
     - *(unset)*
   * - ``--aggregate-from DIR``
     - ``PRTHINKER_AGGREGATE_FROM``
     - *(unset)*

``--output-json`` flips ``review-pr`` from "post to GitHub" to
"serialise the partial ``ReviewResult`` to disk". The shard runs the
pipeline normally but does **not** upsert the summary comment, submit
the inline review, or open the gate; those are deferred to the
``aggregate`` subcommand, which reads every JSON under
``--aggregate-from`` and emits one combined post.

Pre-merge gate
--------------

.. list-table::
   :header-rows: 1
   :widths: 40 30 30

   * - CLI flag
     - Env var
     - Default
   * - ``--gate-on {none,warning,error}``
     - ``PRTHINKER_GATE_ON``
     - ``none``

See :doc:`../concepts/ci-and-gate`. Set to ``none`` for advisory mode,
``error`` to fail the Check Run when any error-severity finding exists.

CI signals
----------

.. list-table::
   :header-rows: 1
   :widths: 35 35 30

   * - CLI flag
     - Env var
     - Default
   * - ``--include-ci-signals``
     - ``PRTHINKER_INCLUDE_CI_SIGNALS``
     - ``false``
   * - ``--ci-signal-max-jobs N``
     - ``PRTHINKER_CI_SIGNAL_MAX_JOBS``
     - ``5``
   * - ``--ci-signal-tail-chars N``
     - ``PRTHINKER_CI_SIGNAL_TAIL_CHARS``
     - ``4000``

Server-side
-----------

These are read by ``codes/run/fastapi_server.py`` at startup, **not** by
the runner CLI.

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Env var
     - Effect
   * - ``PRTHINKER_DISMISSED_PATH``
     - Path to ``dismissed.jsonl``. Empty / missing → filter off.
   * - ``PRTHINKER_DISMISSED_THRESHOLD``
     - Cosine similarity floor for dropping repeats. Default ``0.85``.
   * - ``PRTHINKER_ACCEPTED_PATH``
     - Path to ``accepted.jsonl``. Empty / missing → no exemplars.
   * - ``PRTHINKER_ACCEPTED_THRESHOLD``
     - Cosine floor for inclusion in top-K. Default ``0.6``.
   * - ``PRTHINKER_ACCEPTED_TOP_K``
     - Number of exemplars to inject. Default ``3``.

Output and logging
------------------

.. list-table::
   :header-rows: 1
   :widths: 35 30 35

   * - CLI flag
     - Env var
     - Default
   * - ``--log-level LEVEL``
     - ``PRTHINKER_LOG_LEVEL``
     - ``INFO``
   * - ``--steps a,b,c``
     - *(none)*
     - *(all registered)*
   * - ``--max-new-tokens N``
     - ``PRTHINKER_MAX_NEW_TOKENS``
     - ``32768``
   * - ``--output-dir PATH``
     - *(review-file only)*
     - *(none)*

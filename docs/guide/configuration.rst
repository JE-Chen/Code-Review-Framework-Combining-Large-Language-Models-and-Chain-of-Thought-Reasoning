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
     - ``REVIEWMIND_BACKEND``
     - ``remote``
   * - ``--remote-url URL``
     - ``REVIEWMIND_REMOTE_URL``
     - *(required for remote)*
   * - ``--remote-api-key TOKEN``
     - ``REVIEWMIND_REMOTE_API_KEY``
     - *(unset)*
   * - ``--remote-timeout SECONDS``
     - ``REVIEWMIND_REMOTE_TIMEOUT``
     - ``600``
   * - ``--use-remote-pipeline``
     - ``REVIEWMIND_USE_REMOTE_PIPELINE``
     - ``false``
   * - ``--model-name NAME``
     - ``REVIEWMIND_MODEL_NAME``
     - ``Qwen/Qwen3-Coder-30B-A3B-Instruct``
   * - ``--lora-path PATH``
     - ``REVIEWMIND_LORA_PATH``
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
     - ``REVIEWMIND_OPENAI_MODEL``
     - ``gpt-4o-mini``
   * - ``--openai-api-key TOKEN``
     - ``REVIEWMIND_OPENAI_API_KEY`` / ``OPENAI_API_KEY``
     - *(required)*
   * - ``--openai-base-url URL``
     - ``REVIEWMIND_OPENAI_BASE_URL``
     - ``https://api.openai.com/v1``
   * - ``--openai-organization ID``
     - ``REVIEWMIND_OPENAI_ORGANIZATION`` / ``OPENAI_ORG_ID``
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
     - ``REVIEWMIND_ANTHROPIC_MODEL``
     - ``claude-opus-4-7``
   * - ``--anthropic-api-key TOKEN``
     - ``REVIEWMIND_ANTHROPIC_API_KEY`` / ``ANTHROPIC_API_KEY``
     - *(required)*
   * - ``--anthropic-base-url URL``
     - ``REVIEWMIND_ANTHROPIC_BASE_URL``
     - ``https://api.anthropic.com``
   * - ``--anthropic-version VER``
     - ``REVIEWMIND_ANTHROPIC_VERSION``
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
     - ``REVIEWMIND_RAG_ENABLED=false``
     - RAG on
   * - ``--remote-rag``
     - ``REVIEWMIND_REMOTE_RAG``
     - ``false``
   * - ``--rag-threshold FLOAT``
     - ``REVIEWMIND_RAG_THRESHOLD``
     - ``0.7``
   * - ``--rules-dir PATH``
     - ``REVIEWMIND_RULES_DIR``
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
     - ``REVIEWMIND_PER_FILE``
     - ``false``
   * - ``--inline-review``
     - ``REVIEWMIND_INLINE_REVIEW``
     - ``false``
   * - ``--max-findings-per-file N``
     - ``REVIEWMIND_MAX_FINDINGS_PER_FILE``
     - ``10``

Inline review requires per-file mode (the inline-findings step needs to
know which file it's looking at). Enabling ``--inline-review`` without
``--per-file`` is harmless but a no-op.

Pre-merge gate
--------------

.. list-table::
   :header-rows: 1
   :widths: 40 30 30

   * - CLI flag
     - Env var
     - Default
   * - ``--gate-on {none,warning,error}``
     - ``REVIEWMIND_GATE_ON``
     - ``none``

See :doc:`/concepts/ci-and-gate`. Set to ``none`` for advisory mode,
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
     - ``REVIEWMIND_INCLUDE_CI_SIGNALS``
     - ``false``
   * - ``--ci-signal-max-jobs N``
     - ``REVIEWMIND_CI_SIGNAL_MAX_JOBS``
     - ``5``
   * - ``--ci-signal-tail-chars N``
     - ``REVIEWMIND_CI_SIGNAL_TAIL_CHARS``
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
   * - ``REVIEWMIND_DISMISSED_PATH``
     - Path to ``dismissed.jsonl``. Empty / missing → filter off.
   * - ``REVIEWMIND_DISMISSED_THRESHOLD``
     - Cosine similarity floor for dropping repeats. Default ``0.85``.
   * - ``REVIEWMIND_ACCEPTED_PATH``
     - Path to ``accepted.jsonl``. Empty / missing → no exemplars.
   * - ``REVIEWMIND_ACCEPTED_THRESHOLD``
     - Cosine floor for inclusion in top-K. Default ``0.6``.
   * - ``REVIEWMIND_ACCEPTED_TOP_K``
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
     - ``REVIEWMIND_LOG_LEVEL``
     - ``INFO``
   * - ``--steps a,b,c``
     - *(none)*
     - *(all registered)*
   * - ``--max-new-tokens N``
     - ``REVIEWMIND_MAX_NEW_TOKENS``
     - ``32768``
   * - ``--output-dir PATH``
     - *(review-file only)*
     - *(none)*

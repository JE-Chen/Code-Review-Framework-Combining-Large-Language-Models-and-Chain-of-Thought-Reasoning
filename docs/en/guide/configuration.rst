Configuration
=============

Every CLI flag has an equivalent environment variable. CLI arguments win
over env vars, env vars win over package defaults. Configuration is
validated at startup — invalid combinations raise immediately, no silent
fallbacks.

A few variables also accept a legacy ``REVIEWMIND_*`` spelling (for
example ``REVIEWMIND_VERIFY_SUGGESTIONS``). When both spellings are
set, the ``PRTHINKER_*`` variable takes precedence; the legacy one is
read only as a fallback.

Backend selection
-----------------

.. list-table::
   :header-rows: 1
   :widths: 35 30 35

   * - CLI flag
     - Env var
     - Default
   * - ``--backend {local,remote,openai,anthropic,gemini,cohere,mistral,claude-cli,codex-cli}``
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

Local agent CLI (``--backend claude-cli``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Runs the locally installed ``claude`` CLI in non-interactive print mode
(``claude -p``), one subprocess per generation. The prompt travels over
stdin — a review prompt embeds whole diffs, which would overflow the
Windows command-line length cap as an argument — and the response is
requested as ``--output-format json`` so the result text and token
usage parse deterministically (plain-text output falls back verbatim).

Unlike the HTTP backends, the CLI can be granted a tool set with
``--claude-cli-allowed-tools`` (forwarded as ``--allowedTools``),
letting the review consult the working tree — read files, grep, follow
imports — with the full local toolchain instead of seeing only the
prompt text. ``--claude-cli-workdir`` scopes which tree those tools
operate on.

.. list-table::
   :header-rows: 1
   :widths: 38 34 28

   * - CLI flag
     - Env var
     - Default
   * - ``--claude-cli-path PATH``
     - ``PRTHINKER_CLAUDE_CLI_PATH``
     - ``claude``
   * - ``--claude-cli-model NAME``
     - ``PRTHINKER_CLAUDE_CLI_MODEL``
     - *(CLI's own default)*
   * - ``--claude-cli-workdir PATH``
     - ``PRTHINKER_CLAUDE_CLI_WORKDIR``
     - ``.``
   * - ``--claude-cli-allowed-tools LIST``
     - ``PRTHINKER_CLAUDE_CLI_ALLOWED_TOOLS``
     - *(unset — CLI's own tool policy)*
   * - ``--claude-cli-timeout SECONDS``
     - ``PRTHINKER_CLAUDE_CLI_TIMEOUT``
     - ``3600``

Local agent CLI (``--backend codex-cli``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Runs the locally installed ``codex`` CLI headless (``codex exec --json
--skip-git-repo-check -C <workdir> -``), one subprocess per generation.
The prompt travels over stdin (the trailing ``-``); output is NDJSON and
the last ``agent_message`` event is the answer, with token usage taken
from ``turn.completed``.

The sandbox mode defaults to ``read-only``: the CLI may read the
working tree with its own toolchain but never mutate it.
``workspace-write`` and ``danger-full-access`` are available for
trusted setups.

.. list-table::
   :header-rows: 1
   :widths: 38 34 28

   * - CLI flag
     - Env var
     - Default
   * - ``--codex-cli-path PATH``
     - ``PRTHINKER_CODEX_CLI_PATH``
     - ``codex``
   * - ``--codex-cli-model NAME``
     - ``PRTHINKER_CODEX_CLI_MODEL``
     - *(CLI's own default)*
   * - ``--codex-cli-workdir PATH``
     - ``PRTHINKER_CODEX_CLI_WORKDIR``
     - ``.``
   * - ``--codex-cli-sandbox {read-only,workspace-write,danger-full-access}``
     - ``PRTHINKER_CODEX_CLI_SANDBOX``
     - ``read-only``
   * - ``--codex-cli-timeout SECONDS``
     - ``PRTHINKER_CODEX_CLI_TIMEOUT``
     - ``3600``

Multi-model arbitration
-----------------------

Off by default. With ``--arbitration``, every backend kind listed in
``--arbitration-backends`` re-judges the primary model's inline
findings: each arbiter receives the findings plus the diff and votes
``confirm`` / ``reject`` per finding, and the strategy combines the
votes — out-voted findings are dropped before anything is posted.

Each arbiter is configured by the same flags / env vars it would use as
the primary backend (an ``openai`` arbiter reads ``--openai-*``, a
``claude-cli`` arbiter reads ``--claude-cli-*``, and so on).

The layer fails open: an arbiter that errors or returns unparseable
output abstains, and a finding with no countable votes is kept.
Arbitration can only remove noise — it never loses findings to arbiter
flakiness.

.. list-table::
   :header-rows: 1
   :widths: 42 34 24

   * - CLI flag
     - Env var
     - Default
   * - ``--arbitration``
     - ``PRTHINKER_ARBITRATION``
     - ``false``
   * - ``--arbitration-backends a,b``
     - ``PRTHINKER_ARBITRATION_BACKENDS``
     - *(unset)*
   * - ``--arbitration-strategy {majority,unanimous,any}``
     - ``PRTHINKER_ARBITRATION_STRATEGY``
     - ``majority``
   * - ``--arbitration-max-new-tokens N``
     - ``PRTHINKER_ARBITRATION_MAX_NEW_TOKENS``
     - ``4096``

``majority`` drops a finding only when rejects outnumber confirms (a
tie keeps it), ``unanimous`` drops on any reject, ``any`` keeps on a
single confirm.

A multi-model review with the two local agent CLIs on the panel
(see ``examples/multi-model-review.sh`` for the full script):

.. code-block:: bash

   prthinker review-pr \
       --repo owner/name --pr-number 42 \
       --per-file --inline-review \
       --arbitration \
       --arbitration-backends claude-cli,codex-cli \
       --arbitration-strategy majority

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

Adaptive review depth
---------------------

.. list-table::
   :header-rows: 1
   :widths: 35 35 30

   * - CLI flag
     - Env var
     - Default
   * - ``--step-plan {full,adaptive}``
     - ``PRTHINKER_STEP_PLAN``
     - ``full``

``adaptive`` classifies every file into a depth tier before any model
call: **skip** (lockfiles, generated / vendored artifacts,
whitespace-only reformatting — zero model calls), **trivial**
(docs / config files or ≤ 5 changed lines — a batched findings-only
call covering up to 6 files or 24K characters of diff), **standard**
(one ``unified_review`` call returning findings + summary + verdict),
and **deep** (≥ 200 changed lines, or risk ≥ 0.7 with
``--risk-weighted`` — the full configured chain). Reduced tiers also
cap the generation budget — trivial 4096 tokens, standard 8192 —
while deep keeps the full ``--max-new-tokens`` budget.

Repository context retrieval
----------------------------

Cross-file repository context for local per-file review: a strategy
other than ``none`` retrieves related files from the work tree and
injects them into each file's prompt.

.. list-table::
   :header-rows: 1
   :widths: 40 35 25

   * - CLI flag
     - Env var
     - Default
   * - ``--repo-context-strategy {none,lexical,semantic,structural,graph,rerank,block_rerank,iterative,query_rewrite,hypothesis,execution}``
     - ``PRTHINKER_REPO_CONTEXT_STRATEGY``
     - ``none``
   * - ``--repo-context-workdir PATH``
     - ``PRTHINKER_REPO_CONTEXT_WORKDIR``
     - ``.``
   * - ``--repo-context-top-k N``
     - ``PRTHINKER_REPO_CONTEXT_TOP_K``
     - ``10``
   * - ``--repo-context-keep-ratio FLOAT``
     - ``PRTHINKER_REPO_CONTEXT_KEEP_RATIO``
     - ``0.0``
   * - ``--repo-context-block-candidates N``
     - ``PRTHINKER_REPO_CONTEXT_BLOCK_CANDIDATES``
     - ``6``
   * - ``--repo-context-votes N``
     - ``PRTHINKER_REPO_CONTEXT_VOTES``
     - ``1``
   * - ``--repo-context-rounds N``
     - ``PRTHINKER_REPO_CONTEXT_ROUNDS``
     - ``3``
   * - ``--repo-context-focus-lines N``
     - ``PRTHINKER_REPO_CONTEXT_FOCUS_LINES``
     - ``0``

``--repo-context-block-candidates``, ``--repo-context-votes``,
``--repo-context-rounds``, and ``--repo-context-focus-lines`` tune the
model-in-the-loop strategies (``block_rerank`` / ``iterative`` /
``hypothesis``); ``--repo-context-rounds`` bounds both the
``iterative`` and ``hypothesis`` loops,
``--repo-context-keep-ratio`` ``0`` keeps the fixed top-k tail, and
``--repo-context-focus-lines`` ``0`` disables the line-window focus.

Review presets
--------------

.. list-table::
   :header-rows: 1
   :widths: 45 35 20

   * - CLI flag
     - Env var
     - Default
   * - ``--review-preset {none,backend,frontend,security,release}``
     - ``PRTHINKER_REVIEW_PRESET``
     - ``none``

A preset expands into a bundle of review modes and safety-check flags
(merged with any explicit ``--review-modes`` list): ``backend`` →
modes ``security,performance,test-coverage`` plus
``--api-consistency`` / ``--dep-upgrade-check``; ``frontend`` → modes
``accessibility,performance,pii,test-coverage``; ``security`` → modes
``security,secret-scan,pii`` plus ``--redact-secrets`` and a
``--gate-on warning`` floor when the gate is still ``none``;
``release`` → modes ``security,test-coverage`` plus
``--api-consistency`` / ``--dep-upgrade-check`` / ``--diff-entropy``
/ ``--reproducibility-check`` / ``--judge``.

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
   * - ``--calibration-gate``
     - ``PRTHINKER_CALIBRATION_GATE``
     - ``false``

See :doc:`../concepts/ci-and-gate`. Set to ``none`` for advisory mode,
``error`` to fail the Check Run when any error-severity finding exists.

With ``--calibration-gate``, the merge gate honours calibrated
abstention: a finding whose confidence falls below the calibrated
threshold from the feedback store stays visible in the summary and
reports but stops blocking the gate, and the gate line appends
``calibration abstained N from blocking``. The sibling
``--calibration-store`` / ``--calibration-author`` /
``--calibration-category`` / ``--calibration-min-samples`` /
``--calibration-half-life-days`` flags configure the store and the
posterior; they have no env-var equivalents.

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

Signals are fetched through the platform adapter: failed GitHub Actions
job logs on GitHub, failed pipeline-job traces on GitLab. Platforms
without a CI API skip the prepend with a log line.

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
   * - ``PRTHINKER_MAX_JOBS``
     - Cap on each async job table (review and ask). Terminal jobs are
       evicted first; when every slot holds an active job the submit
       endpoints return ``503``. Default ``32``.
   * - ``PRTHINKER_MAX_INPUT_TOKENS``
     - Reject a request whose prompt exceeds this token budget at the
       boundary instead of hitting a CUDA OOM mid-review. Default
       ``16384``.
   * - ``PRTHINKER_MAX_NEW_TOKENS``
     - Server-side ceiling on requested generation length; the wire
       schemas clamp ``max_new_tokens`` to the same range. Default
       ``32768``.

Decoding determinism
~~~~~~~~~~~~~~~~~~~~~

The inference server decodes review generations **greedily by default**.
Greedy decoding is deterministic: the same diff yields the same findings
on every run, which makes reviews reproducible and audit-friendly and
lets an A/B comparison between two configurations be attributed to the
change rather than to sampling noise.

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Env var
     - Effect
   * - ``PRTHINKER_SAMPLING``
     - Set to ``1`` to opt back into the checkpoint's own sampling
       behaviour (its generation-config ``do_sample`` / temperature /
       top-p / top-k). Any other value — including unset — keeps greedy
       decoding. Default greedy.

This is a **server-side** setting read by the inference image, so it
takes effect when that image is (re)built or restarted — not from the
runner CLI.

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

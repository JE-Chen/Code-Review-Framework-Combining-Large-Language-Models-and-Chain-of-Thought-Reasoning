Secret redaction and MCP integration
====================================

Two unrelated additions that share a single concern: making prthinker
safe and convenient to drive from outside the original GHA workflow.

Secret redaction (``--redact-secrets``)
---------------------------------------

When the backend is a paid third-party API (OpenAI, Anthropic, …), the
PR diff payload may contain real secrets that slipped past
``.gitignore`` — an ``.env`` file shown in the diff, a hard-coded token
in a test fixture, a JWT in a snapshot test. With
``--redact-secrets`` (env ``PRTHINKER_REDACT_SECRETS=true``) the runner
runs every diff through a pre-pass that replaces well-known secret
patterns with ``<REDACTED:<kind>>`` before any backend call.

Patterns covered
~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - kind
     - matches
   * - ``private-key``
     - PEM ``-----BEGIN ... PRIVATE KEY-----`` blocks (whole block)
   * - ``github-token``
     - ``ghp_`` / ``gho_`` / ``ghu_`` / ``ghs_`` / ``ghr_`` PATs
   * - ``anthropic-key``
     - ``sk-ant-...``
   * - ``openai-key``
     - ``sk-...`` and ``sk-proj-...`` (excluding the Anthropic prefix)
   * - ``stripe-key``
     - ``sk_live_…`` / ``sk_test_…`` / ``rk_live_…`` / ``rk_test_…``
   * - ``aws-access-key-id``
     - ``AKIA`` / ``ASIA`` / ``AIDA`` / ``AROA`` / ``AGPA`` / ``ANPA`` / ``ANVA``
   * - ``slack-token``
     - ``xoxa-`` / ``xoxb-`` / ``xoxp-`` / ``xoxr-`` / ``xoxs-`` tokens
   * - ``gcp-api-key``
     - ``AIza…`` (39 chars)
   * - ``twilio-sid``
     - ``AC`` + 32 hex chars
   * - ``jwt``
     - three base64url segments joined with ``.`` (header starts ``eyJ``)

The detector is conservative on purpose — false positives in a code
review are noisy but recoverable; false negatives are not.

Design properties
~~~~~~~~~~~~~~~~~

* **Idempotent.** Feeding an already-redacted diff in again does
  nothing — the ``<REDACTED:...>`` placeholders are not themselves
  detected as secrets.
* **Cache-friendly.** Redaction runs before the prompt is built and
  before the cache key is computed, so two runs of the same PR hit the
  cache identically whether or not a secret was redacted.
* **Logged but never leaked.** The ``RedactionReport`` returned alongside
  the redacted text counts matches by kind — never the content. The
  warning line is safe to ship to CI logs.

When NOT to enable
~~~~~~~~~~~~~~~~~~

* If your backend is the local Hugging Face backend or your own
  self-hosted FastAPI server inside the same network boundary as the
  repo, redaction is mostly cosmetic — secrets aren't going anywhere
  new. Leave it off to keep the diff readable.
* For paid third-party backends, treat it as mandatory.

Model Context Protocol integration
----------------------------------

The Model Context Protocol (MCP) is an open standard for letting LLM
clients (Claude Desktop, Cursor, Continue, Cline, Zed, etc.) invoke
external tools. prthinker ships an MCP server adapter so any MCP
client can drive reviews from inside the IDE — no GHA round-trip
required.

Install
~~~~~~~

.. code-block:: bash

   pip install -e ".[mcp]"

This adds the ``mcp`` SDK on top of the runner extras.

Tools exposed
~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - tool name
     - what it does
   * - ``review_diff``
     - Run the CoT pipeline against a unified diff string. Returns a
       markdown body identical to what would land in the PR summary
       comment. ``redact_secrets`` defaults to ``True``.
   * - ``stats``
     - Aggregate the local telemetry SQLite over a time window and
       return a markdown table. Useful for "how much did this week of
       reviews cost us?" prompts.

Configuration
~~~~~~~~~~~~~

Backend selection uses the same ``PRTHINKER_*`` env vars as the CLI;
secrets stay in env vars, never in the MCP server's own config.

Example Claude Desktop entry (``~/Library/Application Support/Claude/
claude_desktop_config.json`` on macOS):

.. code-block:: json

   {
     "mcpServers": {
       "prthinker": {
         "command": "prthinker",
         "args": ["mcp"],
         "env": {
           "PRTHINKER_BACKEND": "anthropic",
           "ANTHROPIC_API_KEY": "sk-ant-...",
           "PRTHINKER_ANTHROPIC_MODEL": "claude-sonnet-4-6",
           "PRTHINKER_CACHE_ENABLED": "true",
           "PRTHINKER_TELEMETRY_ENABLED": "true"
         }
       }
     }
   }

Same shape works for Cursor, Continue, Cline, and Zed — see each
client's MCP docs for the file path.

Typical IDE flow
~~~~~~~~~~~~~~~~

1. Stage a change locally: ``git add -p``.
2. In the IDE chat: *"Run prthinker on my staged diff"*.
3. The client's LLM invokes ``review_diff`` with
   ``$(git diff --cached)``.
4. The markdown review streams back into the chat panel; the user
   accepts / discards suggestions inline.

This is the killer feature for solo developers who don't want to push
through a PR + GHA loop just to get review feedback.

Trade-offs
~~~~~~~~~~

* RAG is disabled in MCP mode (``NoOpRetriever``). Loading FAISS in a
  stdio subprocess is heavy and the embedding model rarely lives on the
  user's laptop; if you need RAG, point ``PRTHINKER_BACKEND=remote``
  and let the FastAPI server own retrieval.
* The MCP server is intentionally stateless across invocations; cache
  and telemetry stores persist between calls so cost visibility still
  works.

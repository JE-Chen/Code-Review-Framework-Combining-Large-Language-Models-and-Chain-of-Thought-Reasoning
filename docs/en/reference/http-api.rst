HTTP API
========

The FastAPI server in ``codes/run/fastapi_server.py`` exposes four
endpoints. All accept and return JSON (``/ask`` returns plain text for
backward compatibility).

All requests support an optional ``Authorization: Bearer <token>``
header. The server does not validate the token itself — wrap it behind a
reverse proxy (nginx, Cloudflare Access, etc.) if you need real auth.

GET /healthz
------------

Liveness probe.

**Response 200**

.. code-block:: json

   {"status": "ok", "model": "Qwen/Qwen3-Coder-30B-A3B-Instruct"}

POST /ask
---------

One-shot text generation. Kept for backwards compatibility — the higher-
level endpoints below are preferred.

**Request body** (``AskRequest``):

.. code-block:: json

   {
     "prompt": "...",
     "max_new_tokens": 32768
   }

**Response 200**: ``text/plain`` with the generated text.

POST /rag
---------

Retrieve RAG rules for a query.

**Request body** (``RagRequest``):

.. code-block:: json

   {
     "query": "the diff or any text",
     "threshold": 0.7,
     "k": 15
   }

**Response 200** (``RagResponse``):

.. code-block:: json

   {
     "docs": ["rule text 1", "rule text 2"]
   }

POST /review
------------

Run the full CoT pipeline server-side. This is the endpoint used by
``prthinker review-pr --use-remote-pipeline``.

**Request body** (``ReviewRequest``):

.. code-block:: json

   {
     "code_diff": "diff --git a/foo.py b/foo.py\n...",
     "file_path": "foo.py",
     "steps": null,
     "rag_enabled": true,
     "rag_threshold": 0.7,
     "max_new_tokens": 32768,
     "extra_rules": ["Always use Path.resolve", "..."]
   }

Field semantics:

* ``file_path`` — when set, the request is treated as a single-file diff
  and the server appends ``InlineFindingsStep`` to the run. The response
  will include parsed ``inline_findings``. When ``null``, the server
  runs the five-step pipeline over the entire diff blob and
  ``inline_findings`` is ``[]``.
* ``steps`` — optional explicit step list. ``null`` runs every registered
  step in declaration order.
* ``extra_rules`` — per-repo team rules appended after RAG-retrieved rules.

**Response 200** (``ReviewResponse``):

.. code-block:: json

   {
     "code_diff": "...",
     "rag_docs": ["...", "..."],
     "steps": [
       {"name": "first_summary", "output": "..."},
       {"name": "first_code_review", "output": "..."},
       {"name": "linter", "output": "..."},
       {"name": "code_smell", "output": "..."},
       {"name": "total_summary", "output": "..."},
       {"name": "inline_findings", "output": "[...]"}
     ],
     "inline_findings": [
       {
         "path": "foo.py",
         "line": 12,
         "severity": "warning",
         "comment": "Prefer logging over print.",
         "suggestion": "    logger.info('hello')",
         "original": "    print('hello')",
         "start_line": null
       }
     ]
   }

The dismissed filter (when configured server-side via
``PRTHINKER_DISMISSED_PATH``) runs before the response is returned, so
findings that match prior dismissals are already filtered out.

**Errors**

* ``400`` — empty ``code_diff``.
* ``422`` — payload fails Pydantic validation.
* ``500`` — generation or RAG failure. Logged server-side; clients
  should retry with backoff.

Schema definitions
------------------

The Pydantic models in :mod:`prthinker.schemas` are the single source
of truth for the wire format. Both the server (FastAPI's
``response_model``) and the runner (``model_validate_json``) reference
them, so type drift is impossible.

.. autoclass:: prthinker.schemas.AskRequest
   :noindex:

.. autoclass:: prthinker.schemas.RagRequest
   :noindex:

.. autoclass:: prthinker.schemas.RagResponse
   :noindex:

.. autoclass:: prthinker.schemas.ReviewRequest
   :noindex:

.. autoclass:: prthinker.schemas.ReviewResponse
   :noindex:

.. autoclass:: prthinker.schemas.InlineFinding
   :noindex:

.. autoclass:: prthinker.schemas.StepOutput
   :noindex:

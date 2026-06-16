HTTP API
========

The FastAPI server in ``codes/run/fastapi_server.py`` exposes a small
synchronous surface (``/healthz``, ``/ask``, ``/rag``, ``/review``) and
a job-pattern surface that mirrors it for long-running calls
(``/review/{submit,result,cancel}`` and ``/ask/{submit,result,cancel}``).

The job-pattern endpoints are the only ones safe to use behind a
reverse proxy with an HTTP idle timeout. Cloudflare's free / pro /
business plans cap a single request at 100 seconds; the 30B MoE
backend takes minutes per per-file review and tens of minutes for a
PR-wide overall-summary synthesis, so any synchronous call through
the proxy will be aborted before it returns. With the submit/poll
pattern, every individual HTTP round-trip returns in well under a
second, while the worker runs to completion server-side.

A single background sweeper thread walks both job tables every 30
seconds and sets the ``cancel_event`` on any running job whose
result endpoint has not been polled for 180 s. This protects the
GPU from continuing to chew on jobs whose client (a cancelled
GitHub Actions runner, a hung CI job, a lost network) is no longer
listening — see the cancel endpoints below.

All requests support an optional ``Authorization: Bearer <token>``
header. The server does not validate the token itself — wrap it behind a
reverse proxy (nginx, Cloudflare Access, etc.) if you need real auth.

GET /healthz
------------

Liveness probe.

**Response 200**

.. code-block:: json

   {"status": "ok", "model": "Qwen/Qwen3-Coder-30B-A3B-Instruct"}

GET /metrics
------------

Prometheus exposition endpoint. Enabled when
``prometheus-fastapi-instrumentator`` is installed (the server logs and
silently skips it otherwise), it exports per-endpoint request counts,
latency histograms (used for the p50 / p95 / p99 panels), and HTTP
status counters. Alongside those transport metrics the server emits
review-domain metrics on the same endpoint — ``prthinker_reviews_total``
(by ``mode`` and ``outcome``), ``prthinker_review_duration_seconds``,
``prthinker_review_findings``, and ``prthinker_reviews_in_progress`` — so
every completed review leaves a data point regardless of HTTP traffic.
Unauthenticated like every other route — the monitoring
overlay's nginx scrapes it on the internal docker network; do not expose
it publicly without a reverse-proxy ACL.

**Response 200**: ``text/plain`` in the Prometheus text exposition
format.

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
     "max_new_tokens": 8192,
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

POST /review/submit
-------------------

Asynchronous counterpart to ``/review``. Returns immediately with a
job id; the server runs the CoT pipeline in a daemon thread. Use this
endpoint whenever the connection between client and server passes
through a proxy with a short HTTP idle timeout — Cloudflare's free /
pro / business plans abort proxied requests at ~100 s, far below the
several-minute run time of a per-file CoT review on a 30B base.

**Request body** (``ReviewRequest``) — identical to ``/review``.

**Response 200** (``ReviewJobSubmitResponse``):

.. code-block:: json

   {"job_id": "fa3d996466ee4666baae72b842d3b149"}

The job is held in a process-local dict with a 1 h TTL; restarting the
server drops in-flight jobs.

GET /review/result/{job_id}
---------------------------

Poll for the result of a submitted job. The client should call this
on a short interval (e.g. 5 s) — each round trip is fast and cannot
trip the proxy's idle timeout. Overall wait time is bounded by the
client's own deadline.

**Response 200** (``ReviewJobStatusResponse``):

.. code-block:: json

   {
     "job_id": "fa3d996466ee4666baae72b842d3b149",
     "status": "running",
     "result": null,
     "error": null
   }

``status`` is one of:

* ``pending`` — submitted but the worker thread has not started yet.
* ``running`` — worker thread is in ``_execute_review``.
* ``done`` — ``result`` is populated with the same ``ReviewResponse``
  shape ``/review`` returns.
* ``error`` — ``error`` is populated with ``"<ExceptionClass>: <msg>"``.
  Clients should surface this directly; no retry will help unless
  the underlying cause (OOM, model load, etc.) is fixed.
* ``cancelled`` — the worker was interrupted by ``/review/cancel`` or
  by the idle sweeper. Terminal; the client should treat this as a
  failed run and stop polling.

Every successful poll refreshes the job's ``last_polled_at``
heartbeat, so a running client never trips the idle sweeper.

**Errors**

* ``404`` — unknown ``job_id`` (or it expired past the TTL).

POST /review/cancel/{job_id}
----------------------------

Mark a running review job for cancellation. Used by client code on
its way out (try/finally around the poll loop) and by the workflow's
own cancellation handlers, so an aborted CI run frees the GPU
instead of running to completion behind nobody's back.

**Response 200**:

.. code-block:: json

   {"job_id": "...", "cancelled": true, "status": "running"}

The endpoint sets the worker thread's ``cancel_event``; the pipeline
checks it between steps, and the local backend's
``StoppingCriteria`` polls it every decoded token so the running
``model.generate`` call returns within ~100 ms instead of finishing
the step. Terminal jobs (``done`` / ``error`` / ``cancelled``)
return ``{"cancelled": false, "status": "<current>"}`` unchanged.

**Errors**

* ``404`` — unknown ``job_id``.

POST /ask/submit
----------------

Job-pattern wrapper around ``/ask``. Pair with ``GET
/ask/result/{job_id}`` for any single-prompt generation that would
otherwise exceed the proxy timeout — for example the aggregator's
PR-wide overall-summary synthesis, which runs at the full
``max_new_tokens=16784`` budget.

**Request body** (``AskRequest``) — identical to ``/ask``.

**Response 200** (``AskJobSubmitResponse``):

.. code-block:: json

   {"job_id": "924c5daea164453f91f7a91feb57fb4c"}

GET /ask/result/{job_id}
------------------------

Poll for the result of a submitted ``/ask`` job. Status semantics
mirror ``GET /review/result/{job_id}``; ``result`` is the generated
text when ``status`` reaches ``done``.

**Response 200** (``AskJobStatusResponse``):

.. code-block:: json

   {
     "job_id": "924c5daea164453f91f7a91feb57fb4c",
     "status": "done",
     "result": "<generated text>",
     "error": null
   }

POST /ask/cancel/{job_id}
-------------------------

Mark a running ask job for cancellation. Same contract as
``/review/cancel`` — sets the worker's ``cancel_event`` so the local
backend's ``StoppingCriteria`` stops generation at the next token.

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

.. autoclass:: prthinker.schemas.ReviewJobSubmitResponse
   :noindex:

.. autoclass:: prthinker.schemas.ReviewJobStatusResponse
   :noindex:

.. autoclass:: prthinker.schemas.InlineFinding
   :noindex:

.. autoclass:: prthinker.schemas.StepOutput
   :noindex:

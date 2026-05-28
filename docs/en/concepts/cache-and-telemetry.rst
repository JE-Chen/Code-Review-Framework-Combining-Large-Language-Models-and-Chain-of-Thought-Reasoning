Cache and telemetry
===================

Two opt-in SQLite stores sit between the pipeline and whichever backend
you picked. They are independent — you can enable one without the other —
and stack as Decorators around the concrete backend at factory time.

The cache (``--cache``)
-----------------------

A read-through cache keyed by the SHA-256 of
``backend_kind | model | prompt | max_new_tokens``. Because the prompt
text itself is part of the key, **prompt-template edits, model swaps,
and token-cap changes all naturally invalidate the cache** — no manual
bust operation is required.

Defaults:

* Path: ``.prthinker/cache.sqlite``.
* TTL: 7 days (override with ``--cache-ttl-days``; ``0`` disables TTL).
* WAL mode is enabled so concurrent readers don't block.

The cache is process-local and uses ``sqlite3`` from the stdlib — no
external service.

When to enable
~~~~~~~~~~~~~~

Always-on for paid providers; expect 60–90% hit rate after the first
few PR runs because most files in a repo don't change between pushes.
For local backends it's still useful (saves GPU time on synchronize
pushes that don't touch a file), but the win is smaller because
generation is "free" once the GPU is bought.

Telemetry (``--telemetry``)
---------------------------

An append-only ``calls`` table that records one row per
``generate()`` invocation:

* ``timestamp`` (unix)
* ``backend`` / ``model``
* ``prompt_tokens`` + ``completion_tokens``  (from the provider's
  ``usage`` block when available; estimated from char counts otherwise —
  see ``tokens_estimated`` column)
* ``latency_ms``
* ``cost_usd`` (computed from :mod:`prthinker.pricing`; ``NULL`` for
  local and self-hosted-remote backends)
* ``cache_hit`` (1 if the upstream ``CachingBackend`` returned the
  cached response)
* ``error`` (set when the upstream call raised; ``NULL`` on success)

Pricing
~~~~~~~

:mod:`prthinker.pricing` holds a static ``(backend, model) → (input_rate,
output_rate)`` table in USD per million tokens. Models not in the table
return ``None`` cost — the row is recorded but ``cost_usd`` is left
``NULL`` so you can spot drift.

Update the table when providers move prices; that's the single source
of truth used by both the live recording and the ``stats`` subcommand.

The ``stats`` subcommand
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   prthinker stats                          # all-time
   prthinker stats --since-days 7           # last week
   prthinker stats --since-days 1           # last 24 h

Sample output::

   # prthinker stats — last 7 day(s)

   backend    model                               calls  hits   in-tok   out-tok       USD   p50 ms   p95 ms
   ----------------------------------------------------------------------------------------------------------
   anthropic  claude-opus-4-7                        12     2    14530      4220   $0.6500     2400     3120
   openai     gpt-4o-mini                            48    36    21044      6800   $0.0073      520     1180
   ----------------------------------------------------------------------------------------------------------
   Total: 60 call(s), 38 cache hits (63.3%), $0.6573

   Cache: 312 entries stored, 119 lifetime hits at .prthinker/cache.sqlite

Why this matters
~~~~~~~~~~~~~~~~

Once paid APIs are wired up, "is Claude Opus actually worth 25× more
than gpt-4o-mini for our reviews?" becomes a real question. The
telemetry rows let you answer it without instrumenting prompts by hand,
and the cache row tells you whether tuning the workflow trigger to
``synchronize`` instead of ``push`` would meaningfully cut your bill.

Wrapping order
--------------

The factory in :func:`prthinker.backends.create_backend` stacks
wrappers in this order::

   InstrumentedBackend(CachingBackend(real_backend))

So the telemetry layer sees cache hits with the correct
``cache_hit=true`` flag while still recording the (free) latency of a
cache lookup.

Disabling
---------

Both wrappers are gated on flags + env vars and default to **off**:

* ``--cache`` / ``PRTHINKER_CACHE_ENABLED``
* ``--telemetry`` / ``PRTHINKER_TELEMETRY_ENABLED``

When disabled the factory returns the concrete backend directly; no
disk activity, no schema migration risk.

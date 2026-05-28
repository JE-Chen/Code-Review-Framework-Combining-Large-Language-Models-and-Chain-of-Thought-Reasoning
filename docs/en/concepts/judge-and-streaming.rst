Judge step and streaming
========================

Two opt-in pipeline behaviours that build on the per-file mode.

Judge step (``--judge``)
------------------------

When enabled, every per-file pipeline run gets one more step appended:
``JudgeStep`` reads the file's ``total_summary`` plus the parsed
``inline_findings`` and emits a JSON object:

.. code-block:: text

   {
     "verdict": "approve" | "request_changes" | "comment",
     "score":   0-10,
     "reasons": ["short bullet", ...]
   }

The parser is intentionally lenient — same posture as the inline
findings parser — and falls back to a safe ``comment`` default rather
than crashing the review when the model strays from the format.

Aggregation across files
~~~~~~~~~~~~~~~~~~~~~~~~

Per-file verdicts collapse into a single PR-level decision with this
conservative rule:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Per-file mix
     - PR-level verdict
   * - Any file ``request_changes``
     - ``request_changes``
   * - All files ``approve``
     - ``approve``
   * - Otherwise
     - ``comment``

That decision then maps directly to the GitHub Review API's ``event``
field on the inline review submission:

* ``approve`` → ``APPROVE``
* ``request_changes`` → ``REQUEST_CHANGES``
* ``comment`` → ``COMMENT`` (the default)

So with ``--inline-review --judge --gate-on error`` together you get a
PR-level review that:

1. Posts every inline finding (with one-click suggestion blocks).
2. Sets the review event to *approve* / *request changes* / *comment*
   based on the judge.
3. Drives the Check Run gate independently from the same findings set.

The gate and the judge are intentionally separate signals — the gate is
mechanical (count error-severity findings), the judge is interpretive.
Both can fire on the same PR.

Paper-aligned ablation
~~~~~~~~~~~~~~~~~~~~~~

Because backend selection is per-process, you can let the judge step
run on a *different* backend from the rest of the review (e.g. local
Qwen for the five CoT steps, Anthropic Claude for the judge). The
schema is in :class:`prthinker.schemas.JudgeVerdict`; the parser and
aggregator are in :mod:`prthinker.judge`.

Streaming (``--stream``)
------------------------

Long reviews (5+ steps × per-file × per-PR) take several minutes; with
streaming off the CLI shows nothing until the whole review is done.
``--stream`` flips every backend call to its incremental path:

* **OpenAI-compat backend** — sets ``stream: true`` on the request and
  parses SSE ``data:`` events, yielding ``choices[0].delta.content``
  chunks. ``last_usage`` is captured from the final event's
  ``stream_options: include_usage`` block.
* **Anthropic backend** — sets ``stream: true``, yields the text inside
  ``content_block_delta`` events, captures ``input_tokens`` from
  ``message_start`` and ``output_tokens`` from ``message_delta``.
* **Local and self-hosted-remote backends** — fall back to the base
  class default, which yields the full ``generate()`` result as a single
  chunk. No streaming benefit, but the caller code does not need to
  branch.

Chunks are written to ``stderr`` so they don't pollute the consolidated
PR comment that goes to ``stdout``. Per-step headers ``[step_name ::
file_path]`` mark transitions. ``CachingBackend`` short-circuits a hit
to one chunk, ``InstrumentedBackend`` records latency / tokens at
stream-close time, so caching and telemetry behave identically whether
streaming is on or off.

Trade-offs
~~~~~~~~~~

* Streaming costs an extra round-trip handshake on each backend call but
  gains visible progress.
* On a slow link, perceived latency drops from "wait three minutes" to
  "first token in two seconds".
* Some OpenAI-compat servers (vLLM at older versions, some self-hosted
  llama.cpp builds) don't honor ``stream_options.include_usage`` and
  return no ``usage`` block on streamed responses — telemetry then
  falls back to char-count estimation for those calls.

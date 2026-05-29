prthinker
============

A Chain-of-Thought code review framework for GitHub Pull Requests, backed
by a fine-tuned Qwen3-Coder model with retrieval-augmented prompting.

``prthinker`` reads a PR diff, runs a five-step Chain-of-Thought review,
and posts a structured summary plus one-click ``suggestion`` blocks back
to the PR. It learns from each repo's history — dismissed comments are
filtered out next time, accepted suggestions are surfaced as in-context
exemplars — and can act as a required status check before merges.

What you get
------------

* **Five-step CoT pipeline** — ``first_summary`` → ``first_code_review`` →
  ``linter`` → ``code_smell`` → ``total_summary``, plus an optional
  per-file inline-findings step that emits structured JSON.
* **Per-file inline review** with GitHub ``suggestion`` blocks.
* **RAG over global rules + per-repo rule packs** via ``--rules-dir``.
* **Two learned corpora**: ``dismissed.jsonl`` (filters repeats),
  ``accepted.jsonl`` (top-K exemplars in the prompt).
* **CI failure signals** prepended to the diff for grounded review.
* **Pre-merge Check Run gate** — wire as a required status check.
* **Pluggable backends**: local in-process Qwen + LoRA, or HTTP remote.

.. toctree::
   :maxdepth: 2
   :caption: Guide

   guide/installation
   guide/quickstart
   guide/end-to-end-example
   guide/github-actions
   guide/configuration
   guide/repo-config

.. toctree::
   :maxdepth: 2
   :caption: Concepts

   concepts/architecture
   concepts/pipeline
   concepts/rag-and-rules
   concepts/corpora
   concepts/ci-and-gate
   concepts/cache-and-telemetry
   concepts/judge-and-streaming
   concepts/redaction-and-mcp
   concepts/hook-self-correct-auto-fix
   concepts/docker-platforms-report
   concepts/research-extensions

.. toctree::
   :maxdepth: 2
   :caption: Reference

   reference/cli
   reference/http-api
   reference/python-api

Indices
-------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

prthinker
============

A Chain-of-Thought code review framework for GitHub, GitLab, and Gitea
pull / merge requests, backed by a fine-tuned Qwen3-Coder model with
retrieval-augmented prompting.

``prthinker`` reads a PR diff, runs a configurable Chain-of-Thought
review chain — with ``--step-plan adaptive`` it scales review depth per
file (skip / trivial / standard / deep) — and posts a structured summary
plus one-click ``suggestion`` blocks back to the PR. It learns from each repo's history — dismissed comments are
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
* **Forge-agnostic frontend**: GitHub, GitLab, and Gitea behind one
  ``PlatformAdapter``; a ready-to-use GitLab pipeline ships at
  ``.gitlab-ci.yml``.

.. toctree::
   :maxdepth: 2
   :caption: Guide

   guide/installation
   guide/quickstart
   guide/end-to-end-example
   guide/github-actions
   guide/gitlab-ci
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

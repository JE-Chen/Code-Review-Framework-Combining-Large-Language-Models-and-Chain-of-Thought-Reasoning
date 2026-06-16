Architecture
============

``prthinker`` is structured around six design patterns called out as
mandatory in the project's ``CLAUDE.md``. Every extension point follows
one of them, so adding a new step, backend, or retriever is a matter of
slotting code into existing seams — not editing the pipeline.

In plain language
-----------------

Before the patterns, the one-paragraph version for anyone: when a
developer proposes a code change (a *Pull Request*), ``prthinker`` reads
it and reviews it the way a careful senior engineer would — summarising
what changed, pointing out bugs and risky spots, and leaving comments
right on the affected lines, many with a one-click "apply this fix"
button. It remembers feedback (comments the team dismissed are not
repeated; suggestions the team accepted are reused as examples) and can
be required as a merge gate.

The codebase has **two halves**:

* A lightweight **runner** (the ``prthinker/`` package) that talks to
  GitHub, builds the prompts, and posts results. It needs no GPU — only
  ``httpx`` and ``pydantic``.
* A heavier **AI brain** (the ``codes/`` tree) — the language model plus
  its training and the FastAPI inference server. This is the part that
  needs a GPU, and it can be swapped for a paid API such as OpenAI or
  Anthropic instead.

Project structure
-----------------

.. only:: html

   .. mermaid::

      graph TD
          GHA[".github/workflows<br/>auto-reviews every PR"] --> CLI

          subgraph RUNNER["prthinker/ &mdash; the runner (thin, no GPU)"]
              direction TB
              CLI["CLI &amp; entry points<br/>cli*.py"]
              PIPE["Pipeline &amp; steps<br/>pipeline.py · steps.py · findings.py"]
              BACK["Backends &mdash; swappable AI brains<br/>local · remote · OpenAI · Anthropic · Gemini…"]
              PLAT["Platforms &mdash; code hosts<br/>GitHub · GitLab · Gitea"]
              CORP["Memory / corpora<br/>accepted · dismissed · lessons · RAG · knowledge-graph"]
              SIG["Model-free triage signals<br/>orientation · bidi · merge markers · debug-left…"]
              EXT["Research extensions (opt-in)<br/>personas · counterfactual · risk-score…"]
              OUT["Reports &amp; output<br/>Markdown · HTML · SARIF · JUnit · Sonar · CSV"]
              SEC["Safety<br/>redaction · injection guard · sandbox"]
              CLI --> PIPE
              PIPE --> BACK & PLAT & CORP & SIG & EXT & OUT & SEC
          end

          subgraph SERVER["codes/ &mdash; training &amp; inference (heavy, GPU)"]
              direction TB
              FAST["FastAPI inference server<br/>codes/run/fastapi_server.py"]
              PROMPT["Prompt templates (source of truth)<br/>codes/run/CoT_Prompts/"]
              TRAIN["LoRA fine-tuning<br/>codes/train/ (Qwen3-Coder-30B…)"]
              UTIL["Model + FAISS utils<br/>codes/util/"]
          end

          BACK -. "HTTP /review · /ask" .-> FAST
          FAST --- PROMPT & UTIL
          TRAIN -. "produces the model" .-> FAST

.. only:: latex

   .. code-block:: text

      .github/workflows  ── auto-reviews every PR, drives the runner
      prthinker/         ── THE RUNNER (thin, no GPU)
        cli*.py            command-line entry points
        pipeline / steps   the step-by-step review engine
        backends/          swappable AI brains (local · OpenAI · Anthropic · Gemini…)
        platforms/         code hosts (GitHub · GitLab · Gitea)
        corpora            memory (accepted · dismissed · lessons · RAG · knowledge-graph)
        signals            model-free triage + research extensions
        reports / safety   output formats + redaction / injection guard / sandbox
      codes/             ── THE AI BRAIN (heavy, GPU)
        run/fastapi_server.py   inference server the runner calls over HTTP
        run/CoT_Prompts/        prompt templates (single source of truth)
        train/                  LoRA fine-tuning (Qwen3-Coder-30B…)
        util/                   model loading + FAISS retrieval

The runner reaches the brain over two HTTP shapes (``/ask`` and
``/review``, both detailed under `Runner vs server`_ below). Supporting
directories sit outside both halves: ``docs/`` (this trilingual Sphinx
site), ``docker/`` (one-command self-hosting), ``datas/`` (RAG rule
documents, architecture diagrams, fixtures), ``paper/`` (the manuscript
and slides), and ``tests/``.

Patterns at a glance
--------------------

================== ================================================================
Pattern             Where it lives
================== ================================================================
Strategy            ``prthinker.backends.base.InferenceBackend`` with
                    ``LocalHFBackend`` and ``RemoteHttpBackend`` implementations.
Factory             ``prthinker.backends.create_backend(config)`` is the only
                    way to build a backend. Heavy imports (torch, transformers)
                    are deferred inside the concrete backend.
Template Method     Each review step provides ``build_prompt(ctx)``; the pipeline
                    drives the same loop over them. Prompt strings live in
                    ``codes/run/CoT_Prompts/`` and are reached via builder
                    helpers — never inlined in execution code.
Registry            ``@register_step`` appends new ``ReviewStep`` subclasses to a
                    module-level list. Adding a step does not require editing
                    ``pipeline.py``.
Repository          All FAISS access goes through
                    ``prthinker.rag.RAGRetriever`` implementations. The
                    embedding model loads once.
Dependency          Backends, retrievers, filters and stores are passed into
Injection           ``CoTPipeline`` as constructor arguments. Nothing reaches
                    for module-level singletons inside the pipeline body.
================== ================================================================

Component map
-------------

::

   ┌────────────────────────────────────────────────────────────┐
   │ prthinker/                                              │
   │                                                            │
   │  cli.py ────────────┐                                      │
   │                     ▼                                      │
   │  pipeline.CoTPipeline ─── backends.InferenceBackend ◀──┐   │
   │      │           │              │                     │   │
   │      │           │              ▼                     │   │
   │      │           │     LocalHFBackend       RemoteHttpBackend
   │      │           │            (GPU)        (HTTP /ask)      │
   │      │           ▼                                          │
   │      │     rag.RAGRetriever ◀── FaissRAGRetriever            │
   │      │                          NoOpRetriever                │
   │      │                          RemoteRAGRetriever (HTTP /rag) │
   │      │                                                       │
   │      ├── steps.ReviewStep registry                            │
   │      │     • first_summary    • code_smell                    │
   │      │     • first_code_review• total_summary                 │
   │      │     • linter           • inline_findings (per-file)    │
   │      │                                                       │
   │      ├── dismissed.DismissedFilter   (drops similar repeats)  │
   │      ├── accepted.AcceptedExamplesRetriever (top-K exemplars) │
   │      │                                                       │
   │      ▼                                                       │
   │  github_api / checks / ci_signals                             │
   │                                                              │
   └──────────────────────────────────────────────────────────────┘

           runner side                    server side (codes/run/fastapi_server.py)
   ┌─────────────────────────┐         ┌─────────────────────────────────────────┐
   │ thin: httpx + pydantic  │ ──HTTP──▶│ heavy: torch, transformers, faiss,     │
   │ no GPU needed           │         │ FaissRAGRetriever, DismissedFilter,    │
   │                         │         │ AcceptedExamplesRetriever              │
   └─────────────────────────┘         └─────────────────────────────────────────┘

The CLI is itself a small package: ``cli.py`` holds only the entry point
and a name → handler registry, ``cli_parser.py`` builds the argparse
tree, and ``cli_review.py`` / ``cli_commands.py`` carry the command
handlers. Adding a subcommand is one registry entry plus one handler —
the dispatch has no ``if/elif`` chain.

Runner vs server
----------------

The runner is intentionally thin — its only required dependencies are
``httpx`` and ``pydantic``. Heavy ML stack and the FAISS index live on
the server. This separation is the reason the GitHub Action can run on a
default GitHub-hosted runner without any GPU.

Two HTTP shapes connect them:

* ``/ask`` — single prompt in, plain text out. Used when the runner
  orchestrates the pipeline (``--backend remote`` without
  ``--use-remote-pipeline``).
* ``/review`` — full diff in, structured ``ReviewResponse`` out. The
  server runs RAG + every step + the dismissed filter and returns
  parsed inline findings. The default mode in the bundled workflow.

Both endpoints share the same backend instance loaded once at server
boot.

Adding a step
-------------

A complete new step lives in a single file. The pipeline picks it up via
the registry — no edits to ``pipeline.py``.

.. code-block:: python

   # prthinker/extras/security_audit.py
   from prthinker.steps import (
       ReviewContext, ReviewStep, register_step,
   )

   _PROMPT = """
   Re-read the code diff and list any input handling that could be a
   security risk. Return a bulleted markdown list, no prose.

   Diff:
   {code_diff}
   """

   @register_step
   class SecurityAuditStep(ReviewStep):
       name = "security_audit"

       def build_prompt(self, ctx: ReviewContext) -> str:
           return _PROMPT.format(code_diff=ctx.code_diff)

Import the module once at process start (for example in
``prthinker/__init__.py``) so the ``@register_step`` decorator runs.
The new step will appear in ``prthinker review-file --steps`` and
will be picked up by the default ``--steps ""`` (all registered).

Adding a backend
----------------

Subclass ``InferenceBackend``, add the construction path to
``create_backend``. The pipeline does not need to change.

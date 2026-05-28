Architecture
============

``prthinker`` is structured around six design patterns called out as
mandatory in the project's ``CLAUDE.md``. Every extension point follows
one of them, so adding a new step, backend, or retriever is a matter of
slotting code into existing seams — not editing the pipeline.

Patterns at a glance
--------------------

================== ================================================================
Pattern             Where it lives
================== ================================================================
Strategy            ``prthinker.backends.base.InferenceBackend`` with
                    ``LocalQwen3Backend`` and ``RemoteHttpBackend`` implementations.
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
   │      │           │     LocalQwen3Backend   RemoteHttpBackend
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

End-to-end example
==================

A single coherent walkthrough that wires together everything prthinker
ships: a GPU inference server, a thin runner driving it (CLI or GitHub
Actions), and a Python API that talks to the same server for one-off
scripted reviews.

.. contents::
   :local:
   :depth: 2


Scenario
--------

Solo developer with one GPU box (≥ 18 GB VRAM). They run the 4-bit
NF4-quantised ``Qwen3-Coder-30B-A3B-Instruct`` model on the GPU host,
have GitHub Actions auto-review every pull request, and occasionally
want to drive a one-off review from a local Python script.


Step 1 — Inference server (GPU host)
-------------------------------------

Two equivalent paths: bare ``uvicorn`` for the simplest setup, or
``docker compose`` (default deploys on ``:9000`` HTTP — see the optional
TLS overlay below for production with nginx + bearer-token gating).

1a. uvicorn
~~~~~~~~~~~

.. code-block:: bash

   # On the GPU machine
   git clone https://github.com/<your-org>/prthinker.git
   cd prthinker
   pip install -e ".[server]"             # torch / transformers / faiss / fastapi

   # Learned corpora (optional; empty files are fine — the server
   # ignores them when len == 0)
   mkdir -p .prthinker && touch \
       .prthinker/dismissed.jsonl \
       .prthinker/accepted.jsonl

   # Launch (model loads at import time; first run downloads weights)
   export HF_HOME=/srv/hf-cache
   export PRTHINKER_DISMISSED_PATH=$PWD/.prthinker/dismissed.jsonl
   export PRTHINKER_ACCEPTED_PATH=$PWD/.prthinker/accepted.jsonl
   export PRTHINKER_CACHE_ENABLED=true
   export PRTHINKER_TELEMETRY_ENABLED=true

   uvicorn codes.run.fastapi_server:app \
       --host 0.0.0.0 --port 9000 --workers 1

``--workers 1`` is required — the model must load exactly once.

Default model is ``Qwen/Qwen3-Coder-30B-A3B-Instruct`` with 4-bit NF4 +
double-quant + bf16 compute. If a LoRA adapter exists at
``codes/train/outputs-lora-qwen3-coder-30b`` it is attached as a QLoRA
adapter; otherwise the pure quantised base is served.

Health check:

.. code-block:: bash

   curl http://localhost:9000/healthz
   # {"status":"ok","model":"Qwen/Qwen3-Coder-30B-A3B-Instruct"}


1b. Docker compose (default — HTTP on :9000)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   cd prthinker/docker
   cp .env.example .env       # PRTHINKER_HOST_PORT defaults to 9000
   docker compose up -d

   curl http://your-host:9000/healthz

Optional: TLS + bearer-token overlay
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For production, layer ``docker-compose.tls.yml`` on top — it adds an
nginx reverse proxy with TLS termination and a bearer-token gate, and
hides the prthinker container behind it.

.. code-block:: bash

   cd prthinker/docker
   # edit .env:
   #   PRTHINKER_BACKEND_TOKEN=<long random string>   # openssl rand -hex 32
   #   TLS_CERT_DIR=/etc/letsencrypt/live/your-host
   docker compose -f docker-compose.yml -f docker-compose.tls.yml up -d

   curl https://your-host/healthz \
       -H "Authorization: Bearer $PRTHINKER_BACKEND_TOKEN"


Step 2 — Runner
---------------

The runner has no GPU dependency — install with the ``runner`` extra.

2a. Local CLI on a developer machine
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install -e ".[runner]"             # only httpx + pydantic

   git diff main..HEAD > my-change.diff

   # Self-hosted server + every research-grade extension enabled
   prthinker review-file my-change.diff \
       --backend remote \
       --remote-url https://your-host \
       --remote-api-key "$PRTHINKER_BACKEND_TOKEN" \
       --use-remote-pipeline \
       --per-file --inline-review \
       --counterfactual --provenance \
       --judge --self-correct \
       --max-findings-per-file 10


2b. GitHub Actions
~~~~~~~~~~~~~~~~~~

Drop the workflow into ``.github/workflows/prthinker.yml``:

.. code-block:: yaml

   name: prthinker
   on:
     pull_request:
       types: [opened, synchronize, reopened]

   permissions:
     contents: read
     pull-requests: write
     checks: write
     actions: read

   concurrency:
     group: prthinker-${{ github.event.pull_request.number }}
     cancel-in-progress: true

   jobs:
     prthinker:
       runs-on: ubuntu-latest
       if: ${{ github.event.pull_request.draft == false }}
       timeout-minutes: 30
       steps:
         - uses: actions/checkout@v4
           with:
             ref: ${{ github.event.pull_request.head.sha }}
             fetch-depth: 1
         - uses: actions/setup-python@v5
           with:
             python-version: "3.12"
             cache: "pip"
         - name: Install runner deps
           run: pip install -e ".[runner]"
         - name: Run prthinker
           env:
             GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
             GITHUB_REPOSITORY: ${{ github.repository }}
             PRTHINKER_PR_NUMBER: ${{ github.event.pull_request.number }}

             # Backend — points at the Step 1 server.
             PRTHINKER_BACKEND: remote
             PRTHINKER_REMOTE_URL: ${{ secrets.PRTHINKER_BACKEND_URL }}
             PRTHINKER_REMOTE_API_KEY: ${{ secrets.PRTHINKER_BACKEND_API_KEY }}
             PRTHINKER_USE_REMOTE_PIPELINE: "true"

             # Five-step CoT + per-file inline review
             PRTHINKER_PER_FILE: "true"
             PRTHINKER_INLINE_REVIEW: "true"
             PRTHINKER_MAX_FINDINGS_PER_FILE: "10"

             # RAG over global + per-repo rule packs
             PRTHINKER_RAG_ENABLED: "true"
             PRTHINKER_REMOTE_RAG: "true"
             PRTHINKER_RULES_DIR: ./team-rules

             # Pre-merge gate: any error-severity finding fails the Check Run
             PRTHINKER_GATE_ON: "error"

             # Failed-job tail logs prepended to the diff for grounded review
             PRTHINKER_INCLUDE_CI_SIGNALS: "true"

             # Research-grade extensions (all opt-in, all require --inline-review)
             PRTHINKER_REPLY_TO_AUTHOR: "true"
             PRTHINKER_COUNTERFACTUAL: "true"
             PRTHINKER_PROVENANCE: "true"
             PRTHINKER_JUDGE: "true"
             PRTHINKER_SELF_CORRECT: "true"
           run: python -m prthinker review-pr

Set two repo secrets under *Settings → Secrets and variables → Actions*:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Secret
     - Value
   * - ``PRTHINKER_BACKEND_URL``
     - ``https://your-host`` (docker path) or ``http://your-host:9000``
       (uvicorn path)
   * - ``PRTHINKER_BACKEND_API_KEY``
     - The ``PRTHINKER_BACKEND_TOKEN`` set in Step 1b; may be empty for
       the uvicorn path.


Step 3 — Python API
-------------------

For embedding prthinker in a custom tool (IDE plugin, Slack bot,
batch-scan-the-repo job), drive the pipeline directly:

.. code-block:: python

   # review_a_diff.py
   from pathlib import Path

   from prthinker.backends.remote import RemoteHttpBackend
   from prthinker.config import RemoteBackendConfig
   from prthinker.pipeline import CoTPipeline, PerFileReviewOptions
   from prthinker.rag import RemoteRAGRetriever


   def review_diff(diff_text: str, *, backend_url: str, token: str) -> dict:
       """Run the full CoT pipeline against a unified diff.

       Returns a dict with the per-file summaries, inline findings,
       counterfactual blocks (if any), provenance citations, and the
       judge verdict — suitable for shipping to a UI."""
       backend = RemoteHttpBackend(
           RemoteBackendConfig(url=backend_url, api_key=token)
       )
       retriever = RemoteRAGRetriever(
           base_url=backend_url, api_key=token, threshold=0.7,
       )
       pipeline = CoTPipeline(backend=backend, retriever=retriever)

       try:
           result = pipeline.run_per_file(
               diff_text,
               PerFileReviewOptions(
                   inline_review=True,
                   counterfactual=True,
                   provenance=True,
                   judge=True,
                   self_correct=True,
                   max_findings_per_file=10,
               ),
           )
       finally:
           backend.close()
           retriever.close()

       return {
           "files": [
               {
                   "path": fr.path,
                   "summary": fr.total_summary,
                   "verdict": fr.verdict.verdict if fr.verdict else None,
                   "findings": [
                       {
                           "line": f.line,
                           "severity": f.severity,
                           "comment": f.comment,
                           "suggestion": f.suggestion,
                           "provenance": (
                               f.provenance.model_dump()
                               if f.provenance else None
                           ),
                       }
                       for f in fr.inline_findings
                   ],
                   "counterfactuals": [
                       cf.model_dump() for cf in fr.counterfactuals
                   ],
               }
               for fr in result.per_file
           ],
       }


   if __name__ == "__main__":
       import json, os, sys
       diff = Path(sys.argv[1]).read_text(encoding="utf-8")
       out = review_diff(
           diff,
           backend_url=os.environ["PRTHINKER_REMOTE_URL"],
           token=os.environ.get("PRTHINKER_REMOTE_API_KEY", ""),
       )
       json.dump(out, sys.stdout, indent=2, ensure_ascii=False)


Run it:

.. code-block:: bash

   git diff main..HEAD > my.diff
   export PRTHINKER_REMOTE_URL=https://your-host
   export PRTHINKER_REMOTE_API_KEY=...
   python review_a_diff.py my.diff > result.json


At a glance
-----------

.. code-block:: text

   ┌────────────────────────────────────────────────────────────────────┐
   │ Step 1: GPU host                                                   │
   │   uvicorn   ◄──  /healthz  /ask  /rag  /review                     │
   │   ├ Qwen3-Coder-30B-A3B-Instruct (4-bit NF4 + double-quant)        │
   │   ├ optional LoRA adapter from codes/train/outputs-lora-…          │
   │   └ FAISS index on global rules                                    │
   └─────────────────────────────▲──────────────────────────────────────┘
                                 │ HTTPS + Bearer
            ┌────────────────────┼────────────────────┐
            │                    │                    │
   ┌────────┴───────┐  ┌─────────┴─────────┐  ┌──────┴──────────┐
   │ Step 2a CLI    │  │ Step 2b GHA       │  │ Step 3 Python   │
   │ review-file    │  │ review-pr → PR    │  │ API → JSON for  │
   │ stdout         │  │ comment + Check   │  │ a custom UI     │
   └────────────────┘  └───────────────────┘  └─────────────────┘

All three paths share one server, one model, and one set of learned
corpora — only the *runner* differs.

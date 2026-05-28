GitHub Actions integration
==========================

The reviewer ships with a ready-to-use workflow at
``.github/workflows/reviewmind.yml``. It fires on
``pull_request`` ``opened`` / ``synchronize`` / ``reopened`` and posts a
review back through the same PR.

Required secrets
----------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Secret
     - Purpose
   * - ``REVIEWMIND_BACKEND_URL``
     - Base URL of your hosted inference server
       (e.g. ``https://gpu-host.internal:8000``).
   * - ``REVIEWMIND_BACKEND_API_KEY``
     - Optional bearer token, sent as ``Authorization: Bearer ...``.

Set these in **Settings → Secrets and variables → Actions**.

Required permissions
--------------------

The workflow declares:

.. code-block:: yaml

   permissions:
     contents: read         # checkout
     pull-requests: write   # upsert summary comment, post inline review
     checks: write          # open + complete the pre-merge Check Run
     actions: read          # fetch failed-job logs for CI signals

If you fork the workflow, keep these permissions or features will be
silently skipped.

Tunable env vars
----------------

The workflow exposes the most useful flags as env vars so you can change
behaviour without editing Python:

.. list-table::
   :header-rows: 1
   :widths: 30 15 55

   * - Variable
     - Default
     - Effect
   * - ``REVIEWMIND_BACKEND``
     - ``remote``
     - ``local`` to load Qwen on the runner (needs self-hosted GPU runner).
   * - ``REVIEWMIND_USE_REMOTE_PIPELINE``
     - ``true``
     - Use ``/review`` (single round trip) vs ``/ask`` per step.
   * - ``REVIEWMIND_PER_FILE``
     - ``true``
     - Loop the pipeline per file.
   * - ``REVIEWMIND_INLINE_REVIEW``
     - ``true``
     - Emit inline ``suggestion`` blocks.
   * - ``REVIEWMIND_MAX_FINDINGS_PER_FILE``
     - ``10``
     - Cap per file.
   * - ``REVIEWMIND_RAG_ENABLED``
     - ``true``
     - Toggle RAG entirely.
   * - ``REVIEWMIND_REMOTE_RAG``
     - ``true``
     - Use server ``/rag`` instead of local FAISS (saves runner memory).
   * - ``REVIEWMIND_GATE_ON``
     - ``error``
     - Severity floor that flips the Check Run to ``failure``:
       ``none`` / ``warning`` / ``error``.
   * - ``REVIEWMIND_INCLUDE_CI_SIGNALS``
     - ``true``
     - Prepend failed-job logs to the diff.
   * - ``REVIEWMIND_RULES_DIR``
     - *(unset)*
     - Path to per-repo ``*.md`` rule files.

A complete list of vars and their CLI counterparts is in
:doc:`configuration` and :doc:`../reference/cli`.

Branch protection
-----------------

To make the reviewer block merges:

1. Run at least one PR with ``REVIEWMIND_GATE_ON=error``. A Check Run named
   ``reviewmind`` will appear on the PR's Checks tab.
2. Go to **Settings → Branches → branch protection rule** for ``main``
   (or your target branch).
3. Enable **Require status checks to pass before merging** and add
   ``reviewmind`` to the required checks.

After that, any PR with at least one ``error``-severity finding cannot be
merged until either:

* the author addresses the finding (and re-runs by pushing or
  re-requesting), or
* a maintainer overrides the check.

The summary comment shows the breakdown of error / warning / info counts,
so authors can see what tripped the gate.

Triggering on CI completion
---------------------------

The default trigger (``pull_request``) fires immediately on push. If you
want the reviewer to wait for your CI workflows to finish so it can see
their logs, switch the trigger:

.. code-block:: yaml

   on:
     workflow_run:
       workflows: ["CI"]
       types: [completed]

You'll need to look up the PR number from the workflow run payload in
that case — see the GitHub Actions docs for ``workflow_run`` context.

Self-hosted GPU runner (optional)
---------------------------------

If you want to skip the remote server and run inference on the runner
itself, you need a self-hosted runner with a CUDA-capable GPU. The
``ubuntu-latest`` GitHub-hosted runner cannot fit the 30B model.

In your workflow:

.. code-block:: yaml

   jobs:
     reviewmind:
       runs-on: [self-hosted, gpu]
       env:
         REVIEWMIND_BACKEND: local
         REVIEWMIND_MODEL_NAME: Qwen/Qwen3-Coder-30B-A3B-Instruct
         REVIEWMIND_LORA_PATH: ../train/outputs-lora-qwen3-coder-30b
         REVIEWMIND_USE_REMOTE_PIPELINE: "false"
         REVIEWMIND_REMOTE_RAG: "false"
       steps:
         - uses: actions/checkout@v4
         - run: pip install -e ".[local]"
         - run: python -m reviewmind review-pr

The same flags work, but expect 5-10 minutes per file instead of 30
seconds with a properly sized server.

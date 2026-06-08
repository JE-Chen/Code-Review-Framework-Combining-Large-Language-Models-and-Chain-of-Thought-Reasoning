GitHub Actions integration
==========================

The reviewer ships with a ready-to-use workflow at
``.github/workflows/prthinker.yml``. It fires on
``pull_request`` ``opened`` / ``synchronize`` / ``reopened`` and posts a
review back through the same PR.

Workflow shape
--------------

The workflow is structured as three jobs so a slow file (or a large PR)
cannot starve the whole review:

1. **enumerate** (12 min) — lists the PR's changed files, drops noise
   paths via ``PRTHINKER_EXCLUDE_GLOBS``, emits the surviving list as
   a JSON output for the next job's matrix, and posts the Copilot-style
   pre-review PR summary (see `Pre-review PR summary`_ below).
2. **review** (matrix, 60 min per shard, ``max-parallel: 1``) — each
   matrix iteration owns exactly one file, passes
   ``PRTHINKER_TARGET_FILE`` to the CLI, and writes a partial
   ``ReviewResult`` JSON to ``$RUNNER_TEMP/partial.json`` via
   ``PRTHINKER_OUTPUT_JSON``. The partial is uploaded as an artifact
   named ``partial-<job-index>``. The runners do **not** post to
   GitHub directly and they do not open the gate — those are the
   aggregator's job.
3. **aggregate** (15 min, ``if: always()``) — downloads every
   ``partial-*`` artifact, runs ``prthinker aggregate`` to merge
   ``inline_findings`` + ``per_file`` + ``step_outputs`` across
   shards, then posts **one** summary comment, **one** inline review,
   and opens + closes the pre-merge gate exactly once.

``max-parallel: 1`` is intentional: the inference backend serialises
on a single GPU, so parallel matrix runners would queue at
``/review/submit`` and waste CI minutes for no wall-time gain. The
benefit of the matrix is per-file isolation — each file gets its own
60-minute budget and a single slow file does not cancel the others.

Why a job-pattern endpoint, not synchronous ``/review``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The remote runner calls ``/review/submit`` then polls
``/review/result/{id}`` every five seconds (see
:doc:`../reference/http-api`). Each round trip completes in well under
one second, so it sits safely inside the 100 s idle timeout that
Cloudflare's free / pro / business proxy applies. A synchronous
``/review`` POST would block long enough for the proxy to return 504
before the 30B MoE finishes one file.

Concurrency and GPU serialization
---------------------------------

The workflow groups concurrency per PR and cancels in progress:

.. code-block:: yaml

   concurrency:
     group: prthinker-pr-${{ github.event.pull_request.number }}
     cancel-in-progress: true

A new commit therefore supersedes the PR's *own* in-flight run — the
stale review is dropped rather than finished against code that no
longer exists. Different PRs are not affected: they run concurrently at
the workflow level.

Cross-PR GPU safety is enforced **server-side**, not by the CI
concurrency group. Every ``model.generate`` on the inference server runs
under one process-wide lock, so two PRs reviewing at once queue on the
GPU rather than running two forward passes that would OOM the card. That
decoupling is what makes the per-PR ``cancel-in-progress`` safe: the CI
layer no longer has to serialize the GPU.

Required secrets
----------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Secret
     - Purpose
   * - ``PRTHINKER_BACKEND_URL``
     - Base URL of your hosted inference server
       (e.g. ``https://gpu-host.internal:9000``).
   * - ``PRTHINKER_BACKEND_API_KEY``
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
   :widths: 30 25 45

   * - Variable
     - Default
     - Effect
   * - ``PRTHINKER_BACKEND``
     - ``remote``
     - ``local`` to load Qwen on the runner (needs self-hosted GPU runner).
   * - ``PRTHINKER_USE_REMOTE_PIPELINE``
     - ``true``
     - Use ``/review/submit`` (one job per file) vs ``/ask`` per step.
   * - ``PRTHINKER_PER_FILE``
     - ``true``
     - Loop the pipeline per file. The matrix workflow requires this.
   * - ``PRTHINKER_INLINE_REVIEW``
     - ``true``
     - Emit inline ``suggestion`` blocks.
   * - ``PRTHINKER_MAX_FINDINGS_PER_FILE``
     - ``10``
     - Cap per file.
   * - ``PRTHINKER_EXCLUDE_GLOBS``
     - ``.idea/*,datas/*,*.md,…``
     - Comma-separated fnmatch patterns; matched files never enter the
       matrix. Workflow and CLI both honour this; set it once in the
       workflow's ``env`` block to keep them in sync.
   * - ``PRTHINKER_TARGET_FILE``
     - *(unset; set by matrix)*
     - Restricts ``--per-file`` mode to one path. The matrix sets this
       per shard from ``matrix.file`` — you should not override it.
   * - ``PRTHINKER_OUTPUT_JSON``
     - *(unset; set by matrix)*
     - Write the partial ``ReviewResult`` here instead of posting.
       Aggregate job consumes the JSON via
       ``PRTHINKER_AGGREGATE_FROM``.
   * - ``PRTHINKER_AGGREGATE_FROM``
     - *(set by aggregate job)*
     - Directory the ``aggregate`` subcommand scans for partials.
   * - ``PRTHINKER_RAG_ENABLED``
     - ``true``
     - Toggle RAG entirely.
   * - ``PRTHINKER_REMOTE_RAG``
     - ``true``
     - Use server ``/rag`` instead of local FAISS (saves runner memory).
   * - ``PRTHINKER_GATE_ON``
     - ``error`` (aggregate) /
       ``none`` (matrix)
     - Severity floor that flips the Check Run to ``failure``. The
       matrix runners run with ``none`` so only the aggregate opens
       and closes the gate.
   * - ``PRTHINKER_INCLUDE_CI_SIGNALS``
     - ``true``
     - Prepend failed-job logs to the diff.
   * - ``PRTHINKER_RULES_DIR``
     - *(unset)*
     - Path to per-repo ``*.md`` rule files.

A complete list of vars and their CLI counterparts is in
:doc:`configuration` and :doc:`../reference/cli`.

Skip and fallback behaviour
---------------------------

The workflow is built to fail gracefully:

* **Empty PR after filtering** — if every changed file matches
  ``PRTHINKER_EXCLUDE_GLOBS``, the ``enumerate`` job sets
  ``empty=true`` and the downstream jobs are skipped via
  ``if: empty == 'false'``. The PR gets no comment and no check run.
* **One matrix shard fails** — ``strategy.fail-fast: false`` keeps the
  other shards running. The aggregate job runs under
  ``if: always()`` so the surviving partials still produce a review.
* **Backend unreachable from a shard** — the shard's preflight curl
  to ``/healthz`` exits 0 with a workflow warning and uploads no
  artifact (``if-no-files-found: ignore``). The aggregate proceeds
  with whatever shards succeeded.
* **Backend unreachable from every shard** — the aggregate finds no
  ``*.json`` under ``PRTHINKER_AGGREGATE_FROM``, posts a single
  *PRThinker — skipped* comment under the standard marker, and exits
  0. The PR is not blocked and the next push overwrites the notice.
* **Workflow cancelled mid-run** — the runner-side client wraps the
  poll loop in a try/finally that posts ``POST /review/cancel/{id}``
  on its way out, so a ``concurrency: cancel-in-progress`` or a
  manual cancel does not leave the backend chewing on a review
  nobody will read. The backend's idle sweeper is the safety net
  for any cancellation path that skipped the cleanup (SIGKILL,
  network partition): every job whose result endpoint has not been
  polled for 180 s gets its ``cancel_event`` set automatically.
* **Transient poll failure** — a single ``/review/result`` GET that
  trips the client's per-call timeout (backend GIL pause, edge
  hiccup, runner network blip) is retried up to five times in a
  row before the loop gives up. A successful poll resets the
  counter, so a long sequence of healthy polls followed by one
  blip is invisible to the workflow.

Pre-review PR summary
---------------------

Before the matrix starts, the ``enumerate`` job runs
``prthinker pr-summary`` to post a Copilot-style brief of the PR. It
reads the PR title, description, and commit messages alongside the diff
and upserts a dedicated comment under its own
``<!-- prthinker:pr-summary -->`` marker — separate from, and posted
earlier than, the review summary — with ``### Overview`` /
``### Key changes`` / ``### Areas to review`` / ``### Notes`` sections
that reconcile what the author wrote against what the diff does. See
:doc:`../reference/cli` for the command.

Keeping the call in ``enumerate`` puts it ahead of the per-file review,
so its one short backend generate stays serial with the reviews on the
shared GPU. The step is best-effort: a retried health probe and a
retried generate ride over a momentarily cold tunnel, and on persistent
failure it exits 0 with a warning so it can never block the matrix.
Distinct from the aggregate-time *Overall Summary* below — that one
summarises the review *findings*; this one summarises the *change*.

PR-wide overall summary
-----------------------

After merging every shard's partial ``ReviewResult``, the aggregate
job asks the backend's job-pattern ``/ask/submit`` for a single
3–5-sentence PR-wide summary built from the per-file summaries.
The reply is stashed in ``merged.step_outputs["total_summary"]``,
which the formatter renders as ``### Overall Summary`` at the top
of the PR comment — right before the per-file ``<details>`` blocks.

The synthesis is best-effort. ``PRTHINKER_REMOTE_URL`` not set, a
backend timeout, a polling deadline of 30 minutes, or any other
``httpx`` exception logs a warning and returns an empty string; the
formatter then falls back to the per-file blocks alone. PRs with
fewer than two surviving file summaries skip the synthesis entirely
— the single file's own summary already covers the whole PR.

Comment, review, and gate dedup
-------------------------------

Re-running a workflow on the same commit (manual *Re-run all jobs*,
``concurrency: cancel-in-progress`` followed by a fresh push to the
same branch tip, etc.) used to accumulate one prthinker artifact
per run on the PR. Each run now cleans up its own predecessors
before posting:

* **Summary comment** — upserted by HTML marker
  (``<!-- prthinker:summary -->``), so the same comment is PATCHed
  in place across runs.
* **Inline review** — every prthinker inline review carries a
  hidden ``<!-- prthinker:inline -->`` marker in its body. Before
  posting a new one, the runner lists the PR's reviews, finds
  every review whose body contains the marker, and DELETEs each
  of its child review comments. The wrapper review remains on the
  timeline (GitHub does not allow dismissing ``COMMENT``-state
  reviews) but it no longer puts duplicate annotations on the
  diff. Cleanup failure is logged at WARNING but never blocks the
  new submission.
* **Check run** — before opening the gate, the runner lists every
  check run named ``prthinker`` on the head commit and PATCHes
  each one to ``status=completed`` /
  ``conclusion=neutral`` with a *superseded* title. GitHub does
  not permit deleting check runs, but the UI collapses the
  superseded ones under the live in-progress entry.

Branch protection
-----------------

To make the reviewer block merges:

1. Run at least one PR with ``PRTHINKER_GATE_ON=error``. A Check Run named
   ``prthinker`` will appear on the PR's Checks tab.
2. Go to **Settings → Branches → branch protection rule** for ``main``
   (or your target branch).
3. Enable **Require status checks to pass before merging** and add
   ``prthinker`` to the required checks.

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
     prthinker:
       runs-on: [self-hosted, gpu]
       env:
         PRTHINKER_BACKEND: local
         PRTHINKER_MODEL_NAME: Qwen/Qwen3-Coder-30B-A3B-Instruct
         PRTHINKER_LORA_PATH: ../train/outputs-lora-qwen3-coder-30b
         PRTHINKER_USE_REMOTE_PIPELINE: "false"
         PRTHINKER_REMOTE_RAG: "false"
       steps:
         - uses: actions/checkout@v4
         - run: pip install -e ".[local]"
         - run: python -m prthinker review-pr

The same flags work, but expect 5-10 minutes per file instead of 30
seconds with a properly sized server.

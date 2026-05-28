Docker, multi-platform, and longitudinal reporting
===================================================

Three additions that take prthinker from "library you import" to
"system you operate":

* **Docker compose** — one-command self-hosted deployment.
* **PlatformAdapter** — GitHub and GitLab behind a single Strategy.
* **``prthinker report``** — cross-store longitudinal summary.

Self-hosted deployment with Docker compose
------------------------------------------

The bundle in ``docker/`` deploys the FastAPI inference server with TLS
termination + bearer-token auth in one command. Three host requirements:

* NVIDIA GPU with a driver that matches the configured CUDA version
  (default ``12.2.0``).
* Docker 24+ with the NVIDIA container runtime
  (``runtime: nvidia`` declared in ``docker-compose.yml``).
* A TLS certificate (Let's Encrypt or self-signed) mounted into the
  nginx container.

Files:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - file
     - role
   * - ``docker/Dockerfile.server``
     - CUDA-runtime base + Python 3.12 + ``pip install -e .[server]``.
       Model weights NOT baked in — pulled into a volume at first run.
   * - ``docker/docker-compose.yml``
     - Two services (``prthinker`` + ``nginx``), three volumes
       (``hf_cache``, ``data``, host TLS dir).
   * - ``docker/nginx.conf``
     - TLS termination, ``/healthz`` bypasses auth, all other paths
       require ``Authorization: Bearer <PRTHINKER_BACKEND_TOKEN>``.
   * - ``docker/entrypoint-nginx.sh``
     - Substitutes the token into ``nginx.conf`` at container start;
       refuses to boot if the env var is missing (fail-fast).
   * - ``docker/.env.example``
     - Template for the bearer token, TLS cert dir, host port, CUDA tag.

Bring-up:

.. code-block:: bash

   cd docker
   cp .env.example .env
   # edit: PRTHINKER_BACKEND_TOKEN=$(openssl rand -hex 32)
   #       TLS_CERT_DIR=/etc/letsencrypt/live/your-host
   docker compose up -d

   # verify
   curl https://your-host/healthz \
       -H "Authorization: Bearer $PRTHINKER_BACKEND_TOKEN"

Volumes:

* ``hf_cache`` — HuggingFace weights. Survives ``docker compose down``;
  delete only if you change models and want to reclaim ~80 GB.
* ``data`` — cache.sqlite, telemetry.sqlite, dismissed.jsonl,
  accepted.jsonl. Back this up.
* TLS dir is a **host bind-mount** so you control cert rotation
  separately from the compose lifecycle.

The image deliberately does NOT bake in weights — an image rebuild
should never invalidate a ~80 GB download. The trade-off is a slow
first request after a fresh ``docker compose up`` while the weights
download into the volume; subsequent requests are warm.

Multi-platform support via ``PlatformAdapter``
----------------------------------------------

The pipeline talks to GitHub / GitLab through one Strategy interface:

.. code-block:: text

   prthinker.platforms.base.PlatformAdapter        (ABC)
       │
       ├── GitHubAdapter   (wraps github_api.py + checks.py)
       └── GitLabAdapter   (direct httpx → /api/v4 endpoints)

The five methods every adapter implements:

.. list-table::
   :header-rows: 1
   :widths: 32 68

   * - method
     - purpose
   * - ``fetch_diff()``
     - Unified diff for the PR / MR.
   * - ``fetch_head_sha()``
     - Head commit SHA — needed by the gate.
   * - ``fetch_base_branch()``
     - Used by auto-fix when opening the draft PR back into the base.
   * - ``upsert_summary_comment(body)``
     - Marker-tagged comment, upserted by ``comment_marker`` substring.
   * - ``submit_inline_review(findings, summary_body, event)``
     - Inline comments + optional ``suggestion`` blocks; ``event`` maps
       to GitHub Review verbs or GitLab discussion prefixes.
   * - ``open_gate(head_sha)`` / ``close_gate(handle, result)``
     - GitHub: Check Run. GitLab: commit status via
       ``POST /projects/:id/statuses/:sha``.

Wire-format differences that the adapter hides
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 28 36 36

   * - concern
     - GitHub
     - GitLab
   * - identifier
     - ``owner/name`` + ``pr_number``
     - ``group/project`` URL-encoded + ``mr_iid``
   * - inline comment
     - ``POST /pulls/:n/reviews`` with ``comments[].line``
     - ``POST /merge_requests/:iid/discussions`` with ``position``
       (``base_sha`` / ``start_sha`` / ``head_sha`` / ``new_path`` /
       ``new_line``)
   * - status check
     - Check Run (``POST /check-runs``)
     - Commit status (``POST /statuses/:sha`` with
       ``state=pending|success|failed``)
   * - review verdict
     - native ``event: APPROVE`` / ``REQUEST_CHANGES`` / ``COMMENT``
     - GitLab has no native verb on discussions; we prefix the body
       with ``**Verdict: APPROVE**`` (future work: actually call
       ``POST /merge_requests/:iid/approve`` when event == APPROVE)
   * - auth header
     - ``Authorization: Bearer <token>``
     - ``PRIVATE-TOKEN: <token>``

CLI usage
~~~~~~~~~

.. code-block:: bash

   # GitHub (default)
   prthinker review-pr --repo owner/name --pr-number 42

   # GitLab on gitlab.com
   prthinker review-pr \
       --platform gitlab \
       --repo group/project \
       --pr-number 42 \
       --github-token "$GITLAB_TOKEN"

   # Self-hosted GitHub Enterprise
   prthinker review-pr \
       --platform github \
       --platform-base-url https://github.example.com/api/v3 \
       --repo owner/name --pr-number 42

The ``--github-token`` flag accepts ``GITLAB_TOKEN`` as a fallback env
var; the CLI knows which one to use based on ``--platform``. The
``--repo`` flag accepts ``CI_PROJECT_PATH`` for GitLab CI compatibility.

Features that are GitHub-only today
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Two pieces of the pipeline still talk directly to the GitHub Actions
API and are skipped on GitLab with a log line:

* **CI signal injection** (``--include-ci-signals``) — uses the
  Actions ``/jobs/:id/logs`` endpoint. The GitLab equivalent is
  ``/projects/:id/jobs/:id/trace`` and is on the roadmap.
* **Auto-fix draft PR** (``--auto-fix-threshold``) — uses the GitHub
  pulls API to create the fix-up PR. The GitLab equivalent is the
  Merge Requests API.

Both are tracked as future work. Everything else (CoT pipeline, gate,
inline review, judge, self-correct) works on both platforms today.

``prthinker report`` — longitudinal summary
--------------------------------------------

The four stores the framework writes (telemetry SQLite, cache SQLite,
dismissed / accepted JSONL) accumulate quietly. ``prthinker report``
joins them and renders a human- or machine-readable summary:

.. code-block:: bash

   # markdown to stdout
   prthinker report --since-days 30

   # html file you can email to ops
   prthinker report --since-days 30 --format html --out report.html

   # json for piping into Grafana / DuckDB
   prthinker report --since-days 30 --format json --out report.json

Sections rendered:

1. **Usage by (backend, model)** — calls, cache hits, in/out tokens,
   USD cost, p50 / p95 latency.
2. **Cache** — entry count + lifetime hit count.
3. **Daily cost sparkline** — ASCII bars over the last 14 days, with
   peak value annotation.
4. **Dismissed corpus** — total + count per reason
   (``thumbs-down reaction`` / ``reply matched: ...``).
5. **Accepted corpus** — total + top 5 files by accepted-suggestion
   count.

Implementation properties:

* **Pure stdlib + project modules.** No numpy, no matplotlib — the
  sparkline uses the eight Unicode block characters
  ``▁▂▃▄▅▆▇█``.
* **Missing files are not an error.** If telemetry or a JSONL store
  doesn't exist yet, the corresponding section renders as "no data"
  and the rest of the report still works.
* **Read-only.** Every store is opened in read mode; running the
  report never mutates state.

When to use each format
~~~~~~~~~~~~~~~~~~~~~~~

* ``markdown`` — paste into a wiki page or commit into the repo for
  weekly stand-ups.
* ``html`` — single self-contained file you can host on a static
  server or attach to an email.
* ``json`` — feed downstream tools (DuckDB, Grafana JSON datasource,
  ad-hoc pandas analysis).

No clustering yet
~~~~~~~~~~~~~~~~~

The current report does NOT cluster dismissed comments by semantic
similarity. The dismissed store's embeddings are computed by the
inference server at startup for the filter; bringing the embedding
model into the runner just to cluster a few hundred comments adds a
heavy dep for little gain. If clustering becomes valuable, the
``--format json`` output is the integration point — feed it through
your own embedding + KMeans of choice without changing this module.

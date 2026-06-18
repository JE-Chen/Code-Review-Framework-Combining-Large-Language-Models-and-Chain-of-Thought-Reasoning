GitLab CI integration
======================

The reviewer is **forge-agnostic**: the same runner CLI
(``python -m prthinker review-pr``) drives a GitHub, GitLab, or Gitea
merge request behind one :class:`~prthinker.platforms.base.PlatformAdapter`
strategy, selected with ``--platform`` (or ``$PRTHINKER_PLATFORM``). A
ready-to-use GitLab pipeline ships at ``.gitlab-ci.yml`` in the repo root.

How it maps to GitLab
---------------------

Nothing in the review path is GitHub-specific. The CLI resolves the
GitLab-CI environment automatically, so the pipeline passes no
identifier flags:

.. list-table::
   :header-rows: 1
   :widths: 38 27 35

   * - GitLab-CI variable
     - CLI argument
     - Meaning
   * - ``$CI_PROJECT_PATH``
     - ``--repo``
     - ``group/project`` slug
   * - ``$CI_MERGE_REQUEST_IID``
     - ``--pr-number``
     - Merge-request iid
   * - ``$GITLAB_TOKEN``
     - ``--github-token``
     - API token (``api`` scope)
   * - ``$PRTHINKER_PLATFORM=gitlab``
     - ``--platform``
     - Selects the GitLab adapter

The adapter posts the summary as a merge-request note, findings as
inline discussion threads on the diff, and the gate as a commit status
named ``prthinker`` — the GitLab counterpart of GitHub's Check Run.

One job, no matrix
------------------

Unlike the GitHub Actions workflow there is no ``enumerate`` / matrix /
``aggregate`` split. That fan-out exists only to shard the single shared
GPU backend across per-file runners. ``review-pr`` reviews every changed
file in one process and posts the summary, inline discussions, and gate
directly, so the GitLab pipeline is a single ``review-pr`` job.

Required CI/CD variables
------------------------

Set these under **Settings → CI/CD → Variables** (mark the tokens
*Masked*):

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Variable
     - Purpose
   * - ``GITLAB_TOKEN``
     - Project / group access token or PAT with the ``api`` scope. The
       built-in ``CI_JOB_TOKEN`` cannot post merge-request notes.
   * - ``PRTHINKER_BACKEND_URL``
     - HTTPS URL of the inference backend; the CI runner needs no GPU.
   * - ``PRTHINKER_BACKEND_API_KEY``
     - Optional bearer token for the backend.

The pipeline file
-----------------

The shipped ``.gitlab-ci.yml`` reduces to one job. The essential shape:

.. code-block:: yaml

   prthinker-review:
     stage: review
     image: python:3.12-slim
     rules:
       - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
     variables:
       PRTHINKER_PLATFORM: "gitlab"
       PRTHINKER_BACKEND: "remote"
       PRTHINKER_REMOTE_URL: "$PRTHINKER_BACKEND_URL"
       PRTHINKER_REMOTE_API_KEY: "$PRTHINKER_BACKEND_API_KEY"
       PRTHINKER_GATE_ON: "error"
     script:
       - pip install -e ".[runner]"
       - python -m prthinker review-pr

The ``rules`` clause mirrors the GitHub ``pull_request`` trigger: the job
runs only on merge-request pipelines.

Blocking merges
---------------

The gate is the ``prthinker`` commit status, not the pipeline's pass /
fail. To hard-block merges, require that status under **Settings → Merge
requests** (merge checks) or the protected-branch rules — the same model
as a required GitHub Check Run. The summary note shows the
error / warning / info breakdown so authors can see what tripped it.

Feature parity
--------------

The review itself — the CoT pipeline, RAG, learned corpora, inline
suggestions, and the gate — is identical across forges. Two GitHub-only
extras degrade gracefully on GitLab (each is logged and skipped, never a
crash): the CI-failure-signal prepend and the auto-fix draft PR.

Self-hosted GitLab works by pointing the adapter at your instance's API
with ``--platform-base-url`` (or ``$PRTHINKER_PLATFORM_BASE_URL``),
e.g. ``https://gitlab.example.com/api/v4``. The same pattern serves
Gitea with ``--platform gitea``.

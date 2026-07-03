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
suggestions, and the gate — is identical across forges, and the GitLab
adapter covers the platform extras too:

* **CI failure signals** (``--include-ci-signals``) read the failed
  pipeline jobs' trace tails via ``/projects/:id/jobs/:id/trace``.
* **Auto-fix** (``--auto-fix-threshold``) opens a ``Draft:`` merge
  request with the applied suggestions — the MR counterpart of the
  GitHub draft PR.
* **Labels, description digest, and PR summary** (``--pr-labels``,
  ``--pr-body-summary``, the ``pr-summary`` subcommand) reconcile the
  managed MR labels, upsert the marker-delimited description block, and
  maintain the standalone summary note. Long reviews paginate across
  several notes; stale pages from a previous longer run are deleted.
* **Verdicts** map onto the approvals API: ``APPROVE`` approves the MR
  and ``REQUEST_CHANGES`` revokes a prior approval (best-effort — a
  token that cannot approve logs a warning and the verdict stays in the
  discussion bodies).
* Inline findings are pre-filtered against the MR's diff hunks before
  posting, so one hallucinated line number costs one dropped finding
  instead of a run of failed discussion POSTs.
* **Stale-thread cleanup**: each run marks its inline discussions with a
  hidden comment and deletes the previous run's marked threads after the
  new ones post — the MR counterpart of GitHub's stale-review dismissal,
  so re-pushes never pile up duplicate findings.
* **Code Quality widget**: the shipped pipeline exports the findings as
  a CodeClimate report (``PRTHINKER_CODEQUALITY_OUT`` +
  ``artifacts:reports:codequality``), GitLab's counterpart of the SARIF
  upload the GitHub workflow performs. This is also the per-line channel
  to use instead of ``--check-annotations`` — commit statuses cannot
  carry Check-Run-style annotations, so those are logged and omitted.
* **Learning-loop harvesting**: ``harvest-dismissed`` and
  ``harvest-accepted`` accept ``--platform gitlab`` and read MR
  discussions instead of PR review comments — a 👎 award emoji or a
  dismissal-keyword reply marks a finding dismissed, and applied
  suggestions (``Apply N suggestion(s) …`` commits) feed the accepted
  corpus.
* **Oversized diffs** degrade the same way as on GitHub: when the
  whole-MR ``raw_diffs`` endpoint fails, the diff is reconstructed from
  the paginated per-file ``diffs`` endpoint instead of failing the
  review.

Self-hosted GitLab works by pointing the adapter at your instance's API
with ``--platform-base-url`` (or ``$PRTHINKER_PLATFORM_BASE_URL``),
e.g. ``https://gitlab.example.com/api/v4``. Inside GitLab CI even that
is unnecessary — the adapter falls back to the pipeline's
``$CI_API_V4_URL`` automatically. The same pattern serves Gitea with
``--platform gitea``.

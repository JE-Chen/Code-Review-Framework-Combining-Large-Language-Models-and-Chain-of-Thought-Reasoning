CLI reference
=============

Invoke the CLI either via the installed entry point or via the module::

   reviewmind <subcommand> [options]
   python -m reviewmind <subcommand> [options]

Global options
--------------

.. option:: --log-level {DEBUG,INFO,WARNING,ERROR}

   Default ``INFO``. Override with ``REVIEWMIND_LOG_LEVEL``.

review-pr
---------

Fetch a PR diff, run the pipeline, post comment + review + gate.

.. code-block:: text

   reviewmind review-pr
       --repo OWNER/NAME           # or $GITHUB_REPOSITORY
       --pr-number N
       --github-token TOKEN        # or $GITHUB_TOKEN
       [--backend {local,remote}]
       [--remote-url URL]
       [--use-remote-pipeline]
       [--no-rag] [--remote-rag] [--rag-threshold 0.7]
       [--rules-dir PATH]
       [--per-file] [--inline-review] [--max-findings-per-file 10]
       [--reply-to-author] [--counterfactual] [--provenance]
       [--diff-since-last] [--diff-cache-path PATH]
       [--verify-suggestions] [--verify-cmd CMD] [--verify-timeout 60] [--verify-workdir PATH]
       [--api-consistency] [--pr-classify] [--reproducibility-check]
       [--dep-upgrade-check]
       [--personas LIST] [--risk-weighted] [--risk-workdir PATH] [--diff-entropy]
       [--judge] [--self-correct]
       [--gate-on {none,warning,error}]
       [--include-ci-signals] [--ci-signal-max-jobs 5] [--ci-signal-tail-chars 4000]
       [--marker '<!-- reviewmind:summary -->']
       [--dry-run]

Notable flags:

* ``--dry-run`` — print the summary comment to stdout instead of posting
  it; also skips opening the Check Run.
* ``--marker`` — sentinel HTML comment used to upsert the PR comment.
  Override only if you need multiple reviewers in one repo.

Research-grade flags (opt-in, ``--inline-review`` required):

.. option:: --reply-to-author

   Read the PR author's replies to the most recent reviewmind summary
   comment and inject them as a *Prior dialogue* block into the
   inline-findings prompt. Closes the loop so the next review does not
   silently repeat a finding the author already addressed. Env:
   ``REVIEWMIND_REPLY_TO_AUTHOR``.

.. option:: --counterfactual

   After inline findings, run a counterfactual / mutation step that
   surfaces competing alternative implementations and a trade-off matrix
   for each *design-choice* finding. Skipped findings that are clear
   bugs / nits. Adds one extra backend call per file. Env:
   ``REVIEWMIND_COUNTERFACTUAL``.

.. option:: --provenance

   Ask the model to cite the RAG rule / accepted-example / diff line(s)
   that informed each finding, and surface those citations as an
   *Audit trail* footer under the per-file block. Out-of-range citations
   are silently dropped; a bad citation never drops a real finding.
   Env: ``REVIEWMIND_PROVENANCE``.

.. option:: --judge

   Per-file self-assessment step that emits an ``approve`` /
   ``request_changes`` / ``comment`` verdict. The CLI aggregates verdicts
   across files and maps the result to the GitHub review event.

.. option:: --self-correct

   Second-pass noise filter: model is shown the surviving findings and
   asked to drop the ones it considers noise. One extra backend call
   per file. Safe-failure direction: malformed output leaves the list
   unchanged.

.. option:: --diff-since-last

   Hash each file's post-change content and reuse cached findings on
   subsequent pushes for files whose hash hasn't changed. SQLite store
   at ``--diff-cache-path`` (default ``.reviewmind/diff-cache.sqlite``),
   keyed on ``(pr_number, repo, file_path, hunk_sha256)`` — cross-PR
   isolated. Env: ``REVIEWMIND_DIFF_SINCE_LAST``.

.. option:: --verify-suggestions

   Clone the workdir into a disposable sandbox, apply each finding's
   ``suggestion`` block at the right line range, and run
   ``--verify-cmd`` (default ``pytest -x``) under ``--verify-timeout``
   (default 60s). Badges each finding ``[verified]`` / ``[FAILED]`` /
   ``[skipped]`` / ``[error]``. Original repo never mutated. Env:
   ``REVIEWMIND_VERIFY_SUGGESTIONS``.

.. option:: --api-consistency

   When the diff touches both backend (``.py``) and frontend (``.ts`` /
   ``.tsx`` / ``.js`` / ``.jsx``) files, run an extra step that
   surfaces *cross-file* drift (renamed fields, removed routes, type
   changes). Skipped silently on single-language PRs. Env:
   ``REVIEWMIND_API_CONSISTENCY``.

.. option:: --pr-classify

   Classify the PR (``bugfix`` / ``feature`` / ``refactor`` / ``docs``
   / ``chore`` / ``unknown``) from diff + title + body, then adapt
   review depth: docs PRs skip inline findings; bugfix PRs use a
   focused prompt with smaller budget. Env:
   ``REVIEWMIND_PR_CLASSIFY``.

.. option:: --reproducibility-check

   Run the inline-findings step twice per file (identical prompt;
   non-zero temperature gives a second sample) and label each finding
   ``stable`` / ``low`` based on cross-pass match. Backend-agnostic
   uncertainty proxy. Env: ``REVIEWMIND_REPRODUCIBILITY_CHECK``.

.. option:: --dep-upgrade-check

   Detect dependency version bumps in lock files
   (``requirements.txt`` / ``pyproject.toml`` / ``package.json``) and
   ask the model whether breaking changes between the old and new
   versions affect this codebase's actual usage. Env:
   ``REVIEWMIND_DEP_UPGRADE_CHECK``.

.. option:: --personas <list>

   Comma-separated list of review personas (``security``,
   ``performance``, ``readability``, ``api_stability``,
   ``maintainability``) — or ``all`` for every persona. Each persona's
   prompt restricts the model to its lens; a conflict-finder step then
   surfaces where the personas disagree. Empty (default) disables.
   Env: ``REVIEWMIND_PERSONAS``.

.. option:: --risk-weighted

   Compute a per-file risk score from churn (``git log`` over the
   default 90-day window), complexity (line count at HEAD), and bug
   history (commit messages matching ``fix:`` / ``bug`` / ``revert``).
   Scales ``max_findings_per_file`` proportional to the score between
   ``floor`` (default 2) and ``ceiling`` (default ``2 ×
   base_budget``). Set ``--risk-workdir`` to point at the git repo.
   Env: ``REVIEWMIND_RISK_WEIGHTED``.

.. option:: --diff-entropy

   Compute the diff's size + dispersion entropy and surface a
   "Consider splitting this PR" warning at the top of the comment
   when the score crosses the ``bomb`` threshold. Pure local CPU; no
   backend call. Env: ``REVIEWMIND_DIFF_ENTROPY``.

review-file
-----------

Run the pipeline against a local file or stdin.

.. code-block:: text

   reviewmind review-file PATH
       [--backend {local,remote}]
       [--remote-url URL] [--remote-api-key TOKEN]
       [--model-name NAME] [--lora-path PATH]
       [--no-rag] [--remote-rag] [--rag-threshold 0.7]
       [--rules-dir PATH]
       [--per-file] [--inline-review] [--max-findings-per-file 10]
       [--counterfactual] [--provenance] [--judge] [--self-correct]
       [--diff-since-last] [--verify-suggestions]
       [--api-consistency] [--pr-classify] [--reproducibility-check]
       [--dep-upgrade-check] [--personas LIST]
       [--risk-weighted] [--diff-entropy]
       [--max-new-tokens 32768]
       [--steps a,b,c]
       [--output-dir PATH]

``PATH`` may be ``-`` to read the diff from stdin.

``--output-dir`` writes each step's raw text output to disk
incrementally — useful for batch experiments and debugging long runs.

``--steps`` accepts a comma-separated list of step names; empty (the
default) runs every registered step.

harvest-dismissed
-----------------

Scan PR review comments and append dismissed findings to a JSONL store.

.. code-block:: text

   reviewmind harvest-dismissed
       --repo OWNER/NAME
       --github-token TOKEN
       [--pr-number N | --max-prs 50]
       [--out .reviewmind/dismissed.jsonl]

When ``--pr-number`` is set, harvests only that PR. Otherwise iterates
the ``--max-prs`` most-recently-updated closed PRs.

harvest-accepted
----------------

Scan PRs for applied suggestion blocks and append to a JSONL store.

.. code-block:: text

   reviewmind harvest-accepted
       --repo OWNER/NAME
       --github-token TOKEN
       [--pr-number N | --max-prs 50]
       [--out .reviewmind/accepted.jsonl]

A PR is considered to have accepted suggestions when any of its commits
has a message starting with ``Apply suggestion(s) from code review``.
Every review comment on that PR that contains a ```suggestion``` block
is kept.

adversarial-eval
----------------

Run a prompt-injection corpus against the configured backend and record
every per-call outcome to SQLite. Emits **no** aggregate detection rate —
that is left to downstream SQL so the raw outputs remain auditable.

.. code-block:: text

   reviewmind adversarial-eval
       --corpus PATH                # JSONL corpus (see seed.jsonl)
       --outcomes-path PATH         # SQLite output store
       [--backend {local,remote,openai,anthropic}]
       [--remote-url URL] [--remote-api-key TOKEN]
       [--openai-model NAME] [--openai-api-key TOKEN]
       [--anthropic-model NAME] [--anthropic-api-key TOKEN]
       [--max-new-tokens 4096]

Corpus format: one JSON object per line, conforming to
:class:`reviewmind.adversarial.AttackCase`. The bundled
``reviewmind/adversarial_corpus/seed.jsonl`` is a hand-authored seed
across four attack families (``direct_injection`` /
``encoded_payload`` / ``split_injection`` / ``role_hijack``); it is
**not** a benchmark.

The outcomes table schema:

.. code-block:: sql

   CREATE TABLE outcomes (
     id          INTEGER PRIMARY KEY AUTOINCREMENT,
     timestamp   REAL    NOT NULL,
     case_id     TEXT    NOT NULL,
     category    TEXT    NOT NULL,
     backend     TEXT    NOT NULL,
     model       TEXT    NOT NULL,
     bypassed    INTEGER NOT NULL,   -- 0/1
     detected    INTEGER NOT NULL,   -- 0/1
     success_markers_hit   TEXT NOT NULL,  -- comma-joined
     detection_markers_hit TEXT NOT NULL,
     output      TEXT    NOT NULL,
     error       TEXT
   );

Exit codes
----------

* ``0`` — success (including dry runs and zero-finding outcomes).
* ``1`` — runtime failure (network, GPU, parse error). When ``--gate-on``
  is active, the Check Run is patched to ``failure`` before propagating.
* ``2`` — argument-parsing or validation error from argparse.

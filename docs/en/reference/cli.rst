CLI reference
=============

Invoke the CLI either via the installed entry point or via the module::

   prthinker <subcommand> [options]
   python -m prthinker <subcommand> [options]

Global options
--------------

.. option:: --log-level {DEBUG,INFO,WARNING,ERROR}

   Default ``INFO``. Override with ``PRTHINKER_LOG_LEVEL``.

review-pr
---------

Fetch a PR diff, run the pipeline, post comment + review + gate.

.. code-block:: text

   prthinker review-pr
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
       [--marker '<!-- prthinker:summary -->']
       [--dry-run]

Notable flags:

* ``--dry-run`` — print the summary comment to stdout instead of posting
  it; also skips opening the Check Run.
* ``--marker`` — sentinel HTML comment used to upsert the PR comment.
  Override only if you need multiple reviewers in one repo.
* ``--exclude-globs`` — comma-separated fnmatch patterns; in
  ``--per-file`` mode, files matching any pattern are skipped.
  Cheap defence against wasting GPU minutes on IDE config, generated
  data, or large markdown changes. Env: ``PRTHINKER_EXCLUDE_GLOBS``.
* ``--target-file`` — when set, ``--per-file`` mode reviews only this
  exact diff path and skips every other file. Lets a CI matrix runner
  own a single file's review so each file gets its own job timeout;
  see :doc:`../guide/github-actions` for the matrix workflow. Env:
  ``PRTHINKER_TARGET_FILE``.
* ``--output-json`` — write a JSON-encoded partial ``ReviewResult`` to
  this path and skip posting to GitHub. Pair with ``--target-file`` in
  a matrix runner so each shard stashes its findings as an artifact
  for a later ``aggregate`` job to merge. Env:
  ``PRTHINKER_OUTPUT_JSON``.

Research-grade flags (opt-in, ``--inline-review`` required):

.. option:: --reply-to-author

   Read the PR author's replies to the most recent prthinker summary
   comment and inject them as a *Prior dialogue* block into the
   inline-findings prompt. Closes the loop so the next review does not
   silently repeat a finding the author already addressed. Env:
   ``PRTHINKER_REPLY_TO_AUTHOR``.

.. option:: --counterfactual

   After inline findings, run a counterfactual / mutation step that
   surfaces competing alternative implementations and a trade-off matrix
   for each *design-choice* finding. Skipped findings that are clear
   bugs / nits. Adds one extra backend call per file. Env:
   ``PRTHINKER_COUNTERFACTUAL``.

.. option:: --provenance

   Ask the model to cite the RAG rule / accepted-example / diff line(s)
   that informed each finding, and surface those citations as an
   *Audit trail* footer under the per-file block. Out-of-range citations
   are silently dropped; a bad citation never drops a real finding.
   Env: ``PRTHINKER_PROVENANCE``.

.. option:: --walkthrough

   Add a per-file ``WalkthroughStep`` that writes a short two-to-four
   sentence narrative of what the file's change does and why, pinned to
   the top of that file's block — the inference-backed counterpart to the
   model-free commit-message PR overview. It only describes the change
   (no review or criticism), depends on nothing but the diff, and so runs
   with or without ``--inline-review``. Env: ``PRTHINKER_WALKTHROUGH``.

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
   at ``--diff-cache-path`` (default ``.prthinker/diff-cache.sqlite``),
   keyed on ``(pr_number, repo, file_path, hunk_sha256)`` — cross-PR
   isolated. Env: ``PRTHINKER_DIFF_SINCE_LAST``.

.. option:: --verify-suggestions

   Clone the workdir into a disposable sandbox, apply each finding's
   ``suggestion`` block at the right line range, and run
   ``--verify-cmd`` (default ``pytest -x``) under ``--verify-timeout``
   (default 60s). Badges each finding ``[verified]`` / ``[FAILED]`` /
   ``[skipped]`` / ``[error]``. Original repo never mutated. Env:
   ``PRTHINKER_VERIFY_SUGGESTIONS``.

.. option:: --api-consistency

   When the diff touches both backend (``.py``) and frontend (``.ts`` /
   ``.tsx`` / ``.js`` / ``.jsx``) files, run an extra step that
   surfaces *cross-file* drift (renamed fields, removed routes, type
   changes). Skipped silently on single-language PRs. Env:
   ``PRTHINKER_API_CONSISTENCY``.

.. option:: --pr-classify

   Classify the PR (``bugfix`` / ``feature`` / ``refactor`` / ``docs``
   / ``chore`` / ``unknown``) from diff + title + body, then adapt
   review depth: docs PRs skip inline findings; bugfix PRs use a
   focused prompt with smaller budget. Env:
   ``PRTHINKER_PR_CLASSIFY``.

.. option:: --reproducibility-check

   Run the inline-findings step twice per file (identical prompt;
   non-zero temperature gives a second sample) and label each finding
   ``stable`` / ``low`` based on cross-pass match. Backend-agnostic
   uncertainty proxy. Env: ``PRTHINKER_REPRODUCIBILITY_CHECK``.

.. option:: --dep-upgrade-check

   Detect dependency version bumps in lock files
   (``requirements.txt`` / ``pyproject.toml`` / ``package.json``) and
   ask the model whether breaking changes between the old and new
   versions affect this codebase's actual usage. Env:
   ``PRTHINKER_DEP_UPGRADE_CHECK``.

.. option:: --personas <list>

   Comma-separated list of review personas (``security``,
   ``performance``, ``readability``, ``api_stability``,
   ``maintainability``) — or ``all`` for every persona. Each persona's
   prompt restricts the model to its lens; a conflict-finder step then
   surfaces where the personas disagree. Empty (default) disables.
   Env: ``PRTHINKER_PERSONAS``.

.. option:: --risk-weighted

   Compute a per-file risk score from churn (``git log`` over the
   default 90-day window), complexity (line count at HEAD), and bug
   history (commit messages matching ``fix:`` / ``bug`` / ``revert``).
   Scales ``max_findings_per_file`` proportional to the score between
   ``floor`` (default 2) and ``ceiling`` (default ``2 ×
   base_budget``). Set ``--risk-workdir`` to point at the git repo.
   It also surfaces a collapsible "high-risk files" note (the score and
   its churn / bug-fix / line-count breakdown) in the summary, so the
   reviewer sees which files history says are most likely to break.
   Env: ``PRTHINKER_RISK_WEIGHTED``.

.. option:: --diff-entropy

   Compute the diff's size + dispersion entropy and surface a
   "Consider splitting this PR" warning at the top of the comment
   when the score crosses the ``bomb`` threshold. Pure local CPU; no
   backend call. Env: ``PRTHINKER_DIFF_ENTROPY``.

.. option:: --review-order

   Add a "Suggested review order" note that ranks the changed files
   most-depended-upon first (using the repo knowledge graph's import
   edges), with the most foundational file marked "start here", so the
   reviewer reads base changes before their call sites. Best-effort:
   omitted when the KG store is absent. Env: ``PRTHINKER_REVIEW_ORDER``.

.. option:: --change-map

   Embed a small Mermaid graph of the import edges *between the changed
   files* (from the repo knowledge graph), so the structure of the
   change is visible inline. GitHub renders the ```mermaid`` block
   natively. Omitted when the change has no internal import edges.
   Env: ``PRTHINKER_CHANGE_MAP``.

review-file
-----------

Run the pipeline against a local file or stdin.

.. code-block:: text

   prthinker review-file PATH
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
       [--max-new-tokens 8192]
       [--steps a,b,c]
       [--output-dir PATH]

``PATH`` may be ``-`` to read the diff from stdin.

``--output-dir`` writes each step's raw text output to disk
incrementally — useful for batch experiments and debugging long runs.

``--steps`` accepts a comma-separated list of step names; empty (the
default) runs every registered step.

triage
------

Run every no-model orientation signal over a diff and print the
non-empty blocks. No backend is loaded, so it is instant and runs on the
runner profile alone — a pre-push check on a laptop, or a GPU-free CI
gate that catches conflict markers, Trojan-Source glyphs, swallowed
exceptions, renames, deletions, mode changes, large pastes, formatting-
only churn, coverage gaps, debug leftovers, and deferred-work markers
before a full review is scheduled.

.. code-block:: text

   prthinker triage
       [--diff-file PATH | --staged | --against REF]
       [--exit-nonzero-on-signal]

The diff is read from stdin by default; ``--diff-file`` reads it from a
file, ``--staged`` runs ``git diff --cached``, and ``--against REF`` runs
``git diff REF`` (e.g. ``origin/main``). With
``--exit-nonzero-on-signal`` the command exits 1 when any signal fires,
so it can gate a CI step; otherwise it always exits 0 (advisory).

.. code-block:: bash

   git diff origin/main | prthinker triage
   prthinker triage --staged --exit-nonzero-on-signal

The signal set is the same one the live PR comment renders below its
digest; see :doc:`../concepts/research-extensions` for what each block
detects.

aggregate
---------

Merge partial-review JSONs produced by ``review-pr --output-json``
runners and post a single summary + inline review + gate close.
Counterpart to the matrix workflow documented in
:doc:`../guide/github-actions`.

.. code-block:: text

   prthinker aggregate
       --repo OWNER/NAME
       --pr-number N
       --github-token TOKEN
       --aggregate-from DIR
       [--marker '<!-- prthinker:summary -->']
       [--inline-review] [--judge]
       [--gate-on {none,warning,error}]
       [--platform {github,gitlab}]
       [--dry-run]

The aggregator walks ``--aggregate-from`` recursively for ``*.json``
files (so the typical ``actions/download-artifact`` layout with one
folder per matrix iteration works without extra wiring), deserialises
each partial back into a ``ReviewResult``, dedupes ``per_file`` entries
by path (last-write-wins on duplicates), and merges
``inline_findings`` + ``step_outputs`` + ``rag_docs`` across shards.
The post-merge path is identical to ``review-pr``'s — same comment
upsert marker, same ``submit_inline_review`` event mapping (with
``--judge`` aggregation when enabled), same gate close.

If the directory holds zero JSONs (e.g. every matrix shard skipped
because the backend was unreachable), the command logs a warning and
exits 0; the workflow's fallback shell step posts a "skipped" notice
under the same marker.

Env equivalents: ``PRTHINKER_AGGREGATE_FROM`` (input dir),
``PRTHINKER_COMMENT_MARKER`` (marker), ``PRTHINKER_GATE_ON`` (gate
floor). The standard ``GITHUB_REPOSITORY``, ``PRTHINKER_PR_NUMBER``,
and ``GITHUB_TOKEN`` cover the rest.

pr-summary
----------

Generate a Copilot-style PR summary from the PR title, description,
commit messages, and diff, then upsert it as a dedicated PR comment
under its own ``<!-- prthinker:pr-summary -->`` marker (separate from
the review summary). Designed to run *before* the per-file review — the
``enumerate`` job in :doc:`../guide/github-actions` invokes it — so
reviewers get an at-a-glance brief while the slower review runs.

.. code-block:: text

   prthinker pr-summary
       --repo OWNER/NAME            # or $GITHUB_REPOSITORY
       --pr-number N                # or $PRTHINKER_PR_NUMBER
       --github-token TOKEN         # or $GITHUB_TOKEN
       [--backend {local,remote,openai,anthropic}]
       [--remote-url URL] [--remote-api-key TOKEN]
       [--platform {github,gitlab,gitea}]
       [--dry-run]

It reconciles what the author *wrote* (title, body, commit subjects)
against what the diff *does* and is asked to flag any discrepancy. The
output is GitHub-flavoured Markdown with ``### Overview``,
``### Key changes``, ``### Areas to review`` and ``### Notes`` sections.

Best-effort by design: generation goes through the injected backend and
is retried a few times on a transient fault (a 5xx, a dropped
connection, an empty reply); on persistent failure it logs a warning and
exits 0, so a flaky backend never blocks the review matrix. ``--dry-run``
prints the rendered comment to stdout instead of posting it.

Env equivalents: ``PRTHINKER_BACKEND`` / ``PRTHINKER_REMOTE_URL`` /
``PRTHINKER_REMOTE_API_KEY`` select the backend; ``GITHUB_REPOSITORY``,
``PRTHINKER_PR_NUMBER`` and ``GITHUB_TOKEN`` cover the target.

harvest-dismissed
-----------------

Scan PR review comments and append dismissed findings to a JSONL store.

.. code-block:: text

   prthinker harvest-dismissed
       --repo OWNER/NAME
       --github-token TOKEN
       [--pr-number N | --max-prs 50]
       [--out .prthinker/dismissed.jsonl]

When ``--pr-number`` is set, harvests only that PR. Otherwise iterates
the ``--max-prs`` most-recently-updated closed PRs.

harvest-accepted
----------------

Scan PRs for applied suggestion blocks and append to a JSONL store.

.. code-block:: text

   prthinker harvest-accepted
       --repo OWNER/NAME
       --github-token TOKEN
       [--pr-number N | --max-prs 50]
       [--out .prthinker/accepted.jsonl]

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

   prthinker adversarial-eval
       --corpus PATH                # JSONL corpus (see seed.jsonl)
       --outcomes-path PATH         # SQLite output store
       [--backend {local,remote,openai,anthropic}]
       [--remote-url URL] [--remote-api-key TOKEN]
       [--openai-model NAME] [--openai-api-key TOKEN]
       [--anthropic-model NAME] [--anthropic-api-key TOKEN]
       [--max-new-tokens 4096]

Corpus format: one JSON object per line, conforming to
:class:`prthinker.adversarial.AttackCase`. The bundled
``prthinker/adversarial_corpus/seed.jsonl`` is a hand-authored seed
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

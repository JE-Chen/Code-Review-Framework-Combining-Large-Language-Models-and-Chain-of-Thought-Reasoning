CI signals and the pre-merge gate
=================================

Two features turn the reviewer from "leave-a-comment" into "act on this
data": **CI failure signals** (input side) and the **Check Run gate**
(output side).

CI failure signals
------------------

When ``--include-ci-signals`` is set, the runner fetches the
already-completed Actions runs for the PR head SHA, picks the failed
ones, and pulls the tail of each failed job's log. These are formatted
into a fenced block and **prepended to the diff** before the pipeline
runs:

.. code-block:: text

   <!-- CI Failure Signals -->
   # CI Failure Signals

   These are failed jobs from the latest CI run on this PR head.
   Correlate findings with the failures below when applicable; do NOT
   invent failures not present here.

   ## CI / test-python (failure)

   ```
   E   AssertionError: expected 1, got 2
   E       at tests/test_auth.py:42
   ...
   ```

   <!-- End CI Failure Signals -->

   diff --git a/auth.py b/auth.py
   ...

The model now has runtime context. Findings can correlate flagged lines
with concrete test failures ("this change to ``auth.py:42`` matches the
``test_auth`` regression above").

Tunables
~~~~~~~~

* ``--ci-signal-max-jobs N`` — cap on number of failed jobs included.
  Default ``5``. Each job's logs are processed independently.
* ``--ci-signal-tail-chars N`` — characters of log to keep per job
  (from the end). Default ``4000``. The model rarely uses more than the
  last few hundred characters effectively.

Both knobs trade prompt-token budget against signal coverage.

Permissions
~~~~~~~~~~~

The Actions API needs ``actions: read`` permission. The bundled workflow
declares it; if you fork, keep it.

Timing
~~~~~~

The default ``pull_request`` trigger fires **immediately on push**,
before any CI runs. The runner takes whatever CI signals already exist
for the head SHA at the moment it runs — typically nothing on first
push, then the previous run's logs on subsequent pushes.

If you want the reviewer to *wait* for CI:

.. code-block:: yaml

   on:
     workflow_run:
       workflows: ["CI"]
       types: [completed]

In ``workflow_run`` mode, fetch the PR number from the run payload — see
the bundled comments in ``prthinker.yml``.

The pre-merge Check Run gate
----------------------------

The ``--gate-on`` flag controls a dedicated Check Run named
``prthinker`` on the PR head commit. The CLI:

1. ``POST /check-runs`` at the start of the review with
   ``status: in_progress``.
2. After the pipeline completes (including the dismissed filter),
   counts surviving inline findings by severity.
3. ``PATCH /check-runs/:id`` with ``status: completed`` and a
   ``conclusion`` derived from the count vs the configured floor.

Conclusion logic
~~~~~~~~~~~~~~~~

================== =================================== ========================
``--gate-on``       Concludes as ``failure`` when…        Concludes as ``success``
================== =================================== ========================
``none``            never                                always
``error``           ``error`` count ≥ 1                    otherwise
``warning``         ``error`` or ``warning`` count ≥ 1    otherwise (only ``info``)
================== =================================== ========================

``info``-severity findings never trip the gate. They exist for nits the
team may or may not care about — gating on them creates merge friction.

Wiring it into branch protection
--------------------------------

1. Run at least one PR with ``PRTHINKER_GATE_ON=error`` so the Check Run
   appears.
2. **Settings → Branches → branch protection rule** for your default
   branch.
3. Enable **Require status checks to pass before merging** and add
   ``prthinker`` to required checks.

After that, any PR with surviving error-severity findings cannot be
merged. The author sees the gate result inline (the Check Run's
summary contains the breakdown of error/warning/info counts).

Failure modes
~~~~~~~~~~~~~

* **Pipeline crash** — the CLI's exception handler PATCHes the Check Run
  to ``conclusion: failure`` with ``title: "Reviewer crashed"`` so the
  PR never gets stuck with a perpetually-running check.
* **Empty diff** — the reviewer skips the run entirely; no Check Run is
  opened, no comment posted.
* **Findings filtered to zero** — gate concludes ``success``. The
  summary comment still shows the empty result so authors know the
  reviewer ran.

Posting the review: comments and inline suggestions
---------------------------------------------------

With ``--pr-overview`` (env ``PRTHINKER_PR_OVERVIEW``) the summary opens
with a model-free **What this PR does (preliminary)** block, built
deterministically from the PR's commit messages and changed files: a
file/directory/extension breakdown, a conventional-commit type tally
(``feat (3) · fix (1)``), and the commit-subject list. It is context, not
a verdict — it answers "what changed" while the digest below answers "is
it any good" — and like the digest it is pinned to the upserted part-1
comment and refreshed on every review.

``--impact-map`` (env ``PRTHINKER_IMPACT_MAP``) adds an **Impacted areas**
note listing the *downstream importers* of the changed files — files that
import a changed module but were not themselves touched — read from the
repo knowledge graph (``repo-kg.sqlite``). It flags ripple effects the
diff alone does not show. Matching is heuristic (module name vs import
target), so it is a hint, and it degrades silently when the KG is absent.

Every per-file summary opens with a **Review at a glance** digest — a
plain-language status (🔴 changes requested / 🟡 review suggested /
🔵 minor notes / ✅ looks good), the finding counts by severity, the
reviewed / with-findings / clean file split, and the *hotspot* files
that carry the most findings. It is pinned to the top of the upserted
part-1 comment, so it is rewritten in place on every re-review and always
reflects the latest run.

When any error-severity findings exist, a **🚨 Must fix** list is pinned
above everything else — the error findings as one-liners with deep links,
so the blocking issues are unmissable without expanding a single block.
Files that contain errors then render expanded (``<details open>``) while
clean / warning / info files stay collapsed, and each file block surfaces
a ``Signal:`` line tallying sandbox-verified suggestions (``✓``) and
low-reproducibility findings (``⚠️``) so high-trust findings stand out.

The per-file blocks are ordered most-severe first (files with errors,
then warnings, then info, ties broken by finding count), each badged with
severity icons (``🔴2 🟡1``) instead of a bare count. ``--summary-table``
(env ``PRTHINKER_SUMMARY_TABLE``) swaps the collapsible blocks for one
compact ``severity | location | finding`` table — faster to scan when a
PR has many findings. On GitHub every
file name — in the hotspots line and the block headers — is a deep link
straight to that file's first finding in the Files-changed tab (set
``PRTHINKER_PR_FILES_URL`` for GitHub Enterprise hosts).

With ``--review-delta`` (env ``PRTHINKER_REVIEW_DELTA``) the digest adds a
``Since last review: +2 new · 3 resolved · 5 carried`` line. Findings are
fingerprinted by ``(path, severity, comment)`` — not line number, which
shifts between pushes — and the set is persisted in the per-PR state
(``--delta-state``, default ``.prthinker/pr-state/findings-fp.json``) that
CI already restores across pushes, so a re-push shows progress at a
glance. The same line appends ``💬 N author reply(ies)`` when the author
has responded since the last review, and the findings that disappeared
are listed struck-through in a collapsed **✅ Resolved since last review**
block at the top — so authors get credit and reviewers see exactly what
was addressed.

A full per-file review can run to hundreds of KB — far past GitHub's
65 536-character limit on a single comment. Rather than truncate, the
summary is **paginated across multiple comments**: it is split between
whole file blocks (never inside one), and every page after the first
carries a ``Part k/N`` label. Across re-pushes the pages are reconciled
by marker — existing comments are updated in place, extra pages are
created, and any leftover pages from a longer previous run are deleted,
so stale parts never linger. Platforms other than GitHub fall back to a
single comment (the overflow stays in the job logs).

With ``--findings-only`` (env ``PRTHINKER_FINDINGS_ONLY``) the summary
lists *only* files that have findings; clean files are collapsed into a
``N file(s) reviewed with no findings — hidden`` line, and a PR with zero
findings collapses to a one-line ``✅ No findings`` confirmation instead
of a full empty result. On a large but mostly-clean PR this often brings
a multi-page summary back down to a single comment.

``--hide-info`` (env ``PRTHINKER_HIDE_INFO``) omits ``info``-severity
findings from the rendered summary — the count badges, the at-a-glance
tally, and the hotspot ranking all ignore them, and a file whose only
findings are info is treated as clean. This is display-only: the inline
review on the diff and the merge gate still see every finding.

``--summary-min-confidence`` (env ``PRTHINKER_SUMMARY_MIN_CONFIDENCE``, a
0–1 float) additionally drops findings whose model confidence is below
the floor; findings without a confidence score are kept (drop nothing on
unknown). Also display-only.

With ``--pr-labels`` (env ``PRTHINKER_PR_LABELS``) the reviewer also
applies two managed labels to the PR — a size bucket
(``prthinker/size-xs`` … ``size-xl``, by reviewed file count) and a
status (``prthinker/changes-requested`` / ``review-suggested`` /
``clean``) — so the PR list is scannable without opening each one. Only
labels under the ``prthinker/`` prefix are reconciled across runs;
human-applied labels are never touched.

Inline suggestions — the one-click *Apply suggestion* blocks on the
diff — are posted as a separate PR review. The new review is submitted
**before** the previous run's inline comments are dismissed, and the
dismissal excludes the review just posted. Posting before dismissing
means a rejected submission (GitHub 422s the *whole* review if any
single comment targets a line outside the diff hunks) leaves the prior
run's suggestions intact instead of wiping them ahead of a failed
re-post.

With ``--check-annotations`` (env ``PRTHINKER_CHECK_ANNOTATIONS``) the
gate's Check Run also carries per-line annotations (one per finding,
``failure`` / ``warning`` / ``notice`` by severity). They render on the
Files-changed and Checks tabs and are a robust *parallel* channel to the
inline review: a single bad line is dropped individually rather than
422-ing the whole batch, and GitHub appends them across requests so a
review with more than 50 findings is sent over several updates.

Other output channels
~~~~~~~~~~~~~~~~~~~~~~~

The review is not confined to the PR conversation. The aggregate job
writes the merged findings as **SARIF** (``--sarif-out`` /
``PRTHINKER_SARIF_OUT``) and the workflow uploads it with
``github/codeql-action/upload-sarif``, so findings also appear in the
**Security tab** and as native diff annotations — dismissable and
deduped by GitHub across PRs. Separately, when ``$GITHUB_STEP_SUMMARY``
is set (every Actions run), the at-a-glance summary is appended to the
**run summary page**, visible straight from the Checks tab without
opening the PR.

Review in progress
~~~~~~~~~~~~~~~~~~~

A GPU review of a large PR takes minutes, during which the PR shows
nothing. The ``post-status`` command upserts a ``⏳ Review in progress…``
placeholder under the summary marker; the CI ``enumerate`` job runs it
first (best-effort), and the later aggregate run reconciles it into the
real summary through the same marker — so reviewers see the review has
started instead of an empty PR.

Combining CI signals + gate
---------------------------

The two features compose: CI signals make findings more likely to
include genuine bugs (because the model can ground its review in
observed failures), the gate then turns those higher-quality findings
into hard merge blockers.

For a stricter setup, also enable ``--rules-dir`` (team-specific rules)
so the model knows what your team considers an error vs a warning.

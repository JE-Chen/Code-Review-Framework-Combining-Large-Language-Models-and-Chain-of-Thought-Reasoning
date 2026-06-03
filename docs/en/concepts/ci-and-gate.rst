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

Inline suggestions — the one-click *Apply suggestion* blocks on the
diff — are posted as a separate PR review. The new review is submitted
**before** the previous run's inline comments are dismissed, and the
dismissal excludes the review just posted. Posting before dismissing
means a rejected submission (GitHub 422s the *whole* review if any
single comment targets a line outside the diff hunks) leaves the prior
run's suggestions intact instead of wiping them ahead of a failed
re-post.

Combining CI signals + gate
---------------------------

The two features compose: CI signals make findings more likely to
include genuine bugs (because the model can ground its review in
observed failures), the gate then turns those higher-quality findings
into hard merge blockers.

For a stricter setup, also enable ``--rules-dir`` (team-specific rules)
so the model knows what your team considers an error vs a warning.

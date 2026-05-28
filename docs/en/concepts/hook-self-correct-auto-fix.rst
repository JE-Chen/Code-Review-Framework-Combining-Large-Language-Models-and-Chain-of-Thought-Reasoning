Pre-commit hook, self-correct, and auto-fix
============================================

Three additions that close the loop between prthinker and the
developer's workflow.

Pre-commit hook (``prthinker hook``)
-------------------------------------

A new subcommand reads ``git diff --cached``, runs the per-file
pipeline, and exits with a non-zero code when at least one finding at
the configured severity floor survives. Combined with the
`pre-commit <https://pre-commit.com>`_ framework, prthinker becomes
the fourth touchpoint alongside CI, IDE (via MCP) and the manual CLI:

.. code-block:: yaml

   # .pre-commit-config.yaml in a consumer repo
   repos:
     - repo: https://github.com/<your-org>/prthinker
       rev: v0.1.0
       hooks:
         - id: prthinker
           env:
             PRTHINKER_BACKEND: openai
             PRTHINKER_OPENAI_MODEL: gpt-4o-mini

The two hook variants in ``.pre-commit-hooks.yaml``:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - hook id
     - exit semantics
   * - ``prthinker``
     - Exits 1 on any error-severity finding (commit blocked). Override
       via ``--block-on warning`` or ``--block-on none``.
   * - ``prthinker-advisory``
     - Always exits 0; findings printed to stderr only. Useful as a
       soft introduction before flipping branch protection on.

Cache + telemetry stack identically here, so a clean commit that
re-runs the hook is a near-instant cache hit.

When NOT to use
~~~~~~~~~~~~~~~

* If your project commits frequently with small WIP changes, the hook
  latency stacks up. Use ``prthinker-advisory`` instead, or keep the
  hook only at ``pre-push`` stage.
* If teammates work without API access, only enable the hook on the
  branches your CI also reviews — otherwise you split the team into
  "hook works" and "hook doesn't".

Self-correct (``--self-correct``)
---------------------------------

After the ``inline_findings`` step produces a JSON array and the
dismissed filter has drained known repeats, the model is asked once
more: "Re-read these findings as a busy senior reviewer; which are
noise / duplicate / over-picky?" The runner drops the indices the
model flags before the inline review is posted.

The prompt :data:`codes.run.CoT_Prompts.finding_self_review.FINDING_SELF_REVIEW_TEMPLATE`
defines five concrete noise patterns (duplicate, over-picky,
speculative, tautological, out-of-scope) and four
keep-it patterns (genuine correctness / security, maintainability with
a concrete fix, subtle bug, team-rule violation). The model returns:

.. code-block:: text

   {
     "drop": [<1-based index>, ...],
     "reasons": ["...", ...]
   }

Safe-failure posture
~~~~~~~~~~~~~~~~~~~~

The parser in :mod:`prthinker.self_review` is intentionally permissive:
malformed output yields an **empty drop set** (no findings lost), not a
"drop everything" set. The asymmetry is deliberate — a wrongly-posted
finding is recoverable; a silently-dropped real bug is not.

Cost
~~~~

One extra backend call per file, regardless of finding count. With
``--cache`` enabled and a stable PR, this becomes a single cold call
followed by hits on every subsequent run.

Auto-fix draft PR (``--auto-fix-threshold``)
--------------------------------------------

When the number of surviving ``warning``-severity findings with a
``suggestion`` block reaches the threshold, the runner:

1. Checks out a new branch ``auto-fix/prthinker-pr-<N>``.
2. For each affected file, applies the suggestions bottom-up so earlier
   line numbers stay valid. Overlapping edits are resolved by
   first-come priority — the second of any two conflicting edits is
   skipped and reported.
3. Commits with a single deterministic message.
4. Pushes the branch (``--force-with-lease`` so re-runs are safe).
5. Opens a **draft** PR pointed at the original PR's base branch, with
   a body that summarises applied / skipped counts and lists changed
   files.

The original PR keeps its own inline review; the auto-fix PR is a
separate, mergeable artifact. The author reviews the diff and either
merges it back into the source branch or closes it.

Severity gating
~~~~~~~~~~~~~~~

Only ``warning``-severity suggestions are auto-applied. ``error``
findings stay as inline comments — the principle is that errors need
human judgment about *whether* the suggested fix is the right one,
even when the patch itself looks valid. ``info`` findings already had
their ``suggestion`` field stripped by the sanitizer at parse time.

Conflict detection
~~~~~~~~~~~~~~~~~~

The pure transform :func:`prthinker.auto_fix.apply_suggestions_to_text`
returns a :class:`prthinker.auto_fix.ConflictReport` with two lists:
``applied`` (edits that made it in) and ``skipped`` (edits that
overlapped a kept edit, with the blocking edit identified). The
detection sorts edits by ``(start, end, finding_index)`` and walks once
in order; first-come wins. This is unit-testable without git — see
``tests/test_auto_fix.py``.

When NOT to use
~~~~~~~~~~~~~~~

* If your CI does not authenticate the bundled ``GITHUB_TOKEN`` to push
  branches (e.g. fork PRs), the push step fails. Auto-fix is most
  reliable on same-repo PRs.
* If the team relies on signed commits, auto-fix's generated commit
  will not be signed by default. Either sign in CI, or disable for
  branches that require signed commits.

Composition with the other features
-----------------------------------

The three additions stack with the rest of the pipeline without
special-casing:

* **hook ↔ cache**: hook re-runs hit the same cache as CI; identical
  diffs cost zero tokens.
* **self-correct ↔ telemetry**: the extra backend call is recorded
  like any other ``generate`` invocation, so cost shows up under the
  same ``(backend, model)`` key in ``prthinker stats``.
* **auto-fix ↔ gate**: the gate is evaluated *before* auto-fix runs,
  so the original PR's Check Run reflects the un-fixed state. After
  the author merges the auto-fix PR back, the next push re-triggers
  the gate on the corrected diff.
* **auto-fix ↔ judge**: judge verdict is set on the original PR; the
  auto-fix PR is created independently and does not itself run
  prthinker (it would loop).

CLI flags summary
-----------------

.. list-table::
   :header-rows: 1
   :widths: 35 30 35

   * - CLI flag
     - Env var
     - Default
   * - ``hook`` subcommand
     - n/a (subcommand)
     - —
   * - ``--advisory`` (hook only)
     - ``PRTHINKER_HOOK_ADVISORY``
     - ``false``
   * - ``--block-on {none,warning,error}`` (hook only)
     - ``PRTHINKER_HOOK_BLOCK_ON``
     - ``error``
   * - ``--self-correct``
     - ``PRTHINKER_SELF_CORRECT``
     - ``false``
   * - ``--auto-fix-threshold N`` (review-pr)
     - ``PRTHINKER_AUTO_FIX_THRESHOLD``
     - ``0`` (disabled)
   * - ``--auto-fix-base-branch BRANCH`` (review-pr)
     - ``PRTHINKER_AUTO_FIX_BASE_BRANCH``
     - *(fetched from PR)*

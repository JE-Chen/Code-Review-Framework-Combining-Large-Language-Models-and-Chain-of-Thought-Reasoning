The CoT pipeline
================

The pipeline runs a chain of *review steps* against a code diff.
Each step produces a markdown blob; later steps may read earlier outputs
from the shared ``ReviewContext``. The default registry has five steps —
this five-step chain is the full (and deep-tier) behaviour; with
``--step-plan adaptive`` it is pruned per file (see below). Per-file
mode opts into a sixth step that emits structured findings.

Step sequence
-------------

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Step
     - What it produces
   * - ``first_summary``
     - A first-pass PR summary — what changed, why, risk areas.
   * - ``first_code_review``
     - Free-form review of the diff against the global rules.
   * - ``linter``
     - Style / formatting issues only.
   * - ``code_smell``
     - Maintainability and design concerns.
   * - ``total_summary``
     - Synthesis: reads all four prior outputs and the diff, issues a
       final verdict and merge recommendation.
   * - ``inline_findings``
     - *(per-file only)* Emits a JSON array of
       ``{line, severity, comment, suggestion?}`` items that the runner
       converts into inline GitHub review comments.

The first five are wrapped by ``build_global_rule_template`` so RAG
rules and per-repo rules are injected uniformly. ``inline_findings``
skips that wrap so the model is more likely to emit raw JSON. All prompt
templates ship with the package at ``prthinker/prompts/``, mirrored
byte-for-byte from the canonical ``codes/run/CoT_Prompts/`` corpus.

Three further prompt-backed steps exist only for reduced review depth
(see the next section):

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Step
     - What it produces
   * - ``compact_review``
     - Single-call substitute for the whole analysis chain — one prompt
       covers correctness, lint-level issues, code smells, and a brief
       conclusion instead of five model calls.
   * - ``unified_review``
     - Findings JSON plus a short analysis summary and verdict in ONE
       model call; the pipeline splits the payload back into the
       historical ``inline_findings`` / ``compact_review`` result keys.
   * - ``batch_findings``
     - The multi-file batch prompt for trivial files: several small
       diffs are reviewed in one call and the flat findings array,
       tagged by ``path``, is split back into per-file findings.

Adaptive step planning (``--step-plan adaptive``)
-------------------------------------------------

By default (``--step-plan full``) every file runs every configured
step. With ``--step-plan adaptive`` a pure, deterministic planner
(``prthinker.step_planner``) assigns each ``FileDiff`` one of four depth
tiers, looking only at the diff (size, file kind) and the per-file risk
score the pipeline already computes. Risk wins over size: a three-line
change to a historically fragile file is never trivial.

skip
   Machine-written files — lockfiles (``package-lock.json``,
   ``poetry.lock``, …), minified bundles, generated artifacts, and
   ``vendor/`` / ``node_modules/`` style vendored trees — plus
   whitespace-only reformatting. Zero model calls and zero retrieval,
   but the file still appears in the summary marked as skipped, so
   "skipped by policy" is visible rather than silent.

trivial
   Documentation / declarative-config suffixes (``.md``, ``.rst``,
   ``.json``, ``.yaml``, ``.toml``, …) or at most 5 changed lines. Only
   the output-producing steps survive (inline findings, walkthrough).
   Trivial files whose whole plan is the findings pass are **batched**:
   up to 6 files / 24 000 characters of diff per model call through the
   ``batch_findings`` prompt. The returned array is split back per file
   by its ``path`` tag through the same validating parser a single-file
   review uses, and each file's findings are cached individually so
   differential review still works per file.

standard
   Everything in between. One ``unified_review`` call returns the
   findings JSON plus a brief summary and verdict, split back into the
   historical ``inline_findings`` / ``compact_review`` result keys so
   findings parsing, reports, and gates are unchanged. With
   ``--counterfactual`` (which consumes the parsed findings) the
   standard tier keeps the two-call ``compact_review`` +
   ``inline_findings`` shape instead.

deep
   200 or more changed lines, or risk score ≥ 0.7 — the risk override
   applies regardless of size or file kind. Keeps the full five-step
   chain plus every configured extra step.

Reduced tiers also cap generation: 4096 new tokens for trivial, 8192
for standard; deep keeps the pipeline-wide budget. The chosen tier is
recorded in each file's ``step_outputs`` under the ``step_plan`` key,
so it travels with the review result into the serialized outputs and
reports and the depth decision stays auditable.

Two execution modes
-------------------

Single-pass
   One prompt sweep over the whole diff. Cheap, but the model only sees
   the file headers — it can't easily say *which line* something belongs
   to. No inline review.

Per-file
   The diff is split into one ``FileDiff`` per file, the pipeline runs
   per file, and each run optionally appends ``InlineFindingsStep`` to
   produce per-line ``InlineFinding`` records. The runner aggregates
   them, applies the dismissed filter, and posts a GitHub review.

Per-file is the production setup; the bundled GHA workflow enables it.

Diff parsing
------------

``prthinker.diff.parse_unified_diff`` splits the unified diff into
``FileDiff`` objects and tracks the set of *new-side* line numbers that
appear in each file. This set drives line validation: any
``InlineFinding`` pointing at a line outside the diff is dropped before
GitHub ever sees it. Comments on removed lines are rejected by GitHub
anyway, so dropping them client-side keeps the review API call clean.

Findings extraction
-------------------

The ``inline_findings`` step asks the model to output a JSON array. The
parser in ``prthinker.findings`` is intentionally lenient:

1. Strip optional Markdown fenced-code wrapping (``\`\`\`json … \`\`\```).
2. Find the outermost ``[ ... ]`` block.
3. Parse with ``json.loads``; on failure, fall back to per-object regex.
4. Validate each item against the ``InlineFinding`` Pydantic schema —
   drop malformed entries.
5. Drop items whose ``line`` is outside the file's diff lines.
6. *Sanitize* the ``suggestion`` field: drop it (but keep the textual
   comment) when:

   * severity is ``info`` (the prompt forbids suggestions for nits).
   * ``start_line > line``.
   * a multi-line suggestion's line count doesn't match the range.
   * ``start_line`` falls outside the diff.

A wrong suggestion is worse than no suggestion (reviewers may apply it
blindly), so the bar for keeping one is high.

The dismissed filter
--------------------

After parsing, an optional ``DismissedFilter`` removes findings whose
*comment text* is too similar to a stored dismissed example. See
:doc:`corpora` for the store shape.

Output channels
---------------

For each PR the reviewer writes through three channels:

* **Summary comment** — one PR conversation comment, upserted by sentinel
  marker so repeated runs do not spam. Per-file mode renders each file as
  a collapsible ``<details>`` block.
* **Inline review** — one ``POST /pulls/:n/reviews`` with each surviving
  finding as a separate comment. Suggestion blocks render as one-click
  *Apply suggestion* buttons.
* **Check Run** — opened in ``in_progress`` at start, completed with
  ``success`` or ``failure`` based on ``--gate-on`` and the surviving
  findings.

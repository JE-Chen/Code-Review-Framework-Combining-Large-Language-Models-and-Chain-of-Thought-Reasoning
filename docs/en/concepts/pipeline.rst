The CoT pipeline
================

The pipeline runs a fixed sequence of *review steps* against a code diff.
Each step produces a markdown blob; later steps may read earlier outputs
from the shared ``ReviewContext``. The default registry has five steps;
per-file mode opts into a sixth that emits structured findings.

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

The first five live in ``codes/run/CoT_Prompts/`` and are wrapped by
``build_global_rule_template`` so RAG rules and per-repo rules are
injected uniformly. ``inline_findings`` skips that wrap so the model is
more likely to emit raw JSON.

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

``reviewmind.diff.parse_unified_diff`` splits the unified diff into
``FileDiff`` objects and tracks the set of *new-side* line numbers that
appear in each file. This set drives line validation: any
``InlineFinding`` pointing at a line outside the diff is dropped before
GitHub ever sees it. Comments on removed lines are rejected by GitHub
anyway, so dropping them client-side keeps the review API call clean.

Findings extraction
-------------------

The ``inline_findings`` step asks the model to output a JSON array. The
parser in ``reviewmind.findings`` is intentionally lenient:

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

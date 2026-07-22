# AGENTS.md

Project-specific instructions for automated contributors. Read the existing top-level project
guide before changing production code, tests, deployment files, documentation, or Git history.

## Thesis and experiment work

- Treat `datas/Results/` as the primary evidence store. Every reported number must be reproducible
  from archived per-case output or a checked-in aggregation script.
- Treat `datas/Research_Data/` as the publication snapshot. When a completed result changes the
  paper, synchronize the raw outputs, aggregate results, reproducibility scripts, status files,
  and `MANIFEST.sha256` in the same work session.
- The 44-case reference issue set is model-derived, not a human gold standard. Use the wording
  "模型產生參考問題集" and preserve that limitation wherever coverage is discussed.
- Coverage and claim correctness use different counting units. Do not call their harmonic mean a
  standard classification F1 unless both measures are rebuilt from one confusion matrix.
- Separate completed results from active experiments. Active or stopped diagnostic batches belong
  in the research-data status files, not in the thesis results or conclusion.
- Retrieval enabled is not evidence that rules entered the prompt. Verify and archive the retrieved
  document count for every case.
- Keep experimental controls fixed across ablation groups: model weights, adapter state, precision,
  review steps, decoding mode, generation limit, and case order. Record the changed factor in a
  condition manifest.
- A client timeout must trigger the cancellation endpoint and wait for a terminal job state before
  the next case is submitted.
- For paired 44-case scores, report paired differences and a paired test. The current analysis uses
  a two-sided Wilcoxon signed-rank test with Holm correction across five dimensions.

## Manuscript handling

- Never edit a thesis `.docx` in place. Use the latest document as a read-only source and generate a
  new numbered version with a reproducible `python-docx` script.
- Run `paper/_check_rules.py` before and after editing. Regenerate a text dump and inspect every
  changed paragraph and table.
- Do not set Word's `w:updateFields` option. Updating all fields on open can trigger a misleading
  external-file warning when the document contains bibliography add-in fields. Retain internal
  TOC, PAGEREF, and SEQ fields, and update them manually in Word when required.
- Use formal Traditional Chinese. Do not include local paths, downloaded-file names, reviewer-file
  names, result-directory names, or drafting metadata in thesis prose.
- Do not mention unfinished comparison groups merely to say that they are absent. Add results only
  after generation, scoring, aggregation, and traceability checks are complete.
- Preserve the distinction among objective issue matching, model-judge scores, historical human
  ratings, and cross-study descriptive comparisons.
- Keep source documents immutable and confirm their SHA-256 after producing the new version.

## Current handoff

Read `paper/AGENT_HANDOFF.md` before resuming the thesis experiments or updating the manuscript.
That file records the completed evidence, current active batch, result locations, and update
checklist. Update the handoff when experiment state changes; do not place transient progress in this
root instruction file.




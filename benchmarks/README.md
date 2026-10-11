# Reproducible benchmark runs

The unified CLI supports conversion, deterministic scoring, and paired
ablation comparison:

```shell
prthinker benchmark convert export.jsonl cases.jsonl --dataset contextcrbench
prthinker benchmark run cases.jsonl run/ --backend openai --openai-model MODEL
prthinker benchmark score cases.jsonl run/outcomes.jsonl --output score.json
prthinker benchmark compare cases.jsonl baseline/outcomes.jsonl treatment/outcomes.jsonl --output ablation.json
```

Supported adapters include CodeFuse-CR-Bench, SWE-PRBench, ContextCRBench,
SWRBench, c-CRAB, CodeReviewQA, ContextBench, and CORE-Bench. Ground truth
remains metadata and is never included in model prompts. CodeReviewQA uses
choice accuracy; ContextBench/CORE-Bench use exact context-ID precision and
recall. Dataset licenses and official evaluators remain authoritative.

PRThinker keeps benchmark input, model output, and run metadata separate so
ground-truth comments cannot leak into the review prompt.

1. Download a public dataset at a pinned revision and record its URL, revision,
   license, and SHA-256 in the experiment log. Dataset files are intentionally
   not committed here.
2. Convert an export to canonical JSONL:

   ```shell
   python -m prthinker.benchmark_datasets source.jsonl cases.jsonl \
     --dataset swe-prbench
   ```

   `codefuse-cr-bench` is also accepted. The adapter recognizes common export
   fields and fails rather than silently creating a case with no diff.
3. Load cases with `prthinker.benchmark.load_cases`, run them through the chosen
   backend, then call `write_run_bundle`. Each run directory contains raw
   `outcomes.jsonl` and `manifest.json` with dataset/output hashes, Git commit,
   runtime, backend, model, seed, and generation parameters.

Never edit a completed run directory.
The bundle writer requires a new output directory (even an existing empty
directory is rejected). The CLI checks this before creating a backend. Bundles
also require unique dataset case IDs and one outcome per case in input order;
incomplete or misaligned results cannot be archived as a completed run.

Create a new run for every changed model,
prompt, dataset revision, or generation parameter. Scoring belongs in a
separate derived artifact and must retain both manifest hashes.

`benchmark score` reports micro precision/recall/F1 plus a seeded bootstrap
95% interval. `benchmark compare` requires identical case IDs and reports a
paired F1 delta with wins/ties/losses. Retrieval runs can be evaluated with
`prthinker retrieval-eval`; each JSONL record carries `retrieved`, `expected`,
`used`, and `cited_correct` arrays.

## Durable sessions and fixed studies

`benchmark run` now writes schema-version 2 archives with an exact input snapshot, per-case success/failed/unsupported outcomes, interruption state, actual retrieved-document count, and provider-reported usage (unknown values remain null). `benchmark validate DIRECTORY` verifies both hashes, counts and case order. Pass `--dataset-manifest` containing dataset, HTTPS url, revision, license, source_sha256, cases_sha256, and `--control-manifest` for fixed generation settings; `--review-pipeline` runs production per-file review. Without that flag, direct prompting is archived as its own execution condition.

`adversarial-benchmark run` uses the bundled versioned synthetic corpus; `score` reports marker proxies and explicit benign/attack denominators. Unsafe executed actions remain unknown. `ablation-study plan/run/compare` creates exactly 17 single-factor treatments and one control. Controls pin model_revision, adapter_state, precision, steps, decoding_mode, max_new_tokens. Database/workdir fixtures are isolated per condition; missing fixtures are unsupported rather than silently disabled. Objective paired differences use bootstrap intervals, rank effects, Wilcoxon tests and Holm correction.

Full model runs are deferred by request. Offline fixtures are test evidence, never publication results. The final release is blocked until `release-check release/evidence.json` verifies all required evidence. Detailed commands and integration contracts are in the three-language evaluation guide.

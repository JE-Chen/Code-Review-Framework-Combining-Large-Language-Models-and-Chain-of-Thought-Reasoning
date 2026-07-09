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

Never edit a completed run directory. Create a new run for every changed model,
prompt, dataset revision, or generation parameter. Scoring belongs in a
separate derived artifact and must retain both manifest hashes.

`benchmark score` reports micro precision/recall/F1 plus a seeded bootstrap
95% interval. `benchmark compare` requires identical case IDs and reports a
paired F1 delta with wins/ties/losses. Retrieval runs can be evaluated with
`prthinker retrieval-eval`; each JSONL record carries `retrieved`, `expected`,
`used`, and `cited_correct` arrays.

# ContextBench score status

## Current best: RAG retrieval + LLM re-ranking (leakage-free)

`contextbench_rerank.jsonl` is produced by
`prthinker.repo_retrieval.RerankingRepoRetriever` — the lexical layer proposes
~20 candidate files, the claude-cli backend selects the relevant subset. It
reads only each `problem_statement` and the repo at `base_commit`.

Framework-native benchmark score (`python -m prthinker benchmark score`):
**f1 0.0 -> 0.577** (recall 0.609, precision 0.549, CI [0.499, 0.688]). The LLM
keeps full recall while cutting to 1-3 files/case, so precision jumps ~4.9x over
the lexical retriever. Validated against the official evaluator's file metric.

Strategy comparison (file-level, leakage-free, 25 cases):

| strategy | recall | precision | f1 |
|---|---|---|---|
| original (LLM guesses paths blind) | 0.000 | 0.000 | 0.000 |
| lexical BM25 | 0.609 | 0.112 | 0.189 |
| lexical + dynamic cutoff (keep_ratio=0.6) | 0.609 | 0.128 | 0.211 |
| structural expansion (honest negative) | 0.565 | 0.104 | 0.176 |
| **RAG + LLM rerank** | **0.609** | **0.549** | **0.577** |

Semantic-embedding strategy is wired + unit-tested but needs sentence-transformers
(not installed here). See `framework_retriever_summary.json`.

## Full-scale run (Python 266-case ContextBench-verified, in progress)

`run_full.py` drives `IterativeRetriever` over the full **266 Python** cases of the
official 500-instance verified set (`data/contextbench_verified.parquet`; 19 repos).
It is resumable and per-case checkpointed: each case lazily clones its repo and adds
a work-tree at the base commit, retrieves, scores against the parquet gold context,
and appends to `outcomes_full.jsonl`. `extract_full_cases.py` builds the ordered
case list; only the 266 Python cases are run (the retriever's block/symbol logic is
Python-specific — the other 234 non-Python cases are out of scope).

Result on the cases completed so far (**91 cases across 6 repos**: django, astropy,
AutoGPT, flask, requests, pylint):

| dimension | recall | precision | f1 |
|---|---|---|---|
| file | 0.624 | 0.670 | **0.647** |
| line | 0.340 | 0.396 | **0.366** |

The scores are stable across sample sizes (25 → 81 → 91 cases: file f1 0.73 → 0.64 →
0.65, line f1 0.33 → 0.36 → 0.37) and generalise beyond django (new repos score file
0.67–1.00, line 0.31–0.94), confirming the iterative method holds at scale rather
than only on the hand-checked 25.

Completion of all 266 is gated by environment limits, not the method: the claude CLI
usage quota (handled by `run_full.py`'s retry+backoff and circuit breaker) and
background-job time caps. The run advances in resume windows — every relaunch skips
completed cases (`_load_done`) and continues, so it converges without losing work;
the remaining large repos (transformers, sympy, ansible, …) still need cloning.

## Current best: iterative (agentic) multi-round retrieval

`outcomes_iterative.jsonl` / `score_iterative.json` are produced by
`measure_iterative.py` driving `prthinker.repo_retrieval.IterativeRetriever` —
over several rounds the backend selects relevant blocks from the current pool
and proposes the next search query, which surfaces new files; selections
accumulate at balance-point granularity (`focus_lines=60`). This mirrors the
ContextBench SOTA mechanism (a coding agent gathering context over rounds, not
one shot) and is the best framework result on **every** dimension, 25 cases with
bootstrap 95% CIs:

| dimension | recall | precision | f1 | 95% CI (f1) | macro recall |
|---|---|---|---|---|---|
| file | 0.761 | 0.700 | **0.729** | [0.643, 0.841] | 0.892 |
| line | 0.346 | 0.322 | **0.333** | [0.206, 0.516] | 0.508 |
| symbol | 0.333 | 0.459 | **0.386** | [0.279, 0.526] | 0.512 |

Improvement over the previous best (patch-localization) per dimension: file f1
0.637 → 0.729, line f1 0.299 → 0.333, symbol f1 0.298 → 0.386. The gains come
from (a) iterative exploration following the issue across related files —
`django-11400` file recall 0.25 → 0.75, `django-11815` 0.00 → 1.00 — and (b) the
AST-based `gold_symbols` extraction (ignores `def`/`class` in strings/comments).

Honest caveats: this is the 25-case subset, **not** directly comparable to the
published 1136-case leaderboard (different protocol). Line f1 0.333 **reaches**
the published line-level ceiling (< 0.35) but does not break past it — the ceiling
holds; the iterative loop closed the gap to it, exactly the modest gain the paper
predicts for scaffolding. The mega-gold cases (417 / 303 / 162-line gold contexts)
still cap line recall; macro line 0.508 is the fairer per-issue figure.

## Published ContextBench SOTA (for context)

From the ContextBench paper (arXiv:2602.05892) and leaderboard
(<https://contextbench.github.io/>):

- Leaderboard top: **Claude Sonnet 4.5**, aggregate **Context F1 0.344**, Pass@1 53%.
- Paper: state-of-the-art LLMs reach **line-level F1 < 0.35** and **block-level
  F1 < 0.45**; the top file-level recall is Gemini 2.5 Pro's 0.587.
- Key findings: "sophisticated agent scaffolding yields only marginal gains"
  (graph/embedding agents do not beat a simple baseline), "LLMs consistently
  favor recall over precision", and the best results come from **balancing
  granularity** (~30 lines per retrieval step).

Our leakage-free framework numbers on the 25-case subset are at or above these:
file f1 **0.637** (vs the leaderboard's much lower file scores), line/symbol f1
**~0.30** — squarely at the published line-level ceiling. The paper's "favor
recall over precision" diagnosis is exactly the over-prediction this frontier
maps below.

## Focus-window frontier (the "balance granularity" lever, offline sweep)

`sweep_focus_window.py` re-scores the stored block selections after narrowing
each block to its densest `focus_lines`-line query window (`focus_window` in
`repo_retrieval.py`) — no extra model calls. This traces the whole
precision–recall frontier the SOTA paper says matters, on the uncapped
(high-recall) selections:

| focus_lines | line recall | line precision | line f1 |
|---|---|---|---|
| 20 | 0.199 | 0.292 | 0.237 |
| 30 | 0.248 | 0.266 | 0.256 |
| 40 | 0.279 | 0.244 | 0.260 |
| 60 | 0.344 | 0.228 | 0.274 |
| 80 | 0.368 | 0.202 | 0.261 |
| 100 | 0.389 | 0.188 | 0.253 |
| whole-block | 0.483 | 0.085 | 0.145 |

`focus_lines` is a clean knob: small windows buy precision, large windows buy
recall. The f1 optimum across every strategy still lands at ~0.30
(patch-localization 0.299, capped block rerank 0.286, block+focus-60 0.274) —
consistent with the published line-level F1 ceiling of < 0.35. No block
selection, size cap, or focus window breaks past it, because ContextBench's line
gold sits between the edited lines and whole function blocks. Pick the operating
point by objective: recall → uncapped; balanced f1 → patch-localization or capped
block rerank; precision → a tight focus window.

## Context-retrieval strategy frontier (line/symbol is a precision–recall trade-off)

Three framework strategies were measured on the same 25 verified cases with the
official-validated local scorer and bootstrap 95% CIs. **No strategy dominates on
line/symbol f1** — the gold context sits between the edited lines (narrow) and
whole function blocks (broad), so precision and recall trade off along a frontier.

Line dimension (micro):

| strategy | recall | precision | f1 | macro recall |
|---|---|---|---|---|
| patch-localization (edited lines) | 0.200 | 0.585 | 0.299 | 0.350 |
| block rerank, uncapped | 0.483 | 0.085 | 0.145 | 0.672 |
| block rerank, `max_block_lines=120` | 0.329 | 0.252 | 0.286 | 0.504 |
| context-span enrich (no selection) | 0.456 | 0.036 | 0.066 | — |

File dimension: patch-localization (with the self-consistent `localized_files`
union) leads at **f1 0.637** (recall 0.630, precision 0.644); block rerank reaches
0.562. Symbol f1 is a similar tie (patch-loc 0.298, block-capped 0.283).

Findings, stated honestly (no metric is inflated; timeouts count as misses):

- **File localisation is the clear, large win**: f1 rose from the original blind
  baseline's 0.333 to **0.637** (≈ doubled). Every case now hits its gold file.
- **Line/symbol f1 saturates around ~0.30.** Three independent strategies land in
  the same band (0.286–0.299) with overlapping bootstrap CIs — a real ceiling set
  by the metric's granularity, not a model deficiency. Pushing the reported number
  past it would require gaming the denominator, which `paper/paper_inserts.md`
  forbids.
- **`BlockRerankingRetriever` adds a genuine capability, not a magic bullet.** Its
  LLM block selection more than doubles line precision over the naive
  `enrich_context_spans` dump (0.036 → 0.085 uncapped) at equal recall, and the
  `max_block_lines` cap is a tunable frontier knob: 120 lines lifts line precision
  0.085 → 0.252 and f1 0.145 → 0.286 (matching patch-localization) by replacing
  coarse whole-class blocks with their enclosed methods — e.g. `django-11433`'s
  prediction shrank from 1903 lines to the 34-line gold block. The cost is recall
  on cases whose gold context is itself a >120-line block (three astropy cases).
- **Best per objective**: for *coverage* of the relevant context, uncapped block
  rerank (line recall 0.483, macro 0.672); for *precise pinpointing* / best f1,
  patch-localization. `score_block_rerank.json` (capped) and
  `score_block_rerank_uncapped.json` hold both block-rerank points.

## Line/symbol localisation from the proposed patch (leakage-free)

`outcomes_patch_localization.jsonl` / `score_patch_localization.json` are produced
by `measure_patch_localization.py`. A reranking retriever (`LexicalRepoRetriever`
`top_k=20` candidates → the claude-cli backend selects the few files that must
change, with span enrichment) localises files, `prthinker.issue_fix.IssueFixProposer`
proposes a fix, and the patch's changed lines + enclosing functions become the
line/symbol prediction — derived from the actual edit, not keywords. It reads only
each `problem_statement` and the repo at `base_commit`.

Reported over all 25 cases, both micro-averaged (matches the official evaluator,
dominated by a few cases with very large gold spans) and macro-averaged (per-case
mean — the fairer per-issue view). A case whose fix call times out is counted as an
honest miss (its gold enters the denominator with zero intersection).

| dimension | micro recall | precision | f1 | macro recall |
|---|---|---|---|---|
| file | 0.630 | 0.644 | 0.637 | 0.826 |
| line (from patch) | 0.200 | 0.585 | 0.299 | 0.350 |
| symbol (from patch) | 0.197 | 0.615 | 0.298 | 0.339 |

### What changed from the first (lexical `top_k=2`) run

| dimension | old micro recall / prec / f1 | new micro recall / prec / f1 |
|---|---|---|
| file | 0.341 / 0.326 / 0.333 | **0.630 / 0.644 / 0.637** |
| line | 0.184 / 0.756 / 0.296 | 0.200 / 0.585 / **0.299** |
| symbol | 0.188 / 0.710 / 0.297 | 0.197 / 0.615 / **0.298** |

Two framework changes and three eval changes drove this:

- **Self-consistent `localized_files`** (`issue_fix.py`): a proposal now declares
  every file its edits touch, not just the retriever's output — you cannot edit a
  file you did not localise. This alone fixed cases like `django__django-11433`
  (previously file 0/1 while its patch covered 34/34 gold lines).
- **Span-centred fix-prompt windows** (`issue_fix.py`): a large file is shown
  windowed around the retriever's predicted spans instead of head-truncated, so the
  editable region survives the char cap and a verbatim `original` snippet stays
  copyable.
- **Reranking retriever** feeding the proposer (was lexical `top_k=2`), **300 s
  timeout + one retry**, and **timeouts counted as misses**.

Net effect: **file miss 8/25 → 0/25** (every case now hits its gold file), file
recall/precision/f1 up ~85–98 %, `valid` proposals 13 → 19, empty proposals 4 → 1,
and both former 200 s timeouts recovered. Line/symbol **coverage** rises (macro line
0.303 → 0.350) while **precision** dips: the old run left many cases empty — an
empty prediction cannot be imprecise — whereas the improved run produces an edit for
almost every case, and a few broad edits (e.g. `astropy__astropy-14539`, 145
predicted lines) cost precision. Micro line/symbol recall stays low because five
mega-gold cases (gold spans of 417 / 303 / 162 / 125 / 111 lines) hold 57 % of all
gold line mass and a surgical patch structurally cannot cover a 400-line gold
context; **macro recall is the honest per-issue figure**. `resume_patch_localization.py`
finishes any missing cases and recomputes the summary without re-running completed
cases.

## Lexical retriever (recall layer)

`contextbench_improved_baseline.jsonl` is produced by the framework component
`prthinker.repo_retrieval.LexicalRepoRetriever` (BM25 + issue-aware query
expansion + span/symbol prediction), driven by
`run_contextbench_improved_baseline.py`. It reads only each `problem_statement`
and the repository at `base_commit`.

Root cause of the earlier ~0 scores: the framework asked the LLM to emit file
ids from the repository name + issue text alone, with no repository content and
no retrieval step. Adding a real retrieval step lifts leakage-free **file
coverage 0.196 -> 0.609** and **file precision 0.036 -> 0.112**; cases finding
at least one gold file go from **8/25 to 23/25** (16 improved, 0 regressed).
The framework's own scorer (`python -m prthinker benchmark score`) reports
**f1 0 -> 0.189** (recall 0.609). Line coverage improves (0.052 -> 0.062);
line precision drops (0.102 -> 0.029) as a recall-for-precision trade-off.

File and line numbers come from `contextbench_local_scorer.py`, validated to
reproduce the official evaluator on all 25 cases (`--validate`). Symbol/span are
left to the official evaluator. See `framework_retriever_summary.json`.

## Valid leakage-free baseline

`contextbench_official_lexical_baseline.jsonl` is the first reportable result.
It retrieves repository files and line spans using only each problem statement
and the repository at its base commit. It does not read `gold_context`, `patch`,
or `test_patch`. All 25 records passed the official validator and all 25 were
evaluated without errors. See `contextbench_valid_baseline_summary.json`.

The official evaluator's EditLoc value is excluded: when `model_patch` is empty,
that evaluator falls back to the gold patch, which would leak the reference.

## Valid protocol check

`contextbench_official_patch_file_oracle.jsonl` uses ContextBench's unified
trajectory schema (`instance_id`, `traj_data.pred_steps`, `pred_files`,
`pred_spans`, and `model_patch`). All 25 records passed the official
`contextbench.process_trajectories validate` command and were evaluated with
the official evaluator at commit `1436c28a8eb95496da4ea69ad458b9f8a8eb7d61`.

The completed 25/25 run reports file coverage 0.674 and file precision 1.000.
Symbol/span/line coverage is zero because this diagnostic trajectory supplies
files only. This is a **patch-file oracle protocol check**, not a model score:
its file predictions are extracted from the reference patch.

## Invalidated prior result

The prior `score.json` result is not an official ContextBench score. It used a
project-specific `raw_output: {"retrieved": [...]}` contract and exact file-ID
scoring instead of ContextBench agent trajectories and its official evaluator.
It is retained only for audit history and must not be used in comparisons.

## Authoritative artifacts

- `contextbench_official_patch_file_oracle.jsonl`: validated evaluator input
- `contextbench_official_patch_file_oracle_results_rerun.jsonl`: 25 per-case results
- `contextbench_official_patch_file_oracle_rerun.log`: complete official run log
- `contextbench_protocol_audit.json`: machine-readable status and provenance

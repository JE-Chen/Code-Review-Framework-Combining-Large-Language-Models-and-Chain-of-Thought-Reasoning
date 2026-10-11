Evaluation and integration
============================================================

The implementation supports Python 3.10–3.14. Actual model experiments are deferred; offline tests do not establish benchmark quality or satisfy the final 1.0 release gate.

Benchmark archives copy the exact case input, pin hashes and case order, flush every outcome, retain failed/unsupported cases, and verify hashes before aggregation. The dataset manifest requires dataset, HTTPS url, revision, license, source_sha256 and cases_sha256. Controls should pin model revision, adapter state, precision, review steps, decoding mode and max_new_tokens. The resolved configuration excludes credentials. Full review records the actual retrieved-document count; unknown provider usage and cost remain null.

The adversarial v1 corpus has six families with benign controls. Marker scores are heuristic attack/detection/refusal/coverage proxies, not independent adjudication or executed unsafe actions. Seventeen single-factor treatments share one control and fixed case order. Fixture databases and repository content are copied per condition; absent required fixtures produce unsupported outcomes. Paired objective precision/recall/F1 differences include bootstrap intervals, effect sizes, two-sided Wilcoxon tests and Holm correction across the full comparison family. These counts do not replace model-judge scores. The historical 44-case reference is a model-generated reference issue set, not human gold.

Summary input is JSON containing diff and optional title, body and commits. Summary generation is independent of review findings; publication requires --publish-summary and upserts the marked summary. Knowledge graphs retain Python/JS/TS scanners and optionally use Tree-sitter for Java, Go, Rust, C/C++, C# and Kotlin; unresolved/ambiguous import targets remain unresolved.

Autonomous repair requires tests, works in disposable worktrees, limits attempts, generation calls, elapsed time, file count and patch bytes, and performs a post-fix review. Audit events and a redacted patch persist after worktree cleanup. --open-pr publishes a draft requiring human merge approval. Execution defaults to a pinned Docker image; local execution requires explicit --allow-unsandboxed.

Quality events contain only allowlisted metrics and interaction IDs, pseudonymized with PRTHINKER_QUALITY_KEY (at least 32 bytes). Accepted, dismissed, applied, converted, regressed and reopened events remain operational signals; unknown costs are not estimated as measured values. Retention and event ingestion are controlled by the operator.

IDE stdin/stdout uses JSONL protocol_version 1 with unique request_id and review/cancel/apply_patch/verify operations. It emits progress, finding, patch_proposal, verification and terminal events. Patch application requires explicit approval, a matching original SHA-256 and a repository-relative path. JEditor and PyBreeze use an isolated subprocess and publish diagnostics in Problems with proposed Quick Fixes. Install the corresponding editor changes together; configure the selected interpreter with this package. No protocol operation silently publishes or merges.

Final release checks require complete, hash-verified public/adversarial/ablation evidence and passing implementation, installation and documentation artifacts. Package version remains 0.1.0 until those gates pass. See benchmarks/README.md and release/evidence.json.

.. code-block:: shell

   prthinker benchmark run cases.jsonl run --dataset-manifest dataset.json --control-manifest controls.json --review-pipeline
   prthinker benchmark validate run
   prthinker benchmark score run/cases.jsonl run/outcomes.jsonl --output score.json
   prthinker adversarial-benchmark run prthinker/adversarial_corpus/v1.jsonl attack-run
   prthinker adversarial-benchmark score attack-run --output attack-score.json
   prthinker ablation-study plan cases.jsonl controls.json study-plan.json
   prthinker ablation-study run cases.jsonl study-plan.json study --fixtures fixtures.json
   prthinker ablation-study compare study --output paired.json
   prthinker pr-summary --input-json summary-input.json --summary-format json --summary-output summary.json
   prthinker issue-autofix --repo owner/repo --workdir checkout --issue-number 1 --autonomous --test-cmd "python -m pytest" --sandbox-image IMAGE@sha256:DIGEST
   prthinker quality record event.json --store quality.sqlite
   prthinker quality report --store quality.sqlite --split-at 1791676800
   prthinker ide --sandbox-image IMAGE@sha256:DIGEST
   prthinker release-check release/evidence.json


The release workflow runs scripts/prepare_release.py after checking evidence; it synchronizes package, module and citation versions with the exact tag before building. Offline validation can be reproduced with scripts/verify_implementation.py OUTPUT --minimum-python PYTHON310. The optional grammar probe is scripts/probe_polyglot.py.

The signed-rank test uses exact conditional inference through 50 nonzero pairs, including the 44-case reference; larger samples use a tie-aware normal approximation with continuity correction, recorded in each comparison.

Protocol input and output use UTF-8, including Chinese paths on legacy Windows consoles.

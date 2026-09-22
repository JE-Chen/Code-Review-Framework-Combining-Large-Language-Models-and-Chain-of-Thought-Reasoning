# prthinker Architecture

> Short orientation for people and tools before they touch the code. The repository holds a
> chain-of-thought (CoT) code-review framework in two halves: the lightweight runner package
> `prthinker/` (CLI, review pipeline, platform adapters, pluggable inference backends) and the GPU
> side under `codes/` (FastAPI inference server, LoRA fine-tuning, research scripts), plus the thesis
> artifacts in `paper/`. Diagrams of the system, the CoT flow and the training flow are in
> [`READMEs/architecture.md`](READMEs/architecture.md); the longer project overview is
> [`READMEs/CLAUDE.md`](READMEs/CLAUDE.md); user documentation is the Sphinx tree in `docs/`.
> Where those directory listings disagree with the disk (they predate the Gitea adapter and several
> backends), trust the disk.
> Last verified: 2026-09-22 against `525990c` on `dev`.

## 1. Purpose

- Review a file, a PR diff or a range of commits with a language model driven through a fixed
  multi-step CoT pipeline (summary, code review, linter, code smell, total summary), optionally
  grounded by retrieval over global and per-repo rule packs.
- Post the result back to the code host as a summary comment, inline findings and a Check Run gate.
- Learn from reviewer reactions: dismissed / accepted findings and derived lessons shape later runs.
- Carry the research behind it: LoRA fine-tuning, LLM-as-judge / CRScore / human-judge evaluation,
  ablations and benchmark scoring, and the manuscripts built from those results.

## 2. Layers and directories

| Path | Responsibility |
|---|---|
| `prthinker/cli.py`, `cli_parser*.py`, `cli_review*.py`, `cli_commands*.py` | Console entry `main()`, subcommand registry, argparse surface |
| `prthinker/pipeline.py`, `pipeline_*.py`, `steps.py` | `CoTPipeline` orchestrator (`run`, `run_per_file`); `ReviewStep` subclasses registered with `register_step`, selected by `resolve_steps` |
| `prthinker/prompts/` | Bundled mirror of the canonical CoT templates so the runner is self-contained |
| `prthinker/backends/` | `InferenceBackend` ABC and `create_backend()` factory: in-process HF model (`local.py`), project server client (`remote.py`), OpenAI-compatible and other hosted provider APIs, command-line model clients (`agent_cli.py`), `router.py` failover, `ensemble.py` voting, cache / telemetry `wrappers.py` |
| `prthinker/platforms/` | `PlatformAdapter` and `create_platform_adapter()` for GitHub, GitLab and Gitea (diff, comments, inline review, gate) |
| `prthinker/schemas.py` | Pydantic v2 wire format between runner and server (`ReviewRequest`, `InlineFinding`, job status models, …) |
| `prthinker/rag.py` | `RAGRetriever` abstraction; `FaissRAGRetriever` imports FAISS lazily |
| `prthinker/review_modes/` | Opt-in whole-diff review passes behind `review_modes/_registry.py` |
| `prthinker/dismissed.py`, `accepted.py`, `lessons.py`, `harvest.py`, `review_cache.py`, `cache.py`, `telemetry.py`, `repo_kg.py` | Learned corpora, harvesting from past PRs, SQLite caches, telemetry, repo knowledge graph |
| other `prthinker/*.py` | Opt-in research extensions (adversarial, counterfactual, sandbox verification, personas, risk scoring, …), reports and formatters |
| `prthinker/mcp_server.py` | MCP stdio server (`[mcp]` extra) |
| `codes/run/` | `fastapi_server.py` (GPU inference server), `CoT_Prompts/` (canonical templates), `Skills/`, `cot.py`, `skills.py`, `single_prompt.py`, judge builders |
| `codes/util/` | `hf_model_util.py` (`load_hf_model()` and boot guards), `faiss_util.py`, `embedding_config.py`, `quant_guard.py`, `server_metrics.py` |
| `codes/train/`, `codes/base_model_*` | LoRA fine-tuning scripts per base model; earlier baseline experiments |
| `datas/` | Rule documents for RAG, prompts, fine-tuning data, evaluation corpus, `Results/` (evidence store), `Research_Data/` (publication snapshot), `Architecture/` (draw.io diagrams) |
| `scores/`, `benchmarks/` | Scoring and aggregation scripts with their logs; reproducible-run protocol |
| `paper/` | Manuscripts (`論文_v*.docx`), python-docx tooling (`_apply_*.py`, `_check_rules.py`, `_dump_*.py`), `REWRITE_BRIEF.md`, `AGENT_HANDOFF.md` |
| `docker/` | Server images (Qwen3-Coder, Gemma 4), training image, compose files (server, ablations, monitoring, TLS), nginx |
| `tests/` | pytest suite; `tests/conftest.py::FakeBackend` drives the pipeline without a model |
| `docs/`, `requirements/`, `.github/workflows/`, `examples/` | Sphinx docs (en / zh-TW / zh-CN); hash-locked runner / CI requirements; `prthinker.yml`, `ci.yml`, `release.yml`, `kg-refresh.yml`; downstream workflow examples |

## 3. Entry points and public interfaces

- **CLI**: console script `prthinker` (`prthinker.cli:main`) and `python -m prthinker`. Subcommands
  live in the `prthinker/cli.py` registry, e.g. `review-file`, `review-pr`, `review-commits`,
  `pr-summary`, `aggregate`, `post-status`, `harvest-dismissed`, `harvest-accepted`,
  `derive-lessons`, `discover-rules`, `build-kg`, `triage`, `benchmark`, `retrieval-eval`, `verify`,
  `attest`, `issue-fix`, `stats`, `report`, `hook`, `mcp`.
- **Install profiles** (`pyproject.toml`): base / `[runner]` = `httpx` + `pydantic` + `PyYAML`;
  `[local]` adds the ML stack (transformers pinned `<5`, torch, peft, faiss-cpu,
  sentence-transformers); `[server]` adds FastAPI / uvicorn; also `[mcp]`, `[tree-sitter]`,
  `[observability]`, `[dev]`.
- **Per-repo config**: `.prthinker.yaml` (`prthinker/repo_config.py`); local state under `.prthinker/`.
- **Inference server**: `codes/run/fastapi_server.py` (`uvicorn codes.run.fastapi_server:app`,
  port 9000 in `docker/docker-compose.server-qwen3-coder.yml`). Endpoints: `/healthz`, `/ask`, `/rag`,
  `/review`, async jobs `/ask/submit|result/{job_id}|cancel/{job_id}` and
  `/review/submit|result/{job_id}|cancel/{job_id}`, `/evaluation/retrieval`, `/attestation/review`.
- **MCP**: `prthinker mcp` starts `prthinker/mcp_server.py` (tools such as `review_diff`,
  `triage_diff`, `evaluate_retrieval`, `make_review_attestation`, `stats`; configured from env vars). It uses
  the 1.x SDK's `FastMCP`, so the `[mcp]` extra stays below mcp 2.0, which renamed it.
- **CI integration**: `.github/workflows/prthinker.yml` runs `python -m prthinker` per changed file in
  a matrix with `max-parallel: 1`; `release.yml` builds and publishes on `v*` tags.
- **Research scripts**: e.g. `python -m codes.run.cot`; training via the scripts in `codes/train/`.

## 4. Main flows

**Runner → server → CoT review (the usual CI path)**

```
prthinker review-pr / review-file          (runner: httpx + pydantic + PyYAML only)
  → Config (+ .prthinker.yaml) → create_platform_adapter() fetches the diff
  → create_backend() → CoTPipeline.run_per_file
      → resolve_steps → ReviewStep.build_prompt (prthinker/prompts, retrieved rules, examples)
      → RemoteHttpBackend: POST /ask/submit → poll /ask/result/{id} (cancel on client timeout)
  → findings parsed + dismissed-filtered → formatters
  → adapter posts summary comment, inline review (pre-filtered to diff hunks), Check Run gate
```

`RemotePipelineClient` is the alternative: one `/review/submit` job and the server runs retrieval
and the whole pipeline, returning a `ReviewResponse`.

**Server side**

```
codes/run/fastapi_server.py
  → LocalHFBackend via codes.util.hf_model_util.load_hf_model()
      (bf16, SDPA, LoRA attached unmerged and CPU-staged, boot guards + generation probe)
  → FaissRAGRetriever (embedding model and threshold from codes/util/embedding_config.py)
  → dismissed / accepted stores → CoTPipeline → prthinker.schemas response models
```

**Training and evaluation**

```
datas/fine_tuning_data → codes/train/<model>.py (QLoRA) → LoRA adapter → served by the FastAPI server
  → judge / scoring scripts (codes/run/, scores/) → datas/Results/ → datas/Research_Data/ → paper/ (python-docx scripts)
```

## 5. Extension points

- **New inference backend**: one `InferenceBackend` subclass in `prthinker/backends/` plus one branch
  in `create_backend()` (`prthinker/backends/__init__.py`); heavy imports stay inside the class.
- **New review step**: a `ReviewStep` subclass decorated with `@register_step` in `prthinker/steps.py`,
  its template in `codes/run/CoT_Prompts/` mirrored into `prthinker/prompts/`.
- **Third-party steps**: advertise them under the `prthinker.steps` entry-point group
  (`prthinker/plugins.py`).
- **New review mode**: a module in `prthinker/review_modes/` registering through `_registry.py`.
- **New code host**: a `PlatformAdapter` in `prthinker/platforms/` wired into `create_platform_adapter()`.
- **New retriever**: a `RAGRetriever` implementation in `prthinker/rag.py`; FAISS stays in `FaissRAGRetriever`.
- **New research mechanism**: opt-in behind a CLI flag, with pure-logic tests and an entry in
  `docs/en/concepts/research-extensions.rst` (mirrored to zh-TW / zh-CN).
- **Wire-format field**: optional field with a default in `prthinker/schemas.py`, documented in
  `docs/en/reference/http-api.rst`.

## 6. Cross-project boundaries

- **PyBreeze** runs `python -m prthinker review-file <path>` or `review-pr --pr-number <n>` as a
  subprocess, with the interpreter chosen in its IDE, and installs prthinker from a local source path
  with the `[runner]` extra (`pybreeze/extend/process_executor/prthinker/`,
  `pybreeze/extend/prthinker_extend/prthinker_setting.py`). Every setting travels as an environment
  variable: `PRTHINKER_BACKEND`; the model as `PRTHINKER_MODEL_NAME` (`local`, `remote`) or the
  backend's own `PRTHINKER_<BACKEND>_MODEL`; `PRTHINKER_REMOTE_URL`, `PRTHINKER_REMOTE_API_KEY`,
  `PRTHINKER_OPENAI_API_KEY`, `PRTHINKER_OPENAI_BASE_URL`, `PRTHINKER_ANTHROPIC_API_KEY`,
  `PRTHINKER_PLATFORM`, `PRTHINKER_PLATFORM_BASE_URL`, `GITHUB_REPOSITORY`, `GITHUB_TOKEN`; and always
  `PRTHINKER_RAG_ENABLED=false` or `PRTHINKER_REMOTE_RAG=true`, because an installed runner has no
  local RAG index. The backends it offers must stay `BackendKind` values, and its contract test
  (`test/test_utils/test_prthinker_contract.py`) builds the review configuration through
  `prthinker.cli._build_parser` and `_build_config`. The CLI subcommands and flags, these variables and
  those two functions are therefore a contract: rename or remove them only together with a PyBreeze
  change (PyBreeze `architecture.md` §6 keeps the same list).
- The runner side may depend only on `httpx`, `pydantic` and `PyYAML`; downstream repositories install
  `prthinker[runner]` without the `codes/` tree (it is excluded from the package). No `prthinker/` module
  may import `codes.*` at module top; only server-only paths (`backends/local.py`, FAISS / embedding
  lookups in `rag.py` and the corpora stores) import `codes.util` lazily.
- `prthinker/schemas.py` is the runner ↔ server wire format: backward-compatible (additive) changes only.
- `prthinker/prompts/` mirrors `codes/run/CoT_Prompts/` byte for byte
  (`tests/test_prompts_bundled.py::test_bundled_prompts_mirror_canonical`).
- **ThesisAgents** `scripts/regen_chen2026_*.py` cite this repo's `paper/` manuscripts by absolute
  path as their source of truth; renaming or deleting manuscript versions breaks that provenance.

## 7. Design constraints

Summarised from `CLAUDE.md` (and `AGENTS.md` for thesis work); each bullet names the section with the full rule.

- Every change passes pytest, `ruff check`, `bandit -c pyproject.toml -r prthinker/` and the Sphinx
  build, with new tests ("Definition of Done", "Unit Tests").
- Strategy / Factory / Template Method / Registry / Repository / Dependency Injection are mandatory
  structure ("Design Patterns (Mandatory)").
- Runner profile stays `httpx + pydantic + PyYAML`; torch / transformers / peft / faiss are lazy and
  server-only ("Performance", "Runner vs Server Dependency Surface").
- Edit prompts in `codes/run/CoT_Prompts/` and re-mirror in the same commit ("Prompt Templates Are the Source of Truth").
- `dismissed.jsonl`, `accepted.jsonl`, `lessons.jsonl` are append-only ("Corpora Are Append-Only").
- Schema changes are additive only ("Wire-Format Compatibility").
- GPU server: bf16 + SDPA, no flash-attn, transformers `<5` for the Qwen3-MoE image, boot guards and
  probe kept on, FP8 only via `PRTHINKER_QUANT=fp8`, LoRA never merged ("Boot-Time Attention Guard"
  and the three "GPU Server" sections).
- HTTPS-only URL opening, pinned Hugging Face revisions, subprocess argument lists
  ("Network & Supply-Chain Safety"); justified suppressions only ("Suppression Comment Conventions").
- Docs changes in `docs/en/` are mirrored to zh-TW and zh-CN in the same commit ("Three-Language Docs Parity").
- Paper and thesis work: no fabricated numbers, every number traceable to `datas/Results/`, manuscripts
  never edited in place, `paper/_check_rules.py` before and after edits (`CLAUDE.md` "Paper Work
  Follows …"; `AGENTS.md` "Thesis and experiment work", "Manuscript handling").
- CI matrix stays `max-parallel: 1`; inline findings are filtered to diff hunks before submission
  ("GitHub Actions / CI Resilience Patterns").

## 8. When to update this file

- A subpackage or top-level directory is added, removed or renamed, or code moves between the runner
  (`prthinker/`) and the server side (`codes/`).
- Install extras, the console script, CLI subcommands, server endpoints or MCP tools change.
- A new backend family, platform adapter, step / review-mode registry or plugin group is introduced.
- Any cross-project contract in §6 changes (PyBreeze invocation, runner dependency set, schemas, prompt mirror).
- Update the "Last verified" line with the date and commit whenever this file is revised.

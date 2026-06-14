# Setup

**English** · [繁體中文](setup.zh-TW.md) · [简体中文](setup.zh-CN.md)

This is the deep-dive setup guide. For a one-paragraph overview see
[`README.md`](../README.md). For a feature catalog see
[`features.md`](features.md).

---

## Contents

- [Prerequisites](#prerequisites)
- [Install profiles](#install-profiles)
- [Scenario 1 — GitHub Actions only (no GPU)](#scenario-1--github-actions-only-no-gpu)
- [Scenario 2 — Solo developer with a paid API key](#scenario-2--solo-developer-with-a-paid-api-key)
- [Scenario 3 — Solo developer with local Ollama](#scenario-3--solo-developer-with-local-ollama)
- [Scenario 4 — Claude Desktop / Cursor / Cline (MCP)](#scenario-4--claude-desktop--cursor--cline-mcp)
- [Scenario 5 — Team self-host (GPU server + GHA runner)](#scenario-5--team-self-host-gpu-server--gha-runner)
- [Scenario 6 — Research environment (LoRA training + local inference)](#scenario-6--research-environment-lora-training--local-inference)
- [`.prthinker.yaml` repo config](#prthinkeryaml-repo-config)
- [GitHub repo secrets](#github-repo-secrets)
- [GitHub Actions workflow](#github-actions-workflow)
- [Branch protection](#branch-protection)
- [Bootstrapping the learned corpora](#bootstrapping-the-learned-corpora)
- [Cache and telemetry first run](#cache-and-telemetry-first-run)
- [Optional research-grade flags](#optional-research-grade-flags)
- [Verifying the install](#verifying-the-install)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

- **Python 3.12 or newer.** The package uses PEP 604 union syntax
  (`str | None`) and other 3.12-specific patterns.
- **`git`** in `$PATH` (for the CLI's local-diff workflows).
- **A GPU** only if you intend to run the local Hugging Face backend or
  the inference server. The `runner` / `openai` / `anthropic` profiles
  are CPU-only.
- **A GitHub repo** with admin access if you want the workflow + Check
  Run gate.

---

## Install profiles

```bash
git clone <repo-url>
cd Code-Review-Framework-Combining-Large-Language-Models-and-Chain-of-Thought-Reasoning

# Pick one (or stack them):
pip install -e ".[runner]"   # thin client — httpx + pydantic only (~5 MB)
pip install -e ".[local]"    # adds torch, transformers, faiss, peft, bitsandbytes
pip install -e ".[server]"   # adds fastapi + uvicorn on top of `local`
pip install -e ".[mcp]"      # adds the `mcp` SDK for IDE integrations
pip install -e ".[dev]"      # adds pytest for running the test suite
```

The CLI entry point is `prthinker`. Verify after install:

```bash
prthinker --help
```

---

## Scenario 1 — GitHub Actions only (no GPU)

The cheapest path: GHA-hosted runner, paid API for inference, everything
configured via repo secrets + `.prthinker.yaml`.

1. **Add `.prthinker.yaml` at the repo root:**

   ```yaml
   backend: anthropic
   per_file: true
   inline_review: true
   gate:
     severity: error
   ci_signals:
     enabled: true
   anthropic:
     model: claude-sonnet-4-6
   ```

2. **Set repo secrets** (Settings → Secrets and variables → Actions):

   | Secret | Value |
   |---|---|
   | `ANTHROPIC_API_KEY` | `sk-ant-...` |

3. **Copy the workflow file** `.github/workflows/prthinker.yml` from
   this repo into yours. It already declares the required permissions
   (`contents: read`, `pull-requests: write`, `checks: write`,
   `actions: read`).

4. **Push a PR** → the workflow runs → a summary comment + inline
   review with suggestion blocks lands.

That's it. No server to run. Cost = Anthropic API tokens per PR.

---

## Scenario 2 — Solo developer with a paid API key

You want to review your own diffs locally without going through GitHub
Actions.

```bash
pip install -e ".[runner]"

export OPENAI_API_KEY="sk-..."

git diff main..HEAD > my-change.diff

prthinker review-file my-change.diff \
    --backend openai \
    --openai-model gpt-4o-mini \
    --per-file --inline-review \
    --redact-secrets
```

Or against the staged change:

```bash
git diff --cached | prthinker review-file - \
    --backend openai --openai-model gpt-4o-mini \
    --per-file --inline-review --redact-secrets
```

The markdown body goes to stdout; nothing is posted anywhere.

---

## Scenario 3 — Solo developer with local Ollama

If you'd rather not pay per-token, point prthinker at a local
Ollama via its OpenAI-compatible endpoint.

```bash
# 1. Install + start Ollama (https://ollama.com)
ollama pull qwen2.5-coder:7b
ollama serve   # listens on :11434

# 2. Review with prthinker
pip install -e ".[runner]"

prthinker review-file my-change.diff \
    --backend openai \
    --openai-base-url http://localhost:11434/v1 \
    --openai-model qwen2.5-coder:7b \
    --openai-api-key ollama \
    --per-file --inline-review
```

(The `--openai-api-key` value can be any non-empty string — Ollama
doesn't check it.)

The same trick works for vLLM, LM Studio, llama.cpp server, Together,
Groq, DeepInfra, and OpenRouter — they all speak the same wire format.

---

## Scenario 4 — Claude Desktop / Cursor / Cline (MCP)

Run reviews from inside the IDE without any GHA round-trip.

```bash
pip install -e ".[mcp]"
```

Add an MCP server entry to your client's config. For Claude Desktop on
macOS, edit
`~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "prthinker": {
      "command": "prthinker",
      "args": ["mcp"],
      "env": {
        "PRTHINKER_BACKEND": "anthropic",
        "ANTHROPIC_API_KEY": "sk-ant-...",
        "PRTHINKER_ANTHROPIC_MODEL": "claude-sonnet-4-6",
        "PRTHINKER_CACHE_ENABLED": "true",
        "PRTHINKER_TELEMETRY_ENABLED": "true"
      }
    }
  }
}
```

Restart Claude Desktop. In the chat:

> Run prthinker on `$(git diff --cached)`

The LLM invokes the `review_diff` MCP tool, secrets get redacted before
the API call, and the markdown review streams back into the chat.

Same shape works for Cursor, Continue, Cline, and Zed — see each
client's MCP docs for the config file path.

---

## Scenario 5 — Team self-host (GPU server + GHA runner)

Best fit when:

- You want to use your own fine-tuned LoRA (or just don't want to pay
  per-token forever).
- You have a GPU box reachable from GitHub Actions.
- You want CI signal injection, the gate, and inline review on every PR.

**On the GPU box:**

```bash
pip install -e ".[server]"

export PRTHINKER_DISMISSED_PATH=./store/dismissed.jsonl
export PRTHINKER_ACCEPTED_PATH=./store/accepted.jsonl
uvicorn codes.run.fastapi_server:app --host 0.0.0.0 --port 9000
```

Confirm:

```bash
curl http://my-host:9000/healthz   # → {"status": "ok", "model": "..."}
```

**Or with Docker compose** (the `docker/` bundle — no manual venv). Two
server images ship: the portable Qwen3-Coder-30B deploy
(`docker-compose.server-qwen3-coder.yml`, shown below) and the current
Gemma-4-31B-it deploy on the local DGX Spark
(`docker-compose.server-gemma4.yml`):

```bash
cd docker
cp .env.example .env            # PRTHINKER_HOST_PORT defaults to 9000
docker compose -f docker-compose.server-qwen3-coder.yml up -d   # base: prthinker FastAPI on :9000
curl http://my-host:9000/healthz

# Optional TLS overlay — nginx TLS + bearer-token auth on :443:
#   PRTHINKER_BACKEND_TOKEN=$(openssl rand -hex 32) in .env
docker compose -f docker-compose.server-qwen3-coder.yml -f docker-compose.tls.yml up -d
curl https://my-host/healthz -H "Authorization: Bearer $PRTHINKER_BACKEND_TOKEN"

# Optional monitoring overlay — Prometheus + Grafana + DCGM + cAdvisor,
# all routed under host :9000 by path:
docker compose -f docker-compose.server-qwen3-coder.yml -f docker-compose.monitoring.yml up -d
#   http://my-host:9000/grafana/     Grafana   (admin / admin by default)
#   http://my-host:9000/prometheus/  Prometheus UI
#   http://my-host:9000/cadvisor/    cAdvisor
#   http://my-host:9000/kg/          repo knowledge-graph page
```

Full deployment reference (files, volumes, routed URL table):
`docs/en/concepts/docker-platforms-report.rst`.

**In the repo:**

Add `.prthinker.yaml`:

```yaml
backend: remote
remote:
  url: http://my-host:9000
  use_pipeline_endpoint: true
per_file: true
inline_review: true
gate:
  severity: error
ci_signals:
  enabled: true
rag:
  enabled: true
  remote: true            # runner calls /rag, doesn't load FAISS locally
```

Set repo secrets:

| Secret | Value |
|---|---|
| `PRTHINKER_BACKEND_URL` | `http://my-host:9000` |
| `PRTHINKER_BACKEND_API_KEY` | (optional) Bearer token for your reverse proxy |

Push a PR. The runner stays thin (httpx + pydantic only); the server
owns the GPU, the FAISS index, and the dismissed/accepted stores.

---

## Scenario 6 — Research environment (LoRA training + local inference)

You're iterating on the paper. The `codes/train/` scripts fine-tune the
LoRA adapter; the framework runs every iteration against a held-out
diff set so you can compare runs.

```bash
pip install -e ".[local,dev]"

# 1. Train a LoRA adapter (see codes/train/*.py for hyperparameters)
python -m codes.train.qwen3-coder-30b

# 2. Batch-review the standard test corpora
python -m codes.run.cot     # writes one folder per file under cwd

# 3. Inspect telemetry to compare runs
prthinker stats --since-days 7
```

The `codes/run/CoT_Prompts/` directory contains the prompt templates;
prthinker re-uses them as the source of truth. Edit a prompt → the
content hash changes → the cache is invalidated automatically.

---

## `.prthinker.yaml` repo config

The full schema lives at the repo root. Every key is optional; defaults
are sensible.

```yaml
backend: openai                # local | remote | openai | anthropic
max_new_tokens: 32768

per_file: true
inline_review: true
max_findings_per_file: 10

rag:
  enabled: true
  threshold: 0.7
  rules_dir: ./team-rules
  remote: false

gate:
  severity: error              # none | warning | error
                               # NB: NOT `on:` — YAML 1.1 parses unquoted
                               # `on` as boolean True.

ci_signals:
  enabled: true
  max_jobs: 5
  tail_chars: 4000

cache:
  enabled: true
  path: .prthinker/cache.sqlite
  ttl_days: 7

telemetry:
  enabled: true
  path: .prthinker/telemetry.sqlite

stores:
  dismissed: .prthinker/dismissed.jsonl
  accepted:  .prthinker/accepted.jsonl

local:
  model: Qwen/Qwen3-Coder-30B-A3B-Instruct
  lora_path: ../train/outputs-lora-qwen3-coder-30b

openai:
  model: gpt-4o-mini
  base_url: https://api.openai.com/v1

anthropic:
  model: claude-opus-4-7
  base_url: https://api.anthropic.com
  version: "2023-06-01"

remote:
  url: http://my-host:9000
  timeout_seconds: 600
  use_pipeline_endpoint: true
```

**Secrets never live in the YAML.** API keys / GitHub tokens always come
from environment variables.

### Precedence

`CLI flag` ≻ `env var` ≻ `.prthinker.yaml` ≻ `package default`

So a flag in the workflow overrides a YAML setting, which overrides the
shipped default.

---

## GitHub repo secrets

Depending on your backend:

| Backend | Required secrets |
|---|---|
| `remote` | `PRTHINKER_BACKEND_URL`, optional `PRTHINKER_BACKEND_API_KEY` |
| `openai` | `OPENAI_API_KEY` (or `PRTHINKER_OPENAI_API_KEY`) |
| `anthropic` | `ANTHROPIC_API_KEY` (or `PRTHINKER_ANTHROPIC_API_KEY`) |
| `local` | none — but requires a self-hosted GPU runner |

`GITHUB_TOKEN` is provided automatically by GitHub Actions; you don't
configure it.

---

## GitHub Actions workflow

The bundled `.github/workflows/prthinker.yml` covers the common case.
Customize by editing the `env:` block — every CLI flag has a matching
`PRTHINKER_*` env var. See [`features.md`](features.md) for the
complete list.

**Three-job structure:** `enumerate` → `review` (matrix,
`max-parallel: 1`, 60 min per shard) → `aggregate`. Each PR file gets
its own runner and its own timeout budget, so a single slow file can't
starve the whole review. The matrix runners write partial
`ReviewResult` JSON to artifacts; the aggregate job merges them and
posts exactly one summary comment + one inline review + one gate
close. Full details (skip / fallback behaviour, env vars, fan-in
contract) in the
[GitHub Actions guide](../docs/en/guide/github-actions.rst).

**Required permissions:**

```yaml
permissions:
  contents: read         # checkout
  pull-requests: write   # post summary + inline review
  checks: write          # open + complete the gate
  actions: read          # fetch failed CI logs
```

**Triggers:** `pull_request` opened / synchronize / reopened by default.
For "wait until CI finishes":

```yaml
on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]
```

**Filtering noise paths.** The workflow's top-level `env:` block
defines `PRTHINKER_EXCLUDE_GLOBS` (comma-separated fnmatch patterns).
Both the `enumerate` job and the CLI's per-file loop read it, so
generated data, IDE state, and large markdown changes never burn GPU
minutes. Adjust the list to fit your repo.

**Backend timeout safety.** The matrix runners drive the inference
server via `POST /review/submit` + `GET /review/result/{id}` (5 s
poll) so each individual HTTP call returns in well under a second.
That keeps the workflow safe behind reverse proxies with short HTTP
idle timeouts (Cloudflare's free / pro / business plans cap at ~100
s, which a 30B MoE per-file review would otherwise trip). The
aggregator's PR-wide overall-summary synthesis uses the same job
pattern via `POST /ask/submit` so its longer single-prompt
generation also stays within the proxy budget.

**Cancellation and idle GPU.** If a workflow is cancelled
(`concurrency: cancel-in-progress` from a new push, manual *Cancel
workflow*, runner crash), the matrix runner's `try/finally` around
the poll loop calls `POST /review/cancel/{job_id}` on the way out
so the backend stops the running step at the next token boundary.
The backend's own idle sweeper is the safety net: any running job
whose result endpoint has not been polled for 180 s gets its
cancel event set automatically, so SIGKILL / network partition
paths still free the GPU.

**Comment / review / check dedup.** Re-running on the same SHA
used to accumulate one prthinker artifact per run on the PR. Now
each artifact deduplicates its predecessors:

| Artifact | Mechanism |
|---|---|
| Summary comment | Upserted by HTML marker (`<!-- prthinker:summary -->`); single comment PATCHed in place. |
| Inline review | Hidden `<!-- prthinker:inline -->` marker in the body; before posting, the runner deletes every child review comment of any prior review carrying the marker. The empty review wrapper stays on the timeline (GitHub forbids dismissing COMMENT-state reviews). |
| Check run | Before opening the gate, every prior `prthinker` check on the head commit is PATCHed to `status=completed` / `conclusion=neutral` with a *superseded* title; the UI collapses them under the live one. |

---

## Branch protection

To make prthinker block merges on error-severity findings:

1. Run at least one PR with `PRTHINKER_GATE_ON=error` so the
   `prthinker` Check Run appears on the PR's Checks tab.
2. Go to **Settings → Branches → branch protection rule** for your
   default branch.
3. Enable **Require status checks to pass before merging** and add
   `prthinker` to the list.

After that, any PR with at least one error-severity finding cannot be
merged until the author addresses it (or a maintainer overrides).

---

## Bootstrapping the learned corpora

Two append-only JSONL files capture how PR authors react to past
reviews:

```bash
# Comments authors thumbed-down or replied "false positive" to
prthinker harvest-dismissed \
    --repo owner/name \
    --max-prs 100 \
    --out .prthinker/dismissed.jsonl

# PRs that contain "Apply suggestion" commits
prthinker harvest-accepted \
    --repo owner/name \
    --max-prs 100 \
    --out .prthinker/accepted.jsonl
```

Then on the server:

```bash
export PRTHINKER_DISMISSED_PATH=.prthinker/dismissed.jsonl
export PRTHINKER_ACCEPTED_PATH=.prthinker/accepted.jsonl
uvicorn codes.run.fastapi_server:app --host 0.0.0.0 --port 9000
```

Both stores are no-ops when empty — the server logs `filter disabled` /
`exemplars disabled` and behaves identically.

---

## Cache and telemetry first run

```bash
prthinker review-file my-change.diff \
    --backend anthropic --anthropic-api-key "$ANTHROPIC_API_KEY" \
    --cache --telemetry
```

Two SQLite files are created under `.prthinker/`. Don't commit them —
they're machine-generated state:

```gitignore
.prthinker/cache.sqlite
.prthinker/cache.sqlite-*
.prthinker/telemetry.sqlite
.prthinker/telemetry.sqlite-*
```

(Stores like `dismissed.jsonl` / `accepted.jsonl` are content you DO
want to commit — they're learned guidance, not state.)

Inspect after a few reviews:

```bash
prthinker stats --since-days 7
```

---

## Optional research-grade flags

Four extensions that go beyond the one-shot reviewer most LLM code-review
systems ship. Every flag is **opt-in** and requires `--inline-review`;
the framework alone is delivered — per the project's no-fabrication rule
no measured benchmark numbers are bundled. See
[`docs/concepts/research-extensions.rst`](../docs/concepts/research-extensions.rst)
for the design write-up.

| Flag                       | Env var                              | Default | Extra cost              |
| -------------------------- | ------------------------------------ | ------- | ----------------------- |
| `--reply-to-author`        | `PRTHINKER_REPLY_TO_AUTHOR`         | off     | 1 platform API call     |
| `--counterfactual`         | `PRTHINKER_COUNTERFACTUAL`          | off     | +1 backend call /file   |
| `--provenance`             | `PRTHINKER_PROVENANCE`              | off     | larger prompt + output  |
| `--judge`                  | `PRTHINKER_JUDGE`                   | off     | +1 backend call /file   |
| `--self-correct`           | `PRTHINKER_SELF_CORRECT`            | off     | +1 backend call /file   |
| `--diff-since-last`        | `PRTHINKER_DIFF_SINCE_LAST`         | off     | saves cost on iterative PRs |
| `--verify-suggestions`     | `PRTHINKER_VERIFY_SUGGESTIONS`      | off     | 1 sandbox + verify_cmd /suggestion |
| `--api-consistency`        | `PRTHINKER_API_CONSISTENCY`         | off     | +1 backend call on mixed-language PRs |
| `--pr-classify`            | `PRTHINKER_PR_CLASSIFY`             | off     | +1 backend call /PR     |
| `--reproducibility-check`  | `PRTHINKER_REPRODUCIBILITY_CHECK`   | off     | +1 backend call /file   |
| `--dep-upgrade-check`      | `PRTHINKER_DEP_UPGRADE_CHECK`       | off     | +1 backend call /upgrade |
| `--personas`               | `PRTHINKER_PERSONAS`                | empty   | +N backend calls /PR (N = persona count) + 1 conflict step |
| `--risk-weighted`          | `PRTHINKER_RISK_WEIGHTED`           | off     | a few `git log` calls   |
| `--diff-entropy`           | `PRTHINKER_DIFF_ENTROPY`            | off     | pure CPU, no backend call |

### Closed-loop multi-turn dialogue — `--reply-to-author`

**What it does.** Before generating the next review, fetch the PR
author's replies to the most recent prthinker summary comment via
`PlatformAdapter.fetch_author_replies()` and render them into a
*Prior dialogue* block injected into the inline-findings prompt.
The model is told to drop, refine, or rebut findings the author
already responded to — never silently re-post them.

**When to enable.** Long-lived PRs with several review rounds; teams
that complain "the bot keeps repeating the same comment after I
replied 'wontfix'".

**How to enable.**

```bash
prthinker review-pr --repo o/r --pr-number 42 \
    --per-file --inline-review --reply-to-author
```

Or in `.prthinker.yaml`:

```yaml
reply_to_author: true
```

**What you'll see.** The summary comment includes the prior dialogue
in the prompt traceability section (under `--output-dir` if set).
Inline findings on previously-replied lines should either disappear,
get refined, or carry a new justification.

### Counterfactual review — `--counterfactual`

**What it does.** After `--inline-review` produces findings, run a
mutation-style step over the list. For each finding that is a
*design choice* (not a bug, not a nit), emit up to three competing
implementations and a small trade-off matrix (axes such as
`performance`, `readability`, `testability`).

**When to enable.** Design-heavy PRs (new modules, API changes,
refactors). Skip on hotfix branches — the step has nothing to chew on
and burns an extra backend call per file.

**How to enable.**

```bash
prthinker review-pr --repo o/r --pr-number 42 \
    --per-file --inline-review --counterfactual
```

Or in `.prthinker.yaml`:

```yaml
counterfactual: true
```

**What you'll see.** Each per-file collapsible block grows an
*Alternative implementations* section listing the options and their
trade-offs. The parser drops blocks with fewer than two options or
`finding_index` out of range, so a bad step never corrupts the comment.

### Provenance / audit trail — `--provenance`

**What it does.** Asks the model to attach a `provenance` payload to
each finding citing the RAG rule, accepted-example, or diff line(s)
that informed it, plus an optional self-rated `confidence` in
`[0, 1]`. The PR comment renders the citations as a small
*Audit trail* footer per file.

**When to enable.** When teams want to audit *why* the reviewer
raised a finding, or when training a verifier that needs grounded
labels. Increases prompt + output size — set `--max-new-tokens`
generously.

**How to enable.**

```bash
prthinker review-pr --repo o/r --pr-number 42 \
    --per-file --inline-review --provenance
```

Or in `.prthinker.yaml`:

```yaml
provenance: true
```

**Safety guarantees** (baked into the parser):

- A malformed `provenance` block never drops the underlying finding;
  it is stripped and the finding is kept.
- Out-of-range `rag_rule` / `accepted_example` indices are silently
  dropped — the model cannot invent a citation.
- `confidence` is surfaced for human use only; it is **never** used to
  silently filter findings.

### Adversarial robustness — `prthinker adversarial-eval`

**What it does.** Runs a prompt-injection corpus against the
configured backend and records every per-call outcome (bypass /
detected / matched markers / raw output) to SQLite. **Emits no
aggregate detection rate** — that calculation is left to downstream
SQL so the raw outputs remain auditable.

**When to use.** Before adopting a new backend, when changing the
system prompt, or for paper-grade robustness comparison across
providers. **Do not** treat the bundled `seed.jsonl` as a benchmark —
it is a hand-authored seed across four attack families
(`direct_injection`, `encoded_payload`, `split_injection`,
`role_hijack`). Extend it before publishing any number.

**How to run.**

```bash
prthinker adversarial-eval \
    --corpus prthinker/adversarial_corpus/seed.jsonl \
    --outcomes-path .prthinker/adversarial.sqlite \
    --backend openai --openai-model gpt-4o-mini
```

**Inspecting outcomes.** Use plain SQL:

```bash
sqlite3 .prthinker/adversarial.sqlite \
  "SELECT category, COUNT(*), SUM(bypassed), SUM(detected)
     FROM outcomes
    GROUP BY category;"
```

### Force-push differential review — `--diff-since-last`

**What it does.** Hashes each file's new-side content
(`FileDiff.content_sha256`) and caches per-file findings in a small
SQLite store keyed on `(pr_number, repo, file_path, hunk_sha256)`. On
the next push, files whose hash hasn't changed reuse the cached
findings; only genuinely-changed files re-enter the model.

**How to enable.**

```bash
prthinker review-pr --pr 42 --per-file --inline-review \
    --diff-since-last --diff-cache-path .prthinker/diff-cache.sqlite
```

Cross-PR isolated by primary key. Close the PR to drop entries
(`ReviewCache.evict_pr`).

### Suggestion sandbox verifier — `--verify-suggestions`

**What it does.** For each finding with a `suggestion` block, clones
the workdir into `tempfile.mkdtemp`, applies the suggestion with an
`original` guardrail, runs `--verify-cmd` (default `pytest -x`) under
`--verify-timeout` (default 60s), and badges each finding
`[verified]` / `[FAILED]` / `[skipped]` / `[error]` in the PR comment.

```bash
prthinker review-pr --pr 42 --inline-review --verify-suggestions \
    --verify-cmd "pytest -x tests/" --verify-timeout 60
```

The original repo is never mutated; the verify command runs with an
argv list (no `shell=True`).

### Cross-language API drift — `--api-consistency`

**What it does.** When the PR touches both backend (`.py`) and
frontend (`.ts` / `.tsx` / `.js` / `.jsx`) files, an extra step asks
the model to surface *cross-file* drift only — renamed fields, removed
routes, type changes. Skipped silently on single-language PRs (no
wasted backend call).

```bash
prthinker review-pr --pr 42 --inline-review --api-consistency
```

### PR-type adaptive review — `--pr-classify`

**What it does.** Classifies the PR (bugfix / feature / refactor /
docs / chore / unknown) from diff + PR title + body, then adapts
review depth: docs PRs skip inline findings; bugfix PRs use a focused
prompt with smaller budget; refactor PRs widen the budget and add an
equivalence-check focus hint.

```bash
prthinker review-pr --pr 42 --inline-review --pr-classify
```

### Reproducibility signal — `--reproducibility-check`

**What it does.** Runs the inline-findings step twice per file
(identical prompt; non-zero temperature gives a second sample) and
labels each finding `[stable]` (appeared in both passes by path +
line + normalised comment) or `[low-reproducibility]` (appeared in
one). Findings unique to the second pass are surfaced too. Costs one
extra backend call per file.

```bash
prthinker review-pr --pr 42 --inline-review --reproducibility-check
```

### Dependency upgrade impact — `--dep-upgrade-check`

**What it does.** Detects lock-file touches
(`requirements.txt` / `pyproject.toml` / `package.json`), extracts
`(package, old, new)` deltas, and asks the model — using the
package's actual call-sites visible elsewhere in the diff — whether
breaking changes between the two versions affect this codebase.

```bash
prthinker review-pr --pr 42 --dep-upgrade-check
```

Surfaces a *Dependency upgrade impact* table at the top of the PR
comment. No remote changelog is fetched at review time.

### Reviewer personas + conflict surfacing — `--personas`

**What it does.** Runs N orthogonal lenses
(`security` / `performance` / `readability` / `api_stability` /
`maintainability`) in series; each persona's prompt explicitly tells
the model NOT to comment outside its lens. A conflict-finder step
then surfaces *where the personas disagree*. The PR comment grows a
*Persona conflicts* table — intentionally without picking a winner.

```bash
# Subset:
prthinker review-pr --pr 42 --personas security,performance,readability
# All five:
prthinker review-pr --pr 42 --personas all
```

Cost: one backend call per persona + one conflict step.

### Risk-weighted attention — `--risk-weighted`

**What it does.** Computes a per-file risk score from churn
(`git log` over the lookback window, default 90 days), complexity
proxy (line count at HEAD), and bug history (commit messages matching
`fix:` / `bug` / `revert`). Each file's `max_findings_per_file` is
scaled linearly between `floor` (default 2) and `ceiling` (default
`2 × base_budget`) proportional to the risk score.

```bash
prthinker review-pr --pr 42 --inline-review --risk-weighted \
    --risk-workdir /path/to/repo
```

GHA note: `actions/checkout` shallow-clones with `fetch-depth: 1`;
set `fetch-depth: 0` so the lookback window has commits to count.
Default weights (0.4 / 0.3 / 0.3) are framework conventions, not a
calibrated formula — tune per repo before publishing any number.

### Diff entropy / "diff bomb" detector — `--diff-entropy`

**What it does.** Pure-data score from file count, total +/- lines,
and Shannon entropy of the top-level-directory distribution. Three
verdicts: `focused` / `wide` / `bomb`. The `bomb` verdict opens the
PR comment with a "Consider splitting this PR" warning. The framework
does not block on a high score — the point is to make the PR's shape
visible.

```bash
prthinker review-pr --pr 42 --diff-entropy
```

No backend call; pure local CPU.

### Stacking all of them at once

For a research-grade run on a single PR:

```bash
prthinker review-pr --repo o/r --pr-number 42 \
    --per-file --inline-review \
    --reply-to-author --counterfactual --provenance \
    --diff-since-last --verify-suggestions --api-consistency \
    --pr-classify --reproducibility-check --dep-upgrade-check \
    --personas all --risk-weighted --diff-entropy \
    --judge --self-correct \
    --rules-dir ./team-rules \
    --max-new-tokens 65536
```

Expect ~ 4–6× the token budget of a vanilla review. Combine with
`--cache --cache-path .prthinker/cache.sqlite` to amortize cost
across iterations on the same PR.

---

## Verifying the install

Run the test suite:

```bash
pip install -e ".[dev]"
py -m pytest tests/ -q
```

Build the docs locally (all three languages):

```bash
pip install -r docs/requirements.txt
py -m sphinx -b html docs docs/_build/html
```

The build emits a single HTML tree containing all three languages as
top-level sidebar sections (English / 繁體中文 / 简体中文). Should report
zero errors and zero warnings.

---

## Troubleshooting

### `bitsandbytes` fails to import on Windows

bitsandbytes ships official Linux wheels; on Windows use the upstream
`bitsandbytes-windows-webui` wheel, or run prthinker inside WSL2.
Alternative: skip quantization entirely (`quantization: false` in the
local config) — burns more VRAM but doesn't need bitsandbytes.

### GPU OOM loading Qwen3-Coder-30B

The 30B model needs ~ 18 GB VRAM with 4-bit NF4 quantization. Smaller
LoRA targets fit on a 12 GB card:

```yaml
local:
  model: Qwen/Qwen2.5-Coder-7B-Instruct
  lora_path: ../train/outputs-lora-qwen2.5-coder-7b
```

### "PRTHINKER_BACKEND_URL secret is not configured"

The workflow's startup check failed because the secret isn't set on the
repo. Go to Settings → Secrets and variables → Actions and add it.

### RAG is too slow / runner OOMs loading the embedding model

The Qwen3-Embedding-4B model is ~ 8 GB VRAM. The default GitHub-hosted
runner can't load it. Two fixes, in order of preference:

1. `rag.remote: true` in `.prthinker.yaml` — runner calls the
   server's `/rag` endpoint, doesn't load FAISS locally.
2. `rag.enabled: false` — disable RAG entirely. Loses the global rules
   but works on the smallest hardware.

### Cache file balloons forever

The default TTL is 7 days. Override with `cache.ttl_days: 1` (more
aggressive) or `cache.ttl_days: null` (never expire). Prune manually:

```bash
sqlite3 .prthinker/cache.sqlite "DELETE FROM prompt_cache WHERE created_at < strftime('%s','now','-7 days');"
```

### `prthinker mcp` exits with "The `mcp` package is not installed"

You installed the runner profile but not the MCP extra:

```bash
pip install -e ".[runner,mcp]"
```

### Inline review fails with HTTP 422

GitHub rejects inline comments on lines that aren't in the diff. The
findings sanitizer should drop these client-side, but a custom prompt
can produce out-of-range entries. Check the runner log for
`Dropping finding on …` — every drop is logged.

### Sphinx build complains about CJK punctuation

If you're editing the Chinese docs and see `Inline literal start-string
without end-string`, the culprit is usually a CJK paren or em-dash
directly adjacent to ``code`` or `**bold**`. Insert a `\ ` (backslash +
space) zero-width separator:

```rst
``foo``\ ──不要這樣
```
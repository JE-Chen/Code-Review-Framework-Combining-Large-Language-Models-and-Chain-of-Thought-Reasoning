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
uvicorn codes.run.fastapi_server:app --host 0.0.0.0 --port 8000
```

Reverse-proxy this behind nginx / Cloudflare Access with TLS. Confirm:

```bash
curl https://my-host:8000/healthz   # → {"status": "ok", "model": "..."}
```

**In the repo:**

Add `.prthinker.yaml`:

```yaml
backend: remote
remote:
  url: https://my-host:8000
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
| `PRTHINKER_BACKEND_URL` | `https://my-host:8000` |
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
  url: https://my-host:8000
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
uvicorn codes.run.fastapi_server:app --host 0.0.0.0 --port 8000
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

| Flag                  | Env var                         | Default | Extra cost          |
| --------------------- | ------------------------------- | ------- | ------------------- |
| `--reply-to-author`   | `PRTHINKER_REPLY_TO_AUTHOR`    | off     | 1 platform API call |
| `--counterfactual`    | `PRTHINKER_COUNTERFACTUAL`     | off     | +1 backend call /file |
| `--provenance`        | `PRTHINKER_PROVENANCE`         | off     | larger prompt + output |
| `--judge`             | `PRTHINKER_JUDGE`              | off     | +1 backend call /file |
| `--self-correct`      | `PRTHINKER_SELF_CORRECT`       | off     | +1 backend call /file |

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

### Stacking all of them at once

For a research-grade run on a single PR:

```bash
prthinker review-pr --repo o/r --pr-number 42 \
    --per-file --inline-review \
    --reply-to-author --counterfactual --provenance \
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

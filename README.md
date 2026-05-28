# prthinker

**English** · [繁體中文](READMEs/README.zh-TW.md) · [简体中文](READMEs/README.zh-CN.md)

> A Chain-of-Thought code review framework for GitHub PRs, backed by a
> fine-tuned Qwen3-Coder model with retrieval-augmented prompting.

`prthinker` reads a Pull Request diff, runs a five-step Chain-of-Thought
review, and posts a structured summary plus one-click `suggestion` blocks
back to the PR. It learns from each repo's history — dismissed comments
are filtered out next time, accepted suggestions are surfaced as in-context
exemplars — and can act as a required status check before merges.

## What you get

- **Five-step CoT pipeline** — first_summary → first_code_review → linter →
  code_smell → total_summary, plus an optional per-file inline-findings
  step that emits structured JSON.
- **Per-file inline review** with GitHub `suggestion` blocks that PR
  authors can apply with one click.
- **RAG over global rules + per-repo `--rules-dir`** for team-specific
  coding standards.
- **Two learned corpora**: `dismissed.jsonl` (filters repeats), `accepted.jsonl`
  (top-K exemplars injected into the prompt).
- **CI failure signals**: failed-job tail logs are prepended to the diff so
  the reviewer can correlate findings with observed test failures.
- **Pre-merge Check Run gate** — block merges when error-severity findings
  exist, wire into branch protection.
- **Pluggable backends**: in-process local Hugging Face causal-LM
  (Qwen / Llama / Mistral / CodeLlama, …) with optional LoRA +
  quantization; the project's own FastAPI inference server; any
  OpenAI-Chat-Completions endpoint (OpenAI, Azure OpenAI, vLLM,
  Ollama `/v1`, LM Studio, Together, Groq, DeepInfra, OpenRouter, …);
  or Anthropic Claude (Messages API).
- **Cost + latency telemetry** — SQLite-backed prompt cache (`--cache`)
  with content-hash invalidation, plus per-call telemetry (`--telemetry`)
  that records tokens, latency, cache-hit status and estimated USD cost.
  `prthinker stats` aggregates by backend / model.
- **`.prthinker.yaml` repo-level config** — pin backend, gate threshold,
  cache + telemetry, per-repo rules in one PR-reviewable file. Secrets
  always come from env vars, never the YAML.
- **Secret redaction** — `--redact-secrets` scrubs AWS / GitHub / OpenAI
  / Anthropic / Stripe / Slack / JWT / PEM keys from the diff before any
  paid backend call. Idempotent, cache-friendly, never logs content.
- **MCP server** — `prthinker mcp` exposes the pipeline as a Model
  Context Protocol stdio server so Claude Desktop, Cursor, Continue,
  Cline, and Zed can run reviews from inside the IDE.

### Research-grade extensions (opt-in)

Four mechanisms most LLM-code-review systems do not ship. All require
`--inline-review`; per the project's no-fabrication rule we publish
the framework only — measured benchmark numbers are future work.

- **Adversarial robustness** (`prthinker adversarial-eval`) — runs a
  prompt-injection corpus across four attack families
  (direct injection / encoded payload / split injection / role hijack)
  and records every per-call outcome to SQLite. The bundled
  `seed.jsonl` is a seed, **not** a benchmark.
- **Closed-loop multi-turn dialogue** (`--reply-to-author`) — fetches
  the PR author's replies to the last prthinker summary comment and
  injects them as *Prior dialogue* into the inline-findings prompt, so
  the next review either drops, refines, or rebuts findings the author
  already addressed.
- **Counterfactual review** (`--counterfactual`) — for findings that
  are *design choices* rather than bugs, surfaces competing
  implementations and a small trade-off matrix instead of one "do X".
- **Provenance / audit trail** (`--provenance`) — every finding gains
  a `provenance` payload citing the RAG rule, accepted-example, or
  diff line(s) that informed it, with an optional model
  self-confidence in [0, 1]. A bad citation never drops a real finding.

See [`docs/concepts/research-extensions.rst`](docs/concepts/research-extensions.rst)
for the design write-up.

## Quickstart

```bash
# Editable install with just the runner deps (no torch/transformers)
pip install -e ".[runner]"

# Review a local diff against a remote inference server
prthinker review-file my-change.diff \
    --backend remote \
    --remote-url https://my-host:8000 \
    --per-file --inline-review

# Review a PR end-to-end (used by the GitHub Action)
prthinker review-pr \
    --repo owner/name --pr-number 42 \
    --backend remote --remote-url https://my-host:8000 \
    --gate-on error --include-ci-signals

# …or use OpenAI / Azure / vLLM / Ollama via the OpenAI-compat backend
prthinker review-pr --repo o/r --pr-number 42 \
    --backend openai \
    --openai-base-url http://localhost:11434/v1 \
    --openai-model llama3.1:8b \
    --openai-api-key ollama

# …or use Anthropic Claude
prthinker review-pr --repo o/r --pr-number 42 \
    --backend anthropic \
    --anthropic-model claude-sonnet-4-6 \
    --anthropic-api-key "$ANTHROPIC_API_KEY"

# …or turn on every research-grade extension at once
prthinker review-pr --repo o/r --pr-number 42 \
    --per-file --inline-review \
    --reply-to-author --counterfactual --provenance \
    --judge --self-correct

# Stress-test backend robustness against prompt-injection patterns
prthinker adversarial-eval \
    --corpus prthinker/adversarial_corpus/seed.jsonl \
    --outcomes-path .prthinker/adversarial.sqlite \
    --backend openai --openai-model gpt-4o-mini
```

To deploy the inference server (requires a GPU and the heavier extras):

```bash
pip install -e ".[server]"
uvicorn codes.run.fastapi_server:app --host 0.0.0.0 --port 8000
```

## GitHub Actions

Copy `.github/workflows/prthinker.yml`, then set two repo secrets:

| Secret               | Purpose                                |
| -------------------- | -------------------------------------- |
| `PRTHINKER_BACKEND_URL`    | Base URL of your FastAPI server        |
| `PRTHINKER_BACKEND_API_KEY`| Bearer token (optional)                |

The workflow fires on `pull_request` opened/synchronize/reopened and
upserts a single collapsible review comment.

## Documentation

- **[`setup.md`](READMEs/setup.md)** — comprehensive setup walkthrough (six
  scenarios, every env var, troubleshooting).
- **[`features.md`](READMEs/features.md)** — full feature catalog.
- **[`docs/`](docs/)** — Read-the-Docs-style deep-dives (English +
  Traditional + Simplified Chinese).

Full documentation lives in [`docs/`](docs/) and is published via Read the
Docs:

- **Guide** — installation, quickstart, configuration, GitHub Actions
- **Concepts** — architecture, pipeline, RAG, corpora, CI signals, the gate
- **Reference** — CLI, HTTP API, Python API

To build the docs locally:

```bash
pip install -r docs/requirements.txt
sphinx-build -b html docs docs/_build/html
```

## Repo layout

```
prthinker/        The standalone Python package (Strategy/Factory/Registry)
codes/run/           Original scripts; cot.py and fastapi_server.py call the package
codes/run/CoT_Prompts/  Prompt templates (single source of truth)
codes/train/         LoRA fine-tuning scripts (Qwen3.1-7B, Qwen2.5-Coder-7B, Qwen3-30B, Qwen3-Coder-30B)
codes/util/          Model loading + FAISS retrieval utilities
datas/               Test data, RAG rule documents
paper/               Manuscript + slide build
.github/workflows/   prthinker.yml — the GHA integration
docs/                Sphinx documentation
```

## Citation

If you use this framework in academic work, please cite the underlying paper
(`paper/`). The Read the Docs site links to the manuscript.

## License

See [LICENSE](LICENSE).

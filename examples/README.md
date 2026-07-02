# Examples

## `multi-model-review.sh` — agent-CLI reviewers + arbitration panel

Three ready-to-adapt invocations:

1. **Local review via the `claude` CLI** (`--backend claude-cli`) — the
   staged diff goes in over stdin and `--claude-cli-allowed-tools
   "Read,Grep,Glob"` grants the CLI read access to the working tree, so
   the review can consult surrounding code with the full local toolchain.
2. **Local review via the `codex` CLI** (`--backend codex-cli`) — runs
   `codex exec --json` headless with a `read-only` sandbox.
3. **Multi-model PR review** — the primary backend produces the inline
   findings, then `--arbitration --arbitration-backends
   claude-cli,codex-cli` has both CLIs vote confirm/reject on every
   finding; the majority decides what gets posted. Arbitration fails
   open: a crashed arbiter abstains and unvoted findings are kept.

All of it is opt-in — without these flags the reviewer runs exactly as
before.

## `prthinker.downstream.yml` — adopt PRThinker in another repository

A ready-to-copy GitHub Actions workflow that gives any repository the full
PRThinker review pipeline **without vendoring the prthinker source**. The
runner is installed from git, so your repo only needs this one file plus a
couple of secrets.

### Setup

1. Copy `prthinker.downstream.yml` to `.github/workflows/prthinker.yml` in
   your repository.
2. Edit `PRTHINKER_PKG` at the top to pin the prthinker version (a tag or
   commit SHA you trust).
3. Choose a backend and add the matching repository secrets under
   **Settings → Secrets and variables → Actions**:
   - **Mode A — self-hosted FastAPI server** (default): set
     `PRTHINKER_BACKEND_URL` and `PRTHINKER_BACKEND_API_KEY`.
   - **Mode B — a hosted LLM** (OpenAI / Anthropic / Azure / vLLM / Ollama /
     Together / Groq / …): set `PRTHINKER_BACKEND` to `openai` or
     `anthropic` in the top-level `env`, follow the inline "Mode B" comments
     in the `review` job (add the API key, turn RAG off, drop the healthz
     preflight). No server to deploy.

`GITHUB_TOKEN` is provided automatically by Actions.

### What you get

Per-file matrix review with inline findings, a consolidated summary comment,
a gate / check-run, PR labels, the incremental skip cache (unchanged files
reuse their prior review), the Copilot-style **pre-review PR summary**, and
**per-PR auto-cancel** (a new commit supersedes the PR's own in-flight run).

### Notes

- The `[runner]` extra is light (httpx + pydantic + PyYAML) — no torch or
  faiss is downloaded.
- Learned corpora, the repo knowledge graph, and caches start empty in a new
  repo and build up per-PR over time; the features that draw on them degrade
  gracefully until then.
- This file lives under `examples/` on purpose so it is **not** executed in
  this repository; it only runs once copied into a downstream repo's
  `.github/workflows/`.

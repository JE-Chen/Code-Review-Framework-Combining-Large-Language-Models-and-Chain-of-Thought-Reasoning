#!/usr/bin/env bash
# Multi-model review — local agent CLIs as reviewers plus an arbitration panel.
#
# Prerequisites:
#   pip install "prthinker[runner]"
#   The `claude` and/or `codex` CLIs installed and authenticated locally.
#
# Every feature shown here is opt-in; without the flags the reviewer
# behaves exactly as before (single backend, no arbitration).
set -euo pipefail

# --- 1) Local review, no forge needed -------------------------------------
# The claude CLI reviews the staged diff. --claude-cli-allowed-tools grants
# it read access to the working tree (the full local toolchain), so it can
# open the files around the diff instead of judging the hunks in isolation.
git diff --cached | prthinker review-file - \
    --backend claude-cli \
    --claude-cli-allowed-tools "Read,Grep,Glob" \
    --claude-cli-workdir . \
    --no-rag

# --- 2) Same review through the codex CLI ---------------------------------
# codex exec runs headless with a read-only sandbox: it may read the repo
# (-C sets the directory) but cannot mutate it.
git diff --cached | prthinker review-file - \
    --backend codex-cli \
    --codex-cli-workdir . \
    --codex-cli-sandbox read-only \
    --no-rag

# --- 3) Multi-model PR review with arbitration ----------------------------
# The primary backend (here the project's remote server) produces the
# findings; the claude and codex CLIs then vote confirm/reject on each
# finding and the majority decides what gets posted. Arbitration fails
# open — a crashed arbiter abstains, a finding nobody voted on is kept.
prthinker review-pr \
    --repo owner/name --pr-number 42 --github-token "$GITHUB_TOKEN" \
    --backend remote --remote-url "$PRTHINKER_REMOTE_URL" \
    --per-file --inline-review \
    --arbitration \
    --arbitration-backends claude-cli,codex-cli \
    --arbitration-strategy majority

# Variants:
#   --arbitration-backends claude-cli,codex-cli,openai   # add an API judge
#   --arbitration-strategy unanimous                     # any reject drops
#   --arbitration-strategy any                           # one confirm keeps

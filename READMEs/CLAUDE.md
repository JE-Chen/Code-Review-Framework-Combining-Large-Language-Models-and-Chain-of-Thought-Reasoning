# Project Guidelines — prthinker

## Project Overview

`prthinker` is a Chain-of-Thought code review framework that drives a
fine-tuned Qwen3-Coder model through a fixed five-step review pipeline,
augments it with RAG over global + per-repo rule packs, and posts the
result back to a GitHub PR as both a summary comment and inline
`suggestion` blocks. Two learned corpora (`dismissed.jsonl` /
`accepted.jsonl`) shape future runs, and the reviewer can act as a
required Check Run before merges.

### Key Directories

- `prthinker/` — the standalone Python package (Strategy / Factory /
  Registry / Repository / DI patterns).
- `prthinker/backends/` — four interchangeable backends
  (LocalHFBackend / RemoteHttpBackend / OpenAICompatBackend /
  AnthropicBackend) behind a single `InferenceBackend` ABC.
- `prthinker/platforms/` — GitHub + GitLab adapters behind
  `PlatformAdapter` (diff / comments / inline review / gate / dialogue).
- `prthinker/{adversarial,counterfactual,dialogue,findings,sandbox,
  review_cache,reproducibility,personas,risk_score,diff_entropy,
  dep_upgrade,api_consistency,pr_classifier,lessons,finding_clusters,
  repo_kg,incremental_save}.py` — research-grade extension modules.
  Each is opt-in behind a CLI flag (see
  `docs/en/concepts/research-extensions.rst`).
- `prthinker/adversarial_corpus/` — hand-authored seed corpus for the
  prompt-injection robustness suite (`seed.jsonl` — labelled "seed,
  NOT a benchmark" per `paper/paper_inserts.md`'s no-fabrication rule).
- `codes/run/` — original entry points (`cot.py`, `skills.py`,
  `fastapi_server.py`). `cot.py` is now a thin wrapper over the package;
  `fastapi_server.py` is the inference server.
- `codes/run/CoT_Prompts/` — prompt templates; single source of truth.
- `codes/run/Skills/` — Skills-style prompts (used by `skills.py`).
- `codes/train/` — LoRA fine-tuning scripts (Qwen3.1-7B, Qwen2.5-Coder-7B,
  Qwen3-30B, Qwen3-Coder-30B).
- `codes/util/` — `hf_model_util.py` (model loading), `faiss_util.py`
  (FAISS-backed RAG).
- `datas/` — test data, RAG rule documents, prompt copies.
- `docs/` — Sphinx documentation, single tree containing all three
  languages under `docs/{en,zh-TW,zh-CN}/`.
- `paper/` — manuscripts (`論文_v*.docx` thesis, `TCSE_v*.docx` conference
  short paper), the python-docx tooling that produces them
  (`_rewrite_*.py`, `_check_rules.py`, `_fix_fonts/_fix_semicolon/
  _fix_dash.py`, `_dump_*.py`), the authoritative rewrite brief
  (`REWRITE_BRIEF.md`), and the slide build (pptxgenjs Node project).
  Manuscript edits go through the `paper-author` subagent.
- `.github/workflows/` — `prthinker.yml` GHA integration with a
  preflight ping + graceful skip when the backend is unreachable.

### Tech Stack

Python 3.12+, PyTorch, Transformers, PEFT (LoRA), FAISS, FastAPI,
Pydantic v2, httpx, Sphinx + Read the Docs.

### Research-grade extensions (opt-in, framework only)

Seventeen mechanisms most LLM-code-review systems do not ship. Per
`paper/paper_inserts.md`'s no-fabrication rule, code + corpora + unit
tests are delivered; **no benchmark numbers are bundled**.

- Adversarial robustness (`prthinker adversarial-eval`).
- Closed-loop multi-turn dialogue (`--reply-to-author`).
- Counterfactual review (`--counterfactual`).
- Provenance / audit trail (`--provenance`).
- Force-push differential review (`--diff-since-last`).
- Suggestion sandbox verifier (`--verify-suggestions`).
- Cross-language API drift detection (`--api-consistency`).
- PR-type adaptive review (`--pr-classify`).
- Reproducibility signal (`--reproducibility-check`).
- Dependency-upgrade impact (`--dep-upgrade-check`).
- Reviewer personas + conflict surfacing (`--personas`).
- Risk-weighted attention (`--risk-weighted`).
- Diff entropy / "diff bomb" detector (`--diff-entropy`).
- Active-learning derived lessons (`derive-lessons` + `--lessons`).
- Cross-PR finding clustering (`discover-rules`).
- Repo knowledge graph (`build-kg` + `--kg-ground`).
- Incremental per-file save / crash-safe partial results
  (`--incremental-save-dir`).

When extending: every new mechanism must (1) be opt-in behind a CLI
flag, (2) ship pure-logic unit tests, (3) update
`docs/en/concepts/research-extensions.rst` in the same commit, and
(4) make NO empirical claim in the docs.

---

## Definition of Done (HARD REQUIREMENT)

Every feature, bug fix, refactor, or behaviour change MUST satisfy ALL of
the following before it can be committed. No exceptions — incomplete
work stays on the working copy until the gates pass.

1. **Unit tests are written and they pass.** New code without new tests
   is incomplete; the commit fails this gate. See the **Unit Tests**
   section below for the exact coverage expectations.
2. `py -m pytest tests/` runs clean (or only skips that already existed
   before the change).
3. `py -m ruff check .` reports no new errors.
4. `py -m bandit -c pyproject.toml -r prthinker/` reports
   `No issues identified`.
5. `py -m sphinx -b html -q docs docs/_build/html` builds with zero
   errors. (Warnings tolerated — RTD does not fail on warnings — but a
   real ERROR fails the gate.)
6. The commit message contains no AI tool/model names and no
   `Co-Authored-By` line.

When you finish editing code, work through this list explicitly before
staging. If a gate fails, fix it — do not ship around it. Skipping tests
"to come back later" is not allowed because later never happens and the
gap compounds.

---

## Git Commit & PR Rules

### Identity (Strict)

- NEVER mention any AI assistant, model, code generator, or automation
  tool in commit messages, branch names, PR titles, PR bodies, or code
  comments (this includes Claude / Claude Code / GPT / Copilot / any
  other AI / model identifier).
- NEVER add `Co-Authored-By:` trailers of any kind.
- NEVER add marketing or attribution lines.
- The git-configured user is the only author.

### Commit Messages

- Write in English, imperative mood.
- Format: `<type>: <short description>` (≤ 72 chars).
- Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`,
  `security`.
- Body (optional) explains **why**, not what. Wrap at 72 chars.
- Examples:
  - `feat: Add step-by-step analysis to CoT pipeline`
  - `fix: Correct threshold filtering in RAG retrieval`
  - `refactor: Extract model loading into shared factory`
  - `perf: Enable 4-bit quantization for 30B model`
  - `security: Validate uploaded code paths against traversal`

### PR Rules

- Title uses the same `<type>: <description>` format.
- Body must include: **Summary**, **Changes**, **Test Plan**.
- Do not reference any AI tool, assistant, or automated authoring source.

### Branch Naming

- `feat/<short-description>`
- `fix/<short-description>`
- `refactor/<short-description>`
- `security/<short-description>`
- `docs/<short-description>`

---

## Code Quality Requirements

### Design Patterns (Mandatory)

These are not suggestions — they are the load-bearing structure of the
package. New code that violates these is rejected at review.

1. **Strategy Pattern** — Pipeline switching (CoT / Skills / Single
   Prompt) and backend selection must be expressed as interchangeable
   strategies. No hardcoded `match/case` branches in execution code.
   Concrete: `prthinker.backends.base.InferenceBackend` with four
   implementations — `LocalHFBackend` (any HF causal-LM in-process, with
   LoRA + quantization), `RemoteHttpBackend` (the project's own FastAPI
   `/ask` server), `OpenAICompatBackend` (any OpenAI-Chat-Completions
   endpoint: OpenAI, Azure, vLLM, Ollama /v1, LM Studio, Together, Groq,
   …), and `AnthropicBackend` (Claude Messages API). Adding a new
   provider means adding one class + one factory branch.
2. **Factory Pattern** — All model instantiation (tokenizer + base model
   + LoRA adapter + quantization) must go through a single factory entry
   point (`load_hf_model()` for models, `create_backend()` for
   backends). Do not construct models ad-hoc.
3. **Template Method Pattern** — Prompt construction always goes through
   template builders (`build_global_rule_template`,
   `format_examples_block`, etc.). Never inline prompt strings in
   execution code. Each `ReviewStep` subclass implements `build_prompt`.
4. **Registry Pattern** — New review steps, new models, and new
   pipelines self-register via `@register_step` and similar decorators.
   Adding one must not require editing existing files (Open/Closed).
5. **Repository Pattern** — All RAG retrieval routes through
   `prthinker.rag.RAGRetriever` implementations. FAISS calls outside
   `FaissRAGRetriever` are forbidden.
6. **Dependency Injection** — Pass backends, retrievers, filters, stores
   as parameters to `CoTPipeline`; do not import singletons inside
   helpers.

### SOLID and Engineering Practices

- **SRP** — One module, one concern. Prompt templates →
  `CoT_Prompts/` or `Skills/`. Model utilities → `util/`. Execution
  flow → `run/`. Domain orchestration → `prthinker/`.
- **OCP** — Add a new CoT step by adding a new prompt file + a step
  class with `@register_step`, not by modifying existing steps.
- **LSP / ISP** — Pipeline strategies share the same minimal interface
  (`run(diff) -> ReviewResult` or `run_per_file(diff)`); do not leak
  pipeline-specific arguments into the base class.
- **DIP** — Pipeline depends on `InferenceBackend` and `RAGRetriever`
  abstractions, never on concrete classes.
- **DRY** — Duplicated model-loading or RAG-injection blocks must be
  consolidated into shared factories or utilities.
- **YAGNI** — Do not add hooks, flags, or abstractions for hypothetical
  future requirements.
- **Fail Fast** — Validate config and inputs at module load. Raise on
  missing model paths, missing prompt templates, or invalid thresholds
  rather than silently degrading.
- **Pure Functions Where Possible** — Prompt builders and post-processors
  should be pure (no I/O, no global state).

### Performance

- **Models load once** at module level. Never reload per request or per
  file.
- **Quantization mandatory** for large models: 4-bit (NF4 + double quant
  + bf16 compute) for ≥30B; 8-bit acceptable for smaller models.
- Wrap all gradient-free inference and embedding paths with
  `@torch.no_grad()`.
- Call `model.eval()` immediately after load.
- Use `device_map="auto"` for multi-GPU; pin `torch_dtype=torch.bfloat16`
  on Ampere+ GPUs.
- Reuse a single tokenizer instance per model.
- Batch inference when input lists are available; do not loop per-sample
  if a batch path exists.

### RAG / FAISS

- Build the FAISS index **once** at import time. Never rebuild per query.
- Use `IndexFlatIP` with L2-normalized vectors (cosine similarity).
- Apply the relevance threshold before injecting rules. The cutoff is
  **per embedding model** (`codes/util/embedding_config.py`): 0.32 for
  the default `google/embeddinggemma-300m`, 0.7 for the legacy
  `Qwen/Qwen3-Embedding-4B` (`EMB_MODEL` selects). Never reuse one
  model's threshold with another — score distributions differ
  (see `codes/run/embedding_threshold_calibration.md`).
- EmbeddingGemma loads through sentence-transformers
  (`encode_query` / `encode_document`); bare `AutoModel` mean pooling
  is only correct for the legacy Qwen path.
- Embedding `max_length=2048` is intentional; do not raise without GPU
  benchmarking.
- Cache embeddings of static rule documents on disk; recompute only when
  source changes.
- Dismissed/accepted corpora are embedded **once** at server startup,
  reused across all `/review` calls.

### I/O

- Stream review results to disk per step (incremental write) to avoid
  losing work on long CoT runs.
- Generation cap: `max_new_tokens=32768`. Do not raise without memory
  testing.
- Use buffered writes; close file handles deterministically (`with`
  blocks).

### Code Style & Conventions

- Follow PEP 8 strictly.
- Type hints on **all** function signatures.
- Use `pathlib.Path` for all filesystem operations; never `os.path` or
  string concatenation.
- Prefer f-strings over `.format()` or `%` for new code.
- `snake_case` for functions/variables, `PascalCase` for classes,
  `UPPER_SNAKE_CASE` for constants.
- Google-style docstrings for public functions; one-line module
  docstrings on every public module.
- All file I/O must specify `encoding="utf-8"`.

### Imports

- Order: standard library → third-party → local. Separate groups with a
  blank line.
- No wildcard imports (`from module import *`).
- Heavy ML imports (torch, transformers, faiss) inside backend
  constructors only — runner-profile installs must not pay the import
  cost.

### Comments

- Default to **no comments**. Add only when the **why** is non-obvious
  (constraint, invariant, workaround).
- Do not narrate **what** the code does — names already do that.
- Do not reference the current task, fix, or callers
  ("used by X", "added for the Y flow", "handles the case from issue #123").

### Code Hygiene

- Delete unused code aggressively — dead functions, commented-out blocks,
  unreferenced imports, unused variables, stale flags, half-finished
  experiments. If something is unreachable or unreferenced, remove it.
- No backwards-compatibility shims, re-exports, or `_legacy_*` aliases
  unless an external consumer is documented.
- Do not introduce abstractions, helpers, or config knobs that the
  current code does not use.
- Prefer editing existing files over creating new ones.

---

## Security (Mandatory — Maximum Bar)

### Input & Path Safety

- Treat **all** code/text passed to the framework as untrusted input.
  Never `eval`, `exec`, or `pickle.load` on it.
- Validate and normalize file paths with `Path.resolve()`. Reject paths
  that escape the intended working directory (path traversal).
- Reject filenames containing null bytes, control characters, or shell
  metacharacters when they are used in subprocess calls.

### Subprocess & Shell

- Never use `shell=True` with untrusted input. Pass arguments as a list.
- Avoid `os.system`. Prefer `subprocess.run([...], check=True, timeout=...)`.

### Secrets & Credentials

- No hardcoded API keys, tokens, or passwords. Read from environment
  variables (`PRTHINKER_REMOTE_API_KEY`, `GITHUB_TOKEN`, etc.) or a secrets
  manager.
- Never log secrets, full request bodies, or model API keys. Redact
  before logging.
- `.env`, `*.key`, `*.pem`, credentials JSON, and the harvested
  `*.jsonl` stores (which may contain quoted code) must remain in
  `.gitignore`.

### Network & Web

- All `urllib.request.urlopen` calls (if added) MUST go through a
  module-level `_https_urlopen` guard that parses the URL with
  `urllib.parse.urlparse` and rejects any scheme other than `https`
  (SonarQube `python:S5332`, bandit `B310`).
- Do NOT call `urllib.request.urlopen` directly in new code. Use
  `httpx.Client` (already pinned in `pyproject.toml`) instead.
- Hugging Face Hub downloads MUST pin a revision (`revision=<sha-or-tag>`,
  bandit `B615`).
- Pin dependency versions in `pyproject.toml`.
- Validate request bodies with Pydantic models; never trust raw JSON.
- Set request size limits and timeouts on all endpoints.
- Disable CORS wildcards in production; whitelist specific origins.
- Sanitize any model output that is rendered as HTML (XSS).
- Do not echo internal stack traces to clients; log internally, return a
  generic error.

### GitHub Integration

- The bundled workflow asks for the **minimum** permissions needed
  (`contents: read`, `pull-requests: write`, `checks: write`,
  `actions: read`). Do not broaden.
- Authenticate to the GitHub REST API exclusively via
  `Authorization: Bearer ${GITHUB_TOKEN}`. The token is provided by
  Actions and must never be echoed to logs.
- Diff content sent to the remote inference server may contain
  secrets that slipped past `.gitignore`. Production deployments should
  add a redaction pass on the runner before sending — track this in the
  paper / future work.

### Data Handling

- Open files with explicit `encoding="utf-8"` and explicit modes; do not
  rely on platform defaults.
- Validate JSON/YAML input with schemas before use.
- Use parameterized queries for any future database access; never
  string-concatenate SQL.

### Supply Chain

- Vet new dependencies; prefer well-maintained packages with active
  security advisories.
- Run dependency audits periodically (e.g., `pip-audit`).

---

## Unit Tests

Tests are not optional polish — they are part of the change. A feature
without tests is an incomplete feature and MUST NOT be committed. This
rule applies equally to bug fixes (regression test required) and
refactors (existing behaviour must remain green; add a test if the
refactor exposes a previously untested path).

### Required coverage for every change

- **Happy path** — the new code does what it advertises on a
  representative input.
- **Edge cases** — empty inputs, single-element inputs, max-size inputs,
  None / missing keys.
- **Error handling** — every `except` branch is exercised; invalid
  inputs raise the documented exception or are clamped to the documented
  safe range.
- **Boundary conditions** — values just inside and just outside any
  range, threshold, or enum (especially `--gate-on` floors and RAG /
  dismissed / accepted thresholds). Off-by-one defects live here.
- **Round-trips** — anything that serialises
  (`InlineFinding`, `DismissedExample`, `AcceptedExample`, the
  `ReviewRequest`/`ReviewResponse` pair) needs a
  `to_dict → from_dict → equal` test.

### Required test types

- **Pure-helper tests.** Extract pure logic out of network / GPU paths
  into helper functions (see `prthinker.diff.parse_unified_diff`,
  `prthinker.findings.parse_inline_findings`,
  `prthinker.checks.evaluate_gate`) and unit-test those directly. No
  network, no GPU.
- **FakeBackend integration test.** Use a stub `InferenceBackend` that
  returns canned strings to exercise `CoTPipeline.run` and
  `run_per_file` end-to-end without loading a model.
- **HTTP API contract test.** Use FastAPI's `TestClient` against
  `codes/run/fastapi_server.py` with a fake backend / fake retriever to
  assert request/response shapes.
- **CLI argparse test.** Parser shape (flag presence, defaults) is
  tested at the argparse level so adding a flag can't silently regress
  the wire format.

### Mechanics

- Use `pytest` style. Module-level functions and `Test*` classes are
  both fine; follow the style of the file you're adding to.
- Test file naming: `tests/test_<module_name>.py`. One test module per
  production module.
- Use shared fixtures in `tests/conftest.py` (`fake_backend`,
  `tmp_dismissed_store`, `tmp_accepted_store`, `tmp_rules_dir`). Do not
  roll your own.
- Never write to a real user's filesystem outside `tmp_path`.
- Run `py -m pytest tests/` before committing. If a test was already
  skipping because of a missing optional dependency, leave it skipping —
  but every NEW test must run, not skip.

### Tests that need GPU / network

GPU-only or network-only tests must be marked with
`@pytest.mark.skipif` against a `PRTHINKER_HAS_GPU` / `PRTHINKER_HAS_NETWORK`
environment variable check. CI's default profile (no GPU) must still
report green; the GPU lane is a separate workflow.

---

## Linter & Static Analysis Compliance

All new and modified code MUST pass the following rules without warnings.
These mirror the default rule sets of SonarQube, Codacy, pylint, flake8,
ruff, and bandit for Python.

### Complexity & Size

- **Cognitive complexity** ≤ 15 per function (SonarQube `python:S3776`).
- **Cyclomatic complexity** ≤ 10 per function (pylint `R1260`).
- **Function length** ≤ 75 logical lines.
- **File length** ≤ 1000 lines (SonarQube `python:S104`).
- **Parameter count** ≤ 7 per function (SonarQube `python:S107`). Group
  related params into a dataclass (`Config`, `LocalBackendConfig`,
  `RemoteBackendConfig`, `GitHubConfig`) when exceeded — there are
  existing examples to copy.
- **Nesting depth** ≤ 4 levels (SonarQube `python:S134`). Use early
  returns / guard clauses.
- **Boolean expression complexity** ≤ 3 operators in one expression
  (SonarQube `python:S1067`). Extract to named booleans.
- **Return statements** ≤ 6 per function (pylint `R0911`).
- **Local variables** ≤ 15 per function (pylint `R0914`).

### Duplication

- Do NOT copy-paste blocks of ≥ 3 statements across functions or files
  (SonarQube `common-python:DuplicatedBlocks`). Extract shared logic to
  `prthinker/`.
- Do NOT declare the same string literal ≥ 3 times (SonarQube
  `python:S1192`). Assign to a module-level constant. Examples in this
  repo: `_API_ROOT`, `_USER_AGENT`, `_SEVERITY_BADGE`.

### Naming (PEP 8)

- `snake_case` for functions, methods, variables, modules.
- `PascalCase` for classes.
- `UPPER_CASE_WITH_UNDERSCORES` for module-level constants.
- `_leading_underscore` for private attributes / methods.
- No single-letter names except loop indices (`i`, `j`, `k`) or
  well-known math symbols (`x`, `y`, `z`, `n`, `k`).

### Errors & Exceptions

- Never use bare `except:` — always specify the exception type
  (SonarQube `python:S5754`, flake8 `E722`).
- Never write `except Exception: pass` without a logged reason and
  comment explaining why it is safe.
- Never catch `BaseException` directly (covers `KeyboardInterrupt`,
  `SystemExit`).
- Raise specific exception types (`ValueError`, `TypeError`,
  `FileNotFoundError`) instead of generic `Exception`.
- Chain exceptions with `raise X from err` to preserve context
  (ruff `B904`).
- Never use `assert` for runtime validation; use explicit `raise`. The
  exception is in tests, where `assert` is the standard.

### Code Smells

- No unused imports, variables, or function parameters (pyflakes `F401`,
  `F841`). Prefix intentionally unused params with `_`.
- No commented-out code. Delete it — git preserves history.
- No `print()` calls in production code; use `logging`. The CLI's stdout
  writes are intentional output, not logging.
- No `TODO` / `FIXME` / `XXX` left in merged code (SonarQube
  `python:S1135`). File an issue instead.
- No magic numbers — extract to `UPPER_CASE` constants (SonarQube
  `python:S109`). Exceptions: `0`, `1`, `-1`, `2` in obvious contexts;
  HTTP status codes; default chunk sizes documented inline.
- Use `is None` / `is not None` (never `== None` / `!= None`).
- Use `isinstance(x, T)` instead of `type(x) == T`.
- No mutable default arguments (`def f(x=[])`) — use `None` and assign
  inside (ruff `B006`).
- No global mutable state; if unavoidable, encapsulate in a module-level
  class or singleton.
- Prefer f-strings over `.format()` or `%`.
- Always use context managers (`with` blocks) for file / resource
  handles. `httpx.Client` must always be closed (use it as a context
  manager or explicitly call `.close()` in a `finally`).
- Prefer `dict.get(key, default)` over `if key in dict: ... else: ...`.

### Security (bandit / SonarQube `python:S*`)

- `pickle.load(s)` on untrusted data is forbidden (bandit `B301`,
  SonarQube `python:S5135`).
- `yaml.load` without `SafeLoader` is forbidden — use `yaml.safe_load`
  (bandit `B506`).
- MD5 / SHA-1 are forbidden for security purposes — use SHA-256+ or
  bcrypt / argon2 (bandit `B303`/`B304`). Allowed for cache keys / file
  de-duplication ONLY with `usedforsecurity=False`.
- `subprocess` with `shell=True` is forbidden when any argument comes
  from user input (bandit `B602`).
- Never use `eval`, `exec`, `compile` on dynamic input (bandit `B307`).
- Never use `tempfile.mktemp()` — use `tempfile.mkstemp()` or
  `NamedTemporaryFile` (bandit `B306`).
- Network binds must not use `0.0.0.0` unless intentional and documented
  (bandit `B104`). The FastAPI server's `0.0.0.0` default in
  documentation examples is for self-hosted deployments and is flagged
  separately.
- XML parsing must use `defusedxml`, never stdlib `xml.etree` on
  untrusted input.
- Random number generation for security must use `secrets`, not
  `random`.

### Typing & Documentation

- Public functions and methods MUST have type hints on parameters and
  return type.
- Public modules and classes MUST have a one-line docstring describing
  their purpose.
- Private helpers may omit docstrings if names are self-explanatory.
- Pydantic models in `prthinker.schemas` are the wire-format source
  of truth — when extending them, also update
  `docs/en/reference/http-api.rst` in the same commit.
- Multi-line docstrings follow the **D212 convention**: the summary
  line lives on the FIRST line, not the second. The mutually-exclusive
  D213 is disabled in both `pyproject.toml` `[tool.pydocstyle]` and
  `.prospector.yaml` so Codacy / Prospector / local pydocstyle all
  agree.

### Codacy / Prospector

The repo is wired to Codacy. After every push to `dev` / `main` and on
every PR, Codacy re-runs Prospector (which bundles pydocstyle, pylint,
mypy, Lizard) over the diff. Local config:

- `[tool.pydocstyle]` in `pyproject.toml` — D212 convention, D213
  disabled.
- `.prospector.yaml` at the repo root — same disable list plus a few
  pylint relaxations for the runner-profile lazy imports.

When Codacy flags a complexity issue (CCN > 8 or function > 50 LoC)
**do not** add a suppression comment — refactor by extracting helper
functions. The recent Codacy-fix commit (see `git log --grep=Codacy`)
is the reference pattern.

### Enforcement

Mentally check each function against the above rules before finalising.
If unavoidable rule violation (e.g., a third-party callback signature
forces extra parameters), add a `# noqa: <rule>` or equivalent
suppression with a brief justification comment on the same line.

---

## Suppression Comment Conventions

Use the right comment for the right tool. They are NOT interchangeable.

| Tool          | Comment form                          | Placement  | Notes                                                  |
| ------------- | ------------------------------------- | ---------- | ------------------------------------------------------ |
| ruff / flake8 | `# noqa: <CODE>` (e.g. `# noqa: S310`)| line-level | List specific codes — never bare `# noqa`.             |
| bandit        | `# nosec B<NNN>` (e.g. `# nosec B310`)| line-level | ruff's `# noqa` does NOT suppress bandit.              |
| SonarCloud    | `# NOSONAR`                           | line-level | Use for hotspots that cannot be config-skipped.        |
| pylint        | `# pylint: disable=<name>`            | line-level | Prefer refactor over suppression.                      |
| type: ignore  | `# type: ignore[<error-code>]`        | line-level | Always include the specific mypy/pyright code.         |

Every suppression MUST include a brief justification on the same line.
Unexplained suppressions will not pass review.

Project-wide skips (systemic false positives) live in `pyproject.toml`
under `[tool.bandit]` / `[tool.ruff]`. When adding a new skip, document
the reason in the comment next to it.

---

## Project-Specific Compliance Patterns

### Runner vs Server Dependency Surface

The same package targets two install profiles:

- **Runner** (`pip install -e ".[runner]"`) — `httpx`, `pydantic` only.
  Used by the GHA workflow on a default ubuntu-latest runner. **MUST
  NOT** import torch / transformers / faiss at module load. Lazy-import
  inside backend / retriever constructors.
- **Local** (`pip install -e ".[local]"`) — adds the full ML stack
  (`torch`, `transformers`, `accelerate`, `bitsandbytes`, `peft`,
  `faiss-cpu`, `numpy`). Used by developers / inference servers.

When adding a new module, check `pip install -e ".[runner]" && python -c
"import prthinker.<module>"` does not require torch. The CI gate
should verify this.

### Prompt Templates Are Source of Truth

Prompt files in `codes/run/CoT_Prompts/` are the single source of truth.
The package's `prthinker.steps` imports them — never inlines them.
When changing a prompt:

1. Edit only the file in `codes/run/CoT_Prompts/`.
2. Update any docs that quote the prompt verbatim
   (`docs/concepts/pipeline.rst`).
3. If the prompt now needs a new template slot, add it as a new field on
   `ReviewContext` and thread it through `CoTPipeline._run_one_file`.

### Corpora Are Append-Only

`harvest-dismissed` and `harvest-accepted` MUST be append-only. The
existing JSONL store is read at startup and lines are added at the end —
never overwrite, never sort, never rewrite. Re-running with `--max-prs
200` after `--max-prs 100` should be safe and produce a strictly larger
file.

### Wire-Format Compatibility

`prthinker.schemas` is the wire format between runner and server.
Breaking changes (renaming a field, changing a default) require:

1. A migration note in `docs/reference/http-api.rst`.
2. A version bump in `prthinker.__version__`.
3. A migration path documented in the release notes.

Additive changes (new optional field with a default) do not need any of
the above.

### GitHub Actions Permissions

The bundled `.github/workflows/prthinker.yml` lists the **minimum**
permissions for current features:

- `contents: read` — checkout.
- `pull-requests: write` — upsert summary comment, post inline review.
- `checks: write` — open + complete the Check Run gate.
- `actions: read` — fetch failed-job logs for CI signals.

Do not broaden these. New features that need additional permissions must
document the increase in their PR description.

---

## Defense Slides (paper/)

The thesis defense deck is generated by a Node.js wrapper that emits an
**editable** `slides.pptx` via `pptxgenjs`. Every text frame, table
cell, and shape stays editable in PowerPoint / Keynote / LibreOffice
Impress — do not replace this with a print-to-PDF or image-export path.

### Source of truth

- The highest-versioned `paper/論文_v*.docx` — the manuscript. Re-extract
  numbers from here when rebuilding slides; do not copy from older
  `slides.md` snapshots.
- `output/*.png` — system / training / CoT flow diagrams referenced by
  the deck.

### Build commands

```bash
cd gen-paper
npm install
npm run build      # node build_slides.js → slides.pptx
```

### Rules

- All slide content lives in `paper/build_slides.js`. Do not reintroduce
  a Marp / `slides.md` pipeline.
- Tables and bullet lists must be assembled with `addTable` / `addText`
  so reviewers can edit individual cells. Do not rasterize tables.
- Numbers (CRSCORE++, LLM Judge, human eval) must come from the latest
  manuscript tables; flag any drift before edits.
- Figures pulled from `../output/`; missing PNGs show a visible
  placeholder rather than failing silently.
- `paper/node_modules/` is build output — keep it out of git.

---

## Documentation

The user-facing docs live in `docs/` (Sphinx, RTD theme) and have three
language trees:

- `docs/` — English (primary).
- `docs/zh-TW/` — Traditional Chinese.
- `docs/zh-CN/` — Simplified Chinese.

When changing user-visible behaviour:

1. Edit the English page in `docs/`.
2. Translate the same change into `docs/zh-TW/` and `docs/zh-CN/` in the
   **same commit**. Stale Chinese docs are not allowed — they mislead
   readers and lose trust.
3. Build the unified docs tree locally:
   `py -m sphinx -b html -q docs docs/_build/html`
4. Verify zero errors (warnings OK). All three languages live in the
   same tree under `docs/{en,zh-TW,zh-CN}/`; one build covers them all.

---

## Common Commands

```bash
# Install dependencies (pick the profile you need)
pip install -e ".[runner]"   # thin client, no GPU
pip install -e ".[local]"    # full ML stack
pip install -e ".[server]"   # FastAPI server

# Run the CoT pipeline against the batch dataset (local GPU)
python -m codes.run.cot

# Start the FastAPI server
uvicorn codes.run.fastapi_server:app --host 0.0.0.0 --port 9000

# Rebuild the docker server image without OOM-killing cloudflared/sshd
# (stops old container -> caps flash-attn nvcc parallelism -> monitors
# RAM -> scans dmesg for oom-killer hits -> verifies boot guard saw
# flash_attention_2 / sdpa)
./docker/rebuild-server.sh
FLASH_ATTN_MAX_JOBS=8 ./docker/rebuild-server.sh   # hosts with more RAM

# Drive a one-off review
prthinker review-file path/to/code.py --backend remote --remote-url http://localhost:9000

# Bootstrap learned corpora
prthinker harvest-dismissed --repo owner/name --max-prs 100
prthinker harvest-accepted  --repo owner/name --max-prs 100

# Pre-commit gates
py -m pytest tests/
py -m ruff check .
py -m bandit -c pyproject.toml -r prthinker/

# Build docs (single tree, three languages as top-level sidebar sections)
py -m sphinx -b html -q docs docs/_build/html
```

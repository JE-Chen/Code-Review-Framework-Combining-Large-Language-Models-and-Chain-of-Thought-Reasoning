# Project Guidelines

## Definition of Done (HARD REQUIREMENT)

Every feature, bug fix, refactor, or behaviour change MUST satisfy ALL of the following before it
can be committed. No exceptions — incomplete work stays on the working copy until the gates pass.

1. **Unit tests are written and they pass.** New code without new tests is incomplete; the commit
   fails this gate. See the **Unit Tests** section below for the exact coverage expectations.
2. `py -m pytest tests/` runs clean (or only skips that already existed before the change).
3. `py -m ruff check .` reports no new errors.
4. `py -m bandit -c pyproject.toml -r prthinker/` reports `No issues identified`.
5. `py -m sphinx -b html -q docs docs/_build/html` builds with zero errors. Warnings are
   tolerated (Read the Docs does not fail on warnings) but a real ERROR fails the gate.
6. The commit message contains no AI tool/model names and no `Co-Authored-By` line.

When you finish editing code, work through this list explicitly before staging. If a gate fails,
fix it — do not ship around it. Skipping tests "to come back later" is not allowed because later
never happens and the gap compounds.

## Git Commits

- NEVER add `Co-Authored-By` lines to commit messages. All commits should only contain the commit
  message itself with no co-author attribution.
- NEVER mention "Claude", "Claude Code", "AI-generated", "GPT", "Copilot", or any AI tool / model
  name anywhere — including commit messages, PR titles, PR descriptions, code comments, and
  documentation.
- Commit message format: `<type>: <short description>` (≤ 72 chars), where type ∈
  `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `security`. Body explains **why**,
  not what; wrap at 72 chars.
- Branch naming: `feat/<short>`, `fix/<short>`, `refactor/<short>`, `security/<short>`,
  `docs/<short>`.

## Code Quality Requirements

### Design Patterns (Mandatory)

These are not suggestions — they are the load-bearing structure of the `prthinker` package. New
code that violates them is rejected at review.

1. **Strategy Pattern** — Pipeline switching (CoT / Skills / Single Prompt) and backend selection
   must be expressed as interchangeable strategies. No hardcoded `match/case` branches in
   execution code. Concrete: `prthinker.backends.base.InferenceBackend` with four implementations
   (`LocalHFBackend` / `RemoteHttpBackend` / `OpenAICompatBackend` / `AnthropicBackend`). Adding a
   new provider means adding one class + one factory branch.
2. **Factory Pattern** — All model and backend instantiation goes through a single factory entry
   point (`load_hf_model()` for models, `create_backend()` for backends). Do not construct
   models ad-hoc.
3. **Template Method Pattern** — Prompt construction always goes through template builders
   (`build_global_rule_template`, `format_examples_block`, etc.). Never inline prompt strings in
   execution code. Each `ReviewStep` subclass implements `build_prompt`.
4. **Registry Pattern** — New review steps and new platform adapters register themselves with
   the central registry. Steps go through `resolve_steps`; platforms go through
   `create_platform_adapter`. No direct imports from execution code.
5. **Repository Pattern** — Corpora access (`dismissed.jsonl`, `accepted.jsonl`, `lessons.jsonl`,
   `findings-index.sqlite`, `repo-kg.sqlite`) goes through repository classes
   (`DismissedExamplesStore`, `AcceptedExamplesStore`, `LessonsStore`, etc.). Callers never open
   the file / db directly.
6. **Dependency Injection** — Pipelines receive their backend and retriever via constructor; the
   pipeline does not know which concrete strategy it holds. Tests inject a `FakeBackend` /
   `NoOpRetriever`.

### Software Engineering Practices

- Separate concerns: keep transport (`backends/`), pipeline (`pipeline.py`, `steps.py`), corpora
  (`accepted.py`, `dismissed.py`, `lessons.py`), and platform (`platforms/`) in distinct layers.
- Write self-documenting code with clear naming; add comments only for non-obvious "why"
  explanations (a constraint, a workaround for a specific bug, a subtle invariant).
- Favor immutability where practical — pydantic models are immutable by convention; dataclasses
  use `frozen=True` where mutation isn't needed.
- Handle errors explicitly at system boundaries; propagate exceptions cleanly through internal
  layers. Cancellation flows via `cancel_event` (`threading.Event`-like), checked between steps
  and per-token inside `model.generate`.
- Keep functions short and focused — one function, one responsibility.
- Delete dead code immediately; do not comment it out or leave unused imports / variables.

### Performance

- **Runner profile is sacred**: `pip install -e ".[runner]"` MUST resolve to `httpx + pydantic +
  PyYAML` only. No `torch`, `numpy`, `faiss`, `transformers`, or anything that pulls them in at
  module-load time. The CI matrix runner installs runner extras and must not download GB-scale
  wheels.
- Heavy ML imports (`torch`, `transformers`, `peft`, `faiss`) MUST be lazy inside the local
  backend / server module, never at the top of a module that the runner profile reaches.
- Build the FAISS index **once** at import time. Never rebuild per query.
- Cache expensive computations: `prompt-cache.sqlite` for round-trip prompts,
  `diff-cache.sqlite` for `--diff-since-last` differential review, `.prthinker/pr-state/` for
  GHA matrix `enumerate`-time pre-filter.
- Use generators and iterators for large corpora to minimize memory footprint.
- For the 30B model: **eager attention is forbidden at runtime**. The boot guard
  (`codes.util.hf_model_util._verify_non_eager_attention`) refuses to start the server if
  `model.config._attn_implementation` resolves to anything other than `"flash_attention_2"` or
  `"sdpa"`. Override only with `PRTHINKER_ALLOW_EAGER_ATTENTION=1` on a GPU with enough headroom.

### Security

- Never hardcode secrets, API keys, tokens, or passwords. Read from environment variables
  (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GITHUB_TOKEN`, `PRTHINKER_REMOTE_API_KEY`,
  `CODACY_PROJECT_TOKEN`, etc.).
- Validate and sanitize ALL external input at system boundaries — PR diffs, model outputs,
  GitHub API responses, CLI arguments. Pydantic schemas (`prthinker/schemas.py`) are the
  wire-format validators; never bypass them.
- Avoid `eval()`, `exec()`, `pickle.loads()` on untrusted data, and `subprocess` with
  `shell=True`. Subprocess calls (`git`, `gh`) use arg lists.
- Use secure defaults: HTTPS only for any outbound URL (`_https_urlopen` guard, see
  `prthinker/redaction.py`), bearer-token auth for the `RemoteHttpBackend`, HF revision pins on
  every `hf_hub_download` call.
- Sanitize file paths to prevent path traversal: workdir-relative paths only; reject `..` and
  absolute paths from PR content.
- Log security-relevant events but never log sensitive data (PR tokens, API keys, raw secret
  values). `prthinker.redaction.redact()` strips known secret patterns before any prompt hits
  a third-party backend.

### Unit Tests

Tests are not optional polish — they are part of the change. A feature without tests is an
incomplete feature and MUST NOT be committed. This rule applies equally to bug fixes (regression
test required) and refactors (existing behaviour must remain green; add a test if the refactor
exposes a previously untested path).

**Required coverage for every change:**

- **Happy path** — the new code does what it advertises on a representative input.
- **Edge cases** — empty inputs, single-element inputs, max-size inputs, None / missing keys,
  empty diffs, diffs with binary or deleted files.
- **Error handling** — every `except` branch is exercised; invalid inputs raise the documented
  exception or are clamped to the documented safe range.
- **Boundary conditions** — the values just inside and just outside any threshold (RAG cosine
  ≥ 0.7, severity floor, retry budget, char cap). Off-by-one defects live here.
- **Round-trips** — every pydantic schema and every JSONL / SQLite row needs a
  `to_dict → from_dict → equal` test. The wire-format compatibility section below is enforced
  by these tests.

**Required test types for every feature:**

- **Pure-helper tests.** Pure logic (parsers, hashers, formatters, hunk filters) is unit-tested
  directly without instantiating a backend or pipeline. Cheap, fast, deterministic.
- **Pipeline integration with `FakeBackend`.** If a feature plugs into `CoTPipeline`, add a test
  that drives it through `tests/conftest.py::FakeBackend` and asserts the visible state
  (per-file results, inline findings, verdict, step outputs). Never spin up a real model.
- **HTTP / platform tests with a scripted client.** If a feature talks to GitHub / a backend
  HTTP server, use a scripted `httpx.Client` stand-in (see
  `tests/test_remote_poll_retry.py::_ScriptedClient`) — never hit a live endpoint.

**Mechanics:**

- Use `pytest` style. Module-level functions and `Test*` classes are both fine; follow the
  style of the file you're adding to.
- Test file naming: `tests/test_<module_name>.py`. One test module per production module.
- Use shared fixtures in `tests/conftest.py` (`fake_backend`, `tmp_path`). Do not roll your own
  RNG seed or backend.
- Never write to the real `.prthinker/` directory under the repo root. Tests must redirect
  paths to `tmp_path` and never touch the developer's actual learned corpora.
- Run `py -m pytest tests/` before committing. If a test was already skipping before the
  change, leave it skipping — but every NEW test must run, not skip.

### Linter & Static Analysis Compliance (SonarQube / Codacy / pylint / flake8 / ruff)

All new and modified code MUST pass the following rules without warnings. These mirror the
default rule sets of SonarQube, Codacy, pylint, flake8, ruff, and bandit for Python, and the
Prospector + Lizard pair Codacy actually runs on this repo.

#### Complexity & Size

- **Cyclomatic complexity (Lizard `ccn-medium`)**: keep each function ≤ 8 (the default Lizard
  cap; Codacy reports anything higher). Break nested branches into helper functions when
  exceeded.
- **Function length (Lizard `nloc-medium`)**: ≤ 50 lines of code per function. Split long
  functions into focused helpers.
- **Cognitive complexity**: keep each function ≤ 15 (SonarQube `python:S3776`).
- **File length**: ≤ 1000 lines (SonarQube `python:S104`). Split large modules.
- **Parameter count**: ≤ 7 per function (SonarQube `python:S107`). Group related params into a
  dataclass or pydantic model when exceeded.
- **Nesting depth**: ≤ 4 levels (SonarQube `python:S134`). Use early returns / guard clauses.
- **Boolean expression complexity**: ≤ 3 operators in one expression (SonarQube `python:S1067`).
  Extract to named booleans.
- **Return statements**: ≤ 6 per function (pylint `R0911`).
- **Local variables**: ≤ 15 per function (pylint `R0914`).

#### Duplication

- Do NOT copy-paste blocks of ≥ 3 statements across functions or files (SonarQube
  `common-python:DuplicatedBlocks`, Codacy duplication detector). Extract shared logic.
- Do NOT declare the same string literal ≥ 3 times (SonarQube `python:S1192`). Assign to a
  module-level constant.

#### Naming (PEP 8)

- `snake_case` for functions, methods, variables, modules (SonarQube `python:S1542`, pylint
  `C0103`).
- `PascalCase` for classes (pylint `C0103`).
- `UPPER_CASE_WITH_UNDERSCORES` for module-level constants.
- `_leading_underscore` for private attributes / methods.
- No single-letter names except loop indices (`i`, `j`, `k`, `x`, `y`, `z`) or well-known math
  symbols.

#### Errors & Exceptions

- Never use bare `except:` — always specify the exception type (SonarQube `python:S5754`,
  flake8 `E722`).
- Never write `except Exception: pass` without a logged reason and comment explaining why it is
  safe (the canonical example is `_best_effort_cancel_ask_job` — failures are logged at
  DEBUG and swallowed because the cancel is best-effort).
- Never catch `BaseException` directly.
- Raise specific exception types (`ValueError`, `TypeError`, `FileNotFoundError`,
  `ReviewCancelledError`) instead of generic `Exception`.
- Chain exceptions with `raise X from err` to preserve context (ruff `B904`).
- Never use `assert` for runtime validation (assertions are stripped under `python -O`); use
  explicit `raise` instead. `assert` is only for invariants in tests.

#### Code Smells

- No unused imports, variables, or function parameters (pyflakes `F401`, `F841`, pylint `W0612`,
  `W0613`). Prefix intentionally unused params with `_` or use `del param`.
- **No `import` inside functions** (Prospector `import-outside-toplevel`). The runner-profile
  rule above gates which modules may be lazy-imported at all; everything else must be at module
  top.
- No commented-out code. Delete it — git preserves history.
- No `print()` calls in production code; use the project's logger (`logging.getLogger(...)`).
- No `TODO` / `FIXME` / `XXX` left in merged code (SonarQube `python:S1135`). File a ticket
  instead.
- No magic numbers — extract to `UPPER_CASE` constants (SonarQube `python:S109`). Exceptions:
  `0`, `1`, `-1`, `2` in obvious contexts; threshold constants near their use site (e.g.
  `_RAG_THRESHOLD = 0.7`).
- Use `is None` / `is not None` (never `== None` / `!= None`) (pycodestyle `E711`).
- Use `isinstance(x, T)` instead of `type(x) == T` (pycodestyle `E721`).
- No mutable default arguments (`def f(x=[])`) — use `None` and assign inside (ruff `B006`,
  pylint `W0102`).
- No global mutable state outside the FastAPI server's job tables (`_JOBS`, `_ASK_JOBS`); those
  are encapsulated behind module-level locks.
- Prefer f-strings over `.format()` or `%` (ruff `UP032`).
- Always use context managers (`with` blocks) for file / `httpx.Client` / SQLite connections
  (ruff `SIM115`).
- Prefer `dict.get(key, default)` over `if key in dict: ... else: ...` (ruff `SIM401`).

#### Security (bandit / SonarQube `python:S*` security rules)

- `pickle.load(s)` on untrusted data is forbidden (`B301`, SonarQube `python:S5135`).
- `yaml.load` without `SafeLoader` is forbidden — use `yaml.safe_load` (`B506`).
- MD5 / SHA-1 are forbidden for security purposes (hashing secrets, signatures) — use SHA-256+
  or bcrypt / argon2 (`B303`, `B304`, SonarQube `python:S4790`). They are allowed for non-
  security uses (cache keys, file de-duplication) ONLY with `usedforsecurity=False`. The
  diff hash key in `review_cache.py` uses SHA-256 and is the canonical example.
- `subprocess` with `shell=True` is forbidden when any argument comes from user input (`B602`).
  All `git` / `gh` calls use arg lists (B603, B607 are project-wide skipped — see Project-Wide
  Skip Configuration below).
- Never use `eval`, `exec`, `compile` on dynamic input (`B307`).
- Never use `tempfile.mktemp()` — use `tempfile.mkstemp()` or `NamedTemporaryFile` (`B306`).
- Network binds must not use `0.0.0.0` unless intentional and documented (`B104`).
- XML parsing must use `defusedxml`, never stdlib `xml.etree` on untrusted input (`B405`–`B411`).
- Random number generation for security must use `secrets` module, not `random` (`B311`).
- `B105` (hardcoded password) false positives on display labels like
  `"pass": "**[verified]**"` are suppressed line-level with
  `# nosec B105 — display label, not credential`.

#### Typing & Documentation

- Public functions and methods SHOULD have type hints on parameters and return type.
- Public modules and classes SHOULD have a one-line docstring describing their purpose.
- Docstring convention: **D212** (summary on first line). D213 (summary on second line) is
  mutually exclusive with D212 and explicitly disabled in `pyproject.toml` `[tool.pydocstyle]`
  and `.prospector.yaml`. Both must stay in sync.

#### Enforcement

When writing or modifying code, mentally check each function against the above rules before
finalising. If unavoidable rule violation (e.g. a callback signature forces extra parameters),
add a `# noqa: <rule>` or equivalent suppression with a brief justification comment on the
same line.

## Project-Specific Compliance Patterns

These patterns were established while zeroing out the Codacy backlog and the cascading
runtime OOMs / 502s. Keep following them so the CI stays green and so new maintainers have an
obvious prior-art example to copy.

### Runner vs Server Dependency Surface

The line between `pip install -e ".[runner]"` and `pip install -e ".[server]"` is **not** "ML
code goes in `server`" — that grouping made things inconsistent. The correct test is **what
the GitHub Actions runner installs on every PR**:

**A feature is server-only when ANY of the following is true:**

1. It needs a **heavy / GPU dependency** (`torch`, `transformers`, `peft`, `faiss`,
   `bitsandbytes`).
2. It runs **inference** on the model (CoT step execution, embedding, judge generation).
3. It needs **on-host GPU resources** at runtime.

**A feature stays runner-safe when:**

- It runs on `httpx + pydantic + PyYAML` only.
- It builds a prompt, parses a model response, talks to GitHub, manages the matrix workflow,
  or persists state. Everything in `prthinker/` outside the inference path.
- A regression failure is at worst a missing inline finding, not a backend crash.

#### Directory rules

- **Runner-safe**: `prthinker/*.py` (every module top-level, except the lazy `from prthinker.
  redaction import redact` patterns gated by an opt-in flag). The CLI, platforms, schemas,
  pipeline orchestration, all extension modules.
- **Server-only**: `codes/run/fastapi_server.py`, `codes/util/hf_model_util.py`, `codes/train/`,
  anything that imports `torch` / `transformers` at module top.

#### Testing runner-safe modules

The CI matrix runner installs only the `[runner]` extra. Any test that requires GPU deps must
gate them with `pytest.importorskip("torch")` at the test-collect site, NOT a module-top
`import torch`. The `tests/conftest.py::FakeBackend` covers everything the pipeline needs to
exercise without a real model.

#### When in doubt

Ask: "if a Cloudflare-fronted FastAPI server is unreachable, should this still run?" If yes →
runner. If no → server.

### Prompt Templates Are the Source of Truth

`codes/run/CoT_Prompts/` is the canonical prompt corpus. Edit there, not in copies. If a
prompt is referenced from multiple language versions (en / zh-TW / zh-CN), the source language
file is the one that gets edited; the others are mirrored downstream.

**Bundled mirror at `prthinker/prompts/`.** The `prthinker` package ships its own copy of
the CoT templates at `prthinker/prompts/` so the runner is **self-contained** and importable
when installed standalone in another repository (`pip install "prthinker[runner] @ git+..."`),
where the `codes` tree does not exist. `prthinker/steps.py`, `pipeline.py`, and `findings.py`
import from `prthinker.prompts`, **never** `codes.run.CoT_Prompts` — a module-top
`codes.run.CoT_Prompts` import in the runner is a regression that breaks every downstream
project (the `ModuleNotFoundError: No module named 'codes'` failure). The server / evaluation
scripts under `codes/run/` still import the canonical `codes.run.CoT_Prompts`.

The two copies are kept in sync **on purpose** (the original is retained, the mirror is added).
When you edit a canonical template, re-copy it into `prthinker/prompts/` in the same commit;
`tests/test_prompts_bundled.py::test_bundled_prompts_mirror_canonical` enforces byte-for-byte
parity and fails the build if they drift.

### Corpora Are Append-Only

`dismissed.jsonl`, `accepted.jsonl`, and `lessons.jsonl` are append-only. Never rewrite
historical rows; instead, write a new row with the corrected payload and let the active-
learning loop converge. SQLite stores (`diff-cache.sqlite`, `findings-index.sqlite`,
`repo-kg.sqlite`, `prompt-cache.sqlite`, `telemetry.sqlite`) may be wholesale-replaced (see
`KnowledgeGraphStore.rebuild`) but rows within a snapshot are not edited in place.

### Wire-Format Compatibility

`prthinker/schemas.py` is the only authoritative pydantic-v2 wire format between runner and
server. Adding a field MUST be backward-compatible (optional with a default); renaming or
removing a field is a breaking change that requires bumping the matrix workflow's pinned
runner version. Tests in `tests/test_schemas_roundtrip.py` lock the contract.

### Boot-Time Attention Guard

`codes.util.hf_model_util._verify_non_eager_attention(model)` runs at the end of
`load_hf_model()` and again after `PeftModel.from_pretrained`. If
`model.config._attn_implementation` is anything other than `"flash_attention_2"` or `"sdpa"`,
the server refuses to start. This is intentional: eager attention OOMs around 1500 tokens of
input on a 30B-class model with a 44 GiB GPU, and the failure mode is an opaque
"Tried to allocate 269 GiB" deep inside a review job. Failing at boot turns that into an
actionable error before any review hits the GPU. Override only with
`PRTHINKER_ALLOW_EAGER_ATTENTION=1`. (The literal "269 GiB" allocation is **not**
eager attention — see the next section — but eager would also OOM, so the guard stays.)

### GPU Server: bf16, no flash-attn, transformers pinned `<5`

The FastAPI server (`Qwen/Qwen3-Coder-30B-A3B-Instruct` + the unmerged 13 GB LoRA) is
only fast in **bf16**, and now loads it **deterministically**: `load_hf_model()`
requests bf16 directly for the A3B models (`torch_dtype=torch.bfloat16`, no
`BitsAndBytesConfig`) — ~75 GB across the two 46 GB L40S with `device_map="auto"`
(base ~28 GB/card; with the CPU-staged LoRA attached the steady-state signature is
"~36–38 GB used on each card"), ~14 tok/s.

**transformers must be pinned `<5`** (`pyproject.toml` `[local]` →
`transformers>=4.51,<5`). transformers **≥ 5 densifies the Qwen3-A3B MoE forward**
to a `[seq, hidden, intermediate]` tensor (**~48 MiB per input token, linear in
length**) and OOMs the L40S on a multi-thousand-token review. This was first seen
as the 4-bit "269 GiB" OOM, but it is **NOT specific to quantization** — it also
densifies in plain **bf16**: observed on **5.10.2** a 2357-token file tried to
allocate **110 GiB** (`quant=none`). The 4.x MoE forward routes sparsely and does
not densify; 4.51+ carries the Qwen3-MoE architecture the model needs. Because
`load_hf_model()` requests bf16 and never passes a `BitsAndBytesConfig`, the
`<5` pin does **not** re-engage bitsandbytes 4-bit. `_verify_quant_safe()` refuses
to boot on transformers ≥ 5 (bf16 or 4-bit) — **model-aware** via
`config.model_type`: only the Qwen3-MoE types (`qwen3_moe`) are refused, an
undetermined model_type fails closed, and dense architectures (e.g.
`google/gemma-4-31B-it`, which *requires* transformers ≥ 5.7 and is served from
its own image, never the Qwen pin's) pass. `_probe_generation()` runs a real
~4 K-token generate at boot — do **not** set `PRTHINKER_SKIP_BOOT_PROBE`, or a
densifying build serves and OOMs on the first review. Override the guard only with
`PRTHINKER_ALLOW_DENSIFYING_QUANT=1` once a fixed 5.x is verified.

Also do **NOT install flash-attn** — the image must dispatch attention to SDPA;
flash-attn nudges bitsandbytes 4-bit back into effect (per-token nf4 dequant of the
MoE crushes decode to ~4.5 tok/s).

The supported deploy is the `docker/Dockerfile.server-qwen3-coder` shipped here: CUDA
`12.2.0-runtime` base, **no** flash-attn step, `[local]` deps with `transformers<5`,
`device_map="auto"` (dual-card), LoRA left **unmerged** and CPU-staged (see "the LoRA
stays UNMERGED" below — never `merge_and_unload`). Keep
`TRANSFORMERS_CACHE=/cache/huggingface/hub` — without the `/hub` segment transformers
obeys the deprecated var and looks in an empty dir, hanging (online) or OSErroring
(offline) on load even though the weights are cached.

`hf_generate` wraps `model.generate` in a `sdpa_kernel([FLASH, EFFICIENT])` context
(falls back to `torch.backends.cuda.sdp_kernel(enable_math=False)` on older PyTorch).
The math backend is *explicitly disabled* for the generate call so a long-context run
either dispatches to the memory-efficient kernel or raises a clear "no available SDPA
backend" error — never the silent 127 GiB attention-score materialisation that the
default dispatcher fell into at ~35K total tokens.

### GPU Server: optional FP8 weights via `PRTHINKER_QUANT=fp8`

Decode on a single memory-bandwidth-bound card (e.g. the DGX Spark GB10 serving the
dense `google/gemma-4-31B-it`) is gated by the bytes read per token, not attention
compute — so flash-attn does **not** help, but **FP8 weights roughly halve those bytes**
and speed decode. Set `PRTHINKER_QUANT=fp8` to load the bf16-family models through
transformers-native `FineGrainedFP8Config` (E4M3, dependency-free, native FP8 matmul on
Blackwell). The default (`bf16` / unset / `none` / `off`) keeps the current bf16 weights;
an unknown value fails fast at boot. The selector logic is the torch-free
`codes.util.quant_guard.normalize_quant_mode`; the GPU-side config build is
`hf_model_util._quant_config_for_mode`. FP8 is **opt-in and reversible** (it only changes
weight precision) and the boot probe still validates the assembled base+LoRA model before
serving — so a broken FP8+adapter combination fails loudly at boot, not mid-review. This
is independent of the Qwen `transformers<5` pin above (FP8 targets the dense gemma deploy
on transformers≥5.7, not the Qwen3-MoE image).

### GPU Server: the LoRA stays UNMERGED — CPU-stage it, never `merge_and_unload`

The ~13 GB r=64 expert LoRA (`codes/train/outputs-lora-qwen3-coder-30b`, targeting
`q/k/v/o_proj` + the MoE `gate/up/down_proj`) is attached at runtime with
`PeftModel.from_pretrained(...)` and **MUST stay unmerged**. Do **NOT** call
`merge_and_unload()`, `merge_adapter()`, or otherwise fold the adapter into the base
weights — not in `load_hf_model()`, not in a "fix the OOM" patch, not anywhere.
This is a hard rule, not a preference.

**Why unmerged (and why merging is the wrong instinct):**

- Merging is **not needed to fit memory.** The only reason anyone reaches for a merge
  here is the boot-time GPU-0 OOM — and that OOM is a *load-placement* bug, already
  solved without merging (see the fix below). Merging to "save memory" trades a solved
  problem for several new ones.
- The base weights live in the shared `hf_cache` volume and are **reused across
  rebuilds**; the adapter is versioned and **retrained independently**. A merge would
  bake a bespoke ~60 GB merged checkpoint that has to be regenerated and re-pushed on
  every retrain, and it kills hot-swapping a new adapter onto the cached base.
- A merge writes the LoRA delta back into the **MoE expert tensors** in bf16; that is
  exactly the densification-adjacent path the rest of this section is built to avoid,
  and it adds a merge-time peak with no upside.

**The supported way to make the LoRA fit (this is the OOM fix, do this instead of
merging):** stage the adapter on **CPU**, not a GPU —
`PeftModel.from_pretrained(model, lora_path, torch_device="cpu")`. PEFT otherwise
defaults the adapter load to `cuda:0` and the transient peak (base already on GPU 0
plus the whole ~13 GB adapter buffered there) OOMs the card and crash-loops the
container — `low_cpu_mem_usage=True` did **not** fix this (it piled the whole adapter
onto `cuda:0`); the load **device** is the lever. With `torch_device="cpu"` the source
sits in host RAM and PEFT moves each tensor straight to its base layer's device, so the
adapter splits evenly (~6.3 GB/card) on top of the ~28 GB/card balanced base
(`quant_guard.balanced_max_memory` `max_memory` cap), settling at **~36–38 GB used per
card** with headroom to spare. If a future change reintroduces the GPU-0 OOM, fix the
load placement — never the merge.

### Three-Language Docs Parity

Every change to `docs/en/concepts/` or `docs/en/guide/` MUST be mirrored to `docs/zh-TW/` and
`docs/zh-CN/` in the same commit. Sphinx's `language=en` build runs first on RTD and the
other two trees are sub-toctrees of the en index, so a missing translation surfaces as a
warning (or an error if the toctree reference is broken).

CJK punctuation adjacent to RST inline markup needs a backslash-space (`\` followed by a
space) zero-width separator — for example, write `（前文）\ ``code`` 之 ...` rather than
`（前文）``code`` 之 ...`. The latter parses as inline-markup-without-end-string.

### Paper Work Follows `paper/paper_inserts.md` + `paper/REWRITE_BRIEF.md`

`paper/paper_inserts.md` carries hard rules: **no fabrication, no hallucination**. Never
invent benchmark numbers, RQs, comparison targets, or references. The framework-side ships
**code + corpora + unit tests** only — empirical claims belong in a separate evaluation
paper that has actually run the experiments. New mechanisms get a §3.7.x design subsection
and a matching §6.4.5 future-work skeleton; both must carry a "本論文未予評估" disclaimer.

For manuscript edits (`paper/論文_v*.docx`, `paper/TCSE_v*.docx`), **use the
`paper-author` subagent** (`.claude/agents/paper-author.md`). It encodes the authoritative
brief (`paper/REWRITE_BRIEF.md`) and the hard writing rules verified by
`paper/_check_rules.py`: full-width punctuation, full-width semicolons and prose dashes
recast as 「，」/「：」, first-occurrence-only glosses, 標楷體 + Times New Roman fonts,
Chinese-numeral figure/table numbering, every number traceable to `datas/Results/`, no
AI-tool authorship. Originals are never edited in place — new versions come out of the
python-docx scripts, and dumps are regenerated after every change.

### Architecture Diagrams

The draw.io architecture diagrams live under `datas/Architecture/v<MAJOR>.<MINOR>/`
(four per version: `系統架構` / `訓練流程` / `程式碼審查流程` / `LLM-as-a-Judge流程`).
When adding a version, restyling, or fixing diagram layout, **use the
`architecture-diagram-author` subagent** (`.claude/agents/architecture-diagram-author.md`)
— it encodes the house style and the routing rules. Non-negotiables it captures:

- **`系統架構` MUST use the AWS icon style** (`mxgraph.aws4.resourceIcon`),
  not plain boxes; concept clusters / hubs stay as rounded boxes.
- The draw.io **export renderer follows edge waypoints literally and never
  routes around obstacles** — so edges crossing boxes/text are a layout bug
  you must hand-fix (order bands by flow, keep hub lanes clear with staggered
  side-spokes, route long edges in the margin/gutter lanes, avoid full-width
  boxes blocking a crossing, prefer layered adjacency over long connectors).
- **Always verify by exporting to PNG and looking at it** (the portable
  draw.io build via `gh release download jgraph/drawio-desktop`, then
  `draw.io.exe -x -f png -s 2 --no-sandbox`); iterate edit → export → view
  until no edge crosses a box. `choco`/`winget` need admin; the portable zip
  does not.
- Per `paper/paper_inserts.md`'s no-fabrication rule, never invent components;
  mirror only what the code actually has.

### GitHub Actions / CI Resilience Patterns

- **CI matrix `max-parallel: 1`** is intentional. The single GPU backend is the bottleneck;
  parallel shards just queue and burn CI minutes. Do not change this without a hardware-side
  change.
- **State cache via `actions/cache`**: per-PR `pr-state` (manifest + partials) AND per-PR
  `diff-since-last.sqlite` ride together. The `enumerate` job is responsible for
  pre-filtering unchanged files OUT of the matrix entirely so unused shards never start.
- **Per-shard checkpoint**: after `review-pr` succeeds, the shard writes its partial to
  `pr-state/partials/<sha256(path)>.json` AND adds `{path, blob_sha}` to manifest. Aggregate
  writes the canonical cache entry; if aggregate fails, the next push's restore prefix picks
  up the last successful shard's checkpoint.
- **Inline findings pre-filter**: GitHub's PR review API rejects the WHOLE review with 422 if
  any single inline comment targets a `side:RIGHT` line outside the diff hunks. Always run
  findings through `github_api._filter_findings_to_diff` before submission and wrap
  `submit_inline_review` in try/except — the summary comment + check run must succeed even if
  the inline annotations fail.

## Network & Supply-Chain Safety

- **All `urllib.request.urlopen` calls MUST go through a module-level `_https_urlopen` guard.**
  Canonical implementation lives at `prthinker/redaction.py::_https_urlopen`. The guard parses
  the URL with `urllib.parse.urlparse`, rejects any scheme other than `https`, then calls
  `urlopen`. This defends against future maintainers and compromised upstream strings slipping
  in `http://`, `file://`, or `ftp://` URLs (SonarQube `python:S5332`, bandit `B310`).
- Do NOT call `urllib.request.urlopen` directly in new code. Import or add a local
  `_https_urlopen` helper instead.
- The internal `urlopen` call inside the guard is the ONLY allowed direct use, and must carry
  `# nosec B310  # scheme validated above` on the same line.
- **Hugging Face Hub downloads MUST pin a revision.** `hf_hub_download(...)` must pass
  `revision=<commit-sha-or-tag>` (bandit `B615`, "unsafe download without explicit revision").
  Default to `info.get("revision", "main")` only if the model info dict already ships an
  explicit revision per model — never leave it fully unpinned.
- **Subprocess calls use arg lists.** `git`, `gh`, and `pytest` calls in the sandbox verifier
  go through `subprocess.run([...], shell=False)`. The B603/B607 project-wide skips below
  cover the intentional reliance on `$PATH`; per-call `shell=True` is never allowed.

## Suppression Comment Conventions

Use the right comment for the right tool. They are NOT interchangeable.

| Tool          | Comment form                            | Placement   | Notes                                               |
|---------------|-----------------------------------------|-------------|-----------------------------------------------------|
| ruff / flake8 | `# noqa: <CODE>` (e.g. `# noqa: B904`)  | line-level  | Must list specific codes — never bare `# noqa`.     |
| bandit        | `# nosec B<NNN>` (e.g. `# nosec B310`)  | line-level  | ruff's `# noqa` does NOT suppress bandit.           |
| SonarCloud    | `# NOSONAR`                             | line-level  | Use for hotspots that cannot be config-skipped.     |
| pylint        | `# pylint: disable=<name>`              | line-level  | Prefer refactor over suppression.                   |

Every suppression MUST include a brief justification on the same line
(`# nosec B310  # scheme validated above`). Unexplained suppressions will not pass review.

## Project-Wide Skip Configuration

Systemic false positives are skipped at the config level, never with per-line comments. The
authoritative skip lists live in:

- `pyproject.toml` `[tool.bandit]` — the canonical source. Each entry MUST be paired with a
  justification comment.
- `pyproject.toml` `[tool.pydocstyle]` — `convention = "pep257"` plus
  `add-ignore = ["D213"]` and `add-select = ["D212"]` so the D212 / D213 mutual exclusivity is
  resolved in favour of D212 (summary on first line).
- `.prospector.yaml` — pydocstyle disables D213, enables D212; pylint disables
  `too-few-public-methods`, `too-many-arguments`, `too-many-locals` (Codacy's default
  thresholds collide with pydantic / config-heavy code).

Current project-wide bandit skips (`pyproject.toml`):

- `B101` — `assert` used. Only for type-narrowing in factory branches after
  `Config.__post_init__` has already validated the matching sub-config.
- `B404` — `import subprocess`. Used to shell out to `git` / `gh` with arg lists.
- `B603` — subprocess call without `shell=True`. That is the *safe* pattern; bandit flags any
  subprocess call for review.
- `B607` — partial executable path (`git`, `gh`). Intentional reliance on `$PATH`.

When adding a new bandit skip:

1. Add it to `pyproject.toml` `[tool.bandit].skips` with a `# B<NNN>: <one-line reason>` comment.
2. Verify locally: `py -m bandit -c pyproject.toml -r prthinker/` must return
   `No issues identified`.

## Local CI Reproduction

Before pushing, reproduce each engine locally so CI does not have to tell you:

- **bandit**: `py -m bandit -c pyproject.toml -r prthinker/`
  (the `-c` flag is REQUIRED — without it, bandit ignores the skip config).
- **ruff**: `py -m ruff check .`
- **pytest**: `py -m pytest tests/`
- **sphinx**: `py -m sphinx -b html -q docs docs/_build/html`

## External Dashboards

- **Codacy project issues**:
  <https://app.codacy.com/gh/JE-Chen/Code-Review-Framework-Combining-Large-Language-Models-and-Chain-of-Thought-Reasoning>
- **GitHub Actions workflow logs**:
  <https://github.com/JE-Chen/Code-Review-Framework-Combining-Large-Language-Models-and-Chain-of-Thought-Reasoning/actions>
- **Read the Docs build**:
  <https://app.readthedocs.org/projects/code-review-framework-combining-large-language-models-and-chain/>

The longer architectural overview, prompt-template anatomy, GitHub integration permissions,
defense-slides build process, and full directory inventory live at `READMEs/CLAUDE.md`. This
document is the contractual top-level — it codifies what every commit must satisfy. The
overview answers "how does this codebase fit together".

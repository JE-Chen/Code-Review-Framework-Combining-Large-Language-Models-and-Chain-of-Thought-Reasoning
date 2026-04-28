# CLAUDE.md

## Project Overview

Code Review Framework combining LLMs with Chain-of-Thought (CoT) reasoning. Uses fine-tuned Qwen3 models (with LoRA) and RAG (FAISS + Qwen3-Embedding-4B) to perform multi-step automated code review, then evaluates review quality via LLM-as-Judge.

### Key Directories

- `codes/run/` - Main execution entry points (cot.py, skills.py, single_prompt.py, fastapi_server.py)
- `codes/run/CoT_Prompts/` - CoT prompt templates (global_rule, linter, code_smell, judge, etc.)
- `codes/run/Skills/` - Skills-based prompt templates
- `codes/train/` - LoRA fine-tuning scripts
- `codes/util/` - Utilities (qwen3_util.py for model loading/inference, faiss_util.py for RAG)
- `datas/` - Test data, RAG rule documents, prompt copies

### Tech Stack

- Python 3.12+, PyTorch, Transformers, PEFT (LoRA), FAISS, FastAPI

---

## Design Patterns (Mandatory)

1. **Strategy Pattern** - Pipeline switching (CoT / Skills / Single Prompt) and model selection must be expressed as interchangeable strategies. No hardcoded `match/case` branches in execution code.
2. **Factory Pattern** - All model instantiation (tokenizer + base model + LoRA adapter + quantization) must go through a single factory entry point (`load_qwen3_model()`). Do not construct models ad-hoc.
3. **Template Method Pattern** - Prompt construction always goes through template builders (`build_global_rule_template`, `build_rag_string`). Never inline prompt strings in execution code.
4. **Registry Pattern** - New review steps, new models, and new pipelines should self-register; adding one must not require editing existing files (Open/Closed Principle).
5. **Repository Pattern** - All RAG retrieval routes through `util/faiss_util.py`. FAISS calls outside this module are forbidden.
6. **Dependency Injection** - Pass models, tokenizers, retrievers as parameters; do not import singletons inside helpers.

---

## Software Engineering Principles

- **SRP (Single Responsibility)** - One module, one concern. Prompt templates → `CoT_Prompts/` or `Skills/`. Model utilities → `util/`. Execution flow → `run/`.
- **DRY (Don't Repeat Yourself)** - Duplicated model-loading or RAG-injection blocks must be consolidated into shared factories or utilities.
- **OCP (Open/Closed)** - Add a new CoT step by adding a new prompt file, not by modifying existing steps.
- **LSP / ISP** - Pipeline strategies must share the same minimal interface (`run(code) -> ReviewResult`); do not leak pipeline-specific arguments.
- **YAGNI** - Do not add hooks, flags, or abstractions for hypothetical future requirements.
- **Fail Fast** - Validate config and inputs at module load. Raise on missing model paths, missing prompt templates, or invalid thresholds rather than silently degrading.
- **Pure Functions Where Possible** - Prompt builders and post-processors should be pure (no I/O, no global state).
- **Path Discipline** - Use `pathlib.Path` for all file system operations; never `os.path` or string concatenation.

---

## Code Style & Conventions

### Python

- Follow PEP 8 strictly.
- Type hints on all function signatures.
- Use `pathlib.Path` for all filesystem operations.
- Prefer f-strings over `.format()` for new code.
- `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants.
- Google-style docstrings for public functions.
- All file I/O must specify `encoding="utf-8"`.

### Imports

- Order: standard library → third-party → local. Separate groups with a blank line.
- No wildcard imports (`from module import *`).

### Comments

- Default to no comments. Add only when the **why** is non-obvious (constraint, invariant, workaround).
- Do not narrate **what** the code does — names already do that.

---

## Performance Best Practices

### Model & Inference

- Models load **once** at module level. Never reload per request or per file.
- Quantization mandatory for large models: 4-bit (NF4 + double quant + bf16 compute) for ≥30B; 8-bit acceptable for smaller models.
- Wrap all gradient-free inference and embedding paths with `@torch.no_grad()`.
- Call `model.eval()` immediately after load.
- Use `device_map="auto"` for multi-GPU; pin `torch_dtype=torch.bfloat16` on Ampere+ GPUs.
- Reuse a single tokenizer instance per model.
- Batch inference when input lists are available; do not loop per-sample if a batch path exists.

### RAG / FAISS

- Build the FAISS index **once** at import time. Never rebuild per query.
- Use `IndexFlatIP` with L2-normalized vectors (cosine similarity).
- Apply the relevance threshold (default `0.7`) before injecting rules.
- Embedding `max_length=2048` is intentional; do not raise without GPU benchmarking.
- Cache embeddings of static rule documents on disk; recompute only when source changes.

### I/O

- Stream review results to disk per step (incremental write) to avoid losing work on long CoT runs.
- Generation cap: `max_new_tokens=32768`. Do not raise without memory testing.
- Use buffered writes; close file handles deterministically (`with` blocks).

---

## Code Hygiene

- **Delete unused code aggressively** — dead functions, commented-out blocks, unreferenced imports, unused variables, stale flags, half-finished experiments. If something is unreachable or unreferenced, remove it; do not leave `# TODO` placeholders.
- No backwards-compatibility shims, re-exports, or `_legacy_*` aliases unless an external consumer is documented.
- Do not introduce abstractions, helpers, or config knobs that the current code does not use.
- Prefer editing existing files over creating new ones.

---

## Security (Mandatory — Maximum Bar)

### Input & Path Safety

- Treat **all** code/text passed to the framework as untrusted input. Never `eval`, `exec`, or `pickle.load` on it.
- Validate and normalize file paths with `Path.resolve()`. Reject paths that escape the intended working directory (path traversal).
- Reject filenames containing null bytes, control characters, or shell metacharacters when they are used in subprocess calls.

### Subprocess & Shell

- Never use `shell=True` with untrusted input. Pass arguments as a list.
- Avoid `os.system`. Prefer `subprocess.run([...], check=True, timeout=...)`.

### Secrets & Credentials

- No hardcoded API keys, tokens, or passwords. Read from environment variables or a secrets manager.
- Never log secrets, full request bodies, or model API keys. Redact before logging.
- `.env`, `*.key`, `*.pem`, credentials JSON must remain in `.gitignore` and must never be committed.

### Network & Web (FastAPI)

- Pin dependency versions in `requirements.txt`.
- Validate request bodies with Pydantic models; never trust raw JSON.
- Set request size limits and timeouts on all endpoints.
- Disable CORS wildcards in production; whitelist specific origins.
- Sanitize any model output that is rendered as HTML (XSS).
- Do not echo internal stack traces to clients; log internally, return a generic error.

### Data Handling

- Open files with explicit `encoding="utf-8"` and explicit modes; do not rely on platform defaults.
- Validate JSON/YAML input with schemas before use.
- Use parameterized queries for any future database access; never string-concatenate SQL.

### Supply Chain

- Vet new dependencies; prefer well-maintained packages with active security advisories.
- Run dependency audits periodically (e.g., `pip-audit`).

---

## Git Commit & PR Rules

### Identity Rules (Strict)

- **NEVER** mention any AI assistant, model, code generator, or automation tool in commit messages, branch names, PR titles, PR bodies, or code comments.
- **NEVER** include `Co-Authored-By` trailers of any kind.
- **NEVER** add marketing or attribution lines.
- The git-configured user is the only author.

### Commit Messages

- Write in English, imperative mood.
- Format: `<type>: <short description>` (≤72 chars).
- Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `security`.
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

---

## Testing

- Test data lives in `datas/code_to_detect/` with three categories: `bad_data`, `code_diff`, `only_code`.
- Each category has `ChatGPT/` and `Copilot/` subdirectories.
- Evaluation uses two judge systems: custom LLM Judge (5 dimensions) and CRScore.
- New test data goes in the matching category/source directory.

---

## Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run CoT pipeline
python -m codes.run.cot

# Run Skills pipeline
python -m codes.run.skills

# Run Single Prompt baseline
python -m codes.run.run_single_prompt

# Start FastAPI server
uvicorn codes.run.fastapi_server:app --reload

# Build LLM Judge prompts
python -m codes.run.build_our_llm_judge
```

---

## Defense Slides (paper/)

The thesis defense deck is generated by a Node.js wrapper that emits an
**editable** `slides.pptx` via `pptxgenjs`. Every text frame, table cell, and
shape stays editable in PowerPoint / Keynote / LibreOffice Impress — do not
replace this with a print-to-PDF or image-export path.

### Source of truth

- `paper/論文_v1.5.docx` — the manuscript. Re-extract numbers from here when
  rebuilding slides; do not copy from older `slides.md` snapshots.
- `output/*.png` — system / training / CoT flow diagrams referenced by the deck.

### Build commands

```bash
cd paper
npm install
npm run build      # node build_slides.js → slides.pptx
```

### Rules

- All slide content lives in `paper/build_slides.js`. Do not reintroduce a
  Marp / `slides.md` pipeline — the deck must remain code-driven and editable.
- Tables and bullet lists must be assembled with `addTable` / `addText` so
  reviewers can edit individual cells. Do not rasterize tables as images.
- Numbers (CRSCORE++, LLM Judge, human eval) must come from the v1.5 manuscript
  tables; flag any drift before edits.
- Figures are pulled from `../output/`; if a referenced PNG is missing the
  builder shows a visible placeholder rather than failing silently.
- `paper/node_modules/` is build output — keep it out of git.

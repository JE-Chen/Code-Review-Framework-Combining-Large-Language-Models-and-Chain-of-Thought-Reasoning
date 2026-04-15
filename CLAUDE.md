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

## Design Patterns & Software Engineering Principles

### Mandatory Patterns

1. **Strategy Pattern** - Model selection and pipeline switching (CoT vs Skills vs Single Prompt) must use Strategy pattern. Avoid hardcoded `match/case` blocks for model loading; extract into a factory or registry.
2. **Template Method Pattern** - All prompt construction must go through template builders (`build_global_rule_template`, `build_rag_string`). Never inline prompt strings directly in execution code.
3. **Factory Pattern** - Model instantiation (tokenizer + model + LoRA) should use factory functions. The current `load_qwen3_model()` is the single entry point; keep it that way.
4. **Single Responsibility Principle (SRP)** - Each module handles one concern. Prompt templates stay in `CoT_Prompts/` or `Skills/`. Model utilities stay in `util/`. Execution logic stays in `run/`.
5. **DRY (Don't Repeat Yourself)** - The model loading `match/case` block is duplicated across cot.py, skills.py, run_single_prompt.py, fastapi_server.py. When refactoring, consolidate into a shared config or factory.
6. **Open/Closed Principle** - Adding a new review step to the CoT pipeline should not require modifying existing steps. New prompts = new files in `CoT_Prompts/`.

### Code Organization Rules

- Prompt templates are **data**, not logic. Keep them as string constants in dedicated files.
- RAG retrieval logic lives in `util/faiss_util.py`. Do not scatter FAISS calls across execution files.
- All file I/O for review results uses `pathlib.Path`. Do not use raw string concatenation for paths.

---

## Code Style & Conventions

### Python

- Follow PEP 8 strictly.
- Use type hints on all function signatures.
- Use `pathlib.Path` for all file system operations, never `os.path`.
- Prefer f-strings over `.format()` for new code (existing prompt templates using `.format()` are acceptable).
- Use `snake_case` for functions and variables, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants.
- Docstrings: use Google style for public functions.
- All source files must use `encoding="utf-8"` when opening files.

### Imports

- Standard library first, third-party second, local modules third. Separate with blank lines.
- No wildcard imports (`from module import *`).

---

## Performance Best Practices

### Model & Inference

- Models are loaded **once** at module level. Never reload models per request or per file.
- Use quantization (4-bit for 30B models, 8-bit for smaller models) via `BitsAndBytesConfig`.
- Use `@torch.no_grad()` for all embedding and inference operations that don't require gradients.
- Set `model.eval()` after loading for inference-only usage.
- Use `device_map="auto"` for automatic multi-GPU distribution.

### RAG / FAISS

- FAISS index is built once at import time. Do not rebuild per query.
- Use cosine similarity (`IndexFlatIP` with L2-normalized vectors).
- Apply threshold filtering (default 0.7) to avoid injecting low-relevance rules.
- Embedding truncation at `max_length=2048` is intentional; do not increase without benchmarking.

### I/O

- Write review results incrementally per step, not all at once at the end. This prevents data loss on long-running CoT pipelines.
- Use `max_new_tokens=32768` as the generation cap. Do not increase without GPU memory testing.

---

## Git Commit & PR Rules

### Identity Rules

- **NEVER** use your own name, alias, or any AI assistant name in commit messages, PR titles, PR descriptions, or `Co-Authored-By` tags.
- **NEVER** include `Co-Authored-By` headers of any kind.
- Commit author should be the git-configured user only.

### Commit Messages

- Write in English.
- Use imperative mood: "Add feature", "Fix bug", "Refactor module".
- Format: `<type>: <short description>` (under 72 characters).
- Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`.
- Examples:
  - `feat: Add step-by-step analysis to CoT pipeline`
  - `fix: Correct threshold filtering in RAG retrieval`
  - `refactor: Extract model loading into shared factory`
  - `perf: Enable 4-bit quantization for 30B model`

### PR Rules

- PR title follows the same `<type>: <description>` format.
- PR body must include: Summary, Changes, Test Plan.
- Do not reference any AI tool or assistant in PR content.

### Branch Naming

- `feat/<short-description>`
- `fix/<short-description>`
- `refactor/<short-description>`

---

## Testing

- Test data is in `datas/code_to_detect/` with three categories: `bad_data`, `code_diff`, `only_code`.
- Each category has `ChatGPT/` and `Copilot/` subdirectories.
- Evaluation uses two judge systems: custom LLM Judge (5 dimensions) and CRScore.
- When adding new test data, place files in the appropriate category/source directory.

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

### Code Review Summary

#### ✅ **Readability & Consistency**
- Indentation and formatting are consistent.
- Comments are minimal but acceptable.
- Slight inconsistency: `GLOBAL_CONFIG` is not consistently named like other variables (e.g., `val`, `input_data`), which could reduce clarity.

#### ✅ **Naming Conventions**
- Class names (`BaseProcessor`, `StringProcessor`, etc.) are descriptive.
- Variables such as `result`, `ch`, and `data` are clear.
- Global config usage (`GLOBAL_CONFIG`) can be made more explicit by using constants or a dedicated config module.

#### ✅ **Software Engineering Standards**
- Modular design with `DataPipeline` and processors supports extensibility.
- No major duplication found.
- Consider extracting conditional logic into helper functions for better testability and readability.

#### ⚠️ **Logic & Correctness**
- Potential edge case in `StringProcessor`: If `data` is empty string, returns empty string — correct behavior.
- In `NumberProcessor`, modulo operation might lead to unexpected results if `data` is negative or very large; consider bounds checking.
- The deeply nested `if` statements in `main()` reduce readability and are hard to maintain.

#### ⚠️ **Performance & Security**
- String concatenation in loop (`result += ch`) may cause performance issues for large strings; use `join()` instead.
- No direct user input or external data processing here, so no major security concerns.

#### ❗ **Documentation & Testing**
- No docstrings or inline comments explaining what each processor does.
- Missing unit tests for core logic (e.g., `StringProcessor`, `NumberProcessor`).

---

### Suggestions for Improvement

- Replace repeated `if` blocks in `main()` with early returns or helper functions.
- Use `str.join()` for efficient string building in `StringProcessor`.
- Add docstrings to explain class and method responsibilities.
- Move global config to a configuration file or constant module for reuse and clarity.
- Validate inputs where possible (especially in `NumberProcessor`).
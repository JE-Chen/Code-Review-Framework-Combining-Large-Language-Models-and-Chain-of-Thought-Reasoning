### Code Review

**Logic & Correctness**
* **StringProcessor Logic:** The `StringProcessor` converts non-alphabetic characters to their integer Unicode value (via `ord`). Since the `NumberProcessor` only processes `int` types, and `StringProcessor` returns a `str`, the `NumberProcessor` will always fall back to `super().process(data)` (returning the string unchanged) when placed after `StringProcessor` in the pipeline.

**Readability & Consistency**
* **Deep Nesting:** The `main()` function contains a deeply nested `if` structure (4 levels). This reduces readability and should be refactored using guard clauses (e.g., `if not GLOBAL_CONFIG["flag"]: return`).

**Performance & Security**
* **String Concatenation:** In `StringProcessor`, `result += ch` inside a loop is inefficient in Python as strings are immutable. Use a list and `''.join(list)` for better performance.

**Naming Conventions**
* **Variable Naming:** The variable `ch` in `StringProcessor` is slightly cryptic; `char` or `character` would be more descriptive.

**Software Engineering Standards**
* **Modularity:** The logic inside `main()` regarding `GLOBAL_CONFIG` is unrelated to the `DataPipeline` logic and should be moved to a separate function to maintain a single responsibility for `main()`.
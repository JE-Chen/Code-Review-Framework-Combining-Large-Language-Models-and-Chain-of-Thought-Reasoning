### Code Review

**Logic & Correctness**
* **StringProcessor Logic:** The `StringProcessor` converts non-alphabetic characters to their integer Unicode values (via `ord`). Since the output is a string, the `NumberProcessor` (which expects an `int`) will always fail its `isinstance(data, int)` check when following a `StringProcessor`, rendering the `NumberProcessor` ineffective in the current pipeline sequence.

**Readability & Consistency**
* **Deep Nesting:** The `main()` function contains a deeply nested `if` structure (4 levels). This reduces readability and should be refactored using guard clauses or combined logical operators.

**Performance & Security**
* **String Concatenation:** In `StringProcessor`, `result += ...` inside a loop is inefficient in Python as strings are immutable. Using a list and `''.join()` is the standard performance practice.

**Naming Conventions**
* **Variable Naming:** `ch` in `StringProcessor` is slightly cryptic; `char` or `character` would be more descriptive.

**Suggestions for Improvement**
* **Refactor Nesting:** Flatten the `GLOBAL_CONFIG` logic in `main()` to improve clarity.
* **Optimize String Building:** Use `"".join([...])` in `StringProcessor.process`.
* **Pipeline Design:** Ensure the output type of one processor matches the expected input type of the next to avoid silent skips.
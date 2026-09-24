### Code Review

**Logic & Correctness**
* **Potential Division by Zero:** In `calculate_average_scores`, `total / len(scores)` will raise a `ZeroDivisionError` if a user has an empty `scores` list.

**Software Engineering Standards**
* **Hardcoded Dependency:** All functions depend directly on the global `DATA` object. This makes the code difficult to test and reuse. Pass the data as arguments to the functions instead.
* **Redundant Logic:** In `process_misc`, the nested `if/else` structure for "Large/Small" is duplicated for both even and odd cases. This can be simplified using string formatting or a helper variable.
* **Manual Summation:** In `calculate_average_scores`, the manual `for` loop to calculate `total` is unnecessary; use the built-in `sum()` function.

**Readability & Naming**
* **Vague Variable Names:** In `calculate_average_scores`, the variable `s` should be renamed to `score` for better clarity.
* **Deep Nesting:** The `main()` function contains deeply nested `if` statements regarding `DATA["config"]["flags"]`, which reduces readability.

**Suggestions for Improvement**
* **Refactor `calculate_average_scores`:** Use `sum(scores) / len(scores) if scores else 0`.
* **Refactor `process_misc`:** Determine the "Size" (Large/Small) and "Parity" (Even/Odd) independently, then combine them into a single string.
* **Decouple Functions:** Change signatures to `def calculate_average_scores(users):` and call them via `calculate_average_scores(DATA["users"])`.
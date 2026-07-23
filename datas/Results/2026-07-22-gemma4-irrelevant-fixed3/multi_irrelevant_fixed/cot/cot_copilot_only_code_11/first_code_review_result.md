### Code Review

**Logic & Correctness**
* **Potential Division by Zero**: In `calculate_average_scores`, `total / len(scores)` will raise a `ZeroDivisionError` if a user has an empty `scores` list.

**Software Engineering Standards**
* **Hardcoded Data Dependency**: Functions like `calculate_average_scores`, `filter_high_scores`, and `process_misc` rely on the global `DATA` variable. Pass `DATA` (or specific subsets of it) as arguments to make functions testable and modular.
* **Redundant Logic**: In `process_misc`, the nested `if/else` structure for "Large/Small" is repeated for both even and odd cases. This can be refactored into a single size check.
* **Manual Summation**: In `calculate_average_scores`, the manual `for` loop to calculate `total` is unnecessary; use the built-in `sum()` function.

**Naming Conventions**
* **Vague Variable Names**: In `calculate_average_scores`, the variable `s` should be renamed to `score` for better clarity.

**Readability & Consistency**
* **Deep Nesting**: The `main()` function contains deeply nested `if` statements regarding `DATA["config"]`. Consider using `elif` or guard clauses to flatten the logic.

**Suggestions for Improvement**
* Use `sum(scores) / len(scores)` for averages.
* Refactor `process_misc` to determine "Large/Small" and "Even/Odd" independently and combine the strings.
* Pass data as parameters to functions instead of accessing global state.
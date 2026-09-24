### Code Review

**Logic & Correctness**
* **Potential Division by Zero**: In `calculate_average_scores`, `total / len(scores)` will raise a `ZeroDivisionError` if a user has an empty `scores` list.

**Software Engineering Standards**
* **Hardcoded Dependency**: Functions (`calculate_average_scores`, `filter_high_scores`, `process_misc`) rely directly on the global `DATA` object. Pass `DATA` or specific subsets as arguments to improve testability and modularity.
* **Redundant Logic**: In `process_misc`, the nested `if/else` structure for "Large/Small" is repeated for both even and odd cases. This can be simplified by determining the size prefix and parity suffix independently.

**Readability & Consistency**
* **Naming**: The variable `s` in loops is too cryptic; use `score` for clarity.
* **Complexity**: The nested `if` statements in `main()` regarding `DATA["config"]["flags"]` are deeply indented and difficult to read.

**Suggestions for Improvement**
* **Refactor `calculate_average_scores`**: Use the built-in `sum()` function: `avg = sum(scores) / len(scores) if scores else 0`.
* **Refactor `process_misc`**:
  ```python
  size = "Large" if item["value"] > DATA["config"]["threshold"] else "Small"
  parity = "Even" if item["value"] % 2 == 0 else "Odd"
  result[item["key"]] = f"{size} {parity}"
  ```
* **Refactor `main`**: Use `elif` or a mapping to flatten the conditional logic for `flags`.
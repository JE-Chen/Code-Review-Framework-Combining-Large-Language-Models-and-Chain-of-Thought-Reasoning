### Code Review

#### Logic & Correctness
*   **`risky_division`**: Returning magic numbers (`9999`, `-1`) to signal errors is dangerous as they can be mistaken for valid calculation results. Use exceptions or `None`.
*   **`read_file`**: The file is opened manually. If `f.read()` raises an exception, `f.close()` will never be called, leading to a resource leak. Use a `with open(...)` block.
*   **`process_data`**: The nested `try-except` blocks and the `try-except` inside the loop are redundant because `convert_to_int` and `risky_division` already handle their own exceptions.

#### Software Engineering Standards
*   **Error Handling**: Over-reliance on generic `except Exception` blocks masks bugs and makes debugging difficult. Catch specific exceptions only.
*   **Modularity**: The `process_data` function mixes data parsing (splitting strings) with business logic (summing divisions).

#### Readability & Consistency
*   **Naming**: `risky_division` is a vague name; a more descriptive name like `safe_divide` or `calculate_half` would be clearer.

#### Suggestions for Improvement
*   **Use Context Managers**: Replace `f = open()` with `with open(filename, "r") as f:`.
*   **Avoid Magic Numbers**: Raise custom exceptions or return `None` instead of `9999` or `-1`.
*   **Simplify `process_data`**: Remove the outer `try-except` wrappers and the loop-level `try-except` since the helper functions are already "safe."
### Code Review

#### 1. Readability & Consistency
- **Formatting:** The indentation and structure are consistent.
- **Logging:** The code mixes `print()` statements for error reporting. In a production environment, a logging library (e.g., `logging`) should be used to allow for different severity levels and better traceability.

#### 2. Naming Conventions
- Names like `risky_division`, `convert_to_int`, and `process_data` are descriptive and follow standard Python naming conventions.

#### 3. Software Engineering Standards
- **Resource Management:** In `read_file`, the file is opened and closed manually. If an exception occurs during `f.read()`, `f.close()` will never be called, leading to a resource leak.
- **Modularity:** The functions are well-separated by responsibility.

#### 4. Logic & Correctness
- **Magic Numbers:** `risky_division` returns `9999` on `ZeroDivisionError` and `-1` on other exceptions. `convert_to_int` returns `0` or `-999`. These "magic numbers" are ambiguous and can be easily mistaken for valid data, leading to silent failures or incorrect calculations in `process_data`.
- **Over-broad Exception Handling:** There is an excessive use of `except Exception:`. This catches everything, including `KeyboardInterrupt` or `SystemExit` in some contexts, and hides the root cause of bugs.
- **Redundant Try-Except:** In `process_data`, there is a nested `try-except` block and a `try-except` inside a loop that wraps `risky_division`. Since `risky_division` already handles its own exceptions and returns a value, the inner `try-except` in the loop is unreachable/redundant.

#### 5. Performance & Security
- **File Handling:** `f.read()` reads the entire file into memory. For very large files, this could lead to a `MemoryError`.

#### 6. Documentation & Testing
- **Missing Documentation:** There are no docstrings explaining the expected input types or the meaning of the return values (especially the magic numbers).
- **Testing:** No unit tests are provided to verify the edge cases (e.g., empty files, non-numeric data).

---

### Recommendations

1.  **Use Context Managers:** Replace `f = open(...)` with `with open(filename, "r") as f:`.
2.  **Avoid Magic Numbers:** Instead of returning `9999` or `-1`, raise a custom exception or return `None` (and handle it explicitly) to distinguish between a valid result and an error.
3.  **Refine Exception Handling:** Catch specific exceptions (e.g., `ValueError`, `IOError`) rather than the base `Exception` class.
4.  **Remove Redundant Blocks:** Clean up the nested `try-except` in `process_data`.

### Score: 4/10
*The code is functional for basic cases but fails significantly on software engineering standards regarding error handling, resource management, and maintainability.*
### Code Review

**Logic & Correctness**
*   **`read_file` Resource Leak:** The file is opened using `open()` but not wrapped in a `with` statement. If `f.read()` raises an exception, `f.close()` will never be called, leading to a leaked file handle.
*   **`risky_division` Magic Numbers:** Returning `9999` or `-1` to signal errors is dangerous, as these could be interpreted as valid calculation results. Use exceptions or `None`.
*   **`convert_to_int` Magic Numbers:** Returning `0` or `-999` on failure creates ambiguity between a failed conversion and the actual integer value 0 or -999.

**Software Engineering Standards**
*   **Over-reliance on Generic Exceptions:** Multiple blocks use `except Exception:`, which catches everything (including `KeyboardInterrupt` or `SystemExit` in some contexts). Catch specific exceptions to avoid masking unrelated bugs.
*   **Redundant Try-Except Blocks:** In `process_data`, there is a nested `try-except` structure and a `try-except` inside a loop calling `risky_division` (which already has its own internal error handling). This creates "silent failure" patterns that make debugging difficult.

**Readability & Consistency**
*   **Inconsistent Error Handling:** Some functions print errors to the console (`print("Unexpected error:", e)`), while others return sentinel strings (`"FILE_NOT_FOUND"`) or magic numbers. A consistent strategy (e.g., logging or raising custom exceptions) should be used.

**Suggestions for Improvement**
*   **Use Context Managers:** Replace `f = open(...)` with `with open(filename, "r") as f:`.
*   **Refactor Sentinels:** Instead of returning `9999` or `-999`, allow exceptions to propagate to the caller or return `None`.
*   **Simplify `process_data`:** Remove the redundant nested `try` blocks; rely on the error handling already implemented within `convert_to_int` and `risky_division`.
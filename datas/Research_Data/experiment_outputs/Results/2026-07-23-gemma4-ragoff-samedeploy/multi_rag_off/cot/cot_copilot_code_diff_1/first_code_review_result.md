### Code Review

**Naming Conventions**
*   **Variable Naming:** `meanVal` uses camelCase, which deviates from the PEP 8 snake_case convention used elsewhere in the file. Suggest renaming to `mean_val`.
*   **Constant Naming:** `DATA` and `RESULTS` are named as constants (uppercase), but they are used as mutable global state. Suggest renaming to `data` and `results`.

**Software Engineering Standards**
*   **Global State:** The use of `global` variables (`DATA`, `RESULTS`) makes the application stateful and not thread-safe. In a production Flask environment (with multiple workers), this will lead to inconsistent data across requests.
*   **Redundancy:** `statistics.mean(DATA)` and `statistics.median(DATA)` are called twice in the `analyze` function. Store the result in a variable and reuse it.

**Logic & Correctness**
*   **Inconsistent State:** The `RESULTS` dictionary is not cleared when `/generate` is called, but it is cleared when `/clear` is called. This means `RESULTS` may contain stale data from a previous dataset if `/analyze` is not called immediately after `/generate`.

**Performance & Security**
*   **Debug Mode:** `app.run(debug=True)` is enabled. This should be disabled or moved to an environment variable for production to avoid exposing the interactive debugger.

**Suggestions for Improvement**
*   **Refactor State:** Move data storage to a database or a cache (like Redis) to ensure thread safety and persistence.
*   **Optimize Calculations:**
    ```python
    # Instead of:
    RESULTS["mean"] = meanVal
    RESULTS["meanAgain"] = statistics.mean(DATA)
    # Use:
    RESULTS["mean"] = meanVal
    RESULTS["meanAgain"] = meanVal
    ```
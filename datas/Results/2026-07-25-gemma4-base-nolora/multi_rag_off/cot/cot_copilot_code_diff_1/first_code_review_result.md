### Code Review

**Naming Conventions**
*   **Variable Naming:** `meanVal` uses camelCase, which deviates from the PEP 8 standard (snake_case) used elsewhere in the script. Suggest renaming to `mean_val`.

**Software Engineering Standards**
*   **State Management:** The use of `global` variables (`DATA`, `RESULTS`) makes the application stateful and not thread-safe. In a production Flask environment (with multiple workers), this will lead to inconsistent data across requests.
*   **Redundant Logic:** `statistics.mean(DATA)` and `statistics.median(DATA)` are called twice within the same block. Store the result in a variable and reuse it.

**Logic & Correctness**
*   **Inconsistent State:** The `RESULTS` dictionary is not cleared when `/generate` is called, but it is cleared when `/clear` is called. This means `RESULTS` can contain stale data from a previous dataset if `/analyze` is not called immediately after `/generate`.

**Performance & Security**
*   **Debug Mode:** `app.run(debug=True)` is enabled. This should be disabled or handled via environment variables to prevent security vulnerabilities in production.

**Suggestions for Improvement**
*   **Refactor:** Move the analysis logic into a separate helper function to improve modularity and testability.
*   **Optimization:** Remove the duplicate calls to `statistics.mean` and `statistics.median`.
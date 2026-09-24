Based on the global rules provided, here is the code review for the submitted snippet.

### 1. Readability & Consistency
*   **Formatting:** The code is well-formatted and follows standard Python indentation.
*   **Consistency:** The style is consistent throughout the file.

### 2. Naming Conventions
*   **Descriptive Names:** Variable and function names (`init_data`, `process_items`, `toggle_flag`) are clear and describe their purpose.
*   **Global Constants:** `GLOBAL_STATE` is named in uppercase, which correctly signals it as a global configuration/state object.

### 3. Software Engineering Standards
*   **Modularity:** The code is broken down into small, single-purpose functions.
*   **State Management:** The use of a global dictionary (`GLOBAL_STATE`) creates tight coupling between all functions. While acceptable for a very small script, this pattern makes the code difficult to test in isolation and is not thread-safe. 
    *   *Recommendation:* Consider encapsulating this state within a class (e.g., `StateManager`) and passing an instance to the functions.

### 4. Logic & Correctness
*   **Logic:** The logic in `process_items` is sound and handles both branches of the `flag` condition correctly.
*   **Boundary Conditions:** The `reset_state` function correctly restores the state to a baseline, though it changes `mode` to `"reset"` rather than returning it to `"default"`. This appears intentional but should be verified against requirements.

### 5. Performance & Security
*   **Performance:** The time complexity of `process_items` is $O(n)$, which is optimal for this operation.
*   **Security:** There are no external inputs or resource handles, so there are no immediate security vulnerabilities.

### 6. Documentation & Testing
*   **Documentation:** The code lacks docstrings. While the functions are simple, adding a brief description of the expected input/output for `process_items` would improve maintainability.
*   **Testing:** There are no unit tests provided. The `main()` function serves as a basic manual integration test, but automated tests (e.g., using `pytest`) are recommended to verify the logic of `process_items` across different `flag` and `threshold` values.

---

### Summary of Findings

| Category | Status | Note |
| :--- | :--- | :--- |
| **Readability** | ✅ Pass | Clean and consistent. |
| **Naming** | ✅ Pass | Meaningful and semantic. |
| **Engineering** | ⚠️ Warning | High reliance on global state; suggests refactoring to a class. |
| **Logic** | ✅ Pass | Correct implementation of requirements. |
| **Performance** | ✅ Pass | Efficient. |
| **Documentation** | ⚠️ Warning | Missing docstrings and formal unit tests. |
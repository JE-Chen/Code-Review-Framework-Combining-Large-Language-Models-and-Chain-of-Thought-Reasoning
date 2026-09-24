### Code Review

**Naming Conventions**
*   **Function Naming:** `functionThatDoesTooMuchAndIsNotClear` is non-descriptive and violates standard Python naming conventions (should be `snake_case`). Rename it to reflect its actual purpose (e.g., `analyze_student_scores`).
*   **Variable Naming:** `ANOTHER_GLOBAL` is vague. Use a name that describes the content, such as `START_MESSAGE`.

**Software Engineering Standards**
*   **Global State:** The use of `global GLOBAL_DF` creates tight coupling and makes the code harder to test and maintain. Pass the DataFrame as an argument and return results instead.
*   **Modularity:** The function violates the Single Responsibility Principle. It handles data creation, data transformation, business logic (age validation), and reporting. Split these into separate functions.

**Logic & Correctness**
*   **Broad Exception Handling:** `except Exception as e` is too generic. Catch specific pandas or value errors to avoid masking unrelated bugs.
*   **Nested Logic:** The nested `if` statements for `mean_age` are redundant. Use `elif` for better readability.

**Readability & Consistency**
*   **Hardcoded Data:** The data dictionary is embedded inside the logic function. Move it to a configuration file or a dedicated data-loading function.

**Suggestions for Improvement**
*   Refactor the code to remove global variables.
*   Implement a clear pipeline: `load_data()` $\rightarrow$ `transform_data()` $\rightarrow$ `validate_metrics()` $\rightarrow$ `print_report()`.
*   Replace the nested `if` blocks with a flat `if/elif/else` structure.
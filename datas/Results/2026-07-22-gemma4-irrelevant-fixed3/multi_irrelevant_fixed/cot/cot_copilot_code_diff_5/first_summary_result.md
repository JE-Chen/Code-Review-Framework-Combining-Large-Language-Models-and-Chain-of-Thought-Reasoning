### Pull Request Summary

*   **Key changes**: Introduced a new data analysis script `data_analysis.py` that creates a sample DataFrame, performs basic arithmetic operations, and prints descriptive statistics.
*   **Purpose of changes**: Initial implementation of data analysis functionality.
*   **Items to confirm**: Review the logic for data processing and the use of global state.

---

### Code Review

#### 1. Readability & Consistency
*   **Formatting**: The code generally follows Python indentation standards, but the logic within the `try` block is deeply nested, reducing readability.

#### 2. Naming Conventions
*   **Function Naming**: `functionThatDoesTooMuchAndIsNotClear` violates naming conventions. It is not descriptive of the function's purpose and uses camelCase instead of the Python-standard `snake_case`.
*   **Variable Naming**: `ANOTHER_GLOBAL` is a generic name that provides no semantic meaning regarding its purpose.

#### 3. Software Engineering Standards
*   **Modularity**: The function violates the Single Responsibility Principle. It handles data creation, data transformation, business logic (age validation), and reporting all in one block. This should be split into separate functions (e.g., `load_data()`, `process_scores()`, `analyze_age()`).
*   **Global State**: The use of `global GLOBAL_DF` is discouraged. It makes the code harder to test and maintain. Data should be passed as arguments and returned as values.

#### 4. Logic & Correctness
*   **Exception Handling**: The `except Exception as e` block is too broad. Catching all exceptions and printing a generic message ("我不管錯誤是什麼") hides potential bugs and makes debugging difficult.
*   **Nested Logic**: The nested `if` statements for `mean_age` can be simplified using `elif` for better clarity.

#### 5. Performance & Security
*   **Resource Management**: No significant performance bottlenecks for this data size, but the reliance on global variables will lead to memory and state issues as the application scales.

#### 6. Documentation & Testing
*   **Documentation**: There are no docstrings or comments explaining the purpose of the logic or the expected input/output.
*   **Testing**: No unit tests are provided for the analysis logic.

### Summary of Recommendations
1.  **Rename** the main function to something descriptive (e.g., `analyze_student_data`) and use `snake_case`.
2.  **Refactor** the code to remove `global` variables; pass the DataFrame as a parameter.
3.  **Decompose** the large function into smaller, single-purpose functions.
4.  **Refine** exception handling to catch specific errors and provide meaningful logs.
5.  **Simplify** the nested `if` logic using `if/elif/else`.
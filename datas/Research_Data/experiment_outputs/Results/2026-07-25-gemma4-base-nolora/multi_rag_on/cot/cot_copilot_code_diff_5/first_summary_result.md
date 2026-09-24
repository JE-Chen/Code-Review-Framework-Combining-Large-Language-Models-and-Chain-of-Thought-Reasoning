## PR Summary

*   **Key changes**: Introduced `data_analysis.py` which initializes a pandas DataFrame with sample data, performs basic arithmetic operations, and prints descriptive statistics.
*   **Purpose of changes**: Initial implementation of data analysis functionality.
*   **Items to confirm**: The current implementation relies heavily on global state and lacks modularity; please review the architectural approach.

---

## Code Review

### 1. Readability & Consistency
*   **Naming Conventions**: The function name `functionThatDoesTooMuchAndIsNotClear` violates standard Python naming conventions (PEP 8 suggests `snake_case`) and is not descriptive of the actual business logic. It should be renamed to reflect its purpose (e.g., `analyze_student_scores`).
*   **Consistency**: The codebase mixes English (variable names) and Chinese (print statements/global strings). It is recommended to stick to one language for consistency, typically English for logs and strings in a professional codebase.

### 2. Software Engineering Standards
*   **Modularity**: The function violates the **Single Responsibility Principle**. It handles data creation, data transformation, business logic validation, and reporting. This should be split into at least three functions:
    1.  `load_data()`
    2.  `process_scores()`
    3.  `print_analysis_report()`
*   **Global State**: The use of `global GLOBAL_DF` is highly discouraged. It makes the code harder to test and maintain. Data should be passed as arguments and returned as return values.

### 3. Logic & Correctness
*   **Exception Handling**: The `try...except Exception as e` block is too broad. Catching all exceptions and printing "我不管錯誤是什麼" (I don't care what the error is) hides potential bugs and makes debugging difficult. Catch specific exceptions (e.g., `KeyError`, `TypeError`).
*   **Nested Logic**: The nested `if` statements for `mean_age` are redundant. They can be simplified using `elif`:
    ```python
    if mean_age <= 20:
        print(...)
    elif mean_age < 50:
        print(...)
    else:
        print(...)
    ```

### 4. Performance & Security
*   **Resource Management**: While not an issue for this small dataset, relying on global variables for DataFrames can lead to significant memory leaks in larger applications as the reference is never cleared.

### 5. Documentation & Testing
*   **Missing Tests**: No unit tests are provided for the logic.
*   **Documentation**: There are no docstrings explaining the purpose of the function or the expected structure of the data.

### Summary of Required Changes
| Category | Issue | Priority |
| :--- | :--- | :--- |
| **Naming** | Rename `functionThatDoesTooMuchAndIsNotClear` to `snake_case` | High |
| **Architecture** | Remove `global` variables; pass data via arguments | High |
| **Modularity** | Split the monolithic function into smaller, single-purpose functions | Medium |
| **Logic** | Refactor broad `Exception` catch to specific errors | Medium |
| **Readability** | Simplify nested `if` statements to `if/elif/else` | Low |
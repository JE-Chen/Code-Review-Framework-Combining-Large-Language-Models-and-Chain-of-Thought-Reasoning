## PR Summary

* **Key changes**: Introduced `data_analysis.py` which creates a sample DataFrame, performs basic arithmetic operations, and prints descriptive statistics.
* **Purpose of changes**: Initial implementation of data analysis functionality.
* **Items to confirm**: Review the use of global state and the naming conventions used in the new module.

---

## Code Review

### 1. Readability & Consistency
* **Formatting**: The code generally follows standard indentation, but the logic within the `try-except` block is deeply nested, reducing readability.

### 2. Naming Conventions
* **Function Naming**: `functionThatDoesTooMuchAndIsNotClear` violates naming conventions. It is not descriptive of the function's purpose and uses camelCase, which is not the Python standard (PEP 8 recommends `snake_case`).
* **Variable Naming**: `ANOTHER_GLOBAL` is non-descriptive.

### 3. Software Engineering Standards
* **Modularity**: The function violates the Single Responsibility Principle. It handles data creation, data transformation, business logic (age validation), and reporting. These should be split into separate functions (e.g., `load_data()`, `calculate_metrics()`, `print_report()`).
* **Global State**: The use of `global GLOBAL_DF` is discouraged. It makes the code harder to test and maintain. Data should be passed as arguments and returned as values.

### 4. Logic & Correctness
* **Exception Handling**: The `except Exception as e` block is too broad. Catching all exceptions and printing a generic message ("我不管錯誤是什麼") hides potential bugs and makes debugging difficult.
* **Nested Logic**: The nested `if` statements for `mean_age` can be simplified using `elif`.

### 5. Performance & Security
* **Resource Management**: No significant performance bottlenecks for this data size, but the reliance on global variables will hinder scalability.

### 6. Documentation & Testing
* **Missing Tests**: No unit tests are provided for the data processing logic.
* **Documentation**: There are no docstrings explaining the purpose or expected output of the function.

### Summary of Suggested Refactorings
1. Rename `functionThatDoesTooMuchAndIsNotClear` to something like `analyze_student_scores`.
2. Remove `GLOBAL_DF` and pass the DataFrame as a parameter.
3. Split the function into smaller, focused components.
4. Replace the broad `Exception` catch with specific exceptions or remove the try-block if the operations are safe.
5. Use `snake_case` for all function and variable names.
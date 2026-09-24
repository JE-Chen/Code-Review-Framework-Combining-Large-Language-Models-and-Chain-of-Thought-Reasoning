Based on the provided global rules, here is the code review for `data_analysis.py`.

### 1. Readability & Consistency
- **Formatting**: The indentation is consistent, but the code lacks docstrings or comments explaining the purpose of the logic.
- **Consistency**: The code mixes English (variable names) and Chinese (print statements), which may hinder maintainability in a multilingual team.

### 2. Naming Conventions
- **Function Naming**: `functionThatDoesTooMuchAndIsNotClear` is a poor name. It is self-deprecating rather than descriptive. It should be renamed to reflect its actual purpose (e.g., `analyze_student_scores`).
- **Variable Naming**: `ANOTHER_GLOBAL` is non-descriptive. It should be named based on its content (e.g., `START_MESSAGE`).

### 3. Software Engineering Standards
- **Modularity**: The function violates the Single Responsibility Principle. It handles data creation, data transformation, business logic (age validation), and reporting all in one block.
- **Global State**: The use of `global GLOBAL_DF` is a bad practice. It makes the code harder to test and debug. Data should be passed as arguments and returned as values.
- **Abstraction**: The data creation logic should be separated from the analysis logic.

### 4. Logic & Correctness
- **Nested Conditionals**: The `if mean_age > 20` block is deeply nested. This can be flattened using `elif` for better readability.
- **Exception Handling**: The `try-except` block catches the generic `Exception` class and prints a non-professional message ("我不管錯誤是什麼"). This masks potential bugs and provides no actionable debugging information.

### 5. Performance & Security
- **Resource Management**: For this small dataset, there are no performance bottlenecks. However, relying on global variables can lead to memory leaks or state corruption in larger applications.

### 6. Documentation & Testing
- **Documentation**: There are no docstrings for the function or the module.
- **Testing**: No unit tests are provided to verify the calculations or the boundary conditions of the age checks.

---

### Summary of Recommendations

| Category | Issue | Recommendation |
| :--- | :--- | :--- |
| **Naming** | Non-descriptive function/variable names | Rename to `analyze_student_scores` and `START_MESSAGE`. |
| **Architecture** | Use of `global` variables | Pass DataFrames as parameters and return results. |
| **Modularity** | Function does too many things | Split into `load_data()`, `process_scores()`, and `print_analysis()`. |
| **Error Handling** | Generic `Exception` catch | Catch specific pandas/type errors and use professional logging. |
| **Logic** | Deeply nested `if` statements | Refactor to `if/elif/else` structure. |
### Code Review

**Naming Conventions**
*   **Function Naming:** `functionThatDoesTooMuchAndIsNotClear` is non-descriptive and violates Python's `snake_case` convention. Rename it to reflect its actual purpose (e.g., `analyze_student_scores`).
*   **Global Variables:** `GLOBAL_DF` and `ANOTHER_GLOBAL` are generic. Use names that describe the data they hold (e.g., `STUDENT_DATA_DF`).

**Software Engineering Standards**
*   **Global State:** The use of `global GLOBAL_DF` creates tight coupling and makes the code harder to test and maintain. Pass the DataFrame as an argument and return the result instead.
*   **Modularity:** The function violates the Single Responsibility Principle. It handles data creation, data transformation, validation/logging, and reporting. These should be split into separate functions.

**Logic & Correctness**
*   **Exception Handling:** The `except Exception as e` block is too broad. Catching all exceptions and printing a generic message ("我不管錯誤是什麼") hides potential bugs and makes debugging difficult.
*   **Nested Logic:** The nested `if` statements for `mean_age` are redundant. Use `elif` for better readability.

**Readability & Consistency**
*   **Language Consistency:** The code mixes English (variable names/logic) and Chinese (print statements). Stick to one language for consistency across the codebase.

**Suggested Improvements**
*   **Refactor to:**
    1.  `load_data()` $\rightarrow$ returns DataFrame.
    2.  `add_random_scores(df)` $\rightarrow$ returns modified DataFrame.
    3.  `validate_age_range(df)` $\rightarrow$ handles the age logic.
    4.  `print_summary(df)` $\rightarrow$ handles the `.describe()` output.
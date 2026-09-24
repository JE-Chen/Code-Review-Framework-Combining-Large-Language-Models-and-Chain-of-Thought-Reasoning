Based on the provided global rules and the specific review template, here is the first-step code review for `data_analysis.py`.

### 1. Readability & Consistency
*   **Formatting:** The indentation is consistent, but the script lacks type hinting and a structured layout, making it feel more like a script than a maintainable module.
*   **Comments:** There are no comments explaining the purpose of the logic or the expected output.

### 2. Naming Conventions
*   **Function Naming:** `functionThatDoesTooMuchAndIsNotClear` is a poor name. It describes a problem rather than the intent. Use a descriptive name like `analyze_student_performance`.
*   **Variable Naming:** 
    *   `GLOBAL_DF` and `ANOTHER_GLOBAL` are vague. Use names that reflect the content (e.g., `STUDENT_DATA_DF` and `START_MESSAGE`).
    *   `ScorePlusRandom` and `ScorePlusRandomAgain` are redundant and implementation-focused.

### 3. Software Engineering Standards
*   **Global State:** The use of `global GLOBAL_DF` is a bad practice. It makes the code harder to test and prone to side effects. Pass data as arguments and return results.
*   **Modularity:** The function violates the Single Responsibility Principle (SRP) by handling data creation, data transformation, analysis, and reporting all in one block. Break these into separate functions.
*   **Hard-coded Data:** Data is hard-coded inside the logic; move data loading to a separate utility or configuration.

### 4. Logic & Correctness
*   **Nested Conditionals:** The `mean_age` checks use deeply nested `if` statements that could be simplified (e.g., using `elif`).
*   **Exception Handling:** `except Exception as e` with a print statement like `"我不管錯誤是什麼"` is an anti-pattern. Catch specific exceptions and use a proper logging system.

### 5. Concise Improvement Suggestions
*   **Refactor Globals:** Replace `global` variables with function parameters and return values.
*   **Rename Functions/Variables:** Change names to reflect business intent (e.g., `calculate_statistics()`) rather than implementation details.
*   **Decompose Logic:** Split the function into `load_data()`, `transform_data()`, and `print_analysis_report()`.
*   **Flatten Logic:** Replace the nested `if` statements for `mean_age` with a flat `if/elif/else` structure.
*   **Improve Error Handling:** Catch specific Pandas or Value errors instead of the generic `Exception` class.
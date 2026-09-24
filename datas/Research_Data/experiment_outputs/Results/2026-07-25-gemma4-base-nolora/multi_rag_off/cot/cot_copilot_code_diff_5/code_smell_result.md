- Code Smell Type: Violation of Single Responsibility Principle (SRP) / Long Function
- Problem Location: `functionThatDoesTooMuchAndIsNotClear()`
- Detailed Explanation: The function is handling multiple unrelated responsibilities: data initialization, data transformation (adding random scores), business logic validation (age range checking), and reporting (printing describe statistics). This makes the code difficult to test, reuse, and maintain.
- Improvement Suggestions: Split the function into smaller, focused functions: `load_data()`, `apply_random_adjustments()`, `validate_age_metrics()`, and `print_summary_statistics()`.
- Priority Level: High

- Code Smell Type: Use of Global State
- Problem Location: `GLOBAL_DF = None` and `global GLOBAL_DF`
- Detailed Explanation: Relying on global variables creates hidden dependencies and makes the code prone to side-effect bugs. It prevents the code from being thread-safe and makes unit testing difficult because the state persists between test cases.
- Improvement Suggestions: Pass the DataFrame as an argument to functions and return the modified DataFrame as a result.
- Priority Level: High

- Code Smell Type: Unclear/Non-Standard Naming
- Problem Location: `functionThatDoesTooMuchAndIsNotClear()` and `ANOTHER_GLOBAL`
- Detailed Explanation: The function name is meta-descriptive rather than semantic (it describes the quality of the code rather than what the code does). `ANOTHER_GLOBAL` is generic and provides no context regarding its purpose. This violates naming conventions for readability and maintainability.
- Improvement Suggestions: Rename the function to something descriptive like `analyze_student_performance()` and rename the global constant to something like `START_MESSAGE`.
- Priority Level: Medium

- Code Smell Type: Overly Broad Exception Handling
- Problem Location: `except Exception as e: print("我不管錯誤是什麼:", e)`
- Detailed Explanation: Catching the base `Exception` class hides potential bugs (like `KeyError` or `TypeError`) that should be handled specifically or allowed to fail fast. The print statement also indicates a lack of proper error logging or recovery strategy.
- Improvement Suggestions: Catch specific exceptions (e.g., `pd.errors.EmptyDataError` or `KeyError`) and use a proper logging library instead of `print`.
- Priority Level: Medium

- Code Smell Type: Deeply Nested Conditionals (Arrow Anti-pattern)
- Problem Location: The `if mean_age > 20: if mean_age < 50:` block.
- Detailed Explanation: Nested `if` statements increase cognitive load and make the logic harder to follow.
- Improvement Suggestions: Use guard clauses or combined logical operators (e.g., `if 20 < mean_age < 50:`).
- Priority Level: Low
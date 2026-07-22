- Code Smell Type: Unclear Naming
- Problem Location: `def functionThatDoesTooMuchAndIsNotClear():`
- Detailed Explanation: The function name is non-descriptive and meta-referential rather than semantic. It does not describe the business logic or the purpose of the operation, which hinders readability and maintainability.
- Improvement Suggestions: Rename the function to reflect its actual purpose, such as `analyze_student_scores()` or `process_and_summarize_data()`.
- Priority Level: High

- Code Smell Type: Use of Global State
- Problem Location: `GLOBAL_DF = None` and `global GLOBAL_DF`
- Detailed Explanation: Relying on global variables creates tight coupling and makes the code difficult to test and debug. It introduces side effects where the state of the application depends on the order of function execution, which can lead to unpredictable behavior in larger systems.
- Improvement Suggestions: Pass the DataFrame as an argument to functions and return the modified DataFrame or results. Encapsulate the logic within a class or a set of pure functions.
- Priority Level: High

- Code Smell Type: Violation of Single Responsibility Principle (SRP)
- Problem Location: `functionThatDoesTooMuchAndIsNotClear()`
- Detailed Explanation: This single function is responsible for data creation, data transformation (adding random scores), business logic validation (age checks), and reporting (printing statistics). This makes the code harder to reuse and test in isolation.
- Improvement Suggestions: Split the function into smaller, focused functions: `load_data()`, `augment_scores()`, `validate_age_range()`, and `print_summary_statistics()`.
- Priority Level: Medium

- Code Smell Type: Overly Broad Exception Handling
- Problem Location: `except Exception as e: print("我不管錯誤是什麼:", e)`
- Detailed Explanation: Catching the base `Exception` class hides potential bugs (like `KeyError` or `TypeError`) and makes debugging difficult. Furthermore, the print statement is unprofessional and provides no actionable information for recovery.
- Improvement Suggestions: Catch specific exceptions (e.g., `pd.errors.EmptyDataError` or `KeyError`) and implement proper logging or error handling strategies.
- Priority Level: Medium

- Code Smell Type: Deeply Nested Conditionals (Arrow Anti-pattern)
- Problem Location: The nested `if mean_age > 20: if mean_age < 50:` block.
- Detailed Explanation: Nested if-statements increase cognitive load and make the logic harder to follow.
- Improvement Suggestions: Use guard clauses or combined logical operators (e.g., `if 20 < mean_age < 50:`) to flatten the structure.
- Priority Level: Low
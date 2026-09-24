- Code Smell Type: Shared Mutable State (Global Variables)
- Problem Location: `GLOBAL_DF = None` and `global GLOBAL_DF` inside `functionThatDoesTooMuchAndIsNotClear()`
- Detailed Explanation: The use of a global variable to store the DataFrame introduces hidden coupling and makes the code difficult to test and reason about. If multiple functions modify `GLOBAL_DF`, it becomes hard to track the state of the data, and it prevents the code from being thread-safe or reusable in a larger system.
- Improvement Suggestions: Remove the global variable. Define the DataFrame within the function or pass it as an argument to functions that need it. Return the resulting DataFrame from the function.
- Priority Level: High

- Code Smell Type: Violation of Single Responsibility Principle (SRP) / Long Function
- Problem Location: `functionThatDoesTooMuchAndIsNotClear()`
- Detailed Explanation: This function is performing multiple unrelated tasks: data initialization, data transformation (adding random scores), business logic validation (age checks), and reporting (printing statistics). This makes the function hard to maintain, test, and reuse.
- Improvement Suggestions: Split the function into smaller, focused functions: `load_data()`, `add_random_scores(df)`, `validate_average_age(df)`, and `print_summary_statistics(df)`.
- Priority Level: High

- Code Smell Type: Unclear Naming
- Problem Location: `functionThatDoesTooMuchAndIsNotClear()`
- Detailed Explanation: The function name is non-descriptive and uses camelCase, which violates Python's PEP 8 naming convention (which prefers `snake_case`). A name should describe *what* the function does, not *how* it is implemented or a critique of its own quality.
- Improvement Suggestions: Rename the function to something descriptive, such as `analyze_student_scores()`.
- Priority Level: Medium

- Code Smell Type: Deeply Nested Conditional Logic
- Problem Location: 
```python
if mean_age > 20:
    if mean_age < 50:
        print("平均年齡在合理範圍:", mean_age)
    else:
        print("平均年齡過高:", mean_age)
else:
    print("平均年齡過低:", mean_age)
```
- Detailed Explanation: The nested `if` statements increase cognitive load and make the logic harder to follow.
- Improvement Suggestions: Use guard clauses or `if-elif-else` structures to flatten the logic.
- Priority Level: Medium

- Code Smell Type: Broad Exception Handling
- Problem Location: `except Exception as e:`
- Detailed Explanation: Catching the base `Exception` class hides potential bugs (like `KeyError` or `TypeError`) and makes debugging difficult because it treats all errors identically.
- Improvement Suggestions: Catch specific exceptions that are expected during the calculation of the mean or DataFrame access.
- Priority Level: Medium
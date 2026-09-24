- Code Smell Type: Unclear Naming & Violation of Naming Conventions
- Problem Location: `def functionThatDoesTooMuchAndIsNotClear():`
- Detailed Explanation: The function name is not descriptive of its actual purpose and uses `camelCase`, which violates PEP 8 standards for Python (which prescribes `snake_case` for functions). Furthermore, the name itself admits to being "not clear," which hinders maintainability and readability.
- Improvement Suggestions: Rename the function to reflect its actual behavior, such as `analyze_student_scores()` or `process_data_analysis()`.
- Priority Level: High

- Code Smell Type: Use of Global State (Tight Coupling)
- Problem Location: `GLOBAL_DF = None` and `global GLOBAL_DF` inside the function.
- Detailed Explanation: Relying on global variables creates hidden dependencies and makes the code difficult to test and debug. If multiple functions modify `GLOBAL_DF`, it becomes nearly impossible to track the state of the data at any given point in the execution flow.
- Improvement Suggestions: Remove the global variable. Define the DataFrame inside the function or pass it as an argument to functions that need it, and return the result.
- Priority Level: High

- Code Smell Type: Violation of Single Responsibility Principle (SRP)
- Problem Location: `functionThatDoesTooMuchAndIsNotClear()`
- Detailed Explanation: This single function is performing four distinct tasks: data initialization, data transformation (adding random scores), business logic validation (age range checks), and reporting (printing describe statistics). This makes the code harder to reuse and test.
- Improvement Suggestions: Break the function into smaller, modular functions:
    1. `load_data()`: To create/load the DataFrame.
    2. `add_random_scores(df)`: To handle the transformations.
    3. `validate_age_metrics(df)`: To handle the age range logic.
    4. `print_summary_statistics(df)`: To handle the output.
- Priority Level: Medium

- Code Smell Type: Overly Broad Exception Handling
- Problem Location: `except Exception as e: print("我不管錯誤是什麼:", e)`
- Detailed Explanation: Catching the base `Exception` class hides potential bugs (like `KeyError` or `TypeError`) that should be handled specifically or allowed to fail fast during development. The print statement also indicates a lack of proper error logging/handling strategy.
- Improvement Suggestions: Catch specific exceptions (e.g., `pd.errors.EmptyDataError` or `KeyError`) and use a proper logging framework instead of `print`.
- Priority Level: Medium

- Code Smell Type: Deeply Nested Conditional Logic (Arrow Anti-pattern)
- Problem Location: 
  ```python
  if mean_age > 20:
      if mean_age < 50:
          ...
  ```
- Detailed Explanation: Nested `if` statements increase cognitive load and make the logic harder to follow.
- Improvement Suggestions: Use `elif` to flatten the structure:
  ```python
  if mean_age <= 20:
      print("平均年齡過低:", mean_age)
  elif mean_age < 50:
      print("平均年齡在合理範圍:", mean_age)
  else:
      print("平均年齡過高:", mean_age)
  ```
- Priority Level: Low
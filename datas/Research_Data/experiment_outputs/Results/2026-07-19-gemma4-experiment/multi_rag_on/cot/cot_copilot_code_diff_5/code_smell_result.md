- Code Smell Type: Unclear Naming & Inconsistent Style
- Problem Location: `functionThatDoesTooMuchAndIsNotClear()`
- Detailed Explanation: The function name is overly verbose and describes its own flaws rather than its purpose. Furthermore, it uses `camelCase`, which violates PEP 8 standards for Python functions (`snake_case`). This reduces readability and professional consistency across the codebase.
- Improvement Suggestions: Rename the function to reflect its actual behavior (e.g., `analyze_student_scores`) and use `snake_case`.
- Priority Level: Medium

- Code Smell Type: Use of Global State
- Problem Location: `GLOBAL_DF = None` and `global GLOBAL_DF`
- Detailed Explanation: Relying on global variables creates tight coupling and makes the code difficult to test and debug. It introduces side effects where the state of the program depends on the order of function execution, which can lead to unpredictable behavior in larger systems.
- Improvement Suggestions: Pass the DataFrame as an argument to functions and return the modified DataFrame or results. Encapsulate the logic within a class or a main execution flow.
- Priority Level: High

- Code Smell Type: Violation of Single Responsibility Principle (SRP)
- Problem Location: `functionThatDoesTooMuchAndIsNotClear()`
- Detailed Explanation: The function is performing multiple unrelated tasks: initializing data, performing calculations, executing business logic (age validation), and printing reports. This makes the code harder to maintain, reuse, or unit test.
- Improvement Suggestions: Split the function into smaller, focused functions:
    1. `load_data()`: To create/load the DataFrame.
    2. `calculate_scores()`: To handle the random score additions.
    3. `validate_age_range()`: To handle the age logic.
    4. `print_summary()`: To handle the output.
- Priority Level: High

- Code Smell Type: Overly Broad Exception Handling
- Problem Location: `except Exception as e: print("我不管錯誤是什麼:", e)`
- Detailed Explanation: Catching the base `Exception` class hides potential bugs (like `KeyError` or `TypeError`) and makes debugging difficult. The print statement is also non-descriptive and unprofessional.
- Improvement Suggestions: Catch specific exceptions (e.g., `pd.errors.EmptyDataError` or `KeyError`) and use a proper logging framework instead of `print` for error reporting.
- Priority Level: Medium

- Code Smell Type: Deeply Nested Conditionals (Arrow Anti-pattern)
- Problem Location: The `if mean_age > 20: if mean_age < 50:` block.
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
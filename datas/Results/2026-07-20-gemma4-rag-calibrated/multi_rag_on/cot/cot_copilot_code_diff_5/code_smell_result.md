- Code Smell Type: Unclear Naming & Violation of Naming Conventions
- Problem Location: `functionThatDoesTooMuchAndIsNotClear()`
- Detailed Explanation: The function name is not descriptive of its purpose and uses camelCase, which violates PEP 8 (the standard Python naming convention that prescribes `snake_case` for functions). This reduces readability and makes the codebase inconsistent.
- Improvement Suggestions: Rename the function to reflect its actual behavior, such as `analyze_student_scores()` or `process_data_summary()`.
- Priority Level: Medium

- Code Smell Type: Tight Coupling & Use of Global State
- Problem Location: `GLOBAL_DF = None` and `global GLOBAL_DF` inside the function.
- Detailed Explanation: The function relies on and modifies a global variable. This creates hidden dependencies, makes the code harder to test in isolation, and can lead to unpredictable behavior if multiple functions modify the same global state.
- Improvement Suggestions: Pass the DataFrame as an argument to the function and return the modified DataFrame or the result of the analysis.
- Priority Level: High

- Code Smell Type: Violation of Single Responsibility Principle (SRP)
- Problem Location: `functionThatDoesTooMuchAndIsNotClear()`
- Detailed Explanation: The function is performing too many distinct tasks: initializing data, performing calculations, handling business logic (age validation), and printing reports. This makes the code difficult to maintain and reuse.
- Improvement Suggestions: Split the function into smaller, focused functions:
    1. `load_data()`: To create/load the DataFrame.
    2. `calculate_scores()`: To handle the random score additions.
    3. `validate_age_range()`: To handle the age-based printing logic.
    4. `print_summary()`: To handle the `describe()` output.
- Priority Level: High

- Code Smell Type: Overly Broad Exception Handling
- Problem Location: `except Exception as e: print("我不管錯誤是什麼:", e)`
- Detailed Explanation: Catching the base `Exception` class hides potential bugs (like `KeyError` or `TypeError`) and makes debugging difficult. Furthermore, the print statement is unprofessional and does not provide actionable information.
- Improvement Suggestions: Catch specific exceptions (e.g., `pd.errors.EmptyDataError` or `KeyError`) and use a proper logging mechanism instead of `print`.
- Priority Level: Medium

- Code Smell Type: Deeply Nested Logic (Arrow Anti-pattern)
- Problem Location: The nested `if mean_age > 20: if mean_age < 50:` block.
- Detailed Explanation: Deep nesting increases cognitive load and makes the logic harder to follow.
- Improvement Suggestions: Use `elif` statements to flatten the logic:
  ```python
  if mean_age <= 20:
      print("平均年齡過低:", mean_age)
  elif mean_age < 50:
      print("平均年齡在合理範圍:", mean_age)
  else:
      print("平均年齡過高:", mean_age)
  ```
- Priority Level: Low
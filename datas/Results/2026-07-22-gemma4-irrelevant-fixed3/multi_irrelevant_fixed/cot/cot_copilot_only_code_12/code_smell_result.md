- Code Smell Type: Excessive Use of Global State
- Problem Location: `DATAFRAME = None`, `resultList = []`, `tempStorage = {}` and the `global` keywords inside `loadData`, `calcStats`, and `plotData`.
- Detailed Explanation: The code relies on global variables to pass data between functions. This creates tight coupling and makes the code difficult to test, debug, and reuse. If this script were integrated into a larger system, these globals would lead to unpredictable side effects and prevent the functions from being thread-safe or re-entrant.
- Improvement Suggestions: Refactor functions to accept parameters and return values. For example, `loadData()` should return a DataFrame, and `calcStats(df)` should take that DataFrame as an argument and return the results.
- Priority Level: High

- Code Smell Type: Duplicate Code & Poor Logic Structure
- Problem Location: Inside `calcStats()`:
  ```python
  if col == "A":
      meanA = st.mean(DATAFRAME[col])
      resultList.append(("meanA", meanA))
      # ...
  else:
      meanB = st.mean(DATAFRAME[col])
      resultList.append(("meanB", meanB))
  ```
- Detailed Explanation: The logic for calculating the mean is duplicated for columns "A" and "B". Furthermore, the function performs redundant calculations (e.g., calling `st.mean` twice for column "A") and stores the same data in both a list and a dictionary without a clear architectural reason.
- Improvement Suggestions: Use a loop or a mapping to handle numeric columns generically. Use pandas' built-in `.mean()` method instead of the `statistics` module for better performance and cleaner syntax.
- Priority Level: Medium

- Code Smell Type: Inconsistent & Non-Descriptive Naming
- Problem Location: `DATAFRAME`, `resultList`, `tempStorage`, `meanA_again`, `dummy`.
- Detailed Explanation: The naming violates PEP 8 conventions (mixing `UPPER_CASE` for mutable globals and `camelCase` for variables). Names like `tempStorage` and `dummy` are non-descriptive and provide no semantic meaning regarding the data they hold.
- Improvement Suggestions: Use `snake_case` for all variables and functions. Rename `resultList` to something descriptive (e.g., `column_statistics`) and `tempStorage` to reflect its actual purpose.
- Priority Level: Low
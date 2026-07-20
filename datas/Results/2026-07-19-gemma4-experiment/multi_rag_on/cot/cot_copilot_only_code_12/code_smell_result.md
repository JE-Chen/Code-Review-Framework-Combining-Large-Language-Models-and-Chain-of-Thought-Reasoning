- Code Smell Type: Excessive Use of Global State
- Problem Location: `DATAFRAME = None`, `resultList = []`, `tempStorage = {}` and the `global` keywords inside `loadData`, `calcStats`, and `plotData`.
- Detailed Explanation: The code relies on global variables to pass data between functions. This creates tight coupling and makes the code difficult to test, debug, and reuse. If this script were expanded, tracking where and when these variables are modified would become a significant maintenance burden and could lead to unpredictable side effects.
- Improvement Suggestions: Refactor functions to accept parameters and return values. For example, `loadData()` should return a DataFrame, and `calcStats(df)` should accept a DataFrame and return the results.
- Priority Level: High

- Code Smell Type: Unclear and Inconsistent Naming
- Problem Location: `DATAFRAME`, `resultList`, `tempStorage`, `meanA`, `meanB`.
- Detailed Explanation: The naming conventions are inconsistent. `DATAFRAME` uses SCREAMING_SNAKE_CASE (usually reserved for constants), while `resultList` and `tempStorage` use camelCase, which deviates from the PEP 8 standard (snake_case) for Python variables. Furthermore, names like `tempStorage` and `resultList` are generic and do not describe the actual data they hold.
- Improvement Suggestions: Rename variables to follow PEP 8 (e.g., `df`, `stats_results`, `summary_metrics`). Use descriptive names that reflect the business logic rather than the data structure.
- Priority Level: Medium

- Code Smell Type: Redundant Logic and Duplicate Code
- Problem Location: Inside `calcStats()`:
  ```python
  resultList.append(("meanA", meanA))
  tempStorage["meanA"] = meanA
  resultList.append(("meanA_again", st.mean(DATAFRAME[col])))
  ```
- Detailed Explanation: The function performs the same calculation (`st.mean`) multiple times for the same column and stores the result in multiple places (`resultList` and `tempStorage`) without a clear purpose. This increases complexity and the risk of inconsistency if the logic changes.
- Improvement Suggestions: Calculate the mean once, store it in a local variable, and use that variable for all subsequent operations. Remove the redundant `meanA_again` and `tempStorage` if they serve no functional purpose.
- Priority Level: Medium

- Code Smell Type: Violation of Single Responsibility Principle (SRP)
- Problem Location: `calcStats()`
- Detailed Explanation: The function is attempting to perform calculations, manage a global list, and update a global dictionary simultaneously. It also contains hardcoded column checks (`if col == "A"`) and arbitrary logic (e.g., `meanB + 42`), mixing data processing with specific business rules.
- Improvement Suggestions: Separate the logic for calculating statistics from the logic for storing/reporting them. Use a mapping or a loop to handle numeric columns generically rather than using `if/else` blocks for specific column names.
- Priority Level: Low
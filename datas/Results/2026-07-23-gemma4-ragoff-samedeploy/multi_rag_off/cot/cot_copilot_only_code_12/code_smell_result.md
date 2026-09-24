- Code Smell Type: Excessive Use of Global State
- Problem Location: `DATAFRAME = None`, `resultList = []`, `tempStorage = {}` and the `global` keywords inside `loadData`, `calcStats`, and `plotData`.
- Detailed Explanation: The code relies on global variables to pass data between functions. This creates tight coupling and makes the code difficult to test, debug, and reuse. If this script were expanded, tracking where and when these variables are modified would become a significant maintenance burden and could lead to unpredictable side effects.
- Improvement Suggestions: Pass data as arguments to functions and return results. For example, `loadData()` should return the DataFrame, and `calcStats(df)` should take the DataFrame as an input and return the results.
- Priority Level: High

- Code Smell Type: Unclear and Inconsistent Naming
- Problem Location: `DATAFRAME`, `resultList`, `tempStorage`, `meanA`, `meanB`.
- Detailed Explanation: The naming conventions are inconsistent. `DATAFRAME` uses SCREAMING_SNAKE_CASE (usually reserved for constants), while `resultList` and `tempStorage` use camelCase, which deviates from the PEP 8 standard (snake_case) for Python variables. Furthermore, names like `tempStorage` and `resultList` are generic and do not describe the actual data they hold.
- Improvement Suggestions: Rename variables to follow PEP 8 (e.g., `df`, `stats_results`, `metrics_cache`). Use descriptive names that reflect the business logic rather than the data structure.
- Priority Level: Medium

- Code Smell Type: Duplicate Code and Poor Logic Structure
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
- Detailed Explanation: The logic for calculating the mean is duplicated for columns "A" and "B". Additionally, the function performs redundant calculations (e.g., calling `st.mean` twice for column "A") and stores the same data in both a list and a dictionary without a clear purpose.
- Improvement Suggestions: Generalize the calculation logic. Iterate through the numeric columns and apply the mean function dynamically. Remove redundant calculations and consolidate the storage of results into a single, consistent structure.
- Priority Level: Medium
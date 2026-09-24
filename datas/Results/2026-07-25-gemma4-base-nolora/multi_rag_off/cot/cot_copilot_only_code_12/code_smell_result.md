- Code Smell Type: Excessive Use of Global State
- Problem Location: `DATAFRAME = None`, `resultList = []`, `tempStorage = {}` and the `global` keywords inside `loadData`, `calcStats`, and `plotData`.
- Detailed Explanation: The code relies heavily on global variables to pass data between functions. This creates tight coupling and makes the code difficult to test, debug, and reuse. If this script were expanded, tracking where and when a global variable was modified would become a significant maintenance burden and could lead to unpredictable side effects.
- Improvement Suggestions: Refactor the functions to accept arguments and return values. For example, `loadData()` should return a DataFrame, and `calcStats(df)` should take that DataFrame as an input and return the results.
- Priority Level: High

- Code Smell Type: Unclear/Inconsistent Naming
- Problem Location: `DATAFRAME`, `resultList`, `tempStorage`, `meanA`, `meanB`.
- Detailed Explanation: The naming conventions are inconsistent. `DATAFRAME` uses SCREAMING_SNAKE_CASE (usually reserved for constants), while `resultList` uses camelCase, and `loadData` uses camelCase. Python (PEP 8) standard is snake_case for variables and functions. Furthermore, names like `tempStorage` and `resultList` are generic and do not describe the *purpose* of the data they hold.
- Improvement Suggestions: Rename variables to follow PEP 8 (e.g., `df`, `results`, `stats_cache`). Use descriptive names that explain the content (e.g., `column_means` instead of `tempStorage`).
- Priority Level: Medium

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
- Detailed Explanation: The logic for calculating the mean is duplicated for columns "A" and "B". Additionally, the function performs redundant calculations (calling `st.mean` twice for column "A") and stores the same data in two different structures (`resultList` and `tempStorage`), which is inefficient and prone to synchronization errors.
- Improvement Suggestions: Use a loop or a mapping to handle numeric columns generically. Calculate the mean once per column and store it in a single, consistent data structure (like a dictionary).
- Priority Level: Medium

- Code Smell Type: Violation of Single Responsibility Principle (SRP)
- Problem Location: `calcStats()`
- Detailed Explanation: The function `calcStats` is doing too many things: it filters columns, performs calculations, manages a global list, and manages a global dictionary. It mixes data processing with state management.
- Improvement Suggestions: Separate the logic into a function that calculates statistics and a separate mechanism for reporting or storing those results.
- Priority Level: Low
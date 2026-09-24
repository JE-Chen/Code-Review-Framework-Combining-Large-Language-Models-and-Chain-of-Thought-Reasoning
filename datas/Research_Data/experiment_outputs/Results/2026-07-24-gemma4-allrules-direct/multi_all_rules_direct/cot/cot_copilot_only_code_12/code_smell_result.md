- Code Smell Type: Shared Mutable State (Global Variables)
- Problem Location: `DATAFRAME = None`, `resultList = []`, `tempStorage = {}` and the use of `global` keywords in `loadData`, `calcStats`, and `plotData`.
- Detailed Explanation: The code relies heavily on global variables to pass data between functions. This creates hidden coupling, making the code difficult to test in isolation and prone to side-effect bugs. If `calcStats` is called before `loadData`, the program will crash. It also prevents the code from being used in a multi-threaded environment or processing multiple datasets.
- Improvement Suggestions: Remove global variables. Pass the DataFrame as an argument to functions and return results explicitly.
- Priority Level: High

- Code Smell Type: Violation of Single Responsibility Principle & Deeply Nested Logic
- Problem Location: `calcStats()` function.
- Detailed Explanation: The function is doing too many things: iterating through columns, performing specific calculations based on column names, updating a list, and updating a dictionary. The nested `if/else` structure (checking for "A" or "B", then specifically "A") increases cognitive load and makes the logic brittle.
- Improvement Suggestions: Refactor the logic into smaller functions. Use a mapping or a strategy pattern to handle different column types instead of hard-coded `if/else` blocks.
- Priority Level: Medium

- Code Smell Type: Unclear Naming & Magic Numbers
- Problem Location: `resultList`, `tempStorage`, `meanB + 42`, `bins=7`.
- Detailed Explanation: `resultList` and `tempStorage` are generic names that do not describe the data they hold. The number `42` and `bins=7` are "magic numbers"—constants without explanation, making it unclear why these specific values were chosen.
- Improvement Suggestions: Rename variables to reflect their purpose (e.g., `column_statistics`). Define constants at the top of the file (e.g., `HISTOGRAM_BINS = 7`) to provide semantic meaning.
- Priority Level: Low

- Code Smell Type: Unnecessary Work inside Loops
- Problem Location: `resultList.append(("meanA_again", st.mean(DATAFRAME[col])))`
- Detailed Explanation: The code calculates the mean of the same column twice in a row. This is redundant and inefficient, especially if the dataset grows larger.
- Improvement Suggestions: Calculate the value once, store it in a local variable, and reuse that variable for all subsequent operations.
- Priority Level: Low
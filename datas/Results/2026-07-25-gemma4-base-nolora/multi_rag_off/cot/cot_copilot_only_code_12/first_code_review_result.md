### Code Review

**1. Readability & Consistency**
* **Naming Style:** The codebase uses inconsistent naming conventions. It mixes `SCREAMING_SNAKE_CASE` (`DATAFRAME`), `camelCase` (`resultList`, `tempStorage`, `loadData`), and `snake_case` (implied by standard Python PEP 8). Recommend using `snake_case` for all functions and variables.

**2. Naming Conventions**
* **Vague Naming:** `resultList` and `tempStorage` are generic. Use names that describe the *content* (e.g., `statistics_results` or `metric_cache`).
* **Hardcoded Column Names:** The use of "A", "B", and "C" makes the logic opaque. Use descriptive names (e.g., `age`, `score`, `category`).

**3. Software Engineering Standards**
* **Global State:** The heavy reliance on `global` variables (`DATAFRAME`, `resultList`, `tempStorage`) makes the code difficult to test and maintain. Pass data as arguments and return values instead.
* **Duplicate Logic:** In `calcStats`, `st.mean(DATAFRAME[col])` is called twice for column "A". Store the result in a variable once.
* **Modularity:** `calcStats` handles both calculation and storage. Separating the logic from the data collection would improve maintainability.

**4. Logic & Correctness**
* **Redundant Storage:** `tempStorage` is populated but never read, making it dead code.
* **Hardcoded Logic:** The `if col == "A"` and `else` (for "B") blocks inside the loop create rigid logic that will break if column names change or new numeric columns are added.

**5. Performance & Security**
* **Pandas Usage:** The code uses the `statistics` module on Pandas series. Using native Pandas methods (e.g., `DATAFRAME[col].mean()`) is significantly more performant and idiomatic.

**6. Documentation & Testing**
* **Missing Documentation:** There are no docstrings explaining the purpose of the functions or the expected structure of the data.
* **Lack of Tests:** No unit tests are provided to verify the statistical calculations.

### Summary of Suggested Improvements
* Replace `global` variables with function parameters and return statements.
* Standardize naming to PEP 8 (`snake_case`).
* Replace `statistics.mean()` with `df.mean()`.
* Remove the unused `tempStorage` dictionary.
* Refactor `calcStats` to be data-driven rather than relying on hardcoded column names ("A", "B").
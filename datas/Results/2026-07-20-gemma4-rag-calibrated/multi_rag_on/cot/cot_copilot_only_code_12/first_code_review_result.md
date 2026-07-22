### Code Review

**1. Readability & Consistency**
* **Naming Style:** The codebase uses inconsistent naming conventions. It mixes `SCREAMING_SNAKE_CASE` (`DATAFRAME`), `camelCase` (`resultList`, `tempStorage`, `loadData`), and `snake_case` (implied by standard Python PEP 8). Recommend using `snake_case` for all functions and variables.

**2. Naming Conventions**
* **Vague Naming:** `DATAFRAME`, `resultList`, and `tempStorage` are generic. Use descriptive names (e.g., `raw_data`, `statistics_results`).
* **Cryptic Labels:** The string `"dummy"` in `calcStats` does not describe what the value (column length) actually represents.

**3. Software Engineering Standards**
* **Global State:** The heavy reliance on `global` variables (`DATAFRAME`, `resultList`, `tempStorage`) makes the code difficult to test and maintain. Pass data as arguments and return values instead.
* **Duplicate Logic:** In `calcStats`, `st.mean(DATAFRAME[col])` is called twice for column "A". Store the result in a variable and reuse it.
* **Modularity:** `calcStats` handles both calculation and storage/logging. These concerns should be separated.

**4. Logic & Correctness**
* **Redundant Storage:** `tempStorage` is populated but never read from, making it dead code.
* **Hardcoded Logic:** The `if col == "A"` and `if col in ["A", "B"]` blocks make the function fragile; adding a new numeric column would require modifying the internal logic of the loop.

**5. Performance & Security**
* **Pandas Usage:** The code uses the `statistics` module on Pandas series. Using native Pandas methods (e.g., `DATAFRAME[col].mean()`) is significantly more performant and idiomatic.

**6. Documentation & Testing**
* **Missing Docs:** There are no docstrings or comments explaining the purpose of the calculations or the expected data structure.
* **No Tests:** No unit tests are provided to verify the statistical calculations.
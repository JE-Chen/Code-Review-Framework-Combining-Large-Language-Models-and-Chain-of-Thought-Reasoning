### Code Review

**Naming Conventions**
* **Inconsistent Naming:** The code mixes `snake_case` (standard for Python) with `camelCase` (`resultList`, `tempStorage`, `loadData`, `calcStats`, `plotData`). Use `snake_case` for all functions and variables.
* **Vague Naming:** `DATAFRAME` (all caps usually denotes a constant) and `tempStorage` are generic. Use more descriptive names like `df_metrics` or `stats_cache`.

**Software Engineering Standards**
* **Global State Abuse:** The heavy reliance on `global` variables (`DATAFRAME`, `resultList`, `tempStorage`) makes the code hard to test and maintain. Pass data as arguments and return values instead.
* **Duplicate Logic:** In `calcStats`, `st.mean(DATAFRAME[col])` is called twice for column "A". Calculate the value once and reuse the variable.
* **Hardcoded Logic:** The `if col == "A"` and `if col in ["A", "B"]` blocks make the function rigid. Consider a mapping or a loop that handles numeric columns generically.

**Logic & Correctness**
* **Redundant Storage:** `resultList` and `tempStorage` store the same data in different formats without a clear architectural reason.
* **Inefficient Statistics:** Using the `statistics` module on a Pandas Series is inefficient. Use built-in Pandas methods (e.g., `DATAFRAME[col].mean()`).

**Readability & Consistency**
* **Formatting:** The code is generally well-indented, but the logic inside `calcStats` is cluttered with repetitive `append` calls.

**Suggestions for Improvement**
* Refactor functions to accept `df` as a parameter and return results.
* Replace `statistics.mean()` with `df[col].mean()`.
* Standardize all naming to `snake_case`.
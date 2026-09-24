### Code Review

**1. Readability & Consistency**
* **Global State:** The use of `global` variables (`DATAFRAME`, `resultList`, `tempStorage`) makes the code harder to track and test. Pass data as arguments and return values instead.
* **Formatting:** The code is generally well-indented, but the logic within `calcStats` is cluttered.

**2. Naming Conventions**
* **Variable Naming:** 
    * `DATAFRAME` uses uppercase, which usually denotes a constant, but it is being reassigned.
    * `resultList` and `tempStorage` use camelCase, which deviates from the PEP 8 standard (snake_case) for Python variables.
    * `st` is a cryptic alias for `statistics`.

**3. Software Engineering Standards**
* **Modularity:** `calcStats` is doing too many things (calculating, storing in a list, and storing in a dictionary).
* **Redundancy:** `st.mean(DATAFRAME[col])` is called twice for column "A", which is unnecessary.

**4. Logic & Correctness**
* **Hardcoded Logic:** The `if col == "A"` and `if col in ["A", "B"]` blocks make the function fragile. If the DataFrame columns change, the logic breaks.
* **Redundant Storage:** `tempStorage` is populated but never read from, making it dead code.

**5. Performance & Security**
* **Pandas Usage:** The code uses the `statistics` module on Pandas series. It is significantly more performant to use built-in Pandas methods (e.g., `DATAFRAME[col].mean()`).

**6. Documentation & Testing**
* **Missing Docs:** There are no docstrings or comments explaining the purpose of the calculations or the expected data structure.

---

### Suggested Improvements
* **Refactor Globals:** Change `loadData()` to return the DataFrame and pass it as a parameter to `calcStats(df)` and `plotData(df)`.
* **Use Pandas Methods:** Replace `st.mean(DATAFRAME[col])` with `DATAFRAME[col].mean()`.
* **Generalize Logic:** Instead of checking for "A" or "B", iterate through numeric columns using `DATAFRAME.select_dtypes(include='number')`.
* **Clean up Naming:** Rename `resultList` $\rightarrow$ `results` and `DATAFRAME` $\rightarrow$ `df`.
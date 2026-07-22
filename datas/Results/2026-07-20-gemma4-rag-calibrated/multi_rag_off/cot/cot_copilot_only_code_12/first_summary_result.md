Here is the code review based on the provided global rules.

### 1. Readability & Consistency
- **Formatting:** The code generally follows PEP 8 indentation, but the use of global variables makes the data flow difficult to track.
- **Consistency:** The naming style is inconsistent. It mixes `camelCase` (`loadData`, `resultList`, `tempStorage`) with `UPPER_CASE` (`DATAFRAME`). Python standard (PEP 8) recommends `snake_case` for functions and variables.

### 2. Naming Conventions
- **Descriptive Names:** 
    - `DATAFRAME` is too generic. A name like `raw_data` or `sensor_readings` would be more meaningful.
    - `resultList` and `tempStorage` are generic. They should describe *what* they are storing (e.g., `calculated_metrics`).
    - `col` is acceptable, but `meanA` and `meanB` are redundant since they are already scoped within a column check.

### 3. Software Engineering Standards
- **Modularity & State Management:** The code relies heavily on `global` variables (`global DATAFRAME`, `global resultList`). This makes the functions non-reusable and difficult to test in isolation. 
    - *Recommendation:* Pass data as arguments to functions and return results (e.g., `def calc_stats(df):`).
- **Duplicate Code:** In `calcStats`, `st.mean(DATAFRAME[col])` is called twice for column "A". This is redundant.
- **Abstraction:** The `calcStats` function uses hardcoded column names ("A", "B"). This makes the code fragile if the input data schema changes.

### 4. Logic & Correctness
- **Redundancy:** `resultList.append(("meanA_again", st.mean(DATAFRAME[col])))` performs the exact same calculation as the line above it.
- **Logic Flow:** `tempStorage` is populated but never read from or used anywhere in the program.

### 5. Performance & Security
- **Pandas Usage:** The code uses the `statistics` module (`st.mean`) on Pandas Series. Pandas has built-in optimized methods (e.g., `DATAFRAME[col].mean()`) which are significantly faster and more idiomatic for dataframes.

### 6. Documentation & Testing
- **Documentation:** There are no docstrings or comments explaining the purpose of the calculations or the expected input/output of the functions.
- **Testing:** No unit tests are provided to verify that `calcStats` produces the correct mathematical results.

---

### Summary of Recommendations

| Category | Issue | Priority | Suggestion |
| :--- | :--- | :--- | :--- |
| **Architecture** | Global State | High | Remove `global` keywords; use function arguments and return values. |
| **Naming** | PEP 8 Compliance | Medium | Rename `loadData` $\rightarrow$ `load_data`, `resultList` $\rightarrow$ `results`. |
| **Performance** | Suboptimal API | Medium | Replace `st.mean(df[col])` with `df[col].mean()`. |
| **Clean Code** | Dead Code | Low | Remove `tempStorage` and the redundant `meanA_again` calculation. |
### Code Review

#### 1. Readability & Consistency
- **Naming Conventions**: 
    - `DATAFRAME` is named like a constant (UPPER_CASE) but is used as a mutable global variable. It should follow `snake_case` (e.g., `df` or `data_frame`).
    - `resultList` and `tempStorage` use `camelCase`, which deviates from the Python standard (`snake_case`).
- **Formatting**: The code is generally well-indented, but the logic within `calcStats` is cluttered.

#### 2. Software Engineering Standards
- **Modularization & State Management**: 
    - The code relies heavily on `global` variables (`DATAFRAME`, `resultList`, `tempStorage`). This makes the code difficult to test, prone to side-effect bugs, and non-reusable. 
    - **Recommendation**: Pass data as arguments to functions and return results instead of modifying global state.
- **Redundancy**: 
    - In `calcStats`, `st.mean(DATAFRAME[col])` is called twice for column "A" and stored in both a list and a dictionary. This is redundant and inefficient.
    - The `if col == "A"` and `else` (for "B") blocks contain nearly identical logic. This should be abstracted into a generic calculation loop.

#### 3. Logic & Correctness
- **Hardcoded Logic**: The `calcStats` function relies on hardcoded column names ("A", "B"). If the DataFrame schema changes, the function will fail or produce incorrect results.
- **Data Types**: The logic assumes columns "A" and "B" are always numeric. There is no validation to ensure `st.mean` won't raise a `TypeError`.

#### 4. Performance & Security
- **Performance**: Using `statistics.mean` on a pandas Series is significantly slower than using the built-in pandas method `DATAFRAME[col].mean()`. For larger datasets, this will become a bottleneck.

#### 5. Documentation & Testing
- **Documentation**: There are no docstrings or comments explaining the purpose of the calculations or the expected data format.
- **Testing**: No unit tests are provided to verify the statistical calculations or the data loading process.

---

### Summary of Recommendations

| Category | Issue | Recommendation |
| :--- | :--- | :--- |
| **Architecture** | Global state usage | Refactor functions to accept parameters and return values. |
| **Naming** | Inconsistent casing | Rename `DATAFRAME`, `resultList`, and `tempStorage` to `snake_case`. |
| **Efficiency** | Suboptimal mean calc | Replace `st.mean(df[col])` with `df[col].mean()`. |
| **Clean Code** | Redundant logic | Remove duplicate calls to `st.mean` and consolidate the "A"/"B" logic. |
| **Robustness** | Hardcoded columns | Use data type checks (e.g., `pd.api.types.is_numeric_dtype`) instead of specific column names. |
Here is the code review based on the provided global rules.

### 1. Readability & Consistency
- **Formatting:** The code follows basic PEP 8 indentation, but the use of global variables makes the data flow difficult to track.
- **Consistency:** The naming style is inconsistent. It mixes `camelCase` (`loadData`, `resultList`, `tempStorage`) with `UPPER_CASE` (`DATAFRAME`). Python convention (PEP 8) suggests `snake_case` for functions and variables.

### 2. Naming Conventions
- **Non-Descriptive Names:** 
    - `DATAFRAME` is too generic.
    - `resultList` and `tempStorage` describe the data structure (List/Storage) rather than the data's purpose.
    - `A`, `B`, and `C` as column names lack semantic meaning.

### 3. Software Engineering Standards
- **Modularization & State Management:** The code relies heavily on `global` variables (`global DATAFRAME`, `global resultList`). This makes the functions tightly coupled, difficult to test in isolation, and prone to side-effect bugs.
- **Refactoring Opportunity:** `calcStats` contains redundant logic. The calculations for columns "A" and "B" are nearly identical and should be abstracted into a loop or a helper function.
- **Dead Code:** `tempStorage` is populated but never read from, making it unnecessary.

### 4. Logic & Correctness
- **Redundancy:** In `calcStats`, `st.mean(DATAFRAME[col])` is called twice for column "A" and appended to the list twice under different names (`meanA` and `meanA_again`). This is inefficient and logically redundant.
- **Hardcoded Logic:** The function `calcStats` uses hardcoded strings (`"A"`, `"B"`) to determine logic. If the DataFrame schema changes, the function will fail or produce incorrect "dummy" results without warning.

### 5. Performance & Security
- **Library Usage:** The code uses the `statistics` module (`st.mean`) on a pandas Series. Pandas has built-in vectorized methods (e.g., `DATAFRAME["A"].mean()`) which are significantly faster and more idiomatic for this data structure.

### 6. Documentation & Testing
- **Documentation:** There are no docstrings or comments explaining the purpose of the calculations or the expected input/output of the functions.
- **Testing:** No unit tests are provided to verify that the statistics are calculated correctly.

---

### Summary of Recommendations
1. **Remove Globals:** Pass the DataFrame as an argument to functions and return results instead of modifying global lists.
2. **Standardize Naming:** Rename functions and variables to `snake_case` (e.g., `load_data`, `results_list`).
3. **Leverage Pandas:** Replace `statistics.mean()` with `.mean()` for better performance.
4. **Clean Logic:** Remove the redundant `meanA_again` calculation and the unused `tempStorage` dictionary.
5. **Improve Genericity:** Instead of checking for specific column names like "A" or "B", check for data types (e.g., `pd.api.types.is_numeric_dtype`).
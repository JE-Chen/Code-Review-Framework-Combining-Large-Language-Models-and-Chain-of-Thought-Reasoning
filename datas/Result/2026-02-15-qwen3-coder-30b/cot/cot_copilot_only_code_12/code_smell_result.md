### Code Smell Type: Global State Dependency
- **Problem Location:** `loadData()`, `calcStats()`, and `plotData()` functions use global variables (`DATAFRAME`, `resultList`, `tempStorage`).
- **Detailed Explanation:** The code relies heavily on global state, which makes the system unpredictable and harder to reason about. Functions depend on external state rather than explicit inputs, making them non-deterministic and difficult to test in isolation.
- **Improvement Suggestions:** Replace global variables with parameters and return values. For example, have `loadData()` return the DataFrame instead of setting a global variable.
- **Priority Level:** High

---

### Code Smell Type: Magic Strings/Numbers
- **Problem Location:** `"A"`, `"B"`, `"C"` in column checks; hardcoded string `"X", "Y", "Z"`; magic number `7` for histogram bins.
- **Detailed Explanation:** Hardcoded literals reduce flexibility and readability. If these values change, they must be updated in multiple places, increasing risk of inconsistency.
- **Improvement Suggestions:** Define constants or configuration structures for such values to improve maintainability and allow easier modification.
- **Priority Level:** Medium

---

### Code Smell Type: Long Function
- **Problem Location:** `calcStats()` function contains multiple nested conditional blocks.
- **Detailed Explanation:** This function does more than one thing — calculating stats and storing them — violating the Single Responsibility Principle. It also includes redundant operations like computing `meanA` twice.
- **Improvement Suggestions:** Split into smaller functions: e.g., `computeMeans`, `storeResults`. Also eliminate duplicated computations.
- **Priority Level:** High

---

### Code Smell Type: Poor Naming Convention
- **Problem Location:** Variables like `DATAFRAME`, `resultList`, `tempStorage`.
- **Detailed Explanation:** These names don’t clearly communicate intent or purpose. They’re vague and do not reflect their roles within the context of the application.
- **Improvement Suggestions:** Rename to be descriptive: `data_frame`, `statistics_results`, `cached_values`.
- **Priority Level:** Medium

---

### Code Smell Type: Duplicated Logic
- **Problem Location:** In `calcStats()`, computation of means happens twice for column A.
- **Detailed Explanation:** Identical logic appears twice, suggesting either copy-paste errors or missed opportunities for abstraction.
- **Improvement Suggestions:** Refactor repeated blocks into helper functions or remove redundancy entirely.
- **Priority Level:** Medium

---

### Code Smell Type: Lack of Input Validation / Assumptions
- **Problem Location:** No validation that columns exist or data types match expectations.
- **Detailed Explanation:** Assumes certain structure exists without checking. Could break silently or raise exceptions in edge cases.
- **Improvement Suggestions:** Add assertions or type hints to validate assumptions at runtime or during development.
- **Priority Level:** Medium

---

### Code Smell Type: Inconsistent Use of External Libraries
- **Problem Location:** Mixing `statistics` module (`st.mean`) with direct `pandas` usage (`DATAFRAME[col]`).
- **Detailed Explanation:** Mixing different abstraction layers can confuse developers and lead to inconsistent behavior or performance issues.
- **Improvement Suggestions:** Choose one consistent approach for statistical calculations (preferably leveraging `pandas` methods where applicable).
- **Priority Level:** Low

---

### Code Smell Type: Unused Return Values
- **Problem Location:** `loadData()` returns the DataFrame but it's ignored by calling code.
- **Detailed Explanation:** Indicates a mismatch between function design and usage — returning something useful but not utilizing it effectively.
- **Improvement Suggestions:** Either remove the return value or make sure it’s consumed properly.
- **Priority Level:** Low

---

### Code Smell Type: Non-Descriptive Comments
- **Problem Location:** Comment “for no reason” in `plotData()`.
- **Detailed Explanation:** Comments that lack clarity or are humorous don’t help understanding and should be replaced with informative ones.
- **Improvement Suggestions:** Replace with meaningful descriptions explaining the plot’s purpose or context.
- **Priority Level:** Low

---
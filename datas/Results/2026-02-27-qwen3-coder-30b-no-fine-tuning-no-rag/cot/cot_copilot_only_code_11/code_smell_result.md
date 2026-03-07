---

### Code Smell Type: Global Variable Usage
- **Problem Location:** `DATA` at the top level
- **Detailed Explanation:** The use of a global variable `DATA` makes the code tightly coupled to external data structures. This reduces modularity, testability, and reusability because functions cannot be easily tested without the global state or reused in different contexts.
- **Improvement Suggestions:** Pass `DATA` as an argument to each function instead of accessing it globally. This improves encapsulation and allows easier unit testing.
- **Priority Level:** High

---

### Code Smell Type: Magic Numbers
- **Problem Location:** In `filter_high_scores()` — hard-coded value `40`
- **Detailed Explanation:** The number `40` appears directly in the code without explanation or context. It's unclear what this represents or whether it could change. This hinders readability and maintainability.
- **Improvement Suggestions:** Replace `40` with a named constant such as `HIGH_SCORE_THRESHOLD`. Define it at module level or within a configuration object for clarity.
- **Priority Level:** Medium

---

### Code Smell Type: Duplicated Logic
- **Problem Location:** Multiple checks on `DATA["config"]["threshold"]` and similar nested access patterns
- **Detailed Explanation:** The code repeatedly accesses nested dictionary keys like `DATA["config"]["threshold"]`, leading to redundancy and increased risk of errors when modifying structure. This also makes future changes harder.
- **Improvement Suggestions:** Extract common access patterns into helper functions or classes. For instance, define a class `Config` that wraps access to config values, reducing duplication.
- **Priority Level:** Medium

---

### Code Smell Type: Long Function
- **Problem Location:** `process_misc()`
- **Detailed Explanation:** The function `process_misc()` contains multiple conditional branches and complex nested logic that reduces readability and makes debugging more difficult. It violates the Single Responsibility Principle by doing too much.
- **Improvement Suggestions:** Break down `process_misc()` into smaller helper functions, e.g., one for determining even/odd classification, another for comparing against threshold.
- **Priority Level:** Medium

---

### Code Smell Type: Poor Control Flow Structure
- **Problem Location:** Nested `if` statements in `main()` under Mode X handling
- **Detailed Explanation:** The nested `if` statements make the control flow harder to read and understand. It’s easy to miss edge cases or misinterpret the intended behavior due to deep nesting.
- **Improvement Suggestions:** Flatten the control flow using early returns or switch-like logic via mapping dictionaries. Consider using a state machine or lookup table approach if applicable.
- **Priority Level:** Medium

---

### Code Smell Type: Lack of Input Validation
- **Problem Location:** All functions accessing `DATA` fields without validation
- **Detailed Explanation:** There is no validation that required keys (`"id"`, `"name"`, `"scores"`, etc.) exist in `DATA`. If any key is missing, runtime exceptions will occur, potentially crashing the application.
- **Improvement Suggestions:** Add defensive checks using `.get()` or try-except blocks where appropriate, especially when accessing deeply nested data structures.
- **Priority Level:** High

---

### Code Smell Type: Ambiguous Naming
- **Problem Location:** `s` used as loop variable in `calculate_average_scores()` and `filter_high_scores()`
- **Detailed Explanation:** Using generic names like `s` for variables reduces clarity. While acceptable in small loops, it becomes ambiguous in larger contexts and can mislead readers about the intent.
- **Improvement Suggestions:** Rename `s` to something more descriptive like `score` for better readability and understanding.
- **Priority Level:** Low

---

### Code Smell Type: Inconsistent Return Types
- **Problem Location:** `calculate_average_scores()` returns list of dicts, while `filter_high_scores()` does too; but `process_misc()` returns dict
- **Detailed Explanation:** Although consistent internally, mixing return types (list vs. dict) across functions can complicate downstream consumers who expect uniformity. This may lead to errors or confusion.
- **Priority Level:** Low

---

### Code Smell Type: Lack of Documentation
- **Problem Location:** No docstrings or inline comments explaining purpose of functions
- **Detailed Explanation:** Without documentation, other developers (or even future you) will have difficulty understanding what each function does, its inputs, outputs, and side effects.
- **Improvement Suggestions:** Add docstrings to explain parameters, return types, and expected behavior of each function. Include examples where useful.
- **Priority Level:** Low

---
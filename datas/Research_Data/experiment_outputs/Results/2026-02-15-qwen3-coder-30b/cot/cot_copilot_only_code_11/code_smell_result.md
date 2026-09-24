---

### Code Smell Type: Global State Dependency
- **Problem Location:** All functions (`calculate_average_scores`, `filter_high_scores`, `process_misc`, `main`) directly access `DATA`.
- **Detailed Explanation:** The use of a global variable `DATA` makes the code tightly coupled to a fixed data source. This hinders reusability, testing, and scalability. It also introduces hidden dependencies that are hard to trace or mock during unit tests.
- **Improvement Suggestions:** Pass `DATA` as an argument to each function instead of relying on global state. Refactor into classes or modules with clear interfaces where appropriate.
- **Priority Level:** High

---

### Code Smell Type: Magic Numbers
- **Problem Location:** In `filter_high_scores()`: hardcoded value `40`; in `process_misc()`: hardcoded thresholds and conditions based on `DATA["config"]["threshold"]`.
- **Detailed Explanation:** Hardcoded values reduce readability and make future changes error-prone. These numbers should be defined as constants or parameters for better maintainability and flexibility.
- **Improvement Suggestions:** Define named constants like `HIGH_SCORE_THRESHOLD = 40` and extract threshold logic from configuration if applicable.
- **Priority Level:** Medium

---

### Code Smell Type: Duplicated Logic
- **Problem Location:** Repeated access patterns in `process_misc()` for checking even/odd and comparing against threshold.
- **Detailed Explanation:** The conditional structure duplicates similar checks multiple times without abstraction. This increases maintenance burden when logic needs updating.
- **Improvement Suggestions:** Extract common logic into helper functions such as `classify_value(value, threshold)` or `evaluate_number_classification(value)`.
- **Priority Level:** Medium

---

### Code Smell Type: Long Function
- **Problem Location:** `main()` function contains multiple unrelated operations.
- **Detailed Explanation:** Violates the Single Responsibility Principle. Each section performs different tasks but exists within one cohesive function, making it harder to understand and modify.
- **Improvement Suggestions:** Split responsibilities into smaller helper functions or separate modules for processing averages, filtering, misc logic, and mode-specific behavior.
- **Priority Level:** High

---

### Code Smell Type: Tight Coupling
- **Problem Location:** Functions assume fixed structure of `DATA` keys (`users`, `config`, `misc`), their subkeys (`info`, `scores`, etc.), and field types.
- **Detailed Explanation:** If the schema changes, all dependent functions break. This limits adaptability and robustness.
- **Improvement Suggestions:** Use explicit schemas or data validation layers before accessing nested structures. Consider defining interfaces or DTOs for expected data formats.
- **Priority Level:** High

---

### Code Smell Type: Poor Naming
- **Problem Location:** Function names like `calculate_average_scores`, `filter_high_scores`, `process_misc` do not clearly reflect what they compute or how they interact.
- **Detailed Explanation:** Ambiguous naming reduces clarity. For example, “misc” does not explain its purpose or context.
- **Improvement Suggestions:** Rename functions more descriptively, e.g., `compute_user_averages`, `find_exceeding_scores`, `categorize_miscellaneous_items`.
- **Priority Level:** Medium

---

### Code Smell Type: Lack of Input Validation
- **Problem Location:** No checks for missing fields or invalid data types in `DATA`.
- **Detailed Explanation:** If any required key is missing or malformed, runtime errors will occur silently or crash unexpectedly.
- **Improvement Suggestions:** Add defensive programming practices—validate inputs and handle edge cases gracefully using try-except blocks or assertions.
- **Priority Level:** Medium

---

### Code Smell Type: Unnecessary Nested Conditions
- **Problem Location:** Deep nesting in conditional logic inside `main()` and `process_misc()`.
- **Detailed Explanation:** Complex nested branches decrease readability and increase chance of logical mistakes.
- **Improvement Suggestions:** Flatten conditionals using guard clauses or early returns. Simplify complex boolean expressions.
- **Priority Level:** Medium

---

### Code Smell Type: Lack of Comments or Documentation
- **Problem Location:** No inline comments or docstrings explaining purpose or usage.
- **Detailed Explanation:** Without explanation, other developers cannot easily comprehend intent or reasoning behind decisions.
- **Improvement Suggestions:** Add docstrings to functions describing parameters, return values, and side effects. Include brief comments where logic is non-obvious.
- **Priority Level:** Low

---

### Code Smell Type: Hardcoded String Literals
- **Problem Location:** `"Mode X"` string literal used in `main()`.
- **Detailed Explanation:** Hardcoded strings are difficult to manage across versions and internationalization efforts.
- **Improvement Suggestions:** Define constants or configuration mappings for these literals to allow easy updates or translation.
- **Priority Level:** Low

---
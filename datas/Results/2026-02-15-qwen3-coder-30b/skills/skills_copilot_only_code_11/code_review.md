---

### **Diff #1**

#### **1. Summary**
This PR introduces a Python script that processes structured data (`DATA`) containing users, configuration options, and miscellaneous key-value pairs. It performs three core operations:
- Calculates average scores per user.
- Filters and reports high individual scores.
- Categorizes and returns processed values based on thresholds and parity.

Affected modules: Entire script as a standalone module.
Plain-language summary: The code reads predefined data, calculates some statistics, filters it, and prints categorized outputs depending on config flags.

---

#### **2. Linting Issues**
- **No explicit linting errors found** in this Python snippet — no PEP8 violations like whitespace or indentation issues.
- However:
  - Missing docstrings for functions.
  - Use of magic numbers such as `40` in `filter_high_scores()` could be replaced with named constants.
  - No type hints used; inconsistent use of global variable `DATA`.

Suggested fixes:
- Add docstrings explaining what each function does.
- Replace hardcoded thresholds with configurable constants or variables.
- Consider using `typing` annotations for clarity.

---

#### **3. Code Smells**
| Problem | Description | Impact |
|--------|-------------|--------|
| Global Variable Dependency | All functions depend directly on `DATA`, making testing harder. | Reduces modularity and reusability. |
| Duplicate Logic | Similar conditional logic exists across multiple functions (`if/else` blocks). | Makes future updates error-prone. |
| Poor Naming | Variables like `s`, `total`, `avg` lack descriptive names. | Decreases readability for new developers. |
| Tight Coupling | Functions assume fixed structure of `DATA`. | Difficult to adapt to new schemas without rewriting logic. |

Recommendations:
- Pass `DATA` as parameters instead of relying on global state.
- Extract common logic into helper functions.
- Rename variables for better semantic meaning.
- Introduce configuration classes or models to decouple business logic from raw data structures.

---
### **Diff #1**

---

### **1. Summary**

- **Purpose**: This change introduces a new Python script (`data_analysis.py`) that performs basic data manipulation and statistical analysis on a sample dataset.
- **Scope**: The file contains a single function (`functionThatDoesTooMuchAndIsNotClear`) which handles multiple responsibilities including data creation, transformation, conditional logic, error handling, and printing outputs.
- **Affected Components**:
  - Module: `data_analysis.py`
  - Function: `functionThatDoesTooMuchAndIsNotClear`
  - Global variables: `GLOBAL_DF`, `ANOTHER_GLOBAL`
- **Plain-Language Explanation**: This script creates dummy employee data, adds some random scores to it, calculates average age and prints related messages, then displays summary statistics. However, it's poorly structured and hard to understand due to unclear naming and excessive responsibilities.

---

### **2. Linting Issues**

| Issue | Description | File & Line |
|-------|-------------|-------------|
| Naming Convention Violation | Function name uses snake_case but doesn't reflect its purpose clearly. | `functionThatDoesTooMuchAndIsNotClear` |
| Global Variable Usage | Use of global variables (`GLOBAL_DF`, `ANOTHER_GLOBAL`) makes code harder to test and reason about. | Lines 4–5 |
| Magic String | Hardcoded string `"分析開始"` without context or localization support. | Line 5 |
| Poor Exception Handling | Generic exception catching with unhelpful message. | Line 19 |

**Recommendations**:
- Rename function to something descriptive like `analyze_employee_data`.
- Avoid using global state; pass parameters instead.
- Replace magic strings with constants or config values.
- Improve logging/error reporting by specifying expected exceptions.

---

### **3. Code Smells**

| Smell | Explanation | Impact |
|-------|-------------|--------|
| **God Function** | One function does too many things: data generation, transformations, condition checks, printing, and error handling. | Makes testing and maintenance difficult. |
| **Ambiguous Naming** | Function and variable names don’t express intent or domain meaning. | Reduces readability for developers unfamiliar with codebase. |
| **Side Effects** | Function modifies global state and prints directly instead of returning or emitting events. | Limits reusability and testability. |
| **Tight Coupling** | Relies heavily on global state and hardcoded assumptions. | Difficult to modify or extend without breaking other parts. |

**Improvement Suggestions**:
- Split functionality into smaller, focused functions.
- Pass dependencies explicitly rather than relying on globals.
- Return computed values instead of printing them.
- Add unit tests for each logical component separately.

---
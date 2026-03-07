### Diff #1
---

### 1. Summary
- **Purpose**: The PR adds a script for data analysis, including DataFrame creation, random value addition, and statistical output.
- **Affected Files**: `data_analysis.py`
- **Plain-Language Explanation**: The code performs basic data analysis and prints results, but the logic is fragmented and not well-structured.

---

### 2. Linting Issues
- **Violation**: Global variables `GLOBAL_DF` and `ANOTHER_GLOBAL` are used without proper encapsulation.
- **Violation**: `print` statements are scattered and lack formatting.
- **Violation**: No explicit error handling or logging for exceptions.

---

### 3. Code Smells
- **Problem**: `functionThatDoesTooMuchAndIsNotClear()` is overly complex and hard to understand.
- **Impact**: Difficult to maintain and test.
- **Improvement**: Break into smaller, focused functions and use object-oriented design.

- **Problem**: Global variables (`GLOBAL_DF`, `ANOTHER_GLOBAL`) are not encapsulated and reused across the file.
- **Impact**: Violates encapsulation principles.
- **Improvement**: Use class or module-level variables instead.

- **Problem**: `print` statements are scattered and lack formatting.
- **Impact**: Makes the code hard to read and debug.
- **Improvement**: Use formatted strings or logging modules.
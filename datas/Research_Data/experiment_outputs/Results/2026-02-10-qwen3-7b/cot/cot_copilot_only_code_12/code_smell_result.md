### Code Smell Types & Issues

---

### 1. Global Variable Usage
**Problem Location**: `DATAFRAME`, `resultList`, and `tempStorage` are declared globally.
**Detailed Explanation**: Global variables are not encapsulated and can lead to maintenance issues. They are also hard to test and modify.
**Improvement Suggestions**: Encapsulate these variables in a class or use them as parameters in functions.
**Priority Level**: High

---

### 2. Duplicated Code in `calcStats`
**Problem Location**: Logic for calculating mean values for "A" and "B" is duplicated.
**Detailed Explanation**: Repeated code blocks reduce readability and increase maintenance costs. It's unclear why the same logic is used for both columns.
**Improvement Suggestions**: Extract common logic into a helper function and apply it to both columns.
**Priority Level**: Medium

---

### 3. Magic Numbers
**Problem Location**: `meanB + 42` is a hardcoded value.
**Detailed Explanation**: Magic numbers are hard to understand and maintain. They should be named or explained.
**Improvement Suggestions**: Rename the value or explain its purpose in comments.
**Priority Level**: Medium

---

### 4. Incomplete Documentation
**Problem Location**: Comments are sparse and not descriptive.
**Detailed Explanation**: Lack of comments makes the code harder to understand, especially for new contributors.
**Improvement Suggestions**: Add inline comments explaining key logic and data flow.
**Priority Level**: Medium

---

### 5. Tight Coupling
**Problem Location**: `main()` calls `loadData()`, `calcStats()`, and `plotData()` directly.
**Detailed Explanation**: Functions are tightly coupled, making it hard to test or refactor independently.
**Improvement Suggestions**: Split into separate modules or services.
**Priority Level**: Medium

---

### 6. Missing Error Handling
**Problem Location**: No checks for empty DataFrame or missing columns.
**Detailed Explanation**: Potential crashes on invalid inputs are unhandled.
**Improvement Suggestions**: Add validation and error handling.
**Priority Level**: Low

---

### Summary of Key Issues
| Code Smell Type | Problem Location | Priority |
|----------------|------------------|----------|
| Global Variables | `DATAFRAME`, `resultList`, `tempStorage` | High |
| Duplicated Code | `calcStats()` | Medium |
| Magic Numbers | `meanB + 42` | Medium |
| Incomplete Documentation | Sparse comments | Medium |
| Tight Coupling | `main()` calls | Medium |
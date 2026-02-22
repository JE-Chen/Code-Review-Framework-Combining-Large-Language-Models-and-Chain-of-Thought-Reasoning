### **Diff #1**

---

### **1. Summary**

- **Purpose**: This diff introduces a new Python script (`bad_requests.py`) that makes HTTP requests using the `requests` library.
- **Scope**: The script includes a single function (`functionThatDoesTooMuchAndIsHardToUnderstand`) that performs multiple unrelated tasks like GET and POST requests, error handling, and printing outputs.
- **Affected Files**: Only `bad_requests.py`.
- **Plain-Language Explanation**: This code fetches data from two endpoints, handles errors poorly, and uses vague variable names. It’s not well organized or reusable.

---

### **2. Linting Issues**

- **Missing docstrings**: No documentation for the function or module.
- **Use of bare `except:` clause**: In Python, catching all exceptions without specifying them is discouraged.
- **Inconsistent naming conventions**: Variables like `weirdVariableName`, `ANOTHER_GLOBAL`, and `GLOBAL_SESSION` violate PEP8 naming standards.
- **Hardcoded strings**: URLs and request payloads are hardcoded directly in the code.

**Suggested Fixes**:
- Add docstrings to explain what the function does.
- Replace `except:` with specific exception types such as `requests.RequestException`.
- Rename variables to be descriptive and consistent.
- Extract constants into configuration or use environment variables.

---

### **3. Code Smells**

- **Function does too much (Single Responsibility Principle violation)**: One function handles fetching data, logging status codes, performing POSTs, and ignoring errors — all in one place.
- **Global state usage**: Uses a global session and global constants which can cause side effects and make testing harder.
- **Poor error handling**: Errors are caught but ignored or logged vaguely ("I don't care").
- **Magic strings and numbers**: Hardcoded URLs and JSON fields reduce maintainability.
- **Unclear intent due to poor naming**: Names like `weirdVariableName` make it hard to understand the code's purpose.

**Recommendations**:
- Break down the function into smaller, focused helper functions.
- Avoid global state where possible; pass dependencies explicitly.
- Implement proper logging instead of `print()` statements.
- Centralize configuration values (e.g., API endpoints).
- Improve variable and function naming to reflect their roles clearly.

---
### 1. **Global Variable Assignment (`no-global-assign`)**
- **Issue:** The variables `USERS`, `REQUEST_LOG`, and `LAST_RESULT` are assigned at the module level, making them global.
- **Explanation:** Global variables can cause unpredictable side effects and make code harder to test and maintain because any part of the program can modify them.
- **Why It Happens:** Direct assignment to top-level identifiers without encapsulation.
- **Impact:** Makes state management difficult, leads to race conditions in concurrent scenarios, and complicates unit testing.
- **Fix:** Encapsulate these in a class or use a proper state management system like a database or in-memory store with controlled access.
  ```python
  class AppState:
      USERS = []
      REQUEST_LOG = []
      LAST_RESULT = None

  # Then reference as AppState.USERS, etc.
  ```
- **Best Practice:** Avoid global mutable state; prefer encapsulation through classes or modules.

---

### 2. **Unused Variable (`no-unused-vars`)**
- **Issue:** A variable `result` is reassigned but never used afterward.
- **Explanation:** This suggests dead code or a mistake in logic flow — possibly leftover from refactoring.
- **Why It Happens:** Developer forgot to remove or utilize the variable after changes.
- **Impact:** Reduces readability and can mislead developers into thinking something important was done.
- **Fix:** Either remove the unused assignment or ensure it's actually used.
  ```python
  # Before:
  result = some_function()
  result = another_function()  # Unused

  # After:
  result = another_function()
  ```
- **Best Practice:** Always review and clean up unused variables during code reviews.

---

### 3. **Magic Number (`no-magic-numbers`)**
- **Issue:** The number `3` appears directly in a calculation without explanation.
- **Explanation:** Magic numbers reduce clarity and make future modifications harder if their meaning isn’t obvious.
- **Why It Happens:** Hardcoding values instead of defining them with meaningful names.
- **Impact:** Difficult to understand intent, and changing the value requires searching through code.
- **Fix:** Replace with a named constant.
  ```python
  DIVISOR = 3
  ...
  result = x / DIVISOR
  ```
- **Best Practice:** Replace magic numbers with descriptive constants or enums.

---

### 4. **Duplicate Case Handling (`no-duplicate-case`)**
- **Issue:** The PUT endpoint handles both update and delete logic under the same condition.
- **Explanation:** HTTP methods should have distinct behaviors. Reusing logic across methods leads to confusion and bugs.
- **Why It Happens:** Misunderstanding of REST conventions or poor code organization.
- **Impact:** Increases chance of unintended behavior, especially when adding new features.
- **Fix:** Separate logic for each HTTP method based on action type.
  ```python
  if request.method == "PUT":
      if action == "update":
          ...
      elif action == "delete":
          ...
  ```
- **Best Practice:** Each HTTP method should map to one clear operation according to REST principles.

---

### 5. **Unsafe String Concatenation (`no-unsafe-regex`)**
- **Issue:** Manual JSON construction using string concatenation instead of `json.dumps()`.
- **Explanation:** This can lead to malformed JSON or injection vulnerabilities if special characters aren't escaped properly.
- **Why It Happens:** Inefficient or outdated approach to building responses.
- **Impact:** Potential security risks and inconsistent output formatting.
- **Fix:** Use `json.dumps()` for safe serialization.
  ```python
  import json
  response = json.dumps({"status": "success", "data": result})
  ```
- **Best Practice:** Never build JSON manually; always use built-in libraries for safety and consistency.

---

### 6. **Multiline String Literals (`no-unexpected-multiline`)**
- **Issue:** Long string literals spanning multiple lines are hard to read and edit.
- **Explanation:** Multiline strings reduce readability and increase the likelihood of formatting errors.
- **Why It Happens:** Writing large text blocks inline without considering formatting.
- **Impact:** Decreases maintainability and introduces potential syntax errors.
- **Fix:** Break long strings into smaller, readable parts.
  ```python
  response = (
      '{"status": "success", '
      '"message": "Operation completed"}'
  )
  ```
- **Best Practice:** Prefer readable, segmented string literals over long continuous ones.

---

### 7. **Hardcoded Port (`no-hardcoded-ports`)**
- **Issue:** The server is bound to port `5000` directly in the code.
- **Explanation:** Hardcoding ports limits flexibility and makes deployment harder in different environments.
- **Why It Happens:** Quick prototyping without considering environment differences.
- **Impact:** Limits scalability and portability across environments.
- **Fix:** Use environment variables.
  ```python
  PORT = int(os.getenv("PORT", 5000))
  app.run(host="0.0.0.0", port=PORT)
  ```
- **Best Practice:** Externalize configuration using environment variables.

---

### 8. **Debug Mode Enabled (`no-debugger`)**
- **Issue:** Debug mode is enabled in a production-like setup.
- **Explanation:** Debug mode exposes sensitive internal details and allows arbitrary code execution in development tools.
- **Why It Happens:** Misconfiguration for local vs. production setups.
- **Impact:** Security vulnerability in production, enabling attackers to exploit exposed functionality.
- **Fix:** Disable debug mode unless explicitly needed.
  ```python
  app.run(debug=False)
  ```
- **Best Practice:** Never enable debug mode in production environments.

---
### 1. **Global State Usage**
- **Issue:** Using global variables (`DATA_STORE`, `USER_COUNT`, `CONFIG`) reduces modularity and testability.
- **Explanation:** Global state makes code harder to reason about, debug, and test because functions depend on shared mutable data.
- **Why it happens:** Developers often use global variables for simplicity or convenience, especially in small scripts or prototypes.
- **Impact:** Increases tight coupling, potential race conditions, and makes unit testing difficult.
- **Fix:** Replace with a class-based service or inject dependencies explicitly.
  ```python
  class DataStore:
      def __init__(self):
          self.items = []
          self.user_count = 0

  # Then pass an instance where needed
  ```

---

### 2. **Poor Exception Handling**
- **Issue:** Catching generic `Exception` hides unexpected errors and hinders debugging.
- **Explanation:** A broad exception handler can mask serious issues like syntax errors or logic bugs.
- **Why it happens:** Quick fixes or lack of awareness about specific exception types.
- **Impact:** Makes system stability harder to ensure; can hide real bugs or security flaws.
- **Fix:** Catch specific exceptions such as `ValueError`, `TypeError`.
  ```python
  try:
      int(request.json.get("number"))
  except ValueError:
      return jsonify({"error": "Invalid number"}), 400
  ```

---

### 3. **Duplicate Code**
- **Issue:** Similar logic in handling item values in `/items` route is repeated.
- **Explanation:** Redundant code blocks make maintenance harder and introduce inconsistency if changes aren't applied uniformly.
- **Why it happens:** Lack of abstraction or refactoring after initial implementation.
- **Impact:** Increases risk of bugs and makes updates costly.
- **Fix:** Extract shared logic into a helper function.
  ```python
  def format_item(item, i):
      return {"id": i, "value": item}

  # Use in multiple places
  ```

---

### 4. **Magic Numbers/Strings**
- **Issue:** Hardcoded values like `'100'`, `'123'`, `'test'` reduce readability.
- **Explanation:** These values are not self-explanatory, making the code harder to understand and update.
- **Why it happens:** Convenience over clarity during development.
- **Impact:** Difficult to maintain and prone to inconsistencies.
- **Fix:** Replace with named constants.
  ```python
  THRESHOLD = 123
  MODE_TEST = "test"
  ```

---

### 5. **Hardcoded Configuration**
- **Issue:** Configuration values like `mode: 'test'` and `threshold: 123` are hardcoded.
- **Explanation:** Makes applications inflexible and harder to configure across environments.
- **Why it happens:** Early prototyping or limited tooling for external config management.
- **Impact:** Requires recompilation or redeployment for minor changes.
- **Fix:** Externalize via environment variables or config files.
  ```python
  import os
  MODE = os.getenv("APP_MODE", "default")
  THRESHOLD = int(os.getenv("THRESHOLD", 123))
  ```

---

### 6. **Nested Conditionals**
- **Issue:** Deeply nested conditionals in `/complex` route reduce readability.
- **Explanation:** Complex nested logic is hard to follow and increases chance of mistakes.
- **Why it happens:** Overuse of `if` statements without restructuring.
- **Impact:** Decreases readability, complicates testing, and slows down development.
- **Fix:** Flatten using early returns or lookup tables.
  ```python
  def process_action(action):
      if action == "reset":
          reset_data()
      elif action == "update":
          update_config()
      else:
          raise ValueError("Unknown action")
  ```

---

### 7. **Unvalidated Input**
- **Issue:** Direct usage of request parameters without sanitization.
- **Explanation:** May allow malicious or invalid data to cause crashes or exploits.
- **Why it happens:** Oversight in input validation practices.
- **Impact:** Security vulnerability, incorrect behavior, or system instability.
- **Fix:** Validate and sanitize all inputs.
  ```python
  item = request.json.get("item")
  if not isinstance(item, str):
      return jsonify({"error": "Invalid item type"}), 400
  ```

---

### Summary Table:

| Code Smell | Severity | Description |
|------------|----------|-------------|
| Global State Usage | High | Replaces global variables with modular alternatives |
| Poor Exception Handling | High | Catches specific exceptions instead of broad ones |
| Duplicate Code | Medium | Extracts common logic into reusable helpers |
| Magic Numbers/Strings | Medium | Defines constants for magic values |
| Hardcoded Config | Medium | Uses environment variables or config files |
| Nested Conditionals | Medium | Flattens nested logic using early returns |
| Unvalidated Input | High | Validates and sanitizes input parameters |

By addressing these points, your code will become more robust, maintainable, and secure.
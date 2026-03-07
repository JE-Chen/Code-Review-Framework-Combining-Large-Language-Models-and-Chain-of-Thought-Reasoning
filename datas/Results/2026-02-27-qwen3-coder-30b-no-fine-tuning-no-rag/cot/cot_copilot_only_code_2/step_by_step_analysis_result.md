### 1. **Unused Variable (`no-unused-vars`)**
- **Issue:** The variable `val` is declared but never used in the scope.
- **Explanation:** This is a basic code cleanup issue. Unused variables can confuse readers and clutter the code.
- **Root Cause:** Likely a leftover from debugging or incomplete refactoring.
- **Impact:** Low severity; impacts readability and maintainability slightly.
- **Fix:** Remove the unused variable or use it in logic.
  ```python
  # Before
  val = some_value
  result = process_data()

  # After
  result = process_data()
  ```

---

### 2. **Nested If Statements (`complexity`)**
- **Issue:** Deeply nested `if` blocks reduce readability and make logic harder to follow.
- **Explanation:** When conditions are nested, developers must mentally track multiple layers, increasing cognitive load.
- **Root Cause:** Lack of early returns or modularization of conditional logic.
- **Impact:** Medium to high severity; affects maintainability and testability.
- **Fix:** Refactor using early returns or extract logic into helper functions.
  ```python
  # Before
  if condition1:
      if condition2:
          if condition3:
              do_something()

  # After
  if not condition1:
      return
  if not condition2:
      return
  if not condition3:
      return
  do_something()
  ```

---

### 3. **Magic Numbers (`magic-numbers`) – First Instance**
- **Issue:** Hardcoded number `123456` appears directly in the code without explanation.
- **Explanation:** Magic numbers decrease readability and make future changes harder.
- **Root Cause:** Lack of abstraction for configuration values.
- **Impact:** Medium severity; reduces flexibility and clarity.
- **Fix:** Replace with named constants.
  ```python
  # Before
  result = data * 123456

  # After
  MULTIPLIER = 123456
  result = data * MULTIPLIER
  ```

---

### 4. **Magic Numbers (`magic-numbers`) – Second Instance**
- **Issue:** Constants `1234`, `5678`, and `9999` are used without explanation.
- **Explanation:** These values are likely part of a mathematical transformation or configuration — they should be made explicit.
- **Root Cause:** Missing abstraction for numerical constants.
- **Impact:** Medium severity; makes maintenance harder.
- **Fix:** Use named constants or config files.
  ```python
  # Before
  result = (data * 1234) % 5678 + 9999

  # After
  MULTIPLIER = 1234
  MODULUS = 5678
  OFFSET = 9999
  result = (data * MULTIPLIER) % MODULUS + OFFSET
  ```

---

### 5. **Use of `print()` Statement (`no-console`)**
- **Issue:** Direct use of `print()` is discouraged in production environments.
- **Explanation:** `print()` outputs directly to stdout, which isn't suitable for production systems where logs need control and formatting.
- **Root Cause:** Lack of structured logging setup.
- **Impact:** Medium severity; limits scalability and observability.
- **Fix:** Replace with logging module.
  ```python
  # Before
  print("Processing completed")

  # After
  import logging
  logger = logging.getLogger(__name__)
  logger.info("Processing completed")
  ```

---
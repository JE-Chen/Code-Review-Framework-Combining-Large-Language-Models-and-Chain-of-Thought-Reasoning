### 1. **Rule: `no-console` – Use of `print()` Detected**
- **Issue**: The code uses `print()` statements for output instead of a logging framework.
- **Explanation**: Using `print()` directly in production code makes output hard to control, especially in different environments (dev, staging, prod).
- **Root Cause**: Developers prefer quick debugging output over structured logging.
- **Impact**: Reduces maintainability and makes output management difficult.
- **Fix**: Replace `print(...)` with `logging.info(...)` or `logging.debug(...)`.
  ```python
  import logging
  logging.info("Processing completed")
  ```
- **Best Practice**: Always use logging libraries for consistent and configurable output across environments.

---

### 2. **Rule: `no-console` – Use of `print()` Detected (Repeat)**
- **Issue**: Same as above, repeated in multiple locations.
- **Fix**: Apply same fix as #1 across all lines.

---

### 3. **Rule: `no-global-assign` – Assignment to Global Variable**
- **Issue**: Global variable `global_config` is assigned and modified.
- **Explanation**: This leads to tight coupling and makes unit testing harder.
- **Root Cause**: Hardcoded global configuration instead of passing it as a parameter.
- **Impact**: Makes code less predictable and harder to debug or extend.
- **Fix**: Pass config as a parameter or use a config manager.
  ```python
  def run_task(config):
      print(config["mode"])
  ```
- **Best Practice**: Avoid global state; favor dependency injection or explicit parameters.

---

### 4. **Rule: `no-eval` – Use of `eval()` Detected**
- **Issue**: Dangerous use of `eval()` on user-provided input.
- **Explanation**: Can execute arbitrary code, leading to security exploits.
- **Root Cause**: Lack of input sanitization or alternative safer methods.
- **Impact**: High risk of remote code execution if input is malicious.
- **Fix**: Use `ast.literal_eval()` or a secure parser.
  ```python
  import ast
  result = ast.literal_eval(user_code)
  ```
- **Best Practice**: Never trust user input. Prefer safe parsing techniques.

---

### 5. **Rule: `no-unsafe-assignment` – Broad Exception Handling**
- **Issue**: Catches generic `Exception`, which masks real bugs.
- **Explanation**: Hides important exceptions like `TypeError`, `KeyError`, etc.
- **Root Cause**: Overly broad exception catching without proper handling.
- **Impact**: Makes debugging harder and can mask logic errors.
- **Fix**: Catch specific exceptions.
  ```python
  try:
      risky_update(data)
  except KeyError:
      pass
  except TypeError:
      pass
  ```
- **Best Practice**: Catch only known exceptions; re-raise unknown ones.

---

### 6. **Rule: `no-magic-numbers` – Magic Numbers Used**
- **Issue**: Hardcoded numbers `7` and `13` appear in logic.
- **Explanation**: These numbers are unclear without context.
- **Root Cause**: No naming or abstraction for numeric values.
- **Impact**: Makes code harder to understand and modify.
- **Fix**: Define constants.
  ```python
  MAGIC_NUMBER_7 = 7
  MAGIC_NUMBER_13 = 13
  ```
- **Best Practice**: Replace magic numbers with named constants for clarity.

---

### 7. **Rule: `no-duplicate-functions` – Duplicate Logic in Function**
- **Issue**: Function `check_value()` duplicates a simple conditional.
- **Explanation**: Unnecessary complexity due to redundant logic.
- **Root Cause**: Over-engineering simple checks.
- **Impact**: Adds unnecessary code and reduces readability.
- **Fix**: Simplify the function.
  ```python
  def check_value(val):
      return val is not None
  ```
- **Best Practice**: Keep logic minimal and readable.

---

### 8. **Rule: `no-unexpected-side-effects` – Side Effect via Global Flag**
- **Issue**: Function `secret_behavior` modifies a global variable.
- **Explanation**: This violates encapsulation and introduces unpredictability.
- **Root Cause**: Relying on global state for behavior changes.
- **Impact**: Difficult to test, debug, and reason about.
- **Fix**: Pass dependencies explicitly.
  ```python
  def secret_behavior(flag):
      ...
  ```
- **Best Practice**: Avoid side effects; make functions pure when possible.

---

### 9. **Code Smell: Magic String**
- **Issue**: Hardcoded string `"admin"` used in conditional.
- **Explanation**: Makes code fragile and hard to update.
- **Fix**: Define constant.
  ```python
  ADMIN_KEYWORD = "admin"
  if ADMIN_KEYWORD in user_input:
      ...
  ```
- **Best Practice**: Never hardcode strings unless absolutely necessary.

---

### 10. **Code Smell: Poor Function Naming**
- **Issue**: Function named `f` lacks descriptive meaning.
- **Explanation**: Confusing for anyone reading the code.
- **Fix**: Rename to reflect functionality.
  ```python
  def calculate_result(x):
      ...
  ```
- **Best Practice**: Choose clear, self-documenting names.

---

### 11. **Code Smell: Global State Dependency**
- **Issue**: Global `global_config` used across functions.
- **Explanation**: Tight coupling reduces modularity and testability.
- **Fix**: Inject config or pass it as argument.
  ```python
  def run_task(config):
      ...
  ```
- **Best Practice**: Avoid global variables; use explicit dependencies.

---

### 12. **Code Smell: Insecure Use of `eval()`**
- **Issue**: User-controlled code evaluated directly.
- **Explanation**: Security vulnerability allowing arbitrary code execution.
- **Fix**: Avoid `eval()`; use safer alternatives.
  ```python
  import ast
  result = ast.literal_eval(user_code)
  ```
- **Best Practice**: Do not allow arbitrary code evaluation.

---

### 13. **Code Smell: Broad Exception Handling**
- **Issue**: Generic `except Exception:` used.
- **Explanation**: Masks real bugs and hinders debugging.
- **Fix**: Handle specific exceptions.
  ```python
  except KeyError:
      ...
  except TypeError:
      ...
  ```
- **Best Practice**: Be precise in exception handling.

---

### 14. **Code Smell: Side Effects in Functions**
- **Issue**: Functions print directly to console.
- **Explanation**: Breaks encapsulation and reduces reusability.
- **Fix**: Remove side effects; let caller handle output.
  ```python
  def process_data(data):
      return data * 2  # No print()
  ```
- **Best Practice**: Keep functions focused on computation, not I/O.

---

### 15. **Code Smell: Lack of Input Validation**
- **Issue**: No validation of input beyond basic types.
- **Explanation**: Could lead to runtime errors or incorrect behavior.
- **Fix**: Add checks for content validity.
  ```python
  if isinstance(user_input, str) and len(user_input) > 0:
      ...
  ```
- **Best Practice**: Validate inputs early and fail fast.

---

### 16. **Code Smell: Unused Variables / Dead Code**
- **Issue**: `hidden_flag` and `secret_behavior` are unused.
- **Explanation**: Indicates incomplete or abandoned features.
- **Fix**: Either remove or integrate properly.
  ```python
  # Remove unused code
  ```

- **Best Practice**: Clean up unused code during development.

---

### 17. **Code Smell: Ambiguous Return Values**
- **Issue**: Returns strings instead of booleans.
- **Explanation**: Forces callers to parse return values.
- **Fix**: Return boolean or use enums.
  ```python
  def check_value(val):
      return val is not None
  ```
- **Best Practice**: Return structured data that’s easy to consume.

---

### 18. **Code Smell: Lack of Documentation**
- **Issue**: No docstrings or comments.
- **Explanation**: Makes understanding the codebase harder.
- **Fix**: Add docstrings and inline comments.
  ```python
  def process_user_input(user_input):
      """Process user input and check for admin rights."""
      ...
  ```
- **Best Practice**: Document everything—functions, parameters, logic.

---

### 19. **Code Smell: Violation of Single Responsibility Principle**
- **Issue**: `run_task()` handles both config and output.
- **Explanation**: Mixes concerns, reducing clarity and testability.
- **Fix**: Separate responsibilities.
  ```python
  def check_config(config):
      ...

  def log_output(message):
      ...
  ```
- **Best Practice**: Each function should do one thing well.

--- 

✅ Summary: Address these issues systematically to improve code quality, readability, and security. Prioritize high-severity items like `eval()`, global state, and broad exception handling.
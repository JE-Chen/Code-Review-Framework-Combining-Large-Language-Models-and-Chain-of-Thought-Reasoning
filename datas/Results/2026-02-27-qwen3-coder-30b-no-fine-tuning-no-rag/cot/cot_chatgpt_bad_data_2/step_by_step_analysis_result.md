### 1. **Unused Parameter (`no-unused-vars`)**
- **Issue**: The `data` parameter in function `process` is not used anywhere in the function body.
- **Explanation**: This suggests that either the parameter was forgotten or the function logic needs updating.
- **Cause**: Either accidental omission or poor design—function should either use the parameter or remove it.
- **Impact**: Reduces code clarity and may confuse developers who expect `data` to be processed.
- **Fix**: Either remove the unused parameter or implement logic to utilize it.
  ```python
  # Before
  def process(service: UserService, data=[], verbose=True):
      pass

  # After
  def process(service: UserService, verbose=True):
      pass
  ```
- **Best Practice**: Follow DRY (Don't Repeat Yourself) and only include parameters you actually need.

---

### 2. **Using Undefined Variable (`no-undef`)**
- **Issue**: Variable `result` is referenced before it's assigned in the current scope.
- **Explanation**: Likely due to incorrect order of operations or missing initialization.
- **Cause**: Incorrect code structure or missing variable declaration.
- **Impact**: Runtime error (`NameError`) when trying to execute the code.
- **Fix**: Initialize `result` before using it.
  ```python
  # Before
  print(result)
  result = "some_value"

  # After
  result = "some_value"
  print(result)
  ```
- **Best Practice**: Always declare variables before using them.

---

### 3. **Magic Number – `10` in `_load_random_users`**
- **Issue**: Hardcoded number `10` used as max user count.
- **Explanation**: Makes assumptions about quantity without clear reasoning.
- **Cause**: Lack of abstraction or documentation around why 10 users are loaded.
- **Impact**: Difficult to change behavior later; reduces readability.
- **Fix**: Extract to a named constant.
  ```python
  MAX_USERS = 10
  range(0, MAX_USERS)
  ```
- **Best Practice**: Replace magic numbers with descriptive constants.

---

### 4. **Magic Number – `100` in `_load_random_users`**
- **Issue**: Hardcoded ID limit `100`.
- **Explanation**: Assumption about maximum user ID value without justification.
- **Cause**: Same root cause as above — lack of abstraction.
- **Impact**: Limits scalability or flexibility in future changes.
- **Fix**: Define constant.
  ```python
  MAX_USER_ID = 100
  random.randint(1, MAX_USER_ID)
  ```
- **Best Practice**: Avoid hardcoding values that could change.

---

### 5. **Magic Number – `0.05` in `_load_random_users`**
- **Issue**: Sleep duration `0.05` appears as a raw number.
- **Explanation**: Not immediately clear what purpose this number serves.
- **Cause**: No abstraction layer for timing behavior.
- **Impact**: Makes code harder to understand and modify.
- **Fix**: Use a named constant.
  ```python
  SLEEP_DURATION = 0.05
  time.sleep(SLEEP_DURATION)
  ```
- **Best Practice**: Name your magic numbers to clarify intent.

---

### 6. **Global Scope Violation (`no-implicit-globals`)**
- **Issue**: Global variable `CONFIG` is not explicitly declared globally.
- **Explanation**: Can lead to confusion and unintended side effects.
- **Cause**: Poor scoping practices, possibly from legacy code.
- **Impact**: Harder to track down bugs and makes testing more complex.
- **Fix**: Make it explicit or move into a config module.
  ```python
  # Option 1: Explicitly global
  global CONFIG

  # Option 2: Module-level constant
  CONFIG = {...}
  ```
- **Best Practice**: Prefer encapsulation over implicit globals.

---

### 7. **Unsafe Exception Handling (`no-unsafe-finally`)**
- **Issue**: Using bare `except:` clause catches all exceptions.
- **Explanation**: Masks unexpected errors, making debugging harder.
- **Cause**: Lazy exception handling.
- **Impact**: Risk of hiding critical bugs.
- **Fix**: Catch specific exceptions.
  ```python
  # Before
  except Exception:

  # After
  except FileNotFoundError:
      logging.error("File not found")
  except IOError:
      logging.error("I/O error occurred")
  ```
- **Best Practice**: Catch specific exceptions and log appropriately.

---

### 8. **Unreachable Code (`no-unreachable-code`)**
- **Issue**: Code after `return` statement is unreachable.
- **Explanation**: Indicates redundant or misplaced lines of code.
- **Cause**: Mistake during refactoring or incomplete logic.
- **Impact**: Wastes space and confuses readers.
- **Fix**: Remove unreachable code.
  ```python
  # Before
  def example():
      return True
      print("This won't run")

  # After
  def example():
      return True
  ```
- **Best Practice**: Ensure all code paths are valid and reachable.

---

### 9. **Duplicate Dictionary Key (`no-duplicate-key`)**
- **Issue**: Duplicate key `'name'` in dictionary literal.
- **Explanation**: Overwrites previous key-value pair silently.
- **Cause**: Typo or oversight during creation.
- **Impact**: Data loss or incorrect behavior.
- **Fix**: Ensure unique keys.
  ```python
  # Before
  user_data = {"name": "John", "name": "Jane"}

  # After
  user_data = {"name": "John", "id": 1}
  ```
- **Best Practice**: Validate dictionaries for uniqueness before use.

---

### 10. **Global State Usage (Code Smell)**
- **Issue**: Class-level dictionary `users` acts as shared state.
- **Explanation**: Leads to non-isolated behavior across instances.
- **Cause**: Violates encapsulation and introduces concurrency issues.
- **Impact**: Testing becomes difficult and behavior unpredictable.
- **Fix**: Move `users` to instance variable.
  ```python
  # Before
  class UserService:
      users = {}

  # After
  class UserService:
      def __init__(self):
          self.users = {}
  ```
- **Best Practice**: Encapsulate internal state within objects.

---

### 11. **Magic Numbers (Multiple Instances)**
- **Issue**: Multiple magic numbers (`10`, `100`, `0.05`) in same function.
- **Explanation**: Repetitive pattern of unexplained numbers.
- **Cause**: Lack of naming and abstraction.
- **Impact**: Reduced maintainability and readability.
- **Fix**: Define constants at top of file or module.
  ```python
  MAX_USERS = 10
  MAX_USER_ID = 100
  SLEEP_DURATION = 0.05
  ```
- **Best Practice**: Apply naming standards consistently across codebase.

---

### 12. **Poor Exception Handling (Code Smell)**
- **Issue**: `except Exception:` hides all possible errors.
- **Explanation**: Prevents detection of real problems like typos or malformed input.
- **Cause**: Incomplete error management strategy.
- **Impact**: Debugging nightmare and unreliable system behavior.
- **Fix**: Handle known exceptions specifically.
  ```python
  try:
      # some operation
  except FileNotFoundError:
      # handle missing file
  except ValueError:
      # handle bad data
  ```
- **Best Practice**: Fail fast and fail clearly.

---

### 13. **Mutable Default Argument (Code Smell)**
- **Issue**: Default value `[]` in function signature.
- **Explanation**: Shared list across function calls.
- **Cause**: Misunderstanding of Python defaults.
- **Impact**: Subtle bugs and unexpected side effects.
- **Fix**: Use `None` and initialize inside function.
  ```python
  def process(service: UserService, data=None, verbose=True):
      if data is None:
          data = []
  ```
- **Best Practice**: Never use mutable defaults in function definitions.

---

### 14. **Inconsistent Return Types (Code Smell)**
- **Issue**: Function returns both `list` and `None`.
- **Explanation**: Unclear contract for consumers.
- **Cause**: Lack of explicit handling for edge cases.
- **Impact**: Potential runtime errors and poor predictability.
- **Fix**: Standardize return type.
  ```python
  # Instead of returning None, raise exception or return empty list
  return [] if not items else items
  ```
- **Best Practice**: Be consistent in return types for predictable APIs.

---

### 15. **Side Effects in Functions (Code Smell)**
- **Issue**: Modifying `data` parameter directly.
- **Explanation**: Changes external state unexpectedly.
- **Cause**: Imperative style without functional discipline.
- **Impact**: Makes functions unpredictable and harder to test.
- **Fix**: Create new object or avoid mutation.
  ```python
  # Before
  data.append(new_item)

  # After
  new_list = data + [new_item]
  ```
- **Best Practice**: Prefer immutability and avoid side effects.

---

### 16. **Tight Coupling (Code Smell)**
- **Issue**: Function `process()` directly accesses `service.users`.
- **Explanation**: Breaks encapsulation and tightens coupling.
- **Cause**: Lack of abstraction layer.
- **Impact**: Difficult to extend or test independently.
- **Fix**: Provide access through interface or getter.
  ```python
  # Instead of accessing .users directly
  service.get_users()
  ```
- **Best Practice**: Favor composition and loose coupling.

---

### 17. **Lack of Input Validation (Code Smell)**
- **Issue**: No check for valid `source` parameter in `load_users`.
- **Explanation**: Could silently ignore invalid inputs.
- **Cause**: Missing validation logic.
- **Impact**: Unexpected behavior or runtime errors.
- **Fix**: Validate input or raise exceptions.
  ```python
  if source not in ["file", "random"]:
      raise ValueError("Invalid source")
  ```
- **Best Practice**: Validate inputs early and fail fast.

---

### 18. **Unused Imports (Code Smell)**
- **Issue**: Imported modules (`os`, `time`, `random`) never used.
- **Explanation**: Cluttered imports reduce clarity.
- **Cause**: Leftover or forgotten code.
- **Impact**: Minor bloat but affects code hygiene.
- **Fix**: Remove unused imports.
  ```python
  # Remove these lines if unused
  import os
  import time
  import random
  ```
- **Best Practice**: Keep imports minimal and relevant.

---

### 19. **Hardcoded File Path (Code Smell)**
- **Issue**: `"users.txt"` hardcoded in `_load_from_file`.
- **Explanation**: Less portable and configurable.
- **Cause**: Hardcoded string values.
- **Impact**: Limits adaptability to different environments.
- **Fix**: Pass path as parameter or define in config.
  ```python
  # Option 1: Pass parameter
  def _load_from_file(filename="users.txt"):

  # Option 2: Config module
  FILENAME = "users.txt"
  ```
- **Best Practice**: Externalize configuration and avoid hardcoded paths.

---

### 20. **Poor Main Function Design (Code Smell)**
- **Issue**: `main()` does not return anything meaningful.
- **Explanation**: Difficult to automate or test script behavior.
- **Cause**: Lack of structured exit signaling.
- **Impact**: Incompatible with CI/CD and testing frameworks.
- **Fix**: Return exit status or raise exceptions.
  ```python
  def main():
      try:
          ...
          return 0  # Success
      except Exception as e:
          print(f"Error: {e}")
          return 1  # Failure
  ```
- **Best Practice**: Design entry points for robustness and automation support.
### 1. **Unused Parameter: `data` in `process` Function**
- **Issue**: The parameter `data` is never used after initialization.
- **Explanation**: A function should either use all parameters or remove unused ones.
- **Root Cause**: Likely leftover from refactoring or incomplete implementation.
- **Impact**: Confuses developers and suggests poor design.
- **Fix**:
  ```python
  def process():
      # Remove unused 'data' parameter
      pass
  ```
- **Best Practice**: Always validate function signatures match actual usage.

---

### 2. **Using Undefined Variable `result`**
- **Issue**: `result` is referenced before assignment.
- **Explanation**: This causes runtime errors unless carefully handled.
- **Root Cause**: Incorrect control flow logic.
- **Impact**: Runtime crashes or incorrect behavior.
- **Fix**:
  ```python
  def main():
      result = process(data)
      print(result)
  ```
- **Best Practice**: Initialize variables before use or ensure correct execution order.

---

### 3. **Unexpected Newline After `return`**
- **Issue**: Line break after `return` can lead to parsing ambiguity.
- **Explanation**: Some parsers treat it differently than intended.
- **Root Cause**: Formatting inconsistency.
- **Impact**: Potential syntax errors in strict environments.
- **Fix**:
  ```python
  return result
  ```
  Instead of:
  ```python
  return
  result
  ```
- **Best Practice**: Consistent formatting improves readability and avoids edge-case issues.

---

### 4. **Magic Number: `100`**
- **Issue**: Directly using `100` without context.
- **Explanation**: Makes assumptions implicit and hard to change.
- **Root Cause**: Lack of abstraction for values with meaning.
- **Impact**: Reduced maintainability.
- **Fix**:
  ```python
  MAX_USERS = 100
  ...
  if count > MAX_USERS:
      ...
  ```
- **Best Practice**: Replace magic numbers with named constants.

---

### 5. **Magic Number: `10`**
- **Issue**: Another hardcoded numeric value.
- **Explanation**: Same as above — lacks clarity.
- **Root Cause**: Missing abstraction layer.
- **Impact**: Difficult to update or reason about.
- **Fix**:
  ```python
  DEFAULT_RETRY_COUNT = 10
  ...
  retry_count = DEFAULT_RETRY_COUNT
  ```
- **Best Practice**: Name values that represent configuration or thresholds.

---

### 6. **Empty `except` Block**
- **Issue**: Silently catching exceptions.
- **Explanation**: Errors are hidden, making debugging harder.
- **Root Cause**: Overlooking error propagation.
- **Impact**: Bugs go unnoticed.
- **Fix**:
  ```python
  try:
      ...
  except Exception as e:
      logger.error(f"Failed to load users: {e}")
      raise  # Re-raise or handle appropriately
  ```
- **Best Practice**: Log exceptions or explicitly handle known error cases.

---

### 7. **Assignment to Global `CONFIG`**
- **Issue**: Modifying a global config object.
- **Explanation**: Can cause unpredictable side effects across modules.
- **Root Cause**: Mutable global state.
- **Impact**: Harder to test and debug.
- **Fix**:
  ```python
  # Avoid mutating CONFIG directly
  config = get_config()
  ```
- **Best Practice**: Prefer immutability or encapsulation over mutation.

---

### 8. **Global Variable in Class: `users`**
- **Issue**: Shared mutable class attribute leads to inconsistent state.
- **Explanation**: All instances share the same dict, causing race conditions.
- **Root Cause**: Misuse of class vs instance attributes.
- **Impact**: Testability and correctness issues.
- **Fix**:
  ```python
  class UserService:
      def __init__(self):
          self.users = {}
  ```
- **Best Practice**: Keep state per instance rather than globally.

---

### 9. **Inconsistent Return Types in `load_users`**
- **Issue**: Function returns `None`, `list`, or `False`.
- **Explanation**: Client code must check types inconsistently.
- **Root Cause**: No standardized return behavior.
- **Impact**: Fragile consumers of this API.
- **Fix**:
  ```python
  def load_users(source):
      if source == "file":
          return []  # Always return list
      elif source == "random":
          return [User(...)]
      else:
          raise ValueError("Invalid source")
  ```
- **Best Practice**: Ensure consistent return types to simplify client logic.

---

### 10. **Unused Parameter: `force=False`**
- **Issue**: Unused optional parameter suggests incomplete logic.
- **Explanation**: Unused parameters add confusion.
- **Impact**: Misleading interface.
- **Fix**:
  ```python
  def load_users(source):
      ...
  ```
- **Best Practice**: Only keep parameters that are actually used.

---

### 11. **Lack of Input Validation**
- **Issue**: No checks on `source` or file existence.
- **Explanation**: Invalid inputs may crash or behave unexpectedly.
- **Impact**: Runtime unpredictability.
- **Fix**:
  ```python
  if source not in VALID_SOURCES:
      raise ValueError("Unsupported source type")
  ```
- **Best Practice**: Validate inputs early to prevent downstream errors.

---

### 12. **Poor Naming: `i`, `f`, `key`**
- **Issue**: Vague variable names reduce clarity.
- **Explanation**: Readers struggle to understand intent.
- **Impact**: Slower comprehension.
- **Fix**:
  ```python
  for index in range(len(items)):
      ...
  ```
- **Best Practice**: Choose descriptive names that reflect purpose.

---

### 13. **Hardcoded Delay: `time.sleep(0.05)`**
- **Issue**: Fixed wait time reduces flexibility.
- **Explanation**: Can mask real problems or slow down tests.
- **Impact**: Test brittleness and performance concerns.
- **Fix**:
  ```python
  DELAY_SECONDS = 0.05
  time.sleep(DELAY_SECONDS)
  ```
- **Best Practice**: Make timing configurable or avoid artificial delays.

---
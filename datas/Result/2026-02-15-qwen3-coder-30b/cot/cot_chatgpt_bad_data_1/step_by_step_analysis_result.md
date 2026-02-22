### 1. **Mutable Default Argument**
- **Issue**: Using a mutable default argument (`items=[]`) causes shared state across function calls.
- **Explanation**: When a list is used as a default parameter, it persists between calls, leading to unintended side effects.
- **Root Cause**: Misunderstanding of how Python handles default arguments.
- **Impact**: Unexpected behavior in repeated function calls.
- **Fix**: Change `items=[]` to `items=None`, then instantiate a new list inside the function.
  ```python
  def process_items(items=None, verbose=False):
      if items is None:
          items = []
      ...
  ```

---

### 2. **Global State Mutation (cache)**
- **Issue**: Modifying global `cache` affects determinism and testability.
- **Explanation**: Functions that alter global state are hard to reason about and debug.
- **Root Cause**: Lack of encapsulation or dependency management.
- **Impact**: Side effects reduce predictability and increase bugs.
- **Fix**: Pass `cache` as a parameter or refactor into a class.
  ```python
  def process_items(items, cache, verbose=False):
      ...
  ```

---

### 3. **Global State Mutation (results)**
- **Issue**: Appending to a global `results` list introduces side effects.
- **Explanation**: Side effects make functions unpredictable and harder to isolate.
- **Root Cause**: Imperative style mixing with functional expectations.
- **Impact**: Reduced reusability and harder testing.
- **Fix**: Return computed values instead of mutating external state.
  ```python
  return [cache[item] for item in items]
  ```

---

### 4. **Insecure Usage of `eval()`**
- **Issue**: Dangerous use of `eval()` opens up injection vulnerabilities.
- **Explanation**: Dynamic evaluation should be avoided unless strictly necessary.
- **Root Cause**: Inefficient or lazy coding practices.
- **Impact**: Security risk and poor maintainability.
- **Fix**: Replace with safe operations.
  ```python
  return x * x
  ```

---

### 5. **Unreachable Code**
- **Issue**: Second call to `process_items` lacks required arguments.
- **Explanation**: This call operates on an empty list due to default behavior.
- **Root Cause**: Incorrect function invocation or incomplete logic flow.
- **Impact**: Confusing and potentially incorrect program behavior.
- **Fix**: Ensure valid parameters are passed.
  ```python
  process_items(items=[...], verbose=True)
  ```

---

### 6. **Inconsistent Return Types**
- **Issue**: Function returns various data types (`None`, `str`, `int`).
- **Explanation**: Makes API usage unpredictable and error-prone.
- **Root Cause**: Poor design around failure states.
- **Impact**: Difficult to handle return values safely.
- **Fix**: Standardize return types or raise exceptions.
  ```python
  def expensive_compute(x):
      if x < 0:
          raise ValueError("Invalid input")
      return x * x
  ```

---

### 7. **Implicit List Append**
- **Issue**: List comprehension used for side effect (appending to list).
- **Explanation**: Violates functional programming principles and readability.
- **Root Cause**: Misuse of language constructs.
- **Impact**: Confusion for readers unfamiliar with side-effect patterns.
- **Fix**: Use explicit iteration.
  ```python
  for item in items:
      results.append(cache[item])
  ```

---

### 8. **Unused Function**
- **Issue**: Function `get_user_data` is defined but never called.
- **Explanation**: Dead code clutters the codebase.
- **Root Cause**: Lack of cleanup after refactoring or feature removal.
- **Impact**: Reduced clarity and increased maintenance cost.
- **Fix**: Remove unused functions.
  ```python
  # delete the whole function block
  ```

---
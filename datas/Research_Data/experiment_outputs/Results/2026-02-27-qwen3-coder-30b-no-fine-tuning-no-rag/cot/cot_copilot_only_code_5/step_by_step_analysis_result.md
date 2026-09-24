### 1. **Global Variable Assignment (`no-global-assign`)**
**Issue:**  
The code attempts to assign a value to a global variable `GLOBAL_STATE`, which is not allowed per the linter rule.

**Explanation:**  
Using global variables directly in assignments makes the code hard to test and maintain. It also breaks encapsulation, making the system brittle.

**Impact:**  
High risk of side effects, poor testability, and reduced modularity.

**Fix:**  
Replace the global assignment with a class-based or local state management approach.

**Before:**
```python
GLOBAL_STATE = {"counter": 0, "data": [], "mode": "default", "threshold": 77, "flag": False}
GLOBAL_STATE["counter"] = 5
```

**After:**
```python
class StateManager:
    def __init__(self):
        self.state = {"counter": 0, "data": [], "mode": "default", "threshold": 77, "flag": False}

    def update_counter(self, value):
        self.state["counter"] = value
```

---

### 2. **Duplicate Keys in Dictionary (`no-duplicate-key`)**
**Issue:**  
Multiple duplicate keys (`counter`, `data`, `mode`, `threshold`, `flag`) are present in the `GLOBAL_STATE` dictionary definition.

**Explanation:**  
A dictionary cannot have duplicate keys — only one key-value pair will be kept, leading to silent overwrites and unpredictable behavior.

**Impact:**  
Causes bugs due to incorrect data retention and confusion among developers.

**Fix:**  
Ensure that each key appears only once in the dictionary.

**Before:**
```python
GLOBAL_STATE = {
    "counter": 0,
    "data": [],
    "mode": "default",
    "threshold": 77,
    "flag": False,
    "counter": 1,  # duplicate!
    "data": [1, 2, 3],  # duplicate!
}
```

**After:**
```python
GLOBAL_STATE = {
    "counter": 1,
    "data": [1, 2, 3],
    "mode": "default",
    "threshold": 77,
    "flag": False
}
```

---

### 3. **Magic Number – Threshold Value (`no-magic-numbers`)**
**Issue:**  
The literal value `77` is used directly as the threshold in the code.

**Explanation:**  
Magic numbers reduce readability and make changes more error-prone. They should be replaced with named constants.

**Impact:**  
Low to medium severity but affects maintainability and clarity.

**Fix:**  
Define a named constant for the threshold.

**Before:**
```python
GLOBAL_STATE["threshold"] = 77
```

**After:**
```python
DEFAULT_THRESHOLD = 77
GLOBAL_STATE["threshold"] = DEFAULT_THRESHOLD
```

---

### 4. **Magic Number – List Comprehension (`no-magic-numbers`)**
**Issue:**  
The magic number `21` is used in a list comprehension without explanation.

**Explanation:**  
Again, magic numbers decrease code clarity and make it harder to understand intent.

**Impact:**  
Medium severity; impacts readability and changeability.

**Fix:**  
Use a named constant.

**Before:**
```python
[ x for x in range(21) ]
```

**After:**
```python
MAX_ITEMS = 21
[ x for x in range(MAX_ITEMS) ]
```

---

### 5. **Unreachable Code (`no-unreachable-code`)**
**Issue:**  
Code after a `return` statement inside `process_items()` is unreachable.

**Explanation:**  
This usually indicates poor control flow logic or leftover code that was never removed.

**Impact:**  
Minor impact but signals potential logical flaws or dead code.

**Fix:**  
Reorganize or remove unreachable code.

**Before:**
```python
def process_items():
    ...
    return result
    print("This line is unreachable")  # Unreachable code
```

**After:**
```python
def process_items():
    ...
    return result
```

---

### 6. **Tight Coupling & Global State Usage (Code Smell)**
**Issue:**  
Functions like `increment_counter`, `process_items`, etc., depend on global state, causing tight coupling.

**Explanation:**  
Functions become tightly bound to a specific global variable, making them hard to test and reuse.

**Impact:**  
High severity — impacts testability, scalability, and robustness.

**Fix:**  
Pass state explicitly to functions instead of relying on global variables.

**Before:**
```python
def increment_counter():
    GLOBAL_STATE["counter"] += 1
```

**After:**
```python
def increment_counter(state):
    state["counter"] += 1
```

---

### 7. **Inconsistent Naming Convention (Code Smell)**
**Issue:**  
Naming conventions are inconsistent (e.g., `GLOBAL_STATE` vs. other lowercase functions).

**Explanation:**  
Inconsistent naming reduces code readability and makes it harder to follow naming standards.

**Impact:**  
Medium severity — affects professionalism and consistency.

**Fix:**  
Standardize to snake_case for variables and constants.

**Before:**
```python
GLOBAL_STATE = {...}
def init_data(): ...
```

**After:**
```python
global_state = {...}
def init_data(): ...
```

---

### 8. **Long Function / Single Responsibility Violation (Code Smell)**
**Issue:**  
Function `process_items()` handles multiple responsibilities — filtering, transformation, and logic branching.

**Explanation:**  
Violates the Single Responsibility Principle, making the function hard to read, debug, and test.

**Impact:**  
High severity — leads to poor design and complexity.

**Fix:**  
Break down the logic into smaller helper functions.

**Before:**
```python
def process_items():
    if flag:
        ...
    else:
        ...
```

**After:**
```python
def apply_threshold_logic(items, threshold):
    ...

def transform_item(item):
    ...

def process_items():
    items = filter_items()
    transformed = [transform_item(x) for x in items]
    return apply_threshold_logic(transformed, threshold)
```

---

### 9. **Lack of Input Validation (Code Smell)**
**Issue:**  
No validation is done when setting or reading from `GLOBAL_STATE`.

**Explanation:**  
This leaves room for invalid inputs or runtime errors.

**Impact:**  
Medium severity — can cause crashes or unexpected behavior.

**Fix:**  
Add input validation checks.

**Before:**
```python
GLOBAL_STATE["threshold"] = "invalid"
```

**After:**
```python
if isinstance(value, int) and value >= 0:
    GLOBAL_STATE["threshold"] = value
else:
    raise ValueError("Invalid threshold value")
```

---

### 10. **Lack of Documentation (Code Smell)**
**Issue:**  
Missing docstrings and comments.

**Explanation:**  
Without documentation, understanding the purpose and usage of code becomes difficult.

**Impact:**  
Medium severity — slows down team collaboration and onboarding.

**Fix:**  
Add clear docstrings.

**Before:**
```python
def increment_counter():
    GLOBAL_STATE["counter"] += 1
```

**After:**
```python
def increment_counter():
    """Increments the counter in the global state."""
    GLOBAL_STATE["counter"] += 1
```

---

### 11. **Testability Issues (Code Smell)**
**Issue:**  
Functions depend on global state, making unit testing difficult.

**Explanation:**  
Unit tests must ensure correct global state before running, which complicates setup.

**Impact:**  
High severity — hinders automated testing and CI pipelines.

**Fix:**  
Refactor to accept dependencies explicitly.

**Before:**
```python
def process_items():
    return GLOBAL_STATE["data"]
```

**After:**
```python
def process_items(state):
    return state["data"]
```

---

### Summary Table

| Code Smell | Description | Severity | Fix |
|------------|-------------|----------|-----|
| Global Assignment | Assigning to `GLOBAL_STATE` | High | Use a class or pass state as parameter |
| Duplicate Keys | Duplicate keys in dict | High | Remove duplicates |
| Magic Numbers | Hardcoded values | Medium | Replace with named constants |
| Unreachable Code | Dead code after return | Medium | Remove or restructure |
| Tight Coupling | Global state dependency | High | Pass state as argument |
| Inconsistent Naming | Mixed case styles | Medium | Standardize to snake_case |
| Long Function | Complex logic in single function | High | Split into helpers |
| Lack of Validation | No checks on values | Medium | Add input validation |
| Lack of Docs | No docstrings/comments | Medium | Add documentation |
| Testability | Depends on global state | High | Make functions injectable |

By addressing these issues, your codebase will become more modular, maintainable, and testable.
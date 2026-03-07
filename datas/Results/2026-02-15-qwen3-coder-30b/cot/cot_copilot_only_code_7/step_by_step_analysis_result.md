### 1. **Global Variables Usage**
**Issue:**  
Using global variables like `GLOBAL_TEXT`, `GLOBAL_COUNTER`, and `GLOBAL_MODE` makes code less modular and harder to test.

**Root Cause:**  
State is shared across functions without explicit boundaries, leading to unintended side effects.

**Impact:**  
Harder to reason about behavior, debug errors, and isolate tests.

**Fix:**  
Replace them with instance attributes in the class:
```python
class MainWindow:
    def __init__(self):
        self.text = ""
        self.counter = 0
        self.mode = "default"
```

**Best Practice:**  
Prefer encapsulation over global state.

---

### 2. **Unused Variable**
**Issue:**  
The variable `GLOBAL_MODE` is declared but not consistently used in handler functions.

**Root Cause:**  
Incomplete implementation or oversight during development.

**Impact:**  
Confusing codebase; developers might miss critical logic paths.

**Fix:**  
Either remove unused variable or ensure consistent usage:
```python
# Remove if not needed
# Or use it in all relevant handlers
```

**Best Practice:**  
Keep only necessary variables and validate assumptions.

---

### 3. **Repeated Conditional Logic**
**Issue:**  
Code duplication in handling different conditions (e.g., checking counter thresholds).

**Root Cause:**  
Lack of abstraction for common behaviors.

**Impact:**  
Maintenance burden due to redundancy.

**Fix:**  
Extract reusable logic into helper methods:
```python
def _check_threshold(self, value):
    return value > 5
```

**Best Practice:**  
DRY – Don’t Repeat Yourself.

---

### 4. **Magic Number**
**Issue:**  
Number `5` has no context or meaning in the code.

**Root Cause:**  
No descriptive name or constant defined.

**Impact:**  
Harder to update or explain behavior.

**Fix:**  
Define a named constant:
```python
MAX_THRESHOLD = 5
if counter > MAX_THRESHOLD:
```

**Best Practice:**  
Use meaningful constants instead of raw numbers.

---

### 5. **Hardcoded Strings**
**Issue:**  
Strings like `'Status: Ready'`, `'Counter small:'` appear directly in code.

**Root Cause:**  
Lack of centralized configuration or constants.

**Impact:**  
Changes require multiple edits; inconsistent UI appearance.

**Fix:**  
Move to constants:
```python
READY_STATUS = "Status: Ready"
SMALL_COUNTER = "Counter small:"
```

**Best Practice:**  
Avoid hardcoded values; centralize configuration.

---

### 6. **Unvalidated Input**
**Issue:**  
User input from `QLineEdit` is appended directly without validation.

**Root Cause:**  
No sanitization or filtering before processing.

**Impact:**  
Security risks and incorrect output if input is malicious or invalid.

**Fix:**  
Sanitize or validate input:
```python
user_input = line_edit.text().strip()
if user_input:
    GLOBAL_TEXT += user_input
```

**Best Practice:**  
Always sanitize and validate external inputs.

---
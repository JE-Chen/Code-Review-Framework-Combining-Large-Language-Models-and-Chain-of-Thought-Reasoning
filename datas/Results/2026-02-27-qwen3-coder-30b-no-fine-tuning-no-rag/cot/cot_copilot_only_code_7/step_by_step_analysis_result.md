### 1. **Global Variables Usage**
**Issue:**  
Using global variables (`GLOBAL_TEXT`, `GLOBAL_COUNTER`, `GLOBAL_MODE`) reduces modularity and testability.

**Explanation:**  
This practice makes the code harder to manage because functions depend on external state, making it difficult to predict behavior or isolate components for testing.

**Root Cause:**  
Code relies on shared mutable state across functions instead of encapsulating data within objects.

**Impact:**  
Makes unit testing complex and increases risk of unintended side effects during updates or debugging.

**Fix Suggestion:**  
Replace global variables with instance attributes in your main class:
```python
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.text_content = ""
        self.counter = 0
        self.mode = "default"
```

**Best Practice:**  
Follow the *encapsulation principle* — keep related data and behavior together inside classes.

---

### 2. **Unused Global Variable**
**Issue:**  
`GLOBAL_MODE` is referenced in `handle_btn2` but never updated outside of reset logic.

**Explanation:**  
The variable is declared and used, yet never changes, suggesting redundancy or incorrect design.

**Root Cause:**  
Inconsistent use of global state leads to confusion about whether the variable is truly needed.

**Impact:**  
Wastes memory and adds unnecessary complexity; may mislead developers into thinking it’s functional.

**Fix Suggestion:**  
Either remove unused variable or ensure proper update logic:
```python
# If not needed, remove GLOBAL_MODE completely
# Or define a default mode properly
```

**Best Practice:**  
Apply the *principle of least privilege* – only expose what’s necessary.

---

### 3. **Duplicate Code**
**Issue:**  
Both `handle_btn1` and `handle_btn3` perform similar operations on `GLOBAL_TEXT` and `GLOBAL_COUNTER`.

**Explanation:**  
Same logic appears in multiple places, violating the DRY (Don’t Repeat Yourself) principle.

**Root Cause:**  
Lack of abstraction or shared helper methods causes duplication.

**Impact:**  
Increases maintenance cost and chances of inconsistency if one part gets updated but not others.

**Fix Suggestion:**  
Extract common logic into a reusable helper method:
```python
def update_state(self, text):
    self.text_content += text + " | "
    self.counter += 1
    self.textArea.append("Added: " + text)
```

**Best Practice:**  
Use *refactoring techniques* to eliminate duplication while preserving functionality.

---

### 4. **Magic Number: Threshold Value**
**Issue:**  
The number `5` used in `handle_btn2` to check counter size is a magic number.

**Explanation:**  
Hardcoded numeric values reduce readability and make future changes harder without understanding context.

**Root Cause:**  
No clear naming for constants that control program behavior.

**Impact:**  
Decreases maintainability and clarity when modifying or explaining the code.

**Fix Suggestion:**  
Define a named constant:
```python
COUNTER_THRESHOLD = 5
if self.counter > COUNTER_THRESHOLD:
    ...
```

**Best Practice:**  
Always replace magic numbers with meaningful constants or configuration values.

---

### 5. **Magic Number: Even/Odd Check**
**Issue:**  
Hardcoded value `2` used to determine even/odd status.

**Explanation:**  
Similar to previous issue, using raw numbers makes code less understandable.

**Root Cause:**  
No abstraction for mathematical concepts like divisibility checks.

**Impact:**  
Reduces readability and increases chance of errors if number is changed incorrectly.

**Fix Suggestion:**  
Use a named constant:
```python
DIVISOR = 2
if self.counter % DIVISOR == 0:
    ...
```

**Best Practice:**  
Avoid hardcoding math-related values unless absolutely necessary.

---

### 6. **Hardcoded Strings**
**Issue:**  
String literals such as `'Status: Ready'`, `'Status: Updated'`, etc., are hardcoded directly in the code.

**Explanation:**  
These strings are repeated throughout the codebase, making localization and updates harder.

**Root Cause:**  
Not extracting UI messages into centralized constants or translations.

**Impact:**  
Makes internationalization and UI consistency difficult; breaks maintainability.

**Fix Suggestion:**  
Create a constants file or class:
```python
STATUS_READY = "Status: Ready"
STATUS_UPDATED = "Status: Updated"
STATUS_RESET_DONE = "Status: Reset Done"
```

**Best Practice:**  
Use *centralized constants* for user-facing strings and messages.

---
### 1. **Unused Variable `app`**
**Issue:**  
The variable `app` is declared but never used anywhere in the code.

**Root Cause:**  
This usually happens due to incomplete refactoring or leftover code from earlier versions. It may have been intended for later use but was forgotten.

**Impact:**  
While not dangerous, it clutters the code and can mislead developers into thinking it's still needed.

**Fix:**  
Remove the unused variable or assign it a meaningful value if it’s meant to be used.

```python
# Before
app = QApplication(sys.argv)

# After (if not needed)
# Remove line entirely
```

**Best Practice:**  
Always clean up unused variables to improve readability and reduce confusion.

---

### 2. **Unused Variable `last_action`**
**Issue:**  
The variable `last_action` is assigned but never used outside its assignment.

**Root Cause:**  
It seems like a placeholder or temporary debugging code that wasn't removed after implementation.

**Impact:**  
Reduces code clarity and may confuse future maintainers who wonder why this variable exists.

**Fix:**  
Either remove the variable or implement logic that uses it.

```python
# Before
self.last_action = "add"

# After
# Remove unused variable
```

**Best Practice:**  
Keep only necessary variables; eliminate dead code to enhance maintainability.

---

### 3. **Implicit Any Type for Parameter `self`**
**Issue:**  
In methods like `add_user`, `delete_user`, and `refresh_status`, the `self` parameter has an implicit `any` type.

**Root Cause:**  
TypeScript/Python type checkers expect explicit typing for parameters unless specified otherwise.

**Impact:**  
Affects static analysis tools and makes the API less predictable and harder to reason about.

**Fix:**  
Explicitly type `self` as `MainWindow`.

```python
def add_user(self: MainWindow) -> None:
    ...
```

**Best Practice:**  
Use explicit typing to ensure type safety and improve IDE support and documentation.

---

### 4. **Empty Block in Exception Handler**
**Issue:**  
There is an empty `except:` block which silently ignores all exceptions.

**Root Cause:**  
Too broad exception handling can hide bugs and prevent proper error propagation.

**Impact:**  
Makes debugging harder and can lead to silent failures in production.

**Fix:**  
Catch specific exceptions or provide logging/comment explaining intent.

```python
# Before
try:
    # Some operation
except:
    pass

# After
try:
    # Some operation
except ValueError:
    self.output.append("Invalid input.")
```

**Best Practice:**  
Avoid bare `except:` blocks. Always catch known exceptions or log them appropriately.

---

### 5. **Assignment to Global Variable `app`**
**Issue:**  
Assigning to the global variable `app` directly is discouraged.

**Root Cause:**  
Global assignments make code harder to manage and test, especially in larger applications.

**Impact:**  
Increases coupling and decreases modularity.

**Fix:**  
Avoid global assignments. Encapsulate logic inside functions or classes.

```python
# Before
app = QApplication(sys.argv)

# After
def create_app():
    return QApplication(sys.argv)

app = create_app()
```

**Best Practice:**  
Minimize global state and prefer encapsulation via functions or modules.

---

### 6. **Magic Number `1000` in Timer Start**
**Issue:**  
The number `1000` appears as a hardcoded interval for a timer.

**Root Cause:**  
Hardcoded values reduce flexibility and readability.

**Impact:**  
Makes tuning difficult and confusing for new developers.

**Fix:**  
Replace with a named constant.

```python
# Before
timer.start(1000)

# After
REFRESH_INTERVAL_MS = 1000
timer.start(REFRESH_INTERVAL_MS)
```

**Best Practice:**  
Use descriptive constants for values that appear repeatedly or have meaning.

---

### 7. **Magic Numbers `0.3` and `0.2` in Sleep Calls**
**Issue:**  
These floating-point values are used directly in `sleep()` calls without explanation.

**Root Cause:**  
Lack of documentation or abstraction around timing behavior.

**Impact:**  
Makes future adjustments brittle and unclear.

**Fix:**  
Define named constants.

```python
# Before
time.sleep(0.3)

# After
ADD_DELAY_SECONDS = 0.3
time.sleep(ADD_DELAY_SECONDS)
```

**Best Practice:**  
Replace magic numbers with meaningful names to increase clarity.

---

### 8. **Duplicate Key `'name'` in Dictionary Literal**
**Issue:**  
Dictionary contains duplicate keys — specifically `'name'`.

**Root Cause:**  
Typo or copy-paste error resulting in overwriting existing entries.

**Impact:**  
Data loss or incorrect behavior depending on how the dict is used.

**Fix:**  
Ensure each key is unique.

```python
# Before
data = {"name": "John", "name": "Jane"}

# After
data = {"name": "John", "age": 30}
```

**Best Practice:**  
Validate data structures to ensure uniqueness of keys, particularly in dynamic scenarios.

---

### 9. **Long Functions (`add_user`, `delete_user`)**
**Issue:**  
Both methods perform too many tasks, violating the Single Responsibility Principle.

**Root Cause:**  
UI logic and business logic are mixed together.

**Impact:**  
Harder to test, debug, and modify. Can block UI thread with `time.sleep`.

**Fix:**  
Break down logic into smaller helper functions.

```python
# Before
def add_user(self):
    # Multiple responsibilities in one function

# After
def add_user(self):
    if not self.validate_input():
        return
    self.update_model()
    self.refresh_ui()
```

**Best Practice:**  
Each function should do one thing well — adhere to SRP.

---

### 10. **Inconsistent Naming Conventions**
**Issue:**  
Variables like `txtAge`, `btn_add_user`, `buttonDelete` mix snake_case and camelCase.

**Root Cause:**  
No consistent naming strategy applied.

**Impact:**  
Reduced readability and consistency across the project.

**Fix:**  
Standardize naming convention (snake_case preferred).

```python
# Before
txtAge, btn_add_user, buttonDelete

# After
txt_age, btn_add_user, button_delete
```

**Best Practice:**  
Stick to a single naming style (PEP8 recommends snake_case).

---

### 11. **Tight Coupling Between UI and Logic**
**Issue:**  
Business logic directly modifies UI components.

**Root Cause:**  
Lack of separation between presentation and domain logic.

**Impact:**  
Difficult to unit test and hard to reuse logic in other parts.

**Fix:**  
Introduce a model layer and communicate via signals/slots or callbacks.

```python
# Instead of modifying QLabel directly...
self.lblStatus.setText("User added")

# Use a signal
self.user_added.emit("User added")
```

**Best Practice:**  
Separate UI from core logic using MVC/MVP patterns.

---

### 12. **Broad Exception Handling**
**Issue:**  
Using `except:` catches all exceptions silently.

**Root Cause:**  
Overgeneralized error handling prevents debugging and reporting.

**Impact:**  
Silent failure in critical paths.

**Fix:**  
Catch specific exceptions.

```python
# Before
except:
    pass

# After
except ValueError:
    self.output.append("Invalid age entered.")
```

**Best Practice:**  
Catch specific exceptions and handle them meaningfully.

---

### 13. **Duplicate Code**
**Issue:**  
Both `add_user` and `delete_user` perform similar validation steps.

**Root Cause:**  
Repetition of logic across similar functions.

**Impact:**  
Maintenance burden increases over time.

**Fix:**  
Create reusable validation utilities.

```python
def validate_input(self, name, age):
    if not name.strip():
        return False
    try:
        int(age)
    except ValueError:
        return False
    return True
```

**Best Practice:**  
Apply DRY (Don’t Repeat Yourself) principle to avoid redundancy.

---

### 14. **Global State Misuse (`last_action`)**
**Issue:**  
Reliance on a global flag to influence UI rendering.

**Root Cause:**  
Hidden dependency leads to unpredictable behavior.

**Impact:**  
Harder to trace side effects and reason about flow.

**Fix:**  
Pass state explicitly or use event-driven communication.

```python
# Instead of relying on last_action
# Emit an event signaling the action type
self.action_performed.emit("add_user")
```

**Best Practice:**  
Avoid hidden state management; make dependencies explicit.

---

### 15. **Lack of Input Sanitization**
**Issue:**  
Raw input from QLineEdit is used without sanitization.

**Impact:**  
Potential vulnerability in future extensions.

**Fix:**  
Sanitize input before displaying or processing.

```python
def sanitize_input(text):
    return text.replace("<", "&lt;").replace(">", "&gt;")
```

**Best Practice:**  
Even in simple apps, sanitize user input when rendered or stored.

---

### 16. **Hardcoded UI Geometry**
**Issue:**  
Window size is hardcoded with fixed coordinates and dimensions.

**Root Cause:**  
Not responsive or adaptable to different screens.

**Impact:**  
Poor user experience on various devices.

**Fix:**  
Use layout managers instead of fixed positioning.

```python
# Before
self.setGeometry(100, 100, 500, 400)

# After
layout = QVBoxLayout()
self.setLayout(layout)
```

**Best Practice:**  
Design flexible layouts that adapt to screen sizes.

---

### 17. **Unused Imports**
**Issue:**  
Imports such as `sys` and `time` are partially used.

**Impact:**  
Cluttered imports reduce readability.

**Fix:**  
Remove unused imports or keep commented for reference.

```python
# Before
import sys
import time

# After
import sys
# import time  # Not currently used
```

**Best Practice:**  
Keep only required imports for cleaner codebases.

---
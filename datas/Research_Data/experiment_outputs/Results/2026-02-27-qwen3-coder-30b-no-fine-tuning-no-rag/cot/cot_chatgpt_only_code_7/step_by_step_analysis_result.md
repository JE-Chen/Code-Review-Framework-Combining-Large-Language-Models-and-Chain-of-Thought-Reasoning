### 1. **Unused Variable `window`**
- **Issue**: The variable `window` is declared but never used.
- **Explanation**: This indicates dead code — a variable that was either accidentally created or forgotten about.
- **Root Cause**: Likely leftover from previous development or copy-paste error.
- **Impact**: Minor impact on readability; no functional harm but reduces clarity.
- **Fix**: Remove the unused line.
```python
# Before
window = some_value  # unused

# After
# Removed unused variable
```
- **Best Practice**: Regularly clean up unused variables to improve maintainability.

---

### 2. **Undefined Variable `window` in Function Scope**
- **Issue**: `window` is referenced but not defined in current scope.
- **Explanation**: A reference exists to a global or outer scope variable that hasn't been declared locally or passed in.
- **Root Cause**: Incorrect scoping or missing declaration in function context.
- **Impact**: Could cause runtime errors if `window` doesn’t exist elsewhere.
- **Fix**: Ensure variable is properly initialized or passed into the function.
```python
# Before
def my_function():
    print(window)  # undefined

# After
window = None  # define or inject
def my_function():
    print(window)
```
- **Best Practice**: Always declare or import variables before use.

---

### 3. **Assignment to Global Variable `app`**
- **Issue**: Assigning to a global variable `app`.
- **Explanation**: Modifying top-level global state directly can lead to unpredictable behavior.
- **Root Cause**: Direct assignment to a global symbol instead of encapsulation.
- **Impact**: Makes testing harder and introduces side effects.
- **Fix**: Avoid modifying globals; use local variables or functions for encapsulation.
```python
# Before
app = MyApp()

# After
def create_app():
    return MyApp()
```
- **Best Practice**: Encapsulate global state changes in controlled functions or classes.

---

### 4. **Magic Number '1000' in Timer Start**
- **Issue**: Hardcoded value `1000` used for refresh interval.
- **Explanation**: Magic numbers reduce readability and make future modifications harder.
- **Root Cause**: No abstraction for time intervals.
- **Impact**: Reduces flexibility and maintainability.
- **Fix**: Replace with named constant.
```python
# Before
timer.start(1000)

# After
REFRESH_INTERVAL_MS = 1000
timer.start(REFRESH_INTERVAL_MS)
```
- **Best Practice**: Use descriptive constants for numeric literals.

---

### 5. **Magic Numbers '0.3' and '0.2' in Sleep Calls**
- **Issue**: Non-descriptive floating-point values in `sleep()` calls.
- **Explanation**: These represent delays but lack meaning without context.
- **Root Cause**: Lack of abstraction or naming for time-based behaviors.
- **Impact**: Makes behavior harder to tune and debug.
- **Fix**: Replace with meaningful constants.
```python
# Before
time.sleep(0.3)
time.sleep(0.2)

# After
ADD_DELAY_SEC = 0.3
DELETE_DELAY_SEC = 0.2
time.sleep(ADD_DELAY_SEC)
time.sleep(DELETE_DELAY_SEC)
```
- **Best Practice**: Prefer named constants over raw numbers.

---

### 6. **Empty Except Block**
- **Issue**: An empty `except:` block catches all exceptions silently.
- **Explanation**: Prevents error logging and makes debugging harder.
- **Root Cause**: Lack of explicit exception handling.
- **Impact**: Can mask real bugs and hinder troubleshooting.
- **Fix**: Log the exception or re-raise it.
```python
# Before
try:
    risky_operation()
except:
    pass

# After
import logging
try:
    risky_operation()
except ValueError as e:
    logging.error(f"Invalid input: {e}")
    raise
```
- **Best Practice**: Handle specific exceptions and log appropriately.

---

### 7. **Duplicate Key in Dictionary Literal**
- **Issue**: Duplicate key `'name'` in dictionary.
- **Explanation**: Only the last value for the key will be retained.
- **Root Cause**: Mistake in constructing dictionary.
- **Impact**: Data loss or incorrect logic due to overwritten entries.
- **Fix**: Correct the duplicate key.
```python
# Before
data = {"name": "John", "name": "Jane"}

# After
data = {"name": "John", "email": "jane@example.com"}
```
- **Best Practice**: Ensure uniqueness of keys in dictionaries.

---

### 8. **Implicit Global Variable `users` in Class Method**
- **Issue**: Using `users` as a global-like variable inside a class method.
- **Explanation**: Violates encapsulation by accessing a class attribute implicitly.
- **Root Cause**: Missing explicit class attribute definition or parameter passing.
- **Impact**: Makes code brittle and harder to reason about.
- **Fix**: Make it explicit by declaring or passing it as a parameter.
```python
# Before
class MainWindow:
    def add_user(self):
        users.append(...)  # implicit global

# After
class MainWindow:
    def __init__(self):
        self.users = []

    def add_user(self):
        self.users.append(...)
```
- **Best Practice**: Explicitly manage class attributes to avoid ambiguity.

---

### 9. **Lambda with No Arguments**
- **Issue**: Lambda expression has no parameters.
- **Explanation**: Confusing syntax; unclear intent.
- **Root Cause**: Misuse of lambda for simple functions.
- **Impact**: Reduces readability and clarity.
- **Fix**: Replace with a named function.
```python
# Before
lambda: update_ui()

# After
def update_ui_callback():
    update_ui()
```
- **Best Practice**: Prefer named functions for better readability and debugging.

---

### 10. **Long Functions (`add_user`, `delete_user`)**
- **Issue**: These methods do too many things at once.
- **Explanation**: Violates the Single Responsibility Principle (SRP).
- **Root Cause**: Merging unrelated actions into one function.
- **Impact**: Difficult to test, modify, or extend.
- **Fix**: Break down into smaller, focused methods.
```python
# Before
def add_user(self):
    validate_input()
    process_data()
    update_ui()
    delay()

# After
def add_user(self):
    self._validate_input()
    self._process_add_user()
    self._update_ui_after_add()
    self._delay_for_animation()
```
- **Best Practice**: Each function should have one clear responsibility.

---

### 11. **Magic Numbers/Strings in Sleep Calls**
- **Issue**: Fixed sleep durations.
- **Explanation**: Makes UI feel sluggish and reduces configurability.
- **Root Cause**: Hardcoding timing values.
- **Impact**: Poor user experience and reduced testability.
- **Fix**: Use named constants.
```python
# Before
time.sleep(0.3)

# After
DELAY_SECONDS = 0.3
time.sleep(DELAY_SECONDS)
```
- **Best Practice**: Abstract timing values into named constants.

---

### 12. **Inconsistent Naming Convention**
- **Issue**: Mixed PascalCase and snake_case naming.
- **Explanation**: Inconsistent style affects readability and professionalism.
- **Root Cause**: Lack of consistent naming policy.
- **Impact**: Minor but noticeable inconsistency in codebase.
- **Fix**: Standardize to snake_case.
```python
# Before
txtAge, btn_add_user

# After
txt_age, btn_add_user
```
- **Best Practice**: Follow PEP 8 naming conventions.

---

### 13. **Tight Coupling Between UI and Logic**
- **Issue**: Direct access to UI elements in logic methods.
- **Explanation**: Mixing UI logic with backend logic reduces modularity.
- **Root Cause**: Not separating concerns.
- **Impact**: Harder to test and refactor.
- **Fix**: Introduce a model to handle data and logic separately.
```python
# Before
self.nameInput.setText(...)

# After
self.model.add_user(...)
self.view.update_display(...)
```
- **Best Practice**: Separate view, model, and controller logic.

---

### 14. **Poor Exception Handling**
- **Issue**: Bare `except:` clause.
- **Explanation**: Catches all exceptions without logging or raising them.
- **Root Cause**: Lack of structured error management.
- **Impact**: Masked errors and poor diagnostics.
- **Fix**: Catch specific exceptions and log them.
```python
# Before
except:
    pass

# After
except ValueError as e:
    logger.warning(f"Invalid input: {e}")
```
- **Best Practice**: Handle known exceptions explicitly and log failures.

---

### 15. **Global State Management**
- **Issue**: Storing mutable data (`users`) directly on widget instance.
- **Explanation**: Violates encapsulation and makes testing harder.
- **Root Cause**: Direct mutation of state outside of proper boundaries.
- **Impact**: Increases complexity and reduces reliability.
- **Fix**: Move data into a dedicated model class.
```python
# Before
self.users = []

# After
class UserManager:
    def __init__(self):
        self.users = []
```
- **Best Practice**: Encapsulate state within models or services.

---

### 16. **Duplicate Code in Status Updates**
- **Issue**: Same UI update logic repeated in two methods.
- **Explanation**: Repetition leads to inconsistencies and maintenance overhead.
- **Root Cause**: Lack of reusable helper functions.
- **Impact**: Risk of divergence and redundancy.
- **Fix**: Extract into a shared utility.
```python
# Before
label.setText("Success!")
label.setStyleSheet("color: green")

# After
def update_status(label, message, color):
    label.setText(message)
    label.setStyleSheet(f"color: {color}")

update_status(lblStatus, "Success!", "green")
```
- **Best Practice**: Eliminate duplication using shared utilities.

---

### 17. **Blocking UI Updates with `time.sleep()`**
- **Issue**: Synchronous delay freezes GUI.
- **Explanation**: Blocks the main thread causing unresponsiveness.
- **Root Cause**: Using blocking I/O in the UI thread.
- **Impact**: Bad UX and possible app freezing.
- **Fix**: Use async patterns or `QTimer.singleShot()`.
```python
# Before
time.sleep(0.3)

# After
QTimer.singleShot(300, lambda: self.on_delay_complete())
```
- **Best Practice**: Never block the main thread in GUI apps.

---

### 18. **Hardcoded Styling in Code**
- **Issue**: Inline CSS styling.
- **Explanation**: Makes theme changes and styling harder to implement.
- **Root Cause**: Mixing presentation with logic.
- **Impact**: Less flexible and harder to update.
- **Fix**: Centralize or externalize styles.
```python
# Before
lblStatus.setStyleSheet("color: red")

# After
STYLES = {"error": "color: red", "success": "color: green"}
lblStatus.setStyleSheet(STYLES["error"])
```
- **Best Practice**: Separate styling from logic using stylesheets or config.

---

### 19. **Lack of Input Validation**
- **Issue**: Minimal validation of inputs.
- **Explanation**: Allows invalid data entry.
- **Root Cause**: Insufficient sanitization or checks.
- **Impact**: Potential corruption or crashes from malformed data.
- **Fix**: Add robust validation.
```python
# Before
if name == "":
    ...

# After
if not name.strip():
    raise ValueError("Name cannot be empty")
```
- **Best Practice**: Validate inputs early and provide feedback to users.
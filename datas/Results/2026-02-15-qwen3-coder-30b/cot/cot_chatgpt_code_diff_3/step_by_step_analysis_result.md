### 1. **Global State Mutation**
- **Issue**: The global variable `GLOBAL_THING` is modified in multiple places, making it hard to track dependencies and test logic reliably.
- **Root Cause**: Using a shared mutable state across modules breaks encapsulation and increases tight coupling.
- **Impact**: Reduces maintainability and introduces unpredictable behavior due to hidden side effects.
- **Fix Suggestion**: Replace with instance attributes or pass state explicitly.
  ```python
  # Before
  GLOBAL_THING["count"] += 1

  # After
  self.state["count"] += 1
  ```
- **Best Practice**: Avoid global state; prefer encapsulated objects or explicit parameters.

---

### 2. **Blocking Operation in UI**
- **Issue**: `time.sleep()` blocks the main thread, causing the UI to freeze during interactions.
- **Root Cause**: Synchronous delays interfere with responsive user experience.
- **Impact**: Poor UX and potential application unresponsiveness.
- **Fix Suggestion**: Use `QTimer.singleShot()` or async alternatives.
  ```python
  # Before
  time.sleep(0.1)

  # After
  QTimer.singleShot(100, callback)
  ```
- **Best Practice**: Never block the UI thread with synchronous operations.

---

### 3. **Magic Number**
- **Issue**: Literal value `777` used as a timer interval without explanation.
- **Root Cause**: Hardcoded numeric values decrease readability and change risk.
- **Impact**: Future modifications require guessing meaning behind values.
- **Fix Suggestion**: Define named constants.
  ```python
  # Before
  timer.start(777)

  # After
  TIMER_INTERVAL = 777
  timer.start(TIMER_INTERVAL)
  ```
- **Best Practice**: Replace magic numbers with descriptive constants.

---

### 4. **Magic String**
- **Issue**: Repeated strings like `'Click maybe'` appear without centralization.
- **Root Cause**: Duplication makes updates and localization harder.
- **Impact**: Maintenance overhead and inconsistency.
- **Fix Suggestion**: Extract to a shared constant or list.
  ```python
  # Before
  label.setText("Click maybe")

  # After
  MESSAGES = ["Click maybe", "Don't click"]
  label.setText(MESSAGES[0])
  ```
- **Best Practice**: Centralize reusable literals for better scalability.

---

### 5. **Inconsistent Naming**
- **Issue**: Function names mix `snake_case` and `camelCase`.
- **Root Cause**: Lack of style consistency across codebase.
- **Impact**: Confusion and reduced team productivity.
- **Fix Suggestion**: Stick to `snake_case` per PEP8.
  ```python
  # Before
  def handleClick(): ...

  # After
  def handle_click(): ...
  ```
- **Best Practice**: Enforce naming conventions early and consistently.

---

### 6. **Hardcoded Values**
- **Issue**: Constants like `300`, `200`, `777` are hardcoded throughout the code.
- **Root Cause**: Configuration is buried in logic, reducing flexibility.
- **Impact**: Requires recompilation or manual edits for minor tweaks.
- **Fix Suggestion**: Move to config files or constants.
  ```python
  # Before
  if x > 300:

  # After
  MAX_WIDTH = 300
  if x > MAX_WIDTH:
  ```
- **Best Practice**: Externalize configurations for adaptability.

---

### 7. **Duplicate Logic**
- **Issue**: Same access pattern to `GLOBAL_THING` appears in multiple methods.
- **Root Cause**: Lack of abstraction leads to redundancy.
- **Impact**: Increases risk of inconsistencies and bugs.
- **Fix Suggestion**: Encapsulate access using getters/setters.
  ```python
  # Before
  GLOBAL_THING["key"] = value

  # After
  def set_global_value(key, value):
      GLOBAL_THING[key] = value
  ```
- **Best Practice**: Abstract common behaviors into reusable utilities.

---

### 8. **Side Effects in Pure Functions**
- **Issue**: `compute_title()` mutates `GLOBAL_THING["mood"]`.
- **Root Cause**: Violates functional purity expectations.
- **Impact**: Makes reasoning about function behavior more complex.
- **Fix Suggestion**: Separate computation from mutation.
  ```python
  # Before
  def compute_title():
      GLOBAL_THING["mood"] = "happy"

  # After
  def get_title():
      return f"Title: {current_mood}"
  ```
- **Best Practice**: Pure functions should not modify external state.

---

### 9. **Long Function**
- **Issue**: `handle_click()` and `do_periodic_stuff()` do too much.
- **Root Cause**: Violates SRP by combining responsibilities.
- **Impact**: Difficult to test, debug, and extend.
- **Fix Suggestion**: Break down large functions into smaller ones.
  ```python
  # Before
  def handle_click():
      update_counter()
      trigger_ui_change()
      change_mood()

  # After
  def handle_click():
      update_counter()
      self.ui.update()
      self.mood_manager.change_state()
  ```
- **Best Practice**: Each function should have one well-defined responsibility.

---

### 10. **Lack of Input Validation**
- **Issue**: No checks on contents of `GLOBAL_THING`.
- **Root Cause**: Assumptions about data integrity may break the program.
- **Impact**: Unexpected crashes or invalid behavior.
- **Fix Suggestion**: Add validation before processing.
  ```python
  # Before
  mood = GLOBAL_THING["mood"]

  # After
  if "mood" in GLOBAL_THING:
      mood = GLOBAL_THING["mood"]
  else:
      mood = "neutral"
  ```
- **Best Practice**: Validate inputs defensively.

---

### 11. **Tight Coupling**
- **Issue**: Multiple components directly depend on `GLOBAL_THING`.
- **Root Cause**: Modules aren’t isolated from each other.
- **Impact**: Difficult to reuse or refactor components independently.
- **Fix Suggestion**: Pass state through interfaces or events.
  ```python
  # Before
  def process_data():
      GLOBAL_THING["value"] += 1

  # After
  def process_data(state):
      state["value"] += 1
  ```
- **Best Practice**: Loose coupling improves modularity and testability.

---

### 12. **Missing Documentation**
- **Issue**: No docstrings or inline comments explain logic.
- **Root Cause**: Lack of clarity for future developers.
- **Impact**: Slower onboarding and higher chance of misuse.
- **Fix Suggestion**: Add docstrings and inline explanations.
  ```python
  def handle_click():
      """Handles click event and updates internal counter."""
      ...
  ```
- **Best Practice**: Document public APIs and obscure logic clearly.

--- 

✅ **Summary of Priorities**:
| Severity | Issue |
|----------|-------|
| ⚠️ High | Global state mutation, side effects, blocking I/O |
| ⚠️ Medium | Magic numbers, long functions, lack of validation |
| ⚠️ Low | Inconsistent naming, missing docs |

These improvements enhance code clarity, robustness, and scalability.
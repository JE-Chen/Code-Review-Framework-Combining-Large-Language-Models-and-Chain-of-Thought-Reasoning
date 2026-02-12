### Diff #1

---

### Summary
This code implements a simple PySide6 GUI application with three buttons for text input, counter display, and reset functionality. The primary purpose is to demonstrate state management using global variables (e.g., `GLOBAL_TEXT`, `GLOBAL_COUNTER`). Key affected components:
- **Files**: Single main application script.
- **Modules**: `PySide6.QtWidgets` for UI components.
- **Core functions**: `MainWindow` class with button handlers (`handle_btn1`, `handle_btn2`, `handle_btn3`).
- **Plain-language explanation**: A text input field and three buttons let users add text (logging to a text area), view a counter with conditional messages, and reset the app. The app uses global variables to track state instead of encapsulating it within the UI class.

---

### Linting Issues
- **Global variables used in methods** (e.g., `handle_btn1`, `handle_btn2`):  
  Violates style rules (e.g., PEP 8) by modifying global state directly.  
  *Suggestion*: Replace with instance attributes (e.g., `self.counter = 0`).

- **Hardcoded status strings** (e.g., `"Status: Ready"`):  
  String literals repeated across methods (e.g., `self.label1.setText("Status: Ready")` vs. `self.label1.setText("Status: Updated")`).  
  *Suggestion*: Define constants or methods for status updates.

- **Inconsistent string formatting**:  
  Mixed use of `+` concatenation (`"Added: " + text`) vs. f-strings (not used here).  
  *Suggestion*: Standardize to f-strings for readability (e.g., `f"Added: {text}"`).

---

### Code Smells
- **Global state pollution**:  
  `GLOBAL_TEXT`, `GLOBAL_COUNTER`, and `GLOBAL_MODE` are mutable globals accessed across all handlers.  
  *Why problematic*:  
  - Breaks encapsulation (state managed outside `MainWindow`).  
  - Causes unexpected side effects (e.g., global state changed by unrelated code).  
  *Recommendation*: Replace with instance attributes (`self.text`, `self.counter`, `self.mode`).

- **Nested conditionals in `handle_btn2`**:  
  Deeply nested logic (e.g., `if GLOBAL_COUNTER > 5: if GLOBAL_MODE == "default": ...`).  
  *Why problematic*:  
  - Hard to read and debug.  
  - Violates the Single Responsibility Principle (handles state + UI updates).  
  *Recommendation*: Extract conditional logic to helper methods (e.g., `get_counter_message()`).

- **State inconsistency**:  
  `GLOBAL_MODE` is reset to `"reset"` in `handle_btn3`, but never used meaningfully (e.g., `GLOBAL_MODE` is ignored in `handle_btn1`).  
  *Why problematic*:  
  - Unnecessary complexity (state not utilized).  
  - Potential for bugs if `GLOBAL_MODE` is referenced elsewhere.  
  *Recommendation*: Remove `GLOBAL_MODE` or implement its intended use.

- **Overuse of global references**:  
  All handlers declare `global` explicitly.  
  *Why problematic*:  
  - Hides dependencies (code becomes fragile to changes).  
  - Prevents unit testing (no dependency injection).  
  *Recommendation*: Encapsulate state within `MainWindow` to avoid globals entirely.
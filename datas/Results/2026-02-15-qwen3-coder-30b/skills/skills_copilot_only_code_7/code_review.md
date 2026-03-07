---

### **Diff #1**

#### **1. Summary**
This PR introduces a basic GUI application using PySide6 that allows users to add text, display a counter, and reset the state. The core functionality resides in a single `MainWindow` class, which manages UI components such as buttons, labels, and text areas. It uses global variables (`GLOBAL_TEXT`, `GLOBAL_COUNTER`, `GLOBAL_MODE`) to track state across button interactions.

- **Files Affected**: One Python file (`main.py` or similar).
- **Modules/Functions**: `MainWindow`, `handle_btn1`, `handle_btn2`, `handle_btn3`, `main`.
- **Plain Language Explanation**: This program lets users type text into a box, click a button to save it, see how many times they've added text, and clear everything when done.

#### **2. Linting Issues**
- No explicit linting errors found (PEP8 compliance appears acceptable).
- Minor stylistic improvement suggestions:
  - Consider aligning spacing around assignment operators for consistency.
  - Line lengths could be capped at 79 characters for readability (though not enforced here).

#### **3. Code Smells**
- **Global State Usage**:
  - *Problem*: Heavy reliance on global variables makes testing difficult and increases side effects.
  - *Impact*: Harder to reason about behavior; prone to bugs due to shared mutable state.
  - *Recommendation*: Replace globals with instance attributes (`self.text`, `self.counter`, etc.) within `MainWindow`.

- **Tight Coupling**:
  - *Problem*: Methods like `handle_btn2` depend directly on external state variables (`GLOBAL_COUNTER`, `GLOBAL_MODE`) rather than encapsulating logic.
  - *Impact*: Difficult to modify logic without breaking other parts of the system.
  - *Recommendation*: Encapsulate logic inside methods or helper classes instead of relying on module-level state.

- **Magic Strings and Numbers**:
  - *Problem*: Constants like `"default"` and threshold `5` appear hardcoded.
  - *Impact*: Makes future changes harder and less flexible.
  - *Recommendation*: Define constants or use configuration objects for these values.

- **Long Function Logic**:
  - *Problem*: `handle_btn2()` has nested conditional blocks making control flow hard to follow.
  - *Impact*: Reduces readability and maintainability.
  - *Recommendation*: Extract complex conditionals into smaller helper functions.

---
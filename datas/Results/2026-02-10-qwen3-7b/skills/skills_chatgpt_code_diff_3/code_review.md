### Diff #1
---

### 1. Summary
- **Purpose**: The PR creates a simple Qt application with a window that updates labels and buttons based on random events and global variables.
- **Affected Files**: `main.py`.
- **Plain-Language Explanation**: The app displays a label and button, updates them based on random events and global state, and handles user clicks.

---

### 2. Linting Issues
- **Violation 1**: Unused imports (`sys`, `random`, `time`) in the code.
  - **File**: `main.py`
  - **Line**: 3, 4, 5
  - **Fix**: Remove unused imports or use them where needed.
- **Violation 2**: Missing docstrings for functions (`compute_title`, `generate_text`, `do_periodic_stuff`).
  - **File**: `main.py`
  - **Line**: 15, 24, 28
  - **Fix**: Add docstrings explaining function purposes.
- **Violation 3**: Global variable `GLOBAL_THING` is used without encapsulation.
  - **File**: `main.py`
  - **Line**: 12
  - **Fix**: Move global state to a class or module.

---

### 3. Code Smells
- **Issue 1**: Global state (`GLOBAL_THING`) is used across multiple functions.
  - **Problem**: Hard to test, maintain, or debug.
  - **Fix**: Encapsulate state in a class or use a module-level variable.
- **Issue 2**: `generate_text` returns a string not used in the UI.
  - **Problem**: Unused return value.
  - **Fix**: Remove or use the return value appropriately.
- **Issue 3**: `compute_title` modifies global state directly.
  - **Problem**: Violates encapsulation and makes state management unclear.
  - **Fix**: Move state updates to a class or use a module-level variable.
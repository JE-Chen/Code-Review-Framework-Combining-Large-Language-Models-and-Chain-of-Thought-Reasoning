### Code Review Summary

- **Key changes**:  
  Replaced global state variables (`GLOBAL_TEXT`, `GLOBAL_COUNTER`, `GLOBAL_MODE`) with class instance attributes to encapsulate state within `MainWindow`. Removed global scope dependencies.

- **Impact scope**:  
  Entire `MainWindow` class and its methods (`handle_btn1`, `handle_btn2`, `handle_btn3`). No external dependencies affected.

- **Purpose of changes**:  
  Eliminate global state anti-pattern to improve maintainability, testability, and reduce unintended side effects. Original functionality preserved.

- **Risks and considerations**:  
  - Mode logic (`GLOBAL_MODE` → `self.mode`) is preserved but requires validation to ensure parity-based behavior remains consistent.  
  - Reset state (`GLOBAL_MODE = "reset"`) now uses instance state instead of global, avoiding race conditions.  
  - *Critical*: Global state removal prevents accidental cross-component mutations.

- **Items to confirm**:  
  - Verify `handle_btn2` behavior matches original when counter >5 and `mode` is not `"default"` (e.g., after reset).  
  - Confirm no residual global variable usage in the codebase.  
  - Validate reset functionality (`handle_btn3`) maintains expected UI state transitions.

---

### Critical Issues Addressed
1. **Global State Removal** (Major Fix):  
   Original code used global variables for state management, violating encapsulation. Now state is properly scoped to `MainWindow` instance.

2. **Logic Clarity**:  
   Removed ambiguous global mode checks. `self.mode` is now a clear instance attribute with consistent lifecycle (set only in `handle_btn3`).

3. **Testability**:  
   Code is now modular. Unit tests can mock `MainWindow` without global state interference.

---

### Minor Improvements (Not Required for Merge)
- Add docstrings for class/methods (e.g., `handle_btn1` description).
- Replace `GLOBAL_MODE` string with enum for type safety (optional).
- Simplify `handle_btn2` condition logic (e.g., move parity check to separate method).

---

### Why This Matters
Global state creates hidden dependencies, making bugs hard to trace and tests impossible. The fix aligns with PySide6 best practices and ensures future changes won’t accidentally break unrelated components. The PR scope is focused and safe—no behavioral changes, only structural improvements.
### Pull Request Summary

*   **Key changes**: Implemented a basic PySide6 GUI application with text input, a counter, and state management.
*   **Purpose of changes**: Provide a functional example of a window with interactive buttons and a text area.
*   **Items to confirm**: Review the state management approach and the conditional logic in the button handlers.

---

### Code Review

#### 1. Readability & Consistency
*   **Naming**: Variable names like `btn1`, `btn2`, `btn3`, `input1`, and `label1` are non-descriptive. They should reflect their purpose (e.g., `add_text_button`, `status_label`).

#### 2. Software Engineering Standards
*   **Modularization**: The `MainWindow` class handles both UI layout and business logic. The logic for managing the text and counter should be decoupled from the UI components to improve testability.

#### 3. Logic & Correctness
*   **Implicit Truthiness**: In `handle_btn1`, `if len(text) > 0:` is used. While correct, it is more idiomatic in Python to use `if text:`.

#### 4. Performance & Security
*   **Input Validation**: While there is a check for empty strings, there is no sanitization or length limit on the input, which could lead to memory issues if extremely large strings are appended repeatedly to the global state.

#### 5. RAG Rules Violations

**Shared Mutable State**
*   **Violation**: The use of `GLOBAL_TEXT`, `GLOBAL_COUNTER`, and `GLOBAL_MODE` at the module level is a significant issue.
*   **Impact**: This introduces hidden coupling and makes the application difficult to test or extend (e.g., if multiple windows were needed).
*   **Recommendation**: Move these variables into the `MainWindow` class as instance attributes (e.g., `self.text_accumulator`).

**Deeply Nested Conditional Logic**
*   **Violation**: `handle_btn2` contains three levels of nested `if/else` statements.
*   **Impact**: Increases cognitive load and reduces readability.
*   **Recommendation**: Use guard clauses to handle the "small counter" case early and flatten the remaining logic.

**Single Responsibility Principle**
*   **Violation**: The `handle_btn` methods are performing state updates, business logic (parity checks), and UI updates simultaneously.
*   **Recommendation**: Separate the state update logic into helper methods.

**Magic Numbers**
*   **Violation**: The number `5` in `if GLOBAL_COUNTER > 5:` is a magic number.
*   **Recommendation**: Define this as a named constant (e.g., `COUNTER_THRESHOLD = 5`) to explain its significance.

---

### Summary of Recommendations

| Severity | Category | Issue | Recommendation |
| :--- | :--- | :--- | :--- |
| **High** | RAG | Global mutable state | Move globals into the class as instance attributes. |
| **Medium** | RAG | Deep nesting in `handle_btn2` | Refactor using guard clauses. |
| **Medium** | Naming | Non-descriptive UI names | Rename `btn1`, `input1`, etc., to descriptive names. |
| **Low** | RAG | Magic number `5` | Extract to a named constant. |
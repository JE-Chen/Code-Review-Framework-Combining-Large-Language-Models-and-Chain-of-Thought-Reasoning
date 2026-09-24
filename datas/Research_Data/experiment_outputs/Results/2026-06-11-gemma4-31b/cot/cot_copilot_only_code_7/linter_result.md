Based on the global rules provided, here is the comprehensive code review of the submitted PySide6 application.

### 1. Readability & Consistency
- **Formatting:** The code follows basic PEP 8 indentation and spacing.
- **Consistency:** The formatting is consistent throughout the file.

### 2. Naming Conventions
- **Generic Naming:** Several variables use non-descriptive names (e.g., `btn1`, `btn2`, `btn3`, `input1`, `label1`). These should reflect their purpose (e.g., `add_text_button`, `status_label`).
- **Global Naming:** While uppercase is used for globals, these are used as mutable state, which is a design flaw (see Software Engineering Standards).

### 3. Software Engineering Standards
- **Global State:** The use of `GLOBAL_TEXT`, `GLOBAL_COUNTER`, and `GLOBAL_MODE` is a significant "code smell." Application state should be encapsulated within the `MainWindow` class or a separate state-management object.
- **Modularization:** The logic for processing the counter and text is embedded directly within the UI event handlers. This makes the logic difficult to unit test without instantiating the full GUI.
- **Tight Coupling:** The UI layout and logic are tightly coupled in the `__init__` method.

### 4. Logic & Correctness
- **Complexity:** `handle_btn2` contains nested `if/else` blocks that increase cognitive load. This logic should be flattened or extracted into a helper method.
- **String Concatenation:** The use of `+` for string building in `handle_btn1` and `handle_btn2` is less efficient than f-strings or `.format()`.

### 5. Performance & Security
- **Input Validation:** While there is a basic check for empty strings (`len(text) > 0`), there is no sanitization or length limiting on the `QLineEdit` input.
- **Resource Management:** The application correctly handles the PySide6 event loop and exits using `sys.exit(app.exec())`.

### 6. Documentation & Testing
- **Missing Documentation:** There are no docstrings for the class or its methods.
- **Testing:** No unit tests are provided. Due to the reliance on global variables and UI-coupled logic, the current code is nearly impossible to test automatically.

---

### Summary Score & Findings

| Category | Rating | Notes |
| :--- | :--- | :--- |
| **Readability** | Good | Clear formatting but poor naming. |
| **Naming** | Fair | Too many generic identifiers (`btn1`, `input1`). |
| **Engineering** | Poor | Heavy reliance on mutable global state. |
| **Logic** | Fair | Correct but poorly structured (nested conditionals). |
| **Performance/Sec** | Good | No major leaks, but lacks input sanitization. |
| **Docs/Testing** | Poor | Total absence of documentation and tests. |

### Recommendations
1. **Refactor State:** Move `GLOBAL_TEXT`, `GLOBAL_COUNTER`, and `GLOBAL_MODE` into `self` attributes of the `MainWindow` class.
2. **Rename Components:** Rename buttons and inputs to descriptive names (e.g., `self.reset_button`).
3. **Decouple Logic:** Move the counter logic from `handle_btn2` into a separate method like `get_counter_status_message()`.
4. **Modernize Strings:** Replace string concatenation with f-strings for better readability and performance.
5. **Add Documentation:** Include class-level and method-level docstrings.
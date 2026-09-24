# Code Review Report

## 1. Readability & Consistency
*   **Formatting:** The indentation and general structure are consistent and follow PEP 8 standards.
*   **Clarity:** The code is easy to follow, though the lack of docstrings for the `MainWindow` class and its methods reduces overall clarity for future maintainers.

## 2. Naming Conventions
*   **Vague Widget Names:** `btn1`, `btn2`, `btn3`, `input1`, and `label1` are non-descriptive. 
    *   *Suggestion:* Rename to `add_text_button`, `show_counter_button`, `reset_button`, `text_input`, and `status_label`.
*   **Vague Method Names:** `handle_btn1` etc. describe the *trigger* rather than the *action*.
    *   *Suggestion:* Rename to `on_add_text_clicked`, `on_show_counter_clicked`, and `on_reset_clicked`.

## 3. Software Engineering Standards
*   **Global State Pollution:** Use of `GLOBAL_TEXT`, `GLOBAL_COUNTER`, and `GLOBAL_MODE` creates tight coupling and makes the code difficult to test and scale.
    *   *Suggestion:* Move these variables into the `MainWindow` class as instance attributes (e.g., `self.text_buffer`, `self.counter`).
*   **Lack of Modularity:** Business logic (calculating parity and counter thresholds) is mixed directly inside UI event handlers.
    *   *Suggestion:* Separate logic into helper methods to improve maintainability.

## 4. Logic & Correctness
*   **Redundant Conditionals:** In `handle_btn2`, the nested `if/else` blocks for `GLOBAL_MODE` and parity are deeply nested.
    *   *Suggestion:* Use guard clauses or a more flattened conditional structure to improve readability.
*   **String Concatenation:** Using `+` for building strings (e.g., `"Added: " + text`) is less efficient and less readable than f-strings in modern Python.

## 5. Performance & Security
*   **Input Validation:** While there is a check for empty strings, there is no upper bound limit on the `input1` text length, which could lead to memory issues if massive amounts of text are appended to `GLOBAL_TEXT`.

## 6. Documentation & Testing
*   **Missing Documentation:** There are no comments explaining the purpose of `GLOBAL_MODE` or the specific behavior of the counter logic.
*   **No Tests:** No unit tests are provided to verify the counter logic or reset functionality.

---

### Summary of Improvement Suggestions
| Component | Issue | Recommended Fix |
| :--- | :--- | :--- |
| **State Management** | Global variables used for app state | Move variables into `MainWindow` class instance. |
| **Naming** | `btn1`, `btn2`, etc. | Use descriptive names (e.g., `reset_button`). |
| **Logic** | Deeply nested `if` in `handle_btn2` | Refactor into a separate logic method or flatten logic. |
| **Syntax** | String concatenation via `+` | Use f-strings for better readability. |
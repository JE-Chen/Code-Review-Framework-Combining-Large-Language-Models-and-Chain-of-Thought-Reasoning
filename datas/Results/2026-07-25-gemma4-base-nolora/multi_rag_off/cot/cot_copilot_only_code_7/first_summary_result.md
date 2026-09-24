This code review is conducted based on the provided global rules.

### 1. Readability & Consistency
*   **Formatting:** The indentation and general structure are consistent.
*   **Clarity:** The code is easy to follow, but the logic within `handle_btn2` is becoming deeply nested, which reduces readability.

### 2. Naming Conventions
*   **Non-Descriptive Names:** The naming of buttons and inputs (`btn1`, `btn2`, `btn3`, `input1`, `label1`) is poor. They should be named based on their function (e.g., `add_text_button`, `status_label`, `text_input`).
*   **Global Variables:** The use of `ALL_CAPS` for `GLOBAL_TEXT`, etc., correctly identifies them as globals, but their existence is a design flaw (see Software Engineering Standards).

### 3. Software Engineering Standards
*   **State Management (Major Issue):** The use of `global` variables inside a class-based GUI application is a significant anti-pattern. These should be instance attributes (e.g., `self.text_accumulator`, `self.counter`) to ensure the application is modular and to avoid side effects if multiple windows were ever instantiated.
*   **Modularity:** The logic for processing the counter and text is tightly coupled with the UI event handlers. This makes the logic impossible to unit test without instantiating the entire GUI.

### 4. Logic & Correctness
*   **String Concatenation:** In `handle_btn1`, `GLOBAL_TEXT` is appended with a pipe `|`. There is no logic to handle the trailing pipe or to trim it, which may lead to formatting issues if that string is used elsewhere.
*   **Boundary Conditions:** The check `if len(text) > 0:` is correct for basic validation, though `.strip()` should be used to prevent users from adding whitespace-only entries.

### 5. Performance & Security
*   **String Accumulation:** Using `+=` for string concatenation in a loop or repeated event handler is inefficient in Python (O(n^2) in some implementations). For a small GUI, this is negligible, but for larger datasets, a list and `"".join()` is preferred.
*   **Input Validation:** There is no limit on the length of the input text, which could lead to memory issues if a user pastes an extremely large string repeatedly.

### 6. Documentation & Testing
*   **Missing Documentation:** There are no docstrings for the `MainWindow` class or its methods.
*   **Lack of Tests:** No unit tests are provided. Because the logic is tied to `PySide6` widgets and global variables, the code is currently "untestable" in a standard CI/CD pipeline.

---

### Summary of Recommendations

| Severity | Issue | Recommendation |
| :--- | :--- | :--- |
| **High** | Global State | Move `GLOBAL_TEXT`, `GLOBAL_COUNTER`, and `GLOBAL_MODE` into `self` as instance variables. |
| **Medium** | Poor Naming | Rename `btn1`, `btn2`, `input1` to descriptive names (e.g., `self.add_button`). |
| **Medium** | Tight Coupling | Extract the logic in `handle_btn2` into a separate method or class to allow for unit testing. |
| **Low** | Input Sanitization | Use `text.strip()` to avoid adding empty whitespace to the global string. |
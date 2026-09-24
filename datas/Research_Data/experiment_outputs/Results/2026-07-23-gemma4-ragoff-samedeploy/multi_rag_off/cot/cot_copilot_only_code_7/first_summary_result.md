This code review is conducted based on the provided global rules.

### 1. Readability & Consistency
- **Formatting:** The indentation and general structure are consistent.
- **Clarity:** The code is easy to follow, but the logic within `handle_btn2` is becoming nested, which reduces readability.

### 2. Naming Conventions
- **Non-Descriptive Names:** Variable and method names are generic and lack semantic meaning.
    - `btn1`, `btn2`, `btn3`, `input1`, `label1` should be renamed to reflect their purpose (e.g., `add_text_button`, `status_label`, `text_input`).
    - `handle_btn1`, `handle_btn2`, `handle_btn3` should be renamed to describe the action (e.g., `on_add_text_clicked`).
- **Global Constants:** `GLOBAL_TEXT`, `GLOBAL_COUNTER`, and `GLOBAL_MODE` use uppercase naming, which usually denotes constants in Python. However, these are being mutated, making them global variables rather than constants.

### 3. Software Engineering Standards
- **State Management (High Concern):** The use of `global` variables (`GLOBAL_TEXT`, `GLOBAL_COUNTER`, `GLOBAL_MODE`) is a significant anti-pattern. This makes the code difficult to test, prevents multiple instances of `MainWindow` from operating independently, and increases the risk of side effects. These should be moved into the `MainWindow` class as instance attributes (e.g., `self.text_accumulator`).
- **Modularity:** The logic for processing the counter and text is tightly coupled with the UI event handlers. This logic should be extracted into separate methods or a controller class to improve testability.

### 4. Logic & Correctness
- **String Concatenation:** In `handle_btn1`, `GLOBAL_TEXT` is appended with a trailing pipe (` | `). There is no logic to handle the trailing separator for the final entry, which may lead to formatting issues if the text is displayed elsewhere.
- **Boundary Conditions:** The check `if len(text) > 0` is correct for basic validation, though `if text.strip():` would be more robust to prevent adding whitespace-only entries.

### 5. Performance & Security
- **String Accumulation:** Using `+=` for string concatenation in a loop or repeated event calls is inefficient in Python for very large strings. While not a bottleneck here, using a list and `"".join()` is the standard for scalable text accumulation.
- **Input Validation:** There is no limit on the length of the input from `QLineEdit`, which could lead to excessive memory usage if a user pastes a massive amount of text.

### 6. Documentation & Testing
- **Missing Documentation:** There are no docstrings for the class or its methods.
- **Lack of Tests:** No unit tests are provided. Because the state is stored in global variables, writing isolated unit tests for the logic would be difficult without resetting the global state between every test case.

---

### Summary of Recommendations
1. **Refactor State:** Move all `GLOBAL_*` variables into the `MainWindow` class as `self` attributes.
2. **Rename Identifiers:** Replace generic names (`btn1`, `handle_btn1`) with descriptive, action-oriented names.
3. **Decouple Logic:** Move the conditional logic in `handle_btn2` into a helper method to reduce nesting and improve readability.
4. **Improve Validation:** Use `.strip()` on input text to avoid empty/whitespace entries.
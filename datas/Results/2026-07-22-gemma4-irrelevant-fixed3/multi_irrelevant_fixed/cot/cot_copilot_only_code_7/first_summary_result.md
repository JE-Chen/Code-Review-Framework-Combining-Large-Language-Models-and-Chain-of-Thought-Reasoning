### Code Review

#### 1. Readability & Consistency
- **Formatting:** The code follows standard Python indentation and formatting.
- **Consistency:** The naming of UI elements (e.g., `btn1`, `btn2`, `input1`) is consistent but lacks semantic meaning.

#### 2. Naming Conventions
- **Poor Descriptive Naming:** Variables like `btn1`, `btn2`, `btn3`, `input1`, and `label1` are non-descriptive. They should be renamed to reflect their purpose (e.g., `add_text_button`, `user_input_field`, `status_label`).
- **Global Constants:** `GLOBAL_TEXT`, `GLOBAL_COUNTER`, and `GLOBAL_MODE` use uppercase, which usually denotes constants in Python, yet they are being mutated throughout the program.

#### 3. Software Engineering Standards
- **Global State Dependency:** The use of `global` variables (`GLOBAL_TEXT`, `GLOBAL_COUNTER`, `GLOBAL_MODE`) is a significant architectural flaw. This makes the code difficult to test, prevents multiple instances of `MainWindow` from operating independently, and increases the risk of side-effect bugs. These should be moved into the `MainWindow` class as instance attributes (e.g., `self.text_accumulator`).
- **Modularization:** The logic for processing the counter and text is tightly coupled with the UI event handlers. Moving the business logic into a separate controller or model class would improve maintainability.

#### 4. Logic & Correctness
- **String Concatenation:** In `handle_btn1`, `GLOBAL_TEXT` is appended to but never actually used or displayed in the UI, making it dead state.
- **Nested Conditionals:** `handle_btn2` contains deeply nested `if/else` blocks. This could be flattened using guard clauses to improve readability.

#### 5. Performance & Security
- **String Building:** Using `+=` for string concatenation in a loop or repeated event handler can be inefficient in Python for very large strings; however, for this specific scale, it is acceptable.
- **Input Validation:** Basic validation is present (`if len(text) > 0`), which prevents empty entries.

#### 6. Documentation & Testing
- **Missing Documentation:** There are no docstrings for the class or its methods.
- **Lack of Tests:** No unit tests are provided to verify the counter logic or the state transitions.

---

### Summary of Recommendations

| Category | Issue | Recommendation |
| :--- | :--- | :--- |
| **Architecture** | Use of `global` variables | Move global state into `MainWindow` as `self` attributes. |
| **Naming** | Generic names (`btn1`, `input1`) | Rename to descriptive names (e.g., `submit_button`). |
| **Logic** | Dead state (`GLOBAL_TEXT`) | Either utilize the accumulated text in the UI or remove it. |
| **Clean Code** | Nested conditionals in `handle_btn2` | Refactor using guard clauses to reduce nesting. |
| **Docs** | No documentation | Add docstrings to explain the purpose of the window and its handlers. |
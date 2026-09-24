This code review is conducted based on the provided global rules.

### 1. Readability & Consistency
- **Formatting:** The code is generally well-formatted and follows standard Python indentation.
- **Consistency:** The use of `self.btn1`, `self.btn2`, etc., is consistent but lacks semantic meaning (see Naming Conventions).

### 2. Naming Conventions
- **Poor Descriptive Naming:** Variables and methods like `btn1`, `btn2`, `btn3`, `input1`, `label1`, `handle_btn1`, etc., are non-descriptive. They should be renamed to reflect their purpose (e.g., `btn_add_text`, `input_text_field`, `handle_add_text`).
- **Global Constants vs. Variables:** `GLOBAL_TEXT`, `GLOBAL_COUNTER`, and `GLOBAL_MODE` are named like constants (UPPER_CASE) but are used as mutable global state. This is misleading.

### 3. Software Engineering Standards
- **Global State Dependency:** The application relies heavily on `global` variables. This makes the code difficult to test, maintain, and scale. These should be encapsulated as attributes of the `MainWindow` class or a separate State/Model class.
- **Lack of Modularity:** The logic for updating the state and updating the UI is tightly coupled within the event handlers.

### 4. Logic & Correctness
- **String Concatenation:** In `handle_btn1`, `GLOBAL_TEXT` is appended with a trailing pipe (` | `). There is no logic to handle the trailing separator for the final entry, which may lead to formatting issues if `GLOBAL_TEXT` is displayed elsewhere.
- **Nested Conditionals:** `handle_btn2` contains deeply nested `if/else` blocks. While logically correct, it reduces readability.

### 5. Performance & Security
- **String Accumulation:** Using `+=` for string concatenation in a loop or repeated event handler can become a performance bottleneck in Python as strings are immutable. For large amounts of text, a list and `.join()` would be more efficient.
- **Input Validation:** While there is a check for `len(text) > 0`, there is no sanitization of the input, though for a simple UI example, this is a low risk.

### 6. Documentation & Testing
- **Missing Documentation:** There are no docstrings for the class or its methods.
- **Missing Tests:** No unit tests are provided to verify the counter logic or the state transitions.

---

### Summary of Recommendations

| Category | Issue | Recommendation |
| :--- | :--- | :--- |
| **Architecture** | Use of `global` variables | Move `GLOBAL_TEXT`, `GLOBAL_COUNTER`, and `GLOBAL_MODE` into the `MainWindow` class as `self.text`, etc. |
| **Naming** | Generic names (`btn1`, `handle_btn1`) | Rename to descriptive names (e.g., `add_button`, `on_add_clicked`). |
| **Clean Code** | Nested logic in `handle_btn2` | Flatten the logic using guard clauses or a mapping. |
| **Documentation** | No docstrings | Add class and method level documentation. |
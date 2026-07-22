### Code Review

**1. Naming Conventions**
* **Vague Naming:** Variables and methods like `btn1`, `btn2`, `btn3`, `input1`, `label1`, `handle_btn1`, etc., are non-descriptive. Rename them to reflect their purpose (e.g., `add_text_button`, `status_label`, `handle_add_text`).

**2. Software Engineering Standards & State Management**
* **Shared Mutable State:** The use of `GLOBAL_TEXT`, `GLOBAL_COUNTER`, and `GLOBAL_MODE` at the module level introduces hidden coupling and makes the code harder to test and maintain. These should be encapsulated as instance attributes within the `MainWindow` class (e.g., `self.text_accumulator`).
* **Hardcoded Logic:** The logic in `handle_btn2` contains nested conditionals that could be simplified or extracted into a helper method to improve readability.

**3. Logic & Correctness**
* **String Concatenation:** `GLOBAL_TEXT` is being appended to, but it is never actually used or displayed in the UI, making it dead state.

**4. Readability & Consistency**
* **String Formatting:** Use f-strings (e.g., `f"Counter small: {self.counter}"`) instead of manual string concatenation for better clarity and performance.

**Suggested Improvements:**
* Move all `GLOBAL_*` variables into `MainWindow.__init__` as `self` attributes.
* Rename UI components to be descriptive (e.g., `self.input1` $\rightarrow$ `self.text_input`).
* Replace `global` keyword usage with instance method access.
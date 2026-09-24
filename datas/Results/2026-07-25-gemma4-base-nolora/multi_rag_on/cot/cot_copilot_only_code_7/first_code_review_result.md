### Code Review

**1. Naming Conventions**
* **Vague Naming:** Variables and methods like `btn1`, `btn2`, `btn3`, `input1`, `label1`, `handle_btn1`, etc., are non-descriptive. Rename them to reflect their purpose (e.g., `btn_add_text`, `input_text`, `handle_add_text`).

**2. Software Engineering Standards & RAG Rules**
* **Shared Mutable State:** The use of `GLOBAL_TEXT`, `GLOBAL_COUNTER`, and `GLOBAL_MODE` violates the rule against shared mutable state at the module level. This introduces hidden coupling and makes the code harder to test.
    * **Suggestion:** Move these variables into the `MainWindow` class as instance attributes (e.g., `self.text_accumulator`, `self.counter`).
* **Hardcoded Strings:** Status messages and labels are hardcoded throughout the logic. For better maintainability, consider defining these as constants.

**3. Logic & Correctness**
* **String Concatenation:** `GLOBAL_TEXT` is being appended to, but it is never actually displayed or used in the UI, making it dead state.
* **Nested Conditionals:** `handle_btn2` contains deeply nested `if/else` blocks. This can be flattened using guard clauses to improve readability.

**4. Readability & Consistency**
* **String Formatting:** The code uses `+` for string concatenation (e.g., `"Added: " + text`). 
    * **Suggestion:** Use f-strings (`f"Added: {text}"`) for better readability and performance.

**Summary of Suggested Improvements:**
* Encapsulate global variables into the `MainWindow` class.
* Rename generic UI elements to descriptive names.
* Replace string concatenation with f-strings.
* Flatten the logic in `handle_btn2`.
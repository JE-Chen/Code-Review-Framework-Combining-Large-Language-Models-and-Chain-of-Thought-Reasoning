### Code Review

**Naming Conventions**
* **Vague Widget Names:** `btn1`, `btn2`, `btn3`, `input1`, and `label1` are non-descriptive. Rename them to reflect their purpose (e.g., `add_text_button`, `status_label`, `text_input`).
* **Vague Handler Names:** `handle_btn1`, `handle_btn2`, and `handle_btn3` should be renamed to describe the action they perform (e.g., `handle_add_text`, `handle_show_counter`).

**Software Engineering Standards**
* **Global State:** The use of `GLOBAL_TEXT`, `GLOBAL_COUNTER`, and `GLOBAL_MODE` creates tight coupling and makes the code harder to test and maintain. These should be instance attributes of the `MainWindow` class (e.g., `self.text_accumulator`).
* **Hardcoded Strings:** Status messages and labels are hardcoded throughout the logic; consider moving these to constants if the application grows.

**Logic & Correctness**
* **Nested Conditionals:** `handle_btn2` contains deeply nested `if/else` blocks. This can be flattened using guard clauses to improve readability.

**Performance & Security**
* **String Concatenation:** Using `GLOBAL_TEXT += text + " | "` in a loop or frequent updates is inefficient in Python. While negligible here, using a list and `"".join()` is the standard for larger datasets.

**Suggestions for Improvement**
* Move global variables into the `MainWindow.__init__` method as `self` attributes.
* Rename UI components to be semantically meaningful.
* Refactor `handle_btn2` to reduce nesting.
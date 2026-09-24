### Code Review

**Naming Conventions**
* **Vague Widget Naming:** `btn1`, `btn2`, `btn3`, `input1`, and `label1` are non-descriptive. Rename them to reflect their purpose (e.g., `add_text_button`, `status_label`, `text_input`).
* **Vague Handler Naming:** `handle_btn1`, `handle_btn2`, and `handle_btn3` should be renamed to describe the action they perform (e.g., `handle_add_text`, `handle_show_counter`).

**Software Engineering Standards**
* **Global State Dependency:** The use of `GLOBAL_TEXT`, `GLOBAL_COUNTER`, and `GLOBAL_MODE` creates tight coupling and makes the code harder to test and maintain. These should be moved into the `MainWindow` class as instance attributes (e.g., `self.text_buffer`).
* **Deep Nesting:** `handle_btn2` contains nested `if/else` blocks that reduce readability. Consider using guard clauses to flatten the logic.

**Logic & Correctness**
* **String Concatenation:** `GLOBAL_TEXT` is updated via concatenation in a loop-like fashion (`+=`). While acceptable for small apps, using a list and `"".join()` is the standard for better performance in Python.

**Readability & Consistency**
* **Hardcoded Strings:** Status messages and labels are hardcoded throughout the logic. Moving these to constants or a configuration dictionary would improve maintainability.

**Suggestions for Improvement**
* **Encapsulation:** Move all `GLOBAL_*` variables into `__init__` as `self.counter`, `self.text`, etc., to remove the need for the `global` keyword.
* **Refactor Logic:** Simplify `handle_btn2` by handling the `GLOBAL_COUNTER <= 5` case first and returning early.
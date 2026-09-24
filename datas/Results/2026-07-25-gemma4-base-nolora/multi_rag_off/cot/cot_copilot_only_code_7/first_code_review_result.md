### Code Review

**Naming Conventions**
* **Vague Widget Naming:** `btn1`, `btn2`, `btn3`, `input1`, and `label1` are non-descriptive. Rename them to reflect their purpose (e.g., `add_text_button`, `counter_button`, `reset_button`, `text_input`, `status_label`).
* **Vague Handler Naming:** `handle_btn1`, `handle_btn2`, and `handle_btn3` should be renamed to describe the action they perform (e.g., `handle_add_text`, `handle_show_counter`, `handle_reset`).

**Software Engineering Standards**
* **Global State Dependency:** The use of `GLOBAL_TEXT`, `GLOBAL_COUNTER`, and `GLOBAL_MODE` creates tight coupling and makes the code difficult to test or scale. These should be moved into the `MainWindow` class as instance attributes (e.g., `self.text_accumulator`, `self.counter`).
* **Deep Nesting:** `handle_btn2` contains nested `if/else` blocks that reduce readability. This can be flattened using guard clauses or a more streamlined logic flow.

**Logic & Correctness**
* **String Concatenation:** `GLOBAL_TEXT` is being appended to, but it is never actually displayed or used in the UI, making it dead logic.

**Readability & Consistency**
* **String Formatting:** The code uses manual string concatenation (e.g., `"Added: " + text`). Using f-strings (e.g., `f"Added: {text}"`) is the modern Python standard and improves readability.

**Suggestions for Improvement**
* **Encapsulation:** Move all `GLOBAL_` variables into the `MainWindow.__init__` method as `self.` variables to eliminate the need for the `global` keyword.
* **Refactor Logic:** Simplify `handle_btn2` by handling the "small counter" case first as a guard clause to reduce indentation levels.
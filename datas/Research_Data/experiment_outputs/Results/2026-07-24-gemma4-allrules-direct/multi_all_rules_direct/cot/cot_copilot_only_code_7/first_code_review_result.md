### Code Review

**Naming Conventions**
* **Vague Naming:** Variables and methods like `btn1`, `btn2`, `btn3`, `input1`, `label1`, `handle_btn1`, etc., are non-descriptive. Use names that reflect their purpose (e.g., `add_text_button`, `status_label`, `handle_add_text`).

**Software Engineering Standards & RAG Rules**
* **Shared Mutable State:** The use of `GLOBAL_TEXT`, `GLOBAL_COUNTER`, and `GLOBAL_MODE` introduces hidden coupling and makes the code harder to test. These should be encapsulated as instance attributes within the `MainWindow` class.
* **Deeply Nested Logic:** `handle_btn2` contains deeply nested `if/else` blocks. This increases cognitive load and should be refactored using guard clauses or a separate logic function.
* **Implicit Truthiness:** In `handle_btn1`, `if len(text) > 0:` is used. While correct, explicit checks or utilizing Python's truthiness for strings is standard, but the logic here is simple enough; however, the overall structure of the method mixes UI updates with state management.

**Logic & Correctness**
* **String Concatenation:** `GLOBAL_TEXT` is being appended to using `+=` in a loop-like fashion (via button clicks). While acceptable for small scales, using a list and `"".join()` is generally preferred for building large strings.

**Suggestions for Improvement**
* **Encapsulate State:** Move all `GLOBAL_*` variables into `self` (e.g., `self.text_accumulator = ""`).
* **Refactor Conditionals:** Simplify `handle_btn2` by returning early or splitting the "default" vs "reset" mode logic into distinct methods.
* **Rename UI Elements:** Rename widgets to reflect their function (e.g., `self.input1` $\rightarrow$ `self.text_input`).
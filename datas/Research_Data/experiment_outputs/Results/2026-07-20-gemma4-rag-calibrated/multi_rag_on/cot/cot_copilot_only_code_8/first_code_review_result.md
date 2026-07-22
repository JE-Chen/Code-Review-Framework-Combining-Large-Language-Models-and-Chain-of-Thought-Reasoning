### Code Review

**Naming Conventions**
* **Vague Naming:** `btnA`, `btnB`, and `labelX` are non-descriptive. Rename them to reflect their purpose (e.g., `btn_calculate_length`, `btn_check_size`, `status_label`).
* **Inconsistent Naming:** `textArea` uses camelCase, while `handle_btnA` uses snake_case. Use snake_case consistently for all attributes and methods per PEP 8.

**Logic & Correctness**
* **Deep Nesting:** `handle_btnB` contains deeply nested `if/else` blocks. This reduces readability and maintainability.

**Software Engineering Standards**
* **Redundant Logic:** Both `handle_btnA` and `handle_btnB` call `self.textArea.toPlainText()`. This could be abstracted into a helper method or property.

**Improvement Suggestions**
* **Refactor `handle_btnB`:** Use `elif` statements instead of nested `if/else` to flatten the logic.
* **String Formatting:** Use f-strings (e.g., `f"Length: {len(text)}"`) instead of string concatenation for better readability.
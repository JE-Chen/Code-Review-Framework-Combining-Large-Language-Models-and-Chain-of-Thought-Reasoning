### Code Review

**Naming Conventions**
* **Vague Naming**: Variables `btnA`, `btnB`, and `labelX` are non-descriptive. Rename them to reflect their purpose (e.g., `btn_calculate_length`, `btn_check_size`, `status_label`).

**Logic & Correctness**
* **Deep Nesting**: `handle_btnB` uses deeply nested `if/else` blocks. This reduces readability and maintainability. Use `elif` statements to flatten the logic.

**Software Engineering Standards**
* **String Concatenation**: In `handle_btnA`, the use of `+ str(len(text))` is outdated. Use f-strings (e.g., `f"Length: {len(text)}"`) for better readability and performance.

**Suggested Improvements**
* **Refactor `handle_btnB`**:
  ```python
  def handle_btnB(self):
      text = self.textArea.toPlainText()
      length = len(text)
      if not text:
          self.labelX.setText("No Input")
      elif length < 5:
          self.labelX.setText("Short")
      elif length < 10:
          self.labelX.setText("Medium")
      elif length < 20:
          self.labelX.setText("Long")
      else:
          self.labelX.setText("Very Long")
  ```
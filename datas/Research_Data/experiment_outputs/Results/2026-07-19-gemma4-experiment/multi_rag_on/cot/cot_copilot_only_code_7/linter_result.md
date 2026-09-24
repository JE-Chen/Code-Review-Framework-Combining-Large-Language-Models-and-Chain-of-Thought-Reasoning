```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable names 'btn1', 'btn2', 'btn3', 'input1', and 'label1' are not descriptive.",
    "line": 13,
    "suggestion": "Rename to descriptive names like 'add_text_button', 'show_counter_button', 'reset_button', 'text_input', and 'status_label'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Method names 'handle_btn1', 'handle_btn2', and 'handle_btn3' are not descriptive.",
    "line": 30,
    "suggestion": "Rename to 'handle_add_text', 'handle_show_counter', and 'handle_reset'."
  },
  {
    "rule_id": "software-engineering-standard",
    "severity": "error",
    "message": "Use of global variables (GLOBAL_TEXT, GLOBAL_COUNTER, GLOBAL_MODE) creates tight coupling and makes the code harder to test and maintain.",
    "line": 4,
    "suggestion": "Encapsulate these variables as instance attributes within the MainWindow class (e.g., self.text, self.counter)."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "info",
    "message": "The check 'if len(text) > 0' is redundant in Python.",
    "line": 33,
    "suggestion": "Use 'if text:' to check for non-empty strings."
  },
  {
    "rule_id": "software-engineering-standard",
    "severity": "warning",
    "message": "Deeply nested conditional logic in handle_btn2 reduces readability.",
    "line": 42,
    "suggestion": "Refactor using guard clauses or a separate helper method to determine the counter message."
  }
]
```
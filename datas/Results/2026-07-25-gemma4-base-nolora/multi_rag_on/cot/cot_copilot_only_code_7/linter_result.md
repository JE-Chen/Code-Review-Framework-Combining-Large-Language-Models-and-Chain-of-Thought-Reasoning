```json
[
  {
    "rule_id": "shared-mutable-state",
    "severity": "error",
    "message": "Use of global mutable state (GLOBAL_TEXT, GLOBAL_COUNTER, GLOBAL_MODE) introduces hidden coupling and makes the code difficult to test and reason about.",
    "line": 4,
    "suggestion": "Encapsulate these variables as instance attributes within the MainWindow class (e.g., self.text, self.counter)."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable names 'btn1', 'btn2', 'btn3', 'input1', and 'label1' are not descriptive.",
    "line": 13,
    "suggestion": "Use meaningful names such as 'add_text_button', 'show_counter_button', 'reset_button', 'text_input', and 'status_label'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Method names 'handle_btn1', 'handle_btn2', and 'handle_btn3' are not descriptive of their actual functionality.",
    "line": 30,
    "suggestion": "Rename to 'handle_add_text', 'handle_show_counter', and 'handle_reset'."
  },
  {
    "rule_id": "logic-simplification",
    "severity": "info",
    "message": "The check 'if len(text) > 0' can be simplified in Python.",
    "line": 33,
    "suggestion": "Use 'if text:' to check for non-empty strings."
  }
]
```
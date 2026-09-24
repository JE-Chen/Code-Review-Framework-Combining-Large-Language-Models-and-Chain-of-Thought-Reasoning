```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable names 'btn1', 'btn2', 'btn3', 'input1', and 'label1' are not descriptive.",
    "line": 14,
    "suggestion": "Rename variables to reflect their purpose (e.g., 'add_text_button', 'status_label')."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Method names 'handle_btn1', 'handle_btn2', and 'handle_btn3' are not descriptive.",
    "line": 31,
    "suggestion": "Rename methods to reflect the action they perform (e.g., 'handle_add_text')."
  },
  {
    "rule_id": "software-engineering-standards",
    "severity": "error",
    "message": "Use of global variables (GLOBAL_TEXT, GLOBAL_COUNTER, GLOBAL_MODE) creates tight coupling and makes the code harder to test and maintain.",
    "line": 32,
    "suggestion": "Encapsulate these variables as instance attributes within the MainWindow class."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "info",
    "message": "Checking 'len(text) > 0' is less idiomatic in Python than checking the truthiness of the string.",
    "line": 34,
    "suggestion": "Use 'if text:' instead of 'if len(text) > 0:'."
  },
  {
    "rule_id": "software-engineering-standards",
    "severity": "warning",
    "message": "Deeply nested conditional logic in 'handle_btn2' reduces readability.",
    "line": 43,
    "suggestion": "Refactor using guard clauses or a separate helper method to flatten the logic."
  }
]
```
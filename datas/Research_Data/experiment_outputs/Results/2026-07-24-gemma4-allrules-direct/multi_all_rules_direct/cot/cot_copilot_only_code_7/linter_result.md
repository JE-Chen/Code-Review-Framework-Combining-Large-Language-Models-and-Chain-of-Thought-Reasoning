```json
[
  {
    "rule_id": "shared-mutable-state",
    "severity": "error",
    "message": "Use of global mutable state (GLOBAL_TEXT, GLOBAL_COUNTER, GLOBAL_MODE) introduces hidden coupling and makes the code harder to test and reason about.",
    "line": 4,
    "suggestion": "Encapsulate these variables as attributes within the MainWindow class or a separate state management object."
  },
  {
    "rule_id": "naming-conventions",
    "severity": "warning",
    "message": "Variable names 'btn1', 'btn2', 'btn3', 'input1', and 'label1' are not descriptive and do not reflect their purpose.",
    "line": 13,
    "suggestion": "Rename to descriptive names like 'add_text_button', 'show_counter_button', 'user_input_field', etc."
  },
  {
    "rule_id": "implicit-truthiness",
    "severity": "info",
    "message": "Using 'len(text) > 0' is an explicit check, but the logic relies on the length of the string. While not a bug, ensure consistency in how empty strings are handled.",
    "line": 33,
    "suggestion": "Consider 'if text:' for idiomatic Python, or keep as is if explicit length is required."
  },
  {
    "rule_id": "deeply-nested-conditionals",
    "severity": "warning",
    "message": "Deeply nested conditional logic in 'handle_btn2' increases cognitive load.",
    "line": 42,
    "suggestion": "Refactor using guard clauses (e.g., 'if GLOBAL_COUNTER <= 5: return') to flatten the structure."
  },
  {
    "rule_id": "single-responsibility",
    "severity": "info",
    "message": "The 'handle_btn' methods are mixing business logic (state mutation) with UI updates.",
    "line": 31,
    "suggestion": "Separate the state update logic into a different method and call it from the event handler."
  }
]
```
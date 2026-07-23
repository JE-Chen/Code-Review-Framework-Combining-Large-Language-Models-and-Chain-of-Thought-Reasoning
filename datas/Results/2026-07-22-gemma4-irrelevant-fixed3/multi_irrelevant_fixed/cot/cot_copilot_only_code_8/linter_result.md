```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable names 'btnA', 'btnB', and 'labelX' are not descriptive. They should reflect the purpose of the widget.",
    "line": 13,
    "suggestion": "Rename to more descriptive names, e.g., 'submit_button', 'clear_button', 'status_label'."
  },
  {
    "rule_id": "software-engineering-standards",
    "severity": "info",
    "message": "The logic in 'handle_btnB' uses deeply nested if-else statements, which reduces readability.",
    "line": 38,
    "suggestion": "Refactor using 'elif' statements to flatten the logic."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "info",
    "message": "The check 'if len(text) > 0' is redundant in Python; empty strings are falsy.",
    "line": 31,
    "suggestion": "Use 'if text:' instead."
  }
]
```
```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable names 'btnA', 'btnB', and 'labelX' are not descriptive. They describe the type or a generic identifier rather than the purpose of the widget.",
    "line": 14,
    "suggestion": "Rename to descriptive names like 'submit_button', 'clear_button', and 'status_label'."
  },
  {
    "rule_id": "software-engineering-standard",
    "severity": "info",
    "message": "The logic in 'handle_btnB' uses deeply nested if-else statements, which reduces readability.",
    "line": 38,
    "suggestion": "Refactor using 'elif' statements to flatten the logic."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "info",
    "message": "The check 'if len(text) > 0' is redundant in Python; empty strings are falsy.",
    "line": 32,
    "suggestion": "Use 'if text:' for consistency and conciseness."
  }
]
```
```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable names 'btnA', 'btnB', and 'labelX' are not descriptive. They should reflect the purpose of the widget.",
    "line": 14,
    "suggestion": "Rename to more descriptive names, e.g., 'submit_button', 'clear_button', 'status_label'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable name 'textArea' uses camelCase, which is inconsistent with Python's PEP 8 snake_case convention.",
    "line": 16,
    "suggestion": "Rename 'textArea' to 'text_area'."
  },
  {
    "rule_id": "software-engineering-standard",
    "severity": "info",
    "message": "The logic in 'handle_btnB' uses deeply nested if-else statements, which reduces readability.",
    "line": 38,
    "suggestion": "Refactor using an elif chain or a mapping/lookup table for length thresholds."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "info",
    "message": "The check 'if len(text) > 0' is redundant in Python; empty strings are falsy.",
    "line": 32,
    "suggestion": "Use 'if text:' instead of 'if len(text) > 0:'."
  }
]
```
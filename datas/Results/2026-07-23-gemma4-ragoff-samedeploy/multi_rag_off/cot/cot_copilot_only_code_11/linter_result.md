```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 's' is not descriptive.",
    "line": 23,
    "suggestion": "Rename 's' to 'score'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 's' is not descriptive.",
    "line": 31,
    "suggestion": "Rename 's' to 'score'."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "error",
    "message": "Potential ZeroDivisionError if 'scores' list is empty.",
    "line": 25,
    "suggestion": "Add a check to ensure len(scores) > 0 before division."
  },
  {
    "rule_id": "software-engineering-standards",
    "severity": "info",
    "message": "Manual summation loop used instead of built-in sum().",
    "line": 23,
    "suggestion": "Use 'total = sum(scores)' to improve readability and performance."
  },
  {
    "rule_id": "readability-consistency",
    "severity": "info",
    "message": "Deeply nested if-else structure reduces readability.",
    "line": 61,
    "suggestion": "Use elif or guard clauses to flatten the logic."
  }
]
```
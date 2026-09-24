```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 's' is not descriptive. Use a more meaningful name like 'score'.",
    "line": 22,
    "suggestion": "Rename 's' to 'score'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 's' is not descriptive. Use a more meaningful name like 'score'.",
    "line": 30,
    "suggestion": "Rename 's' to 'score'."
  },
  {
    "rule_id": "software-engineering-standard",
    "severity": "info",
    "message": "Manual summation loop used instead of built-in sum() function.",
    "line": 21,
    "suggestion": "Replace the for loop with 'total = sum(scores)'."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "error",
    "message": "Potential ZeroDivisionError if 'scores' list is empty.",
    "line": 24,
    "suggestion": "Add a check to ensure len(scores) > 0 before division."
  },
  {
    "rule_id": "readability-consistency",
    "severity": "info",
    "message": "Deeply nested if-else structure reduces readability.",
    "line": 61,
    "suggestion": "Flatten the logic using guard clauses or a more structured mapping."
  }
]
```
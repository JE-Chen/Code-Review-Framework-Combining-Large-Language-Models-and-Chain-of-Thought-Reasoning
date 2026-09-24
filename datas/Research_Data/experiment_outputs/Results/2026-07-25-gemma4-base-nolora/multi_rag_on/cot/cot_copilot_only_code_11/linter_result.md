```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 's' is not descriptive.",
    "line": 22,
    "suggestion": "Rename 's' to 'score'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 's' is not descriptive.",
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
    "line": 23,
    "suggestion": "Add a check to ensure len(scores) > 0 before division."
  },
  {
    "rule_id": "software-engineering-standard",
    "severity": "info",
    "message": "Deeply nested conditional logic reduces readability.",
    "line": 61,
    "suggestion": "Flatten the nested if-else structure using elif or a mapping strategy."
  }
]
```
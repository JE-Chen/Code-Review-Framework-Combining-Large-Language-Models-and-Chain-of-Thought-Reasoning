```json
[
  {
    "rule_id": "performance-string-concatenation",
    "severity": "warning",
    "message": "Repeated string concatenation using '+=' in a loop is inefficient in Python.",
    "line": 11,
    "suggestion": "Collect characters in a list and use ''.join(list) at the end."
  },
  {
    "rule_id": "cognitive-complexity",
    "severity": "warning",
    "message": "Deeply nested conditional blocks (4 levels) reduce readability and maintainability.",
    "line": 52,
    "suggestion": "Use guard clauses or combine conditions to flatten the logic."
  }
]
```
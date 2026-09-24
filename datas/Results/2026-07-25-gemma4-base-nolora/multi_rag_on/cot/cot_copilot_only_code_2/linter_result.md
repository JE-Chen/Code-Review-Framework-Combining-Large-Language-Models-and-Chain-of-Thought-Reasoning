```json
[
  {
    "rule_id": "performance-string-concatenation",
    "severity": "warning",
    "message": "Inefficient string concatenation inside a loop. In Python, repeated use of '+=' on strings creates new objects, leading to O(n^2) complexity.",
    "line": 12,
    "suggestion": "Collect characters in a list and use ''.join(list) at the end."
  },
  {
    "rule_id": "cognitive-complexity",
    "severity": "info",
    "message": "Deeply nested conditional blocks (4 levels) reduce readability and maintainability.",
    "line": 54,
    "suggestion": "Use guard clauses (early returns/continues) to flatten the logic."
  }
]
```
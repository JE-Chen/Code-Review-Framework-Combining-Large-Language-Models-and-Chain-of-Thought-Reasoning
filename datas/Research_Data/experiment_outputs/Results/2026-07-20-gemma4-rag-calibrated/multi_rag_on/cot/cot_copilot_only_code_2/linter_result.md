```json
[
  {
    "rule_id": "performance-string-concatenation",
    "severity": "warning",
    "message": "Repeated string concatenation using '+=' in a loop is inefficient in Python as it creates new string objects.",
    "line": 11,
    "suggestion": "Collect characters in a list and use ''.join(result_list) at the end."
  },
  {
    "rule_id": "cognitive-complexity",
    "severity": "info",
    "message": "Deeply nested if-statements reduce readability and maintainability.",
    "line": 53,
    "suggestion": "Use guard clauses or combine conditions to flatten the logic."
  }
]
```
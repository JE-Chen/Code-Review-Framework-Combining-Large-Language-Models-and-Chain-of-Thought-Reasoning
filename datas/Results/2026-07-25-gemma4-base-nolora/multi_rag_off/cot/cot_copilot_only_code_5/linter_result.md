```json
[
  {
    "rule_id": "no-global-state",
    "severity": "warning",
    "message": "Use of a global mutable dictionary (GLOBAL_STATE) for state management can lead to side effects and makes the code harder to test and maintain.",
    "line": 1,
    "suggestion": "Encapsulate the state within a class or pass state as an argument to functions."
  },
  {
    "rule_id": "complexity-nested-if",
    "severity": "info",
    "message": "Deeply nested if-else blocks in process_items reduce readability.",
    "line": 26,
    "suggestion": "Consider using a helper function or a mapping strategy to handle the item processing logic."
  }
]
```
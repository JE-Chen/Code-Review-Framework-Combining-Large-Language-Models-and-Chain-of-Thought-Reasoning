```json
[
  {
    "rule_id": "no-global-state",
    "severity": "warning",
    "message": "Use of a global mutable dictionary (GLOBAL_STATE) for state management can lead to side effects and makes the code harder to test and maintain.",
    "line": 1,
    "suggestion": "Encapsulate the state within a class or pass state as an argument to functions."
  }
]
```
```json
[
  {
    "rule_id": "no-global-mutable-state",
    "severity": "warning",
    "message": "Use of a global mutable dictionary (GLOBAL_STATE) can lead to side effects and makes the code harder to test and maintain.",
    "line": 1,
    "suggestion": "Encapsulate the state within a class or pass the state as an argument to functions."
  },
  {
    "rule_id": "naming-convention",
    "severity": "info",
    "message": "GLOBAL_STATE uses SCREAMING_SNAKE_CASE, which is typically reserved for constants, but this object is mutated throughout the program.",
    "line": 1,
    "suggestion": "Rename to lowercase if it is intended to be a mutable variable, or treat it as a constant and avoid mutation."
  }
]
```
```json
[
  {
    "rule_id": "avoid-global-state",
    "severity": "warning",
    "message": "The use of a global dictionary 'GLOBAL_STATE' for application state makes the code harder to test, maintain, and is not thread-safe.",
    "line": 1,
    "suggestion": "Encapsulate the state within a class or pass state objects as arguments to functions."
  },
  {
    "rule_id": "naming-convention",
    "severity": "info",
    "message": "Variable 'GLOBAL_STATE' uses SCREAMING_SNAKE_CASE, which is typically reserved for constants, but it is being mutated throughout the program.",
    "line": 1,
    "suggestion": "Rename to 'global_state' or move to a state management object."
  }
]
```
```json
[
  {
    "rule_id": "shared-mutable-state",
    "severity": "error",
    "message": "Use of a global mutable dictionary 'GLOBAL_STATE' introduces hidden coupling and makes the code difficult to test and reason about.",
    "line": 1,
    "suggestion": "Encapsulate state within a class or pass state explicitly as arguments to functions."
  },
  {
    "rule_id": "magic-number",
    "severity": "warning",
    "message": "Hard-coded constant '77' used for threshold without a descriptive name.",
    "line": 5,
    "suggestion": "Define a named constant (e.g., DEFAULT_THRESHOLD = 77) at the top of the module."
  },
  {
    "rule_id": "deeply-nested-logic",
    "severity": "warning",
    "message": "Deeply nested conditional logic in 'process_items' increases cognitive load.",
    "line": 24,
    "suggestion": "Refactor the inner logic into a separate function or use guard clauses to flatten the structure."
  }
]
```
```json
[
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "Use of global mutable state (DATA_STORE, USER_COUNT) can introduce hidden coupling and make the application difficult to test and scale.",
    "line": 5,
    "suggestion": "Encapsulate state within a database or a dedicated state management class."
  },
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "Use of global mutable state (USER_COUNT) via the 'global' keyword.",
    "line": 14,
    "suggestion": "Pass state explicitly or use a thread-safe counter/database."
  },
  {
    "rule_id": "deeply-nested-logic",
    "severity": "warning",
    "message": "Deeply nested conditional logic increases cognitive load and reduces readability.",
    "line": 26,
    "suggestion": "Refactor the logic into smaller functions or use guard clauses to flatten the structure."
  },
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "Use of global mutable state (DATA_STORE, USER_COUNT) via the 'global' keyword.",
    "line": 36,
    "suggestion": "Encapsulate state management in a separate service or repository layer."
  },
  {
    "rule_id": "deeply-nested-logic",
    "severity": "error",
    "message": "Excessively deep nesting of conditional statements (4+ levels).",
    "line": 43,
    "suggestion": "Use guard clauses (e.g., 'if not param: return ...') to reduce nesting levels."
  },
  {
    "rule_id": "single-responsibility",
    "severity": "info",
    "message": "The 'complex_route' function handles input validation, business logic, and response generation in one block.",
    "line": 41,
    "suggestion": "Split the parameter validation and the value-checking logic into separate functions."
  }
]
```
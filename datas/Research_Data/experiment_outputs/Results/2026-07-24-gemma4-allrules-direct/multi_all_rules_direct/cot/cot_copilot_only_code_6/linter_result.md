```json
[
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "Use of global mutable state (DATA_STORE, USER_COUNT) can introduce hidden coupling and make the application difficult to test or scale.",
    "line": 5,
    "suggestion": "Encapsulate state in a database or a dedicated state management object."
  },
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "Use of global mutable state (USER_COUNT) can introduce hidden coupling.",
    "line": 6,
    "suggestion": "Encapsulate state in a database or a dedicated state management object."
  },
  {
    "rule_id": "broad-exception",
    "severity": "error",
    "message": "Catching a broad exception (Exception) can hide unexpected bugs and make debugging difficult.",
    "line": 18,
    "suggestion": "Catch specific exceptions, such as TypeError or AttributeError, depending on the expected failure."
  },
  {
    "rule_id": "unnecessary-work-in-loop",
    "severity": "info",
    "message": "The check 'CONFIG[\"mode\"] == \"test\"' is invariant inside the loop and is evaluated on every iteration.",
    "line": 26,
    "suggestion": "Move the conditional check outside the loop to improve performance."
  },
  {
    "rule_id": "deeply-nested-logic",
    "severity": "warning",
    "message": "Deeply nested conditional logic increases cognitive load and reduces readability.",
    "line": 44,
    "suggestion": "Refactor using guard clauses or split the logic into smaller helper functions."
  },
  {
    "rule_id": "implicit-truthiness",
    "severity": "info",
    "message": "Relying on implicit truthiness for 'param' can be ambiguous.",
    "line": 45,
    "suggestion": "Use an explicit comparison such as 'if param != \"\":'."
  }
]
```
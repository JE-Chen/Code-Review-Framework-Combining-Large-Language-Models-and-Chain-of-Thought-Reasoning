```json
[
  {
    "rule_id": "no-global-mutable-state",
    "severity": "error",
    "message": "Usage of global mutable state (GLOBAL_DATA_THING, GLOBAL_FLAG) introduces hidden coupling and makes testing and reasoning about behavior difficult.",
    "line": 23,
    "suggestion": "Pass state explicitly through parameters or encapsulate it in a dedicated class."
  },
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Variable 'MAGIC_NUMBER' is defined but not used beyond its declaration.",
    "line": 24,
    "suggestion": "Remove unused constant or use it to improve clarity."
  },
  {
    "rule_id": "no-implicit-exception-handling",
    "severity": "error",
    "message": "Catch-all exception handlers (empty `except:` clauses) mask unexpected errors and hinder debugging.",
    "line": 52,
    "suggestion": "Catch specific exceptions or re-raise after logging."
  },
  {
    "rule_id": "no-implicit-exception-handling",
    "severity": "error",
    "message": "Catch-all exception handlers (empty `except:` clauses) mask unexpected errors and hinder debugging.",
    "line": 72,
    "suggestion": "Catch specific exceptions or re-raise after logging."
  },
  {
    "rule_id": "no-implicit-exception-handling",
    "severity": "error",
    "message": "Catch-all exception handlers (empty `except:` clauses) mask unexpected errors and hinder debugging.",
    "line": 77,
    "suggestion": "Catch specific exceptions or re-raise after logging."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic numbers like 0.0001 and 0.7 should be named constants for readability and maintainability.",
    "line": 84,
    "suggestion": "Define named constants for magic numbers."
  },
  {
    "rule_id": "no-unexpected-side-effects",
    "severity": "warning",
    "message": "Functions modify global flags and variables without explicit contract, increasing risk of unintended side effects.",
    "line": 52,
    "suggestion": "Minimize reliance on global state and make side effects explicit."
  }
]
```
```json
[
  {
    "rule_id": "global-variable-usage",
    "severity": "warning",
    "message": "Use of global variables reduces modularity and testability.",
    "line": 7,
    "suggestion": "Pass dependencies as parameters or use a class-based structure."
  },
  {
    "rule_id": "magic-number",
    "severity": "warning",
    "message": "Magic numbers used without explanation.",
    "line": 13,
    "suggestion": "Replace magic numbers with named constants."
  },
  {
    "rule_id": "duplicate-computation",
    "severity": "error",
    "message": "Redundant computation of median value.",
    "line": 26,
    "suggestion": "Store computed median once and reuse it."
  },
  {
    "rule_id": "inconsistent-naming",
    "severity": "warning",
    "message": "Variable naming is inconsistent (snake_case vs camelCase).",
    "line": 10,
    "suggestion": "Adhere to snake_case naming convention throughout."
  },
  {
    "rule_id": "function-side-effects",
    "severity": "warning",
    "message": "Functions have side effects on global state.",
    "line": 18,
    "suggestion": "Avoid modifying global state; return values instead."
  },
  {
    "rule_id": "lack-of-documentation",
    "severity": "info",
    "message": "Missing docstrings for functions.",
    "line": 10,
    "suggestion": "Add docstrings explaining purpose and behavior of each function."
  },
  {
    "rule_id": "no-input-validation",
    "severity": "warning",
    "message": "No validation of user inputs or data integrity.",
    "line": 22,
    "suggestion": "Validate data before processing to avoid unexpected errors."
  }
]
```
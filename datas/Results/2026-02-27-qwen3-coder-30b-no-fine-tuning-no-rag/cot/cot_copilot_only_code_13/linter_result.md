```json
[
  {
    "rule_id": "global-variables",
    "severity": "warning",
    "message": "Usage of global variables reduces modularity and testability.",
    "line": 6,
    "suggestion": "Pass state as parameters or use a game state object."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic numbers like 7 for enemy count should be replaced with named constants.",
    "line": 16,
    "suggestion": "Define ENEMY_COUNT as a constant."
  },
  {
    "rule_id": "no-duplicate-code",
    "severity": "warning",
    "message": "Collision detection logic is duplicated in multiple places; consider encapsulating.",
    "line": 35,
    "suggestion": "Extract collision detection into a helper function."
  },
  {
    "rule_id": "inconsistent-naming",
    "severity": "warning",
    "message": "Variable naming is inconsistent; some use snake_case, others camelCase.",
    "line": 16,
    "suggestion": "Use consistent snake_case for all variable names."
  },
  {
    "rule_id": "no-inline-styles",
    "severity": "info",
    "message": "Hardcoded color values make it difficult to adjust theme or styling later.",
    "line": 29,
    "suggestion": "Define colors as constants at the top of the file."
  },
  {
    "rule_id": "no-implicit-returns",
    "severity": "warning",
    "message": "Functions do not explicitly return values when they could.",
    "line": 11,
    "suggestion": "Add explicit returns where appropriate for clarity."
  }
]
```
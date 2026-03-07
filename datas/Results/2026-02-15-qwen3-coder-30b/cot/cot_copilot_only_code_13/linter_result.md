```json
[
  {
    "rule_id": "global-variables",
    "severity": "warning",
    "message": "Use of global variables reduces modularity and testability.",
    "line": 6,
    "suggestion": "Pass state as parameters or use a game state object."
  },
  {
    "rule_id": "magic-numbers",
    "severity": "warning",
    "message": "Magic numbers used for screen dimensions and sizes.",
    "line": 11,
    "suggestion": "Define constants with descriptive names for WIDTH, HEIGHT, etc."
  },
  {
    "rule_id": "inconsistent-naming",
    "severity": "warning",
    "message": "Variable naming inconsistency between snake_case and camelCase.",
    "line": 12,
    "suggestion": "Consistently use snake_case for variable names."
  },
  {
    "rule_id": "tight-coupling",
    "severity": "warning",
    "message": "Functions directly manipulate global state without encapsulation.",
    "line": 21,
    "suggestion": "Encapsulate game state in a class and pass references explicitly."
  },
  {
    "rule_id": "imperative-style",
    "severity": "warning",
    "message": "Imperative style makes code harder to reason about and extend.",
    "line": 27,
    "suggestion": "Consider functional or object-oriented patterns to improve clarity."
  },
  {
    "rule_id": "hardcoded-values",
    "severity": "warning",
    "message": "Hardcoded color values and positions reduce flexibility.",
    "line": 34,
    "suggestion": "Move magic values into configuration or constants."
  },
  {
    "rule_id": "lack-of-documentation",
    "severity": "info",
    "message": "No docstrings or inline comments explaining functionality.",
    "line": 16,
    "suggestion": "Add docstrings to functions describing their behavior and parameters."
  }
]
```
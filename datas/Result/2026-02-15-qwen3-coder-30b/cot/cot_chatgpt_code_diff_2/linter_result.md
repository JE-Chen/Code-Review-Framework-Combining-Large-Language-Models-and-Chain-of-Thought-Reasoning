```json
[
  {
    "rule_id": "no-global-state",
    "severity": "error",
    "message": "Use of global state ('STATE') reduces modularity and testability.",
    "line": 14,
    "suggestion": "Encapsulate game state in a class or pass it explicitly."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic numbers used in calculations (e.g., 57, 10, 15).",
    "line": 59,
    "suggestion": "Replace magic numbers with named constants."
  },
  {
    "rule_id": "no-duplicated-code",
    "severity": "warning",
    "message": "Repeated modulo operations on color components can be extracted.",
    "line": 33,
    "suggestion": "Create helper functions for color updates."
  },
  {
    "rule_id": "no-unreachable-code",
    "severity": "warning",
    "message": "Unreachable code after `STATE['running'] = False` in event loop.",
    "line": 53,
    "suggestion": "Consider early exit or restructuring the loop."
  },
  {
    "rule_id": "no-implicit-logic",
    "severity": "error",
    "message": "Inconsistent movement logic due to conditional velocity checks.",
    "line": 38,
    "suggestion": "Ensure consistent behavior when velocity is zero."
  },
  {
    "rule_id": "no-hardcoded-colors",
    "severity": "warning",
    "message": "Hardcoded RGB values used directly in rendering.",
    "line": 44,
    "suggestion": "Define colors as constants or use a configuration module."
  },
  {
    "rule_id": "no-unsafe-operations",
    "severity": "warning",
    "message": "Potential division by zero or invalid square root in movement logic.",
    "line": 27,
    "suggestion": "Add explicit bounds checking before sqrt or division."
  }
]
```
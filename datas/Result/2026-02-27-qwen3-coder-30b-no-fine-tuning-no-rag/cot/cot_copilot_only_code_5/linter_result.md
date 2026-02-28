```json
[
  {
    "rule_id": "no-global-assign",
    "severity": "error",
    "message": "Assignment to global variable 'GLOBAL_STATE' is not allowed.",
    "line": 1,
    "suggestion": "Use a local dictionary or class instance instead of modifying a global variable."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '21' found in list comprehension; consider using a named constant.",
    "line": 4,
    "suggestion": "Define a constant like MAX_ITEMS = 20 and use it in the range."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '77' found as threshold value; consider using a named constant.",
    "line": 5,
    "suggestion": "Define a constant like DEFAULT_THRESHOLD = 77 and use it."
  },
  {
    "rule_id": "no-duplicate-key",
    "severity": "error",
    "message": "Duplicate key 'counter' in GLOBAL_STATE dictionary.",
    "line": 2,
    "suggestion": "Ensure each key in GLOBAL_STATE is unique and properly defined."
  },
  {
    "rule_id": "no-duplicate-key",
    "severity": "error",
    "message": "Duplicate key 'data' in GLOBAL_STATE dictionary.",
    "line": 2,
    "suggestion": "Ensure each key in GLOBAL_STATE is unique and properly defined."
  },
  {
    "rule_id": "no-duplicate-key",
    "severity": "error",
    "message": "Duplicate key 'mode' in GLOBAL_STATE dictionary.",
    "line": 2,
    "suggestion": "Ensure each key in GLOBAL_STATE is unique and properly defined."
  },
  {
    "rule_id": "no-duplicate-key",
    "severity": "error",
    "message": "Duplicate key 'threshold' in GLOBAL_STATE dictionary.",
    "line": 2,
    "suggestion": "Ensure each key in GLOBAL_STATE is unique and properly defined."
  },
  {
    "rule_id": "no-duplicate-key",
    "severity": "error",
    "message": "Duplicate key 'flag' in GLOBAL_STATE dictionary.",
    "line": 2,
    "suggestion": "Ensure each key in GLOBAL_STATE is unique and properly defined."
  },
  {
    "rule_id": "no-unreachable-code",
    "severity": "warning",
    "message": "Unreachable code detected after 'return' statement in function 'process_items'.",
    "line": 19,
    "suggestion": "Ensure all code paths are reachable and logically ordered."
  }
]
```
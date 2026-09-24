```json
[
  {
    "rule_id": "shared-mutable-state",
    "severity": "error",
    "message": "Global mutable state (DATA, RESULTS) is used to store application data. This introduces hidden coupling and is not thread-safe in a web server environment.",
    "line": 6,
    "suggestion": "Use a database or a proper state management system (e.g., Redis) to store data."
  },
  {
    "rule_id": "shared-mutable-state",
    "severity": "error",
    "message": "Global mutable state (RESULTS) is used to store application data. This introduces hidden coupling and is not thread-safe in a web server environment.",
    "line": 7,
    "suggestion": "Use a database or a proper state management system (e.g., Redis) to store data."
  },
  {
    "rule_id": "naming-conventions",
    "severity": "warning",
    "message": "Variable 'meanVal' uses camelCase, which is inconsistent with Python's snake_case convention (PEP 8).",
    "line": 27,
    "suggestion": "Rename 'meanVal' to 'mean_val'."
  },
  {
    "rule_id": "unnecessary-work-in-loop",
    "severity": "warning",
    "message": "Redundant computation: statistics.mean(DATA) is called twice and stored in two different keys.",
    "line": 29,
    "suggestion": "Reuse the 'meanVal' variable instead of recalculating the mean."
  },
  {
    "rule_id": "unnecessary-work-in-loop",
    "severity": "warning",
    "message": "Redundant computation: statistics.median(DATA) is called twice.",
    "line": 36,
    "suggestion": "Calculate the median once and store it in a variable before using it for multiple assignments."
  },
  {
    "rule_id": "implicit-truthiness",
    "severity": "info",
    "message": "Using 'len(DATA) == 0' is explicit, but checking for empty containers can be simplified or standardized.",
    "line": 24,
    "suggestion": "Consider 'if not DATA:' for idiomatic Python, or maintain explicit comparison if preferred for clarity."
  }
]
```
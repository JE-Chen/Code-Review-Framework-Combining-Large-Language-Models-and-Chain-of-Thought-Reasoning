```json
[
  {
    "rule_id": "shared-mutable-state",
    "severity": "error",
    "message": "Use of global mutable state (DATA, RESULTS) can lead to race conditions and hidden coupling in a web application.",
    "line": 6,
    "suggestion": "Use a database or a proper state management system instead of global variables."
  },
  {
    "rule_id": "shared-mutable-state",
    "severity": "error",
    "message": "Use of global mutable state (DATA, RESULTS) can lead to race conditions and hidden coupling in a web application.",
    "line": 7,
    "suggestion": "Use a database or a proper state management system instead of global variables."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 'meanVal' does not follow the snake_case naming convention for Python variables.",
    "line": 27,
    "suggestion": "Rename 'meanVal' to 'mean_val'."
  },
  {
    "rule_id": "duplicate-code",
    "severity": "info",
    "message": "Redundant call to statistics.mean(DATA).",
    "line": 29,
    "suggestion": "Use the already calculated 'meanVal' variable."
  },
  {
    "rule_id": "duplicate-code",
    "severity": "info",
    "message": "Redundant call to statistics.median(DATA).",
    "line": 36,
    "suggestion": "Store the result of statistics.median(DATA) in a variable and reuse it."
  }
]
```
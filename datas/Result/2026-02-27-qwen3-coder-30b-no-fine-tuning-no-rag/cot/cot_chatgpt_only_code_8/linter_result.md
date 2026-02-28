```json
[
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Variable 'app' is defined but never used.",
    "line": 10,
    "suggestion": "Remove unused variable 'app' or use it in the application."
  },
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Variable 'last_action' is assigned but never used outside of assignment.",
    "line": 54,
    "suggestion": "Consider removing or using 'last_action' for additional functionality."
  },
  {
    "rule_id": "no-implicit-any",
    "severity": "error",
    "message": "Implicit any type for parameter 'self' in method 'add_user'.",
    "line": 40,
    "suggestion": "Explicitly type the 'self' parameter as 'MainWindow' if needed."
  },
  {
    "rule_id": "no-implicit-any",
    "severity": "error",
    "message": "Implicit any type for parameter 'self' in method 'delete_user'.",
    "line": 58,
    "suggestion": "Explicitly type the 'self' parameter as 'MainWindow' if needed."
  },
  {
    "rule_id": "no-implicit-any",
    "severity": "error",
    "message": "Implicit any type for parameter 'self' in method 'refresh_status'.",
    "line": 66,
    "suggestion": "Explicitly type the 'self' parameter as 'MainWindow' if needed."
  },
  {
    "rule_id": "no-empty-block",
    "severity": "warning",
    "message": "Empty block detected in exception handler.",
    "line": 49,
    "suggestion": "Add specific exception handling or a comment explaining why the block is intentionally empty."
  },
  {
    "rule_id": "no-global-assign",
    "severity": "error",
    "message": "Assignment to global variable 'app' is discouraged.",
    "line": 10,
    "suggestion": "Avoid assigning to global variables; consider encapsulating within a function or class."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '1000' found in timer start.",
    "line": 51,
    "suggestion": "Replace magic number with named constant like 'REFRESH_INTERVAL_MS'."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic numbers '0.3' and '0.2' found in sleep calls.",
    "line": 50,
    "suggestion": "Use constants instead of hardcoded floats for better readability."
  },
  {
    "rule_id": "no-duplicate-key",
    "severity": "error",
    "message": "Duplicate key 'name' in dictionary literal.",
    "line": 53,
    "suggestion": "Ensure all keys in dictionaries are unique."
  }
]
```
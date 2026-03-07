```json
[
  {
    "rule_id": "missing-docstrings",
    "severity": "error",
    "message": "Class and function docstrings are missing.",
    "line": 12,
    "suggestion": "Add docstrings to classes and methods for clarity."
  },
  {
    "rule_id": "no-exception-handling",
    "severity": "warning",
    "message": "Uncaught exceptions are not handled in fetch method.",
    "line": 14,
    "suggestion": "Wrap exceptions in try/except blocks for better error propagation."
  },
  {
    "rule_id": "no-global-variable-usage",
    "severity": "warning",
    "message": "GLOBAL_CACHE is used but not declared in the class.",
    "line": 10,
    "suggestion": "Declare GLOBAL_CACHE as a class-level variable for clarity."
  },
  {
    "rule_id": "no-conditional-logic",
    "severity": "info",
    "message": "Conditional logic in process_all is not well-documented.",
    "line": 18,
    "suggestion": "Add comments explaining the logic behind result filtering."
  }
]
```
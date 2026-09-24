```json
[
  {
    "rule_id": "no-global-variables",
    "severity": "error",
    "message": "Usage of global variables (GLOBAL_TEXT, GLOBAL_COUNTER, GLOBAL_MODE) reduces modularity and testability.",
    "line": 5,
    "suggestion": "Replace globals with instance attributes or pass data through parameters."
  },
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Variable 'GLOBAL_MODE' is set but not used in all handler functions.",
    "line": 28,
    "suggestion": "Remove unused variable or ensure consistent usage."
  },
  {
    "rule_id": "no-duplicated-code",
    "severity": "warning",
    "message": "Logic in handle_btn2 duplicates conditional checks that could be abstracted.",
    "line": 28,
    "suggestion": "Refactor repeated conditionals into helper methods for clarity."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '5' used in comparison without explanation.",
    "line": 28,
    "suggestion": "Define constant with descriptive name like MAX_THRESHOLD."
  },
  {
    "rule_id": "no-hardcoded-strings",
    "severity": "warning",
    "message": "Hardcoded strings like 'Status: Ready', 'Counter small:', etc., reduce maintainability.",
    "line": 18,
    "suggestion": "Move hardcoded strings to constants or configuration."
  },
  {
    "rule_id": "no-unchecked-input",
    "severity": "warning",
    "message": "Input from QLineEdit is directly concatenated without validation.",
    "line": 19,
    "suggestion": "Validate and sanitize input before appending to GLOBAL_TEXT."
  }
]
```
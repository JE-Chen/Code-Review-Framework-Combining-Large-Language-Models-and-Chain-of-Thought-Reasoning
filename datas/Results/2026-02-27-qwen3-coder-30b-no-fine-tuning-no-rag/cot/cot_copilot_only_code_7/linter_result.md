```json
[
  {
    "rule_id": "no-global-variables",
    "severity": "error",
    "message": "Usage of global variables (GLOBAL_TEXT, GLOBAL_COUNTER, GLOBAL_MODE) reduces modularity and testability.",
    "line": 5,
    "suggestion": "Replace global variables with instance attributes or pass data through parameters."
  },
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Variable 'GLOBAL_MODE' is referenced in handle_btn2 but never updated outside of reset functionality.",
    "line": 29,
    "suggestion": "Consider removing unused or redundant global state."
  },
  {
    "rule_id": "no-duplicate-code",
    "severity": "warning",
    "message": "The logic in handle_btn1 and handle_btn3 both modify GLOBAL_TEXT and GLOBAL_COUNTER, leading to duplicated behavior.",
    "line": 18,
    "suggestion": "Extract shared logic into a helper method to reduce duplication."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "The number 5 is used as a magic number in handle_btn2 to determine counter size.",
    "line": 26,
    "suggestion": "Define this value as a named constant for clarity and maintainability."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "The number 2 is used as a magic number in handle_btn2 to check even/odd status.",
    "line": 32,
    "suggestion": "Use a named constant instead of hardcoding 2 for readability."
  },
  {
    "rule_id": "no-hardcoded-strings",
    "severity": "warning",
    "message": "String literals like 'Status: Ready', 'Status: Updated', and 'Status: Reset Done' are hardcoded and should be extracted into constants.",
    "line": 14,
    "suggestion": "Move string literals to a constants module or class for consistency and localization support."
  }
]
```
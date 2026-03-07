```json
[
  {
    "rule_id": "no-global-variables",
    "severity": "error",
    "message": "Global variables 'conn' and 'cursorThing' are used, which reduces modularity and testability.",
    "line": 3,
    "suggestion": "Pass database connections as parameters or use dependency injection."
  },
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Variables 'anotherName' and 'anotherAge' are defined but could be simplified into a loop or list.",
    "line": 19,
    "suggestion": "Refactor repeated insertions into a loop with data structures."
  },
  {
    "rule_id": "no-duplicate-code",
    "severity": "error",
    "message": "SQL string concatenation is repeated multiple times, increasing risk of SQL injection and reducing readability.",
    "line": 15,
    "suggestion": "Use parameterized queries instead of string concatenation."
  },
  {
    "rule_id": "no-bare-except",
    "severity": "error",
    "message": "Catch-all exception handling suppresses errors without logging or proper recovery.",
    "line": 10,
    "suggestion": "Catch specific exceptions and log them appropriately."
  },
  {
    "rule_id": "no-bare-except",
    "severity": "error",
    "message": "Catch-all exception handling suppresses errors without logging or proper recovery.",
    "line": 24,
    "suggestion": "Catch specific exceptions and log them appropriately."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic numbers like 0 and 1 are used directly in indexing, making code less readable.",
    "line": 28,
    "suggestion": "Use named constants or descriptive variable names for indices."
  },
  {
    "rule_id": "no-long-function",
    "severity": "error",
    "message": "Function 'functionThatDoesTooManyThingsAndIsHardToRead' does too many things and violates single responsibility principle.",
    "line": 5,
    "suggestion": "Break down the function into smaller, focused functions."
  },
  {
    "rule_id": "no-hardcoded-strings",
    "severity": "warning",
    "message": "Hardcoded strings such as table and column names reduce flexibility and readability.",
    "line": 10,
    "suggestion": "Move hardcoded values to configuration or constants."
  }
]
```
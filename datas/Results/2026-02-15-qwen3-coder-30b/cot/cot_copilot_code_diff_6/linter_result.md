```json
[
  {
    "rule_id": "no-global-assign",
    "severity": "error",
    "message": "Assignment to global variable 'GLOBAL_SESSION' is discouraged.",
    "line": 3,
    "suggestion": "Avoid modifying global state; use local variables or dependency injection."
  },
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Unused variable 'ANOTHER_GLOBAL' declared but not used in scope.",
    "line": 4,
    "suggestion": "Remove unused global variable or use it in logic."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '200' used directly instead of a named constant.",
    "line": 19,
    "suggestion": "Define a constant like HTTP_OK = 200 for better readability."
  },
  {
    "rule_id": "no-catch-exception",
    "severity": "error",
    "message": "Catching generic Exception without handling or re-raising can mask bugs.",
    "line": 10,
    "suggestion": "Catch specific exceptions or at least log and re-raise the error."
  },
  {
    "rule_id": "no-empty-except",
    "severity": "error",
    "message": "Empty except block ignores all exceptions silently.",
    "line": 22,
    "suggestion": "Handle exceptions explicitly or raise them after logging."
  },
  {
    "rule_id": "no-console-log",
    "severity": "warning",
    "message": "Use of print() statements makes code hard to test and maintain.",
    "line": 8,
    "suggestion": "Replace print() calls with proper logging framework."
  },
  {
    "rule_id": "no-long-function",
    "severity": "error",
    "message": "Function performs too many unrelated tasks and violates single responsibility principle.",
    "line": 6,
    "suggestion": "Break function into smaller, focused helper functions."
  },
  {
    "rule_id": "no-implicit-boolean-check",
    "severity": "warning",
    "message": "Checking response status using direct equality rather than explicit boolean check.",
    "line": 19,
    "suggestion": "Explicitly check if response.ok or compare against expected codes."
  }
]
```
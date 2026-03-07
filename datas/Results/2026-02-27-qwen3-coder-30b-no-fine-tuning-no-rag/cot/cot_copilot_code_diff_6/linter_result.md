```json
[
  {
    "rule_id": "no-global-assign",
    "severity": "error",
    "message": "Assignment to global variable 'GLOBAL_SESSION' is not allowed.",
    "line": 3,
    "suggestion": "Avoid modifying global variables. Consider passing dependencies as parameters or using a class-based approach."
  },
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Unused variable 'ANOTHER_GLOBAL' declared but never used.",
    "line": 4,
    "suggestion": "Remove unused global variable 'ANOTHER_GLOBAL' if it's not needed."
  },
  {
    "rule_id": "function-name",
    "severity": "warning",
    "message": "Function name 'functionThatDoesTooMuchAndIsHardToUnderstand' is too long and doesn't clearly describe what it does.",
    "line": 6,
    "suggestion": "Rename the function to better reflect its specific responsibilities, e.g., 'fetch_and_print_post_data'."
  },
  {
    "rule_id": "no-catch-undefined",
    "severity": "error",
    "message": "Catching generic Exception without specifying type can hide unexpected errors.",
    "line": 10,
    "suggestion": "Catch specific exceptions like `requests.exceptions.RequestException` instead of bare `except:`."
  },
  {
    "rule_id": "no-catch-undefined",
    "severity": "error",
    "message": "Catching all exceptions with bare 'except:' clause prevents proper error propagation.",
    "line": 18,
    "suggestion": "Use specific exception types such as `requests.exceptions.RequestException` to handle expected failures."
  },
  {
    "rule_id": "variable-naming",
    "severity": "warning",
    "message": "Variable name 'weirdVariableName' is not descriptive enough.",
    "line": 22,
    "suggestion": "Use a more descriptive name like 'post_response' to clarify its purpose."
  },
  {
    "rule_id": "no-console",
    "severity": "warning",
    "message": "Console output (print) should not be used in production code.",
    "line": 11,
    "suggestion": "Replace print statements with logging for better control over output and debugging."
  },
  {
    "rule_id": "no-console",
    "severity": "warning",
    "message": "Console output (print) should not be used in production code.",
    "line": 12,
    "suggestion": "Replace print statements with logging for better control over output and debugging."
  },
  {
    "rule_id": "no-console",
    "severity": "warning",
    "message": "Console output (print) should not be used in production code.",
    "line": 15,
    "suggestion": "Replace print statements with logging for better control over output and debugging."
  },
  {
    "rule_id": "no-console",
    "severity": "warning",
    "message": "Console output (print) should not be used in production code.",
    "line": 16,
    "suggestion": "Replace print statements with logging for better control over output and debugging."
  },
  {
    "rule_id": "no-console",
    "severity": "warning",
    "message": "Console output (print) should not be used in production code.",
    "line": 20,
    "suggestion": "Replace print statements with logging for better control over output and debugging."
  },
  {
    "rule_id": "no-console",
    "severity": "warning",
    "message": "Console output (print) should not be used in production code.",
    "line": 23,
    "suggestion": "Replace print statements with logging for better control over output and debugging."
  }
]
```
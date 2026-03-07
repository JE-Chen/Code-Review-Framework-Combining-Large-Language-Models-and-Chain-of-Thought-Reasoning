```json
[
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Variable 'GLOBAL_CACHE' is declared but not used in the functions.",
    "line": 5,
    "suggestion": "Remove or comment out 'GLOBAL_CACHE' if it's not used."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "warning",
    "message": "Function 'process_all()' lacks docstring.",
    "line": 13,
    "suggestion": "Add a docstring explaining the function's purpose and behavior."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "warning",
    "message": "Function 'main()' lacks docstring.",
    "line": 17,
    "suggestion": "Add a docstring explaining the main function's purpose."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "warning",
    "message": "Function 'get_users()' lacks docstring.",
    "line": 12,
    "suggestion": "Add a docstring explaining the function's purpose and parameters."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "warning",
    "message": "Function 'get_posts()' lacks docstring.",
    "line": 14,
    "suggestion": "Add a docstring explaining the function's purpose and parameters."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "warning",
    "message": "Function 'get_todos()' lacks docstring.",
    "line": 16,
    "suggestion": "Add a docstring explaining the function's purpose and parameters."
  },
  {
    "rule_id": "no-exception-handling-specific",
    "severity": "warning",
    "message": "The 'fetch()' method catches a general exception without specifying the type.",
    "line": 10,
    "suggestion": "Catch specific exceptions like ConnectionError or Timeout for better error handling."
  },
  {
    "rule_id": "duplicate-code",
    "severity": "warning",
    "message": "The 'get_users()', 'get_posts()', and 'get_todos()' functions share similar logic.",
    "line": 12,
    "suggestion": "Refactor into a common helper function to reduce duplication."
  }
]
```
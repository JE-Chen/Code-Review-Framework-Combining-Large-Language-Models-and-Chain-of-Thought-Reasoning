```json
[
  {
    "rule_id": "no-global-variables",
    "severity": "warning",
    "message": "Usage of global variable 'GLOBAL_CACHE' reduces modularity and testability.",
    "line": 8,
    "suggestion": "Pass cache as a parameter or use a class-based approach to encapsulate state."
  },
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Variable 'r' in the main loop is unused; it's only used for printing.",
    "line": 48,
    "suggestion": "Remove unused variable or refactor to use it meaningfully."
  },
  {
    "rule_id": "no-duplicate-code",
    "severity": "warning",
    "message": "Functions 'get_users', 'get_posts', and 'get_todos' have nearly identical logic and can be refactored into one generic function.",
    "line": 21,
    "suggestion": "Create a single reusable function that accepts an endpoint and handles caching."
  },
  {
    "rule_id": "no-implicit-exception-handling",
    "severity": "warning",
    "message": "Catching all exceptions without specifying types may mask unexpected errors.",
    "line": 16,
    "suggestion": "Catch specific exceptions such as requests.RequestException or ValueError."
  },
  {
    "rule_id": "no-hardcoded-values",
    "severity": "warning",
    "message": "Hardcoded strings like 'Special User:', 'Long Post:', etc., should be extracted to constants or configuration.",
    "line": 37,
    "suggestion": "Define these string literals as constants at module level for consistency and maintainability."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic numbers 5 and 20 are used directly in conditional logic; consider extracting them into named constants.",
    "line": 51,
    "suggestion": "Replace magic numbers with named constants (e.g., MIN_RESULTS_THRESHOLD, MAX_RESULTS_THRESHOLD)."
  },
  {
    "rule_id": "no-side-effects-in-functions",
    "severity": "warning",
    "message": "Function 'get_users', 'get_posts', and 'get_todos' modify the global cache, which creates side effects.",
    "line": 21,
    "suggestion": "Avoid modifying external state from functions; instead, return data and let calling code handle caching."
  },
  {
    "rule_id": "no-unneeded-else",
    "severity": "warning",
    "message": "Nested if statements can be simplified by restructuring logic.",
    "line": 53,
    "suggestion": "Simplify nested conditionals using elif or early returns to improve readability."
  }
]
```
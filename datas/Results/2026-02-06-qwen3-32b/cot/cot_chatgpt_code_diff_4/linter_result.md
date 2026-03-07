[
  {
    "rule_id": "sql-injection",
    "severity": "error",
    "message": "SQL query built with string interpolation using unvalidated input may lead to SQL injection vulnerability.",
    "line": 24,
    "suggestion": "Use parameterized queries to prevent SQL injection."
  },
  {
    "rule_id": "global-state",
    "severity": "warning",
    "message": "Global database connection and cursor variables make the code less testable and maintainable.",
    "line": 6,
    "suggestion": "Encapsulate database operations in a class or use dependency injection."
  },
  {
    "rule_id": "no-docstring",
    "severity": "info",
    "message": "Function lacks a docstring explaining its purpose and usage.",
    "line": 10,
    "suggestion": "Add a docstring to describe the function's behavior and parameters."
  },
  {
    "rule_id": "conditional-commit",
    "severity": "warning",
    "message": "Conditional commit based on random choice may lead to inconsistent state.",
    "line": 27,
    "suggestion": "Commit transactions consistently or use a transaction manager."
  },
  {
    "rule_id": "bad-function-name",
    "severity": "warning",
    "message": "Function name is unclear and contains unnecessary negative phrasing.",
    "line": 44,
    "suggestion": "Rename to reflect actual business logic, e.g., 'generate_user_activity_logs'."
  },
  {
    "rule_id": "swallow-exception",
    "severity": "warning",
    "message": "Catching all exceptions and ignoring them may hide serious errors.",
    "line": 55,
    "suggestion": "Handle specific exceptions or log the error instead of swallowing."
  }
]
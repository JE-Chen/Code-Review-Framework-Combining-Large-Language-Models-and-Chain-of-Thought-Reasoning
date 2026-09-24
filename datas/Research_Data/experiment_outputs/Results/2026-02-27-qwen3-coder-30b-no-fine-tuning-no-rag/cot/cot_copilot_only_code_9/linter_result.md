```json
[
  {
    "rule_id": "no-global-variables",
    "severity": "warning",
    "message": "Use of global variable 'GLOBAL_RESULTS' reduces modularity and testability.",
    "line": 5,
    "suggestion": "Pass results as parameters or return them from functions instead of using a global variable."
  },
  {
    "rule_id": "no-duplicate-code",
    "severity": "error",
    "message": "Duplicate code pattern found in get_users, get_posts, and get_comments functions.",
    "line": 10,
    "suggestion": "Refactor into a single reusable function that accepts endpoint as parameter."
  },
  {
    "rule_id": "no-duplicate-code",
    "severity": "error",
    "message": "Duplicate code pattern found in get_users, get_posts, and get_comments functions.",
    "line": 17,
    "suggestion": "Refactor into a single reusable function that accepts endpoint as parameter."
  },
  {
    "rule_id": "no-duplicate-code",
    "severity": "error",
    "message": "Duplicate code pattern found in get_users, get_posts, and get_comments functions.",
    "line": 24,
    "suggestion": "Refactor into a single reusable function that accepts endpoint as parameter."
  },
  {
    "rule_id": "no-bad-exception-handling",
    "severity": "warning",
    "message": "Catching generic Exception may hide unexpected errors; consider catching specific exceptions.",
    "line": 11,
    "suggestion": "Catch more specific exceptions like requests.exceptions.RequestException."
  },
  {
    "rule_id": "no-bad-exception-handling",
    "severity": "warning",
    "message": "Catching generic Exception may hide unexpected errors; consider catching specific exceptions.",
    "line": 18,
    "suggestion": "Catch more specific exceptions like requests.exceptions.RequestException."
  },
  {
    "rule_id": "no-bad-exception-handling",
    "severity": "warning",
    "message": "Catching generic Exception may hide unexpected errors; consider catching specific exceptions.",
    "line": 25,
    "suggestion": "Catch more more specific exceptions like requests.exceptions.RequestException."
  },
  {
    "rule_id": "no-unhandled-errors",
    "severity": "warning",
    "message": "Errors are printed but not re-raised or handled further, potentially masking issues.",
    "line": 12,
    "suggestion": "Consider logging the error or re-raising it for proper error propagation."
  },
  {
    "rule_id": "no-unhandled-errors",
    "severity": "warning",
    "message": "Errors are printed but not re-raised or handled further, potentially masking issues.",
    "line": 19,
    "suggestion": "Consider logging the error or re-raising it for proper error propagation."
  },
  {
    "rule_id": "no-unhandled-errors",
    "severity": "warning",
    "message": "Errors are printed but not re-raised or handled further, potentially masking issues.",
    "line": 26,
    "suggestion": "Consider logging the error or re-raising it for proper error propagation."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic numbers used in conditional checks (10, 50) reduce readability and maintainability.",
    "line": 36,
    "suggestion": "Define named constants for these values to improve clarity."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic numbers used in conditional checks (10, 50) reduce readability and maintainability.",
    "line": 39,
    "suggestion": "Define named constants for these values to improve clarity."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic numbers used in conditional checks (10, 50) reduce readability and maintainability.",
    "line": 42,
    "suggestion": "Define named constants for these values to improve clarity."
  }
]
```